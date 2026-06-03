#!/usr/bin/env python3
"""
ACW Executor — AI Company Wars 自动调度器 v2

功能:
  1. 自动扫描 round 状态，推进角色链
  2. 红蓝双队并行执行同阶段角色
  3. 卡住检测（超时报警 + 自动重试）
  4. 两队完成后自动触发 Judge
  5. P0: 死循环熔断（QA 连续失败自动标记 requires_human）
  6. P1: Git push 自动化（token 检查 + 四步验证）
  7. P2: 自动推进 + 缓冲期（Judge 后自动开下一轮）
  8. P3: --preview 模式（PM→Dev→QA 跑通不 push 不 deploy）

用法:
  python3 scripts/executor.py                           # 推进当前轮次
  python3 scripts/executor.py --dry-run                 # 只看不跑
  python3 scripts/executor.py --status                  # 查看状态
  python3 scripts/executor.py --new-round 2026-round-6  # 创建新轮次
  python3 scripts/executor.py --preview 2026-round-6    # 预览模式
  python3 scripts/executor.py --reset-circuit red       # 重置熔断器
"""

import argparse
import json
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone, timedelta

# ── 路径常量 ──────────────────────────────────────────────

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROUND_JSON = os.path.join(BASE_DIR, "runtime", "round.json")
RUNNER = os.path.join(BASE_DIR, "scripts", "run-round.py")
LOGS_DIR = os.path.join(BASE_DIR, "logs")

# 角色执行顺序（per-team）
ROLE_CHAIN = ["product", "dev", "devops", "growth"]

# 角色 → Hermes skill 名
ROLE_SKILL = {
    "product": "ai-company-wars-product",
    "dev": "ai-company-wars-dev",
    "devops": "ai-company-wars-devops",
    "growth": "ai-company-wars-growth",
    "judge": "ai-company-wars-judge",
}

# Round 状态 → 应执行的角色
STATE_TO_ROLE = {
    "ROUND_CREATED": "product",
    "PLANNING": "product",
    "DEVELOPMENT": "dev",
    "RELEASING": "devops",
    "PROMOTING": "growth",
    "JUDGING": "judge",
}

# ── P0: 熔断器配置 ────────────────────────────────────────

CIRCUIT_BREAKER_THRESHOLD = 3  # QA 连续失败 N 次触发熔断

# ── P2: 自动推进配置 ──────────────────────────────────────

ROUND_ADVANCE_POLICY = "manual"  # "manual" | "auto_30min" | "auto_1hour"
ROUND_ADVANCE_BUFFER_SECONDS = {
    "manual": 0,
    "auto_30min": 1800,
    "auto_1hour": 3600,
}

# ── P1: Git push 配置 ─────────────────────────────────────

GITHUB_API = "https://api.github.com"

# 默认卡住阈值（分钟）
DEFAULT_STUCK_THRESHOLD = 30

os.makedirs(LOGS_DIR, exist_ok=True)


# ── 日志 ──────────────────────────────────────────────────

def log(msg: str):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    log_file = os.path.join(LOGS_DIR, f"{datetime.now().strftime('%Y-%m-%d')}.log")
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(line + "\n")


# ── JSON 工具 ─────────────────────────────────────────────

def read_json(path):
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def now_iso():
    return datetime.now(timezone.utc).isoformat()


# ── 状态查询 ──────────────────────────────────────────────

def get_team_status(team: str) -> dict | None:
    path = os.path.join(BASE_DIR, "teams", team, "runtime", "status.json")
    return read_json(path)


def save_team_status(team: str, status: dict):
    path = os.path.join(BASE_DIR, "teams", team, "runtime", "status.json")
    write_json(path, status)


def get_round_data() -> dict | None:
    return read_json(ROUND_JSON)


def get_role_status(team: str, role: str) -> str:
    ts = get_team_status(team)
    if ts is None:
        return "missing"
    return ts.get("roles", {}).get(role, {}).get("status", "pending")


def is_role_done(status: str) -> bool:
    return status in ("completed", "skipped")


def is_role_ended(status: str) -> bool:
    """角色是否已结束（含失败/阻塞），用于判断阶段是否可以推进"""
    return status in ("completed", "skipped", "failed", "blocked")


def is_role_running(status: str) -> bool:
    return status == "in_progress"


# ── 卡住检测 ──────────────────────────────────────────────

def check_stuck(team: str, role: str, threshold_min: int) -> tuple[bool, str]:
    """检查角色是否卡在 in_progress 超时"""
    ts = get_team_status(team)
    if ts is None:
        return False, "no status file"

    role_data = ts.get("roles", {}).get(role, {})
    if role_data.get("status") != "in_progress":
        return False, "not in_progress"

    last_run = role_data.get("last_run")
    if not last_run:
        return False, "no last_run"

    try:
        last = datetime.fromisoformat(last_run)
    except ValueError:
        return False, "bad last_run format"

    elapsed = datetime.now(timezone.utc) - last
    if elapsed > timedelta(minutes=threshold_min):
        return True, f"in_progress 已 {elapsed.total_seconds() / 60:.0f} 分钟 (阈值 {threshold_min}min)"
    return False, f"running {elapsed.total_seconds() / 60:.1f} min"


# ── P0: 熔断器 ───────────────────────────────────────────

def get_circuit_breaker(team: str) -> dict:
    """获取熔断器状态"""
    ts = get_team_status(team)
    if ts is None:
        return {"consecutive_qa_failures": 0, "threshold": CIRCUIT_BREAKER_THRESHOLD, "blocked": False}
    return ts.get("circuit_breaker", {
        "consecutive_qa_failures": 0,
        "threshold": CIRCUIT_BREAKER_THRESHOLD,
        "blocked": False,
        "reason": None,
    })


def update_circuit_breaker(team: str, qa_success: bool):
    """更新熔断器：QA 成功则归零，失败则累加"""
    ts = get_team_status(team)
    if ts is None:
        return

    cb = ts.get("circuit_breaker", {
        "consecutive_qa_failures": 0,
        "threshold": CIRCUIT_BREAKER_THRESHOLD,
        "blocked": False,
        "reason": None,
    })

    if qa_success:
        cb["consecutive_qa_failures"] = 0
    else:
        cb["consecutive_qa_failures"] += 1
        if cb["consecutive_qa_failures"] >= cb["threshold"]:
            cb["blocked"] = True
            cb["reason"] = f"QA 连续失败 {cb['consecutive_qa_failures']} 次，触发熔断"
            log(f"🔥 [{team}] 熔断触发: {cb['reason']}")

    ts["circuit_breaker"] = cb
    save_team_status(team, ts)


def check_circuit_breaker(team: str) -> tuple[bool, str]:
    """检查熔断器是否阻塞。返回 (blocked, reason)"""
    cb = get_circuit_breaker(team)
    if cb.get("blocked"):
        return True, cb.get("reason", "circuit breaker triggered")
    return False, ""


def reset_circuit_breaker(team: str):
    """重置熔断器"""
    ts = get_team_status(team)
    if ts is None:
        log(f"❌ {team} 无状态文件")
        return
    ts["circuit_breaker"] = {
        "consecutive_qa_failures": 0,
        "threshold": CIRCUIT_BREAKER_THRESHOLD,
        "blocked": False,
        "reason": None,
    }
    save_team_status(team, ts)
    log(f"✅ [{team}] 熔断器已重置")


# ── P1: Git push 自动化 ──────────────────────────────────

def check_github_token() -> tuple[bool, str]:
    """检查 GitHub token 是否有效"""
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GITHUB_TOKEN_Classic")
    if not token:
        # 尝试从 .env 文件读取
        env_file = os.path.expanduser("~/.hermes/.env")
        if os.path.exists(env_file):
            for line in open(env_file):
                if line.startswith("GITHUB_TOKEN=") and not line.startswith("#"):
                    token = line.strip().split("=", 1)[1]
                    break
    if not token:
        # 尝试从 Windows 环境变量读取
        try:
            proc = subprocess.run(
                ["powershell.exe", "-Command", "[Environment]::GetEnvironmentVariable('GITHUB_TOKEN_Classic', 'User')"],
                capture_output=True, text=True, timeout=10,
            )
            token = proc.stdout.strip().replace("\r", "").replace("\n", "")
        except Exception:
            pass

    if not token:
        return False, "未找到 GitHub token (GITHUB_TOKEN / GITHUB_TOKEN_Classive)"

    # 验证 token 有效性
    try:
        proc = subprocess.run(
            ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}",
             "-H", f"Authorization: token {token}", f"{GITHUB_API}/user"],
            capture_output=True, text=True, timeout=15,
        )
        code = proc.stdout.strip()
        if code == "200":
            return True, token
        elif code == "401":
            return False, "GitHub token 无效 (401 Unauthorized)"
        elif code == "403":
            return False, "GitHub API rate limit 或权限不足 (403)"
        else:
            return False, f"GitHub API 返回 {code}"
    except Exception as e:
        return False, f"GitHub API 检查失败: {e}"


def check_git_remote(project_dir: str) -> tuple[bool, str]:
    """检查 git remote 是否已配置"""
    try:
        proc = subprocess.run(
            ["git", "remote", "-v"],
            capture_output=True, text=True, timeout=10,
            cwd=project_dir,
        )
        if "origin" in proc.stdout:
            return True, proc.stdout.strip().split("\n")[0]
        return False, "未配置 origin remote"
    except Exception as e:
        return False, f"git remote 检查失败: {e}"


def auto_push(team: str, round_id: str, dry_run: bool = False) -> dict:
    """
    自动 push 到 GitHub。
    四步检查: token → remote → 有变更 → push
    返回 {"success", "skipped", "reason"}
    """
    project_dir = os.path.join(BASE_DIR, "teams", team, "project")
    result = {"success": False, "skipped": False, "reason": None}

    if not os.path.exists(os.path.join(project_dir, ".git")):
        result["skipped"] = True
        result["reason"] = "项目目录无 .git，跳过 push"
        log(f"[{team}/push] ⏭ {result['reason']}")
        return result

    # Step 1: token 检查
    token_ok, token_info = check_github_token()
    if not token_ok:
        result["skipped"] = True
        result["reason"] = f"token 检查失败: {token_info}"
        log(f"[{team}/push] ⏭ {result['reason']}")
        return result
    token = token_info

    # Step 2: remote 检查
    remote_ok, remote_info = check_git_remote(project_dir)
    if not remote_ok:
        result["skipped"] = True
        result["reason"] = f"remote 检查失败: {remote_info}"
        log(f"[{team}/push] ⏭ {result['reason']}")
        return result

    # Step 3: 有变更？
    try:
        proc = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True, text=True, timeout=10,
            cwd=project_dir,
        )
        has_changes = len(proc.stdout.strip()) > 0
    except Exception:
        has_changes = True  # 保守：假设有变更

    if not has_changes:
        # 检查是否有未 push 的 commit
        try:
            proc = subprocess.run(
                ["git", "log", "origin/main..HEAD", "--oneline"],
                capture_output=True, text=True, timeout=10,
                cwd=project_dir,
            )
            has_unpushed = len(proc.stdout.strip()) > 0
        except Exception:
            has_unpushed = False

        if not has_unpushed:
            result["success"] = True
            result["reason"] = "无变更且无未 push 的 commit"
            log(f"[{team}/push] ✅ {result['reason']}")
            return result

    if dry_run:
        result["success"] = True
        result["reason"] = "dry-run: 将会 push"
        log(f"[{team}/push] ✅ {result['reason']}")
        return result

    # Step 4: push（token 嵌入 URL，git 原生不读环境变量）
    original_url = ""
    try:
        # 获取当前 remote URL
        url_proc = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            capture_output=True, text=True, timeout=10,
            cwd=project_dir,
        )
        original_url = url_proc.stdout.strip()
        # 嵌入 token: https://github.com/... → https://<token>@github.com/...
        if original_url.startswith("https://"):
            auth_url = original_url.replace("https://", f"https://{token}@")
        else:
            auth_url = original_url

        # 临时设置带 token 的 URL
        subprocess.run(
            ["git", "remote", "set-url", "origin", auth_url],
            capture_output=True, text=True, timeout=10,
            cwd=project_dir,
        )

        proc = subprocess.run(
            ["git", "push", "origin", "main"],
            capture_output=True, text=True, timeout=120,
            cwd=project_dir,
        )

        # 恢复原始 URL（不留 token 在 config 里）
        subprocess.run(
            ["git", "remote", "set-url", "origin", original_url],
            capture_output=True, text=True, timeout=10,
            cwd=project_dir,
        )

        if proc.returncode == 0:
            result["success"] = True
            result["reason"] = "push 成功"
            log(f"[{team}/push] ✅ push 成功")
        else:
            result["skipped"] = True
            result["reason"] = f"push 失败: {proc.stderr[-200:]}"
            log(f"[{team}/push] ⏭ {result['reason']}")
    except Exception as e:
        # 异常时也恢复 URL
        try:
            subprocess.run(
                ["git", "remote", "set-url", "origin", original_url],
                capture_output=True, text=True, timeout=10,
                cwd=project_dir,
            )
        except Exception:
            pass
        result["skipped"] = True
        result["reason"] = f"push 异常: {e}"
        log(f"[{team}/push] ⏭ {result['reason']}")

    return result


# ── 执行单个角色 ──────────────────────────────────────────

def run_role(team: str, role: str, round_id: str, dry_run: bool = False,
             preview: bool = False) -> dict:
    """
    执行一个角色的完整流程:
    1. run-round.py --team X --role Y --round Z  (前置检查 + 标记 in_progress)
    2. hermes chat -s <skill> -q <prompt>         (实际执行)
    3. run-round.py --team X --role Y --round Z --complete  (回写状态)

    preview 模式: dev/devops 不 push，devops 不 deploy

    返回 {"team", "role", "success", "duration_s", "error"}
    """
    result = {"team": team, "role": role, "success": False, "duration_s": 0, "error": None}

    # P0: 熔断检查（dev 角色执行前检查 QA 是否熔断）
    if role == "dev":
        blocked, reason = check_circuit_breaker(team)
        if blocked:
            result["error"] = f"熔断: {reason}"
            log(f"[{team}/{role}] 🔥 熔断阻塞: {reason}")
            return result

    # Step 1: 前置检查
    log(f"[{team}/{role}] 前置检查...")
    check_cmd = [sys.executable, RUNNER, "--team", team, "--role", role, "--round", round_id]
    if dry_run:
        check_cmd.append("--dry-run")

    try:
        proc = subprocess.run(check_cmd, capture_output=True, text=True, timeout=30)
        check_output = proc.stdout + proc.stderr
    except subprocess.TimeoutExpired:
        result["error"] = "前置检查超时"
        log(f"[{team}/{role}] ❌ 前置检查超时")
        return result

    # 判断前置检查结论
    if "结论: BLOCKED" in check_output:
        reason = "blocked"
        for line in check_output.split("\n"):
            if "原因:" in line or "不满足" in line:
                reason = line.strip()
                break
        result["error"] = reason
        log(f"[{team}/{role}] 🚫 {reason}")
        return result

    if "结论: SKIPPED" in check_output:
        reason = "skipped"
        for line in check_output.split("\n"):
            if "原因:" in line or "无需重复执行" in line:
                reason = line.strip()
                break
        result["success"] = True
        result["error"] = reason
        log(f"[{team}/{role}] ⏭ {reason}")
        return result

    if "结论: CAN_RUN" not in check_output:
        result["error"] = f"前置检查输出异常: {check_output[-200:]}"
        log(f"[{team}/{role}] ❌ {result['error']}")
        return result

    if dry_run:
        result["success"] = True
        result["error"] = "dry-run"
        log(f"[{team}/{role}] ✅ CAN_RUN (dry-run)")
        return result

    # Step 2: 执行角色
    skill = ROLE_SKILL.get(role)
    if not skill:
        result["error"] = f"未知角色: {role}"
        log(f"[{team}/{role}] ❌ {result['error']}")
        return result

    # P3: preview 模式下注入额外指令
    extra = ""
    if preview:
        if role == "dev":
            extra = "\n\n⚠️ 预览模式：写代码但不要 git push。"
        elif role == "devops":
            extra = "\n\n⚠️ 预览模式：不要实际部署，只写部署文档。"

    log(f"[{team}/{role}] 执行中 (skill: {skill}){'[preview]' if preview else ''}...")
    start = time.time()

    # 轮次上下文（每轮不同的项目方向）
    ROUND_CONTEXT = {
        "2026-round-8": "本轮方向：开发一个 RAG（检索增强生成）相关的 Hermes Agent 技能。技能应帮助用户构建或优化 RAG 系统，例如：PDF 解析、向量检索、混合检索、Reranker 精排、查询分解等。产出是一个完整的 SKILL.md 文件，可直接安装到 Hermes Agent 使用。",
    }
    round_context = ROUND_CONTEXT.get(round_id, "")

    prompt = f"""你是 AI Company Wars 的 {role} 角色。
队伍: {team}
轮次: {round_id}
项目路径: {os.path.join(BASE_DIR, 'teams', team, 'project')}

{round_context}

请加载 {skill} 技能并执行你的职责。{extra}"""

    try:
        exec_proc = subprocess.run(
            ["hermes", "chat", "-s", skill, "-q", prompt],
            capture_output=True, text=True, timeout=900,
            cwd=BASE_DIR,
        )
        duration = time.time() - start
        result["duration_s"] = round(duration, 1)

        if exec_proc.returncode != 0:
            result["error"] = f"hermes chat 退出码 {exec_proc.returncode}: {exec_proc.stderr[-300:]}"
            log(f"[{team}/{role}] ❌ 执行失败 ({duration:.0f}s): {result['error'][:100]}")
            _complete_role(team, role, round_id, "failed", result["error"])
            # P0: 更新熔断器（QA 失败时累加）
            if role == "dev":
                update_circuit_breaker(team, False)
            return result

    except subprocess.TimeoutExpired:
        duration = time.time() - start
        result["duration_s"] = round(duration, 1)
        result["error"] = f"执行超时 ({duration:.0f}s)"
        log(f"[{team}/{role}] ❌ 执行超时")
        _complete_role(team, role, round_id, "failed", "执行超时 900s")
        if role == "dev":
            update_circuit_breaker(team, False)
        return result

    # Step 3: 回写完成
    log(f"[{team}/{role}] 执行完成 ({duration:.0f}s)，回写状态...")
    _complete_role(team, role, round_id, "completed")
    result["success"] = True
    log(f"[{team}/{role}] ✅ 完成")

    # P0: QA 成功时归零熔断器
    if role == "dev":
        update_circuit_breaker(team, True)

    # P1: dev 完成后自动 push（非 preview）
    if role == "dev" and not preview:
        push_result = auto_push(team, round_id, dry_run)
        result["push"] = push_result

    return result


def _complete_role(team: str, role: str, round_id: str, result: str, error_msg: str | None = None):
    """调用 run-round.py --complete 回写状态"""
    cmd = [sys.executable, RUNNER, "--team", team, "--role", role, "--round", round_id, "--complete"]
    if result == "failed":
        cmd.extend(["--result", "failed"])
        if error_msg:
            cmd.extend(["--error-message", error_msg[:200]])
    try:
        subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    except Exception as e:
        log(f"[{team}/{role}] ⚠️ 回写失败: {e}")


# ── 并行执行双队同阶段 ────────────────────────────────────

def run_phase_parallel(role: str, round_id: str, dry_run: bool = False,
                       preview: bool = False, max_workers: int = 2) -> dict:
    """并行执行红蓝两队的同一角色"""
    log(f"═══ 阶段: {role} (红蓝并行){' [preview]' if preview else ''} ═══")

    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = {
            pool.submit(run_role, team, role, round_id, dry_run, preview): team
            for team in ("red", "blue")
        }
        for future in as_completed(futures):
            team = futures[future]
            try:
                r = future.result()
                results.append(r)
            except Exception as e:
                results.append({"team": team, "role": role, "success": False, "error": str(e), "duration_s": 0})

    both_ok = all(r["success"] for r in results)
    ok_count = sum(1 for r in results if r["success"])
    log(f"═══ {role} 阶段完成: {ok_count}/2 成功 ═══")
    return {"results": results, "both_success": both_ok}


# ── Judge 执行 ────────────────────────────────────────────

def run_judge(round_id: str, dry_run: bool = False) -> dict:
    """执行全局 Judge"""
    log("═══ 阶段: Judge (全局) ═══")
    r = run_role("red", "judge", round_id, dry_run)
    log(f"═══ Judge 完成: {'✅' if r['success'] else '❌'} ═══")
    return r


# ── 轮次初始化 ────────────────────────────────────────────

def init_round(round_id: str):
    """初始化新轮次"""
    round_data = {
        "round_id": round_id,
        "created_at": now_iso(),
        "current_state": "ROUND_CREATED",
        "teams": {
            "red": {"status": "pending"},
            "blue": {"status": "pending"},
        },
        "judge_status": "pending",
        "updated_at": now_iso(),
    }
    write_json(ROUND_JSON, round_data)

    for team in ("red", "blue"):
        status = {
            "round_id": round_id,
            "team": team,
            "current_state": "pending",
            "roles": {
                r: {"status": "pending", "last_run": None, "error": None, "outputs": []}
                for r in ROLE_CHAIN + ["judge"]
            },
            "circuit_breaker": {
                "consecutive_qa_failures": 0,
                "threshold": CIRCUIT_BREAKER_THRESHOLD,
                "blocked": False,
                "reason": None,
            },
            "latest_artifacts": {},
            "updated_at": now_iso(),
        }
        save_team_status(team, status)

    log(f"轮次 {round_id} 已初始化")


# ── 主推进逻辑 ────────────────────────────────────────────

def advance(dry_run: bool = False, stuck_threshold: int = DEFAULT_STUCK_THRESHOLD,
            preview: bool = False) -> dict:
    """自动推进当前轮次"""
    round_data = get_round_data()
    if round_data is None:
        log("❌ round.json 不存在，请先 --new-round 创建轮次")
        return {"error": "no round.json"}

    round_id = round_data["round_id"]
    all_results = []
    phases_executed = []

    log(f"=== ACW Executor 启动 | 轮次: {round_id}{' [preview]' if preview else ''} ===")

    # 检查卡住
    for team in ("red", "blue"):
        for role in ROLE_CHAIN + ["judge"]:
            stuck, reason = check_stuck(team, role, stuck_threshold)
            if stuck:
                log(f"⚠️ [{team}/{role}] 卡住: {reason}")
                if not dry_run:
                    _retry_role(team, role, round_id)

    # 主循环
    max_iterations = 20
    dry_run_roles_done = set()
    for _ in range(max_iterations):
        round_data = get_round_data()
        if round_data is None:
            break

        current_state = round_data.get("current_state", "ROUND_CREATED")

        if current_state == "ROUND_CLOSED":
            log(f"轮次 {round_id} 已关闭")

            # P2: 自动推进
            if ROUND_ADVANCE_POLICY != "manual" and not dry_run:
                buffer = ROUND_ADVANCE_BUFFER_SECONDS.get(ROUND_ADVANCE_POLICY, 0)
                if buffer > 0:
                    log(f"⏳ 缓冲期 {buffer // 60} 分钟后自动开下一轮...")
                    # 记录下次推进时间供 cron 查询
                    next_advance = (datetime.now(timezone.utc) + timedelta(seconds=buffer)).isoformat()
                    round_data["next_advance_at"] = next_advance
                    write_json(ROUND_JSON, round_data)
            break

        target_role = STATE_TO_ROLE.get(current_state)
        if target_role is None:
            log(f"未知状态: {current_state}，停止")
            break

        # 检查该阶段是否已完成
        if target_role == "judge":
            judge_status = round_data.get("judge_status", "pending")
            if is_role_done(judge_status):
                log(f"Judge 已完成 ({judge_status})，round 应自动关闭")
                break
        else:
            all_done = True
            for team in ("red", "blue"):
                s = get_role_status(team, target_role)
                if dry_run and target_role in dry_run_roles_done:
                    continue
                if not is_role_ended(s):
                    all_done = False
                    break
            if all_done:
                log(f"两队 {target_role} 均已完成，round 应自动推进到下一阶段")
                _force_advance_round(round_data)
                continue

        # 执行
        if target_role == "judge":
            r = run_judge(round_id, dry_run)
            all_results.append(r)
            phases_executed.append("judge")
        else:
            phase_result = run_phase_parallel(target_role, round_id, dry_run, preview)
            all_results.extend(phase_result["results"])
            phases_executed.append(target_role)

        if dry_run:
            dry_run_roles_done.add(target_role)
            _force_advance_round(round_data)

    summary = {
        "round_id": round_id,
        "phases_executed": phases_executed,
        "total_results": len(all_results),
        "success_count": sum(1 for r in all_results if r.get("success")),
        "fail_count": sum(1 for r in all_results if not r.get("success")),
    }

    log(f"=== ACW Executor 完成 | 执行了 {len(phases_executed)} 个阶段, "
        f"{summary['success_count']} 成功, {summary['fail_count']} 失败 ===")

    # 轮次结束后自动 commit + push 主仓库
    if not dry_run and phases_executed:
        _sync_main_repo(round_id)

    return summary


def _retry_role(team: str, role: str, round_id: str):
    """重置卡住的角色"""
    cmd = [sys.executable, RUNNER, "--team", team, "--role", role, "--round", round_id, "--retry"]
    try:
        subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        log(f"[{team}/{role}] 已重置 (retry)")
    except Exception as e:
        log(f"[{team}/{role}] 重置失败: {e}")


def _sync_main_repo(round_id: str):
    """轮次结束后自动 commit + push 主仓库"""
    log("📦 同步主仓库到 GitHub...")
    try:
        # git add -A
        subprocess.run(["git", "add", "-A"], capture_output=True, text=True, timeout=10, cwd=BASE_DIR)

        # 检查是否有变更
        proc = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True, timeout=10, cwd=BASE_DIR)
        if not proc.stdout.strip():
            log("📦 主仓库无变更，跳过")
            return

        # git commit
        msg = f"Round {round_id} 自动同步"
        subprocess.run(["git", "commit", "-m", msg], capture_output=True, text=True, timeout=10, cwd=BASE_DIR)

        # git push（用 token）
        token = _get_token()
        if not token:
            log("📦 ⚠️ 无 GitHub token，跳过 push")
            return

        # 获取当前 remote URL
        url_proc = subprocess.run(["git", "remote", "get-url", "origin"], capture_output=True, text=True, timeout=10, cwd=BASE_DIR)
        original_url = url_proc.stdout.strip()
        if not original_url:
            log("📦 ⚠️ 无 origin remote，跳过 push")
            return

        # 嵌入 token push
        if original_url.startswith("https://"):
            auth_url = original_url.replace("https://", f"https://{token}@")
        else:
            auth_url = original_url

        subprocess.run(["git", "remote", "set-url", "origin", auth_url], capture_output=True, text=True, timeout=10, cwd=BASE_DIR)
        push_proc = subprocess.run(["git", "push", "origin", "master"], capture_output=True, text=True, timeout=120, cwd=BASE_DIR)
        subprocess.run(["git", "remote", "set-url", "origin", original_url], capture_output=True, text=True, timeout=10, cwd=BASE_DIR)

        if push_proc.returncode == 0:
            log("📦 ✅ 主仓库已同步到 GitHub")
        else:
            log(f"📦 ⚠️ push 失败: {push_proc.stderr[-200:]}")
    except Exception as e:
        log(f"📦 ⚠️ 同步异常: {e}")


def _get_token() -> str:
    """获取 GitHub token"""
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GITHUB_TOKEN_Classic")
    if not token:
        env_file = os.path.expanduser("~/.hermes/.env")
        if os.path.exists(env_file):
            for line in open(env_file):
                if line.startswith("GITHUB_TOKEN=") and not line.startswith("#"):
                    token = line.strip().split("=", 1)[1]
                    break
    if not token:
        try:
            proc = subprocess.run(
                ["powershell.exe", "-Command", "[Environment]::GetEnvironmentVariable('GITHUB_TOKEN_Classic', 'User')"],
                capture_output=True, text=True, timeout=10,
            )
            token = proc.stdout.strip().replace("\r", "").replace("\n", "")
        except Exception:
            pass
    return token or ""


def _force_advance_round(round_data: dict):
    """手动推进 round 状态"""
    state_order = ["ROUND_CREATED", "PLANNING", "DEVELOPMENT", "RELEASING", "PROMOTING", "JUDGING", "ROUND_CLOSED"]
    current = round_data.get("current_state", "ROUND_CREATED")
    if current in state_order:
        idx = state_order.index(current)
        if idx < len(state_order) - 1:
            next_state = state_order[idx + 1]
            round_data["current_state"] = next_state
            round_data["updated_at"] = now_iso()
            write_json(ROUND_JSON, round_data)
            log(f"  ✅ Round 强制推进: {current} → {next_state}")


# ── P2: 自动推进检查（供 cron 调用） ──────────────────────

def check_auto_advance():
    """检查是否到了自动推进的时间"""
    round_data = get_round_data()
    if round_data is None:
        return

    if round_data.get("current_state") != "ROUND_CLOSED":
        return

    next_at = round_data.get("next_advance_at")
    if not next_at:
        return

    try:
        next_time = datetime.fromisoformat(next_at)
    except ValueError:
        return

    if datetime.now(timezone.utc) >= next_time:
        # 计算新轮次 ID
        old_id = round_data["round_id"]
        # 简单递增: round-5 → round-6
        parts = old_id.rsplit("-", 1)
        if len(parts) == 2 and parts[1].isdigit():
            new_id = f"{parts[0]}-{int(parts[1]) + 1}"
        else:
            new_id = f"{old_id}-next"

        log(f"⏰ 缓冲期到，自动创建新轮次: {new_id}")
        init_round(new_id)


# ── 状态查看 ──────────────────────────────────────────────

def show_status():
    """显示当前轮次状态"""
    round_data = get_round_data()
    if round_data is None:
        print("无 round.json")
        return

    round_id = round_data["round_id"]
    state = round_data["current_state"]
    judge = round_data.get("judge_status", "pending")
    next_at = round_data.get("next_advance_at", "")

    print(f"\n{'='*60}")
    print(f"  ACW 状态 | 轮次: {round_id}")
    print(f"  Round 状态: {state} | Judge: {judge}")
    if next_at:
        print(f"  下次自动推进: {next_at[:16]}")
    print(f"{'='*60}\n")

    for team in ("red", "blue"):
        ts = get_team_status(team)
        if ts is None:
            print(f"  {team}: 无状态文件")
            continue
        print(f"  [{team.upper()}] 状态: {ts.get('current_state', 'N/A')}")
        for role in ROLE_CHAIN + ["judge"]:
            rd = ts.get("roles", {}).get(role, {})
            status = rd.get("status", "pending")
            last = rd.get("last_run", "")
            icon = {"completed": "✅", "failed": "❌", "in_progress": "🔄",
                    "blocked": "🚫", "skipped": "⏭"}.get(status, "⬜")
            last_str = last[:16] if last else ""
            print(f"    {icon} {role:10s} {status:12s} {last_str}")

        # P0: 熔断器状态
        cb = ts.get("circuit_breaker", {})
        if cb.get("blocked"):
            print(f"    🔥 熔断: {cb.get('reason', 'unknown')}")
        elif cb.get("consecutive_qa_failures", 0) > 0:
            print(f"    ⚡ QA 失败计数: {cb['consecutive_qa_failures']}/{cb.get('threshold', 3)}")

        print()


# ── 主入口 ────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="ACW Executor v2 — AI Company Wars 自动调度器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--new-round", metavar="ROUND_ID", help="创建新轮次")
    parser.add_argument("--dry-run", action="store_true", help="只看不跑")
    parser.add_argument("--status", action="store_true", help="查看当前状态")
    parser.add_argument("--preview", metavar="ROUND_ID", help="预览模式（不 push 不 deploy）")
    parser.add_argument("--reset-circuit", metavar="TEAM", help="重置熔断器 (red/blue)")
    parser.add_argument("--check-auto-advance", action="store_true", help="检查是否该自动推进（cron 用）")
    parser.add_argument("--stuck-threshold", type=int, default=DEFAULT_STUCK_THRESHOLD,
                        help=f"卡住阈值（分钟，默认 {DEFAULT_STUCK_THRESHOLD}）")

    args = parser.parse_args()

    if args.status:
        show_status()
        return

    if args.reset_circuit:
        reset_circuit_breaker(args.reset_circuit)
        return

    if args.check_auto_advance:
        check_auto_advance()
        return

    if args.preview:
        init_round(args.preview)
        log(f"轮次 {args.preview} 已创建 [preview 模式]，开始推进...")
        advance(dry_run=False, stuck_threshold=args.stuck_threshold, preview=True)
        return

    if args.new_round:
        init_round(args.new_round)
        log(f"轮次 {args.new_round} 已创建，开始推进...")

    advance(dry_run=args.dry_run, stuck_threshold=args.stuck_threshold)


if __name__ == "__main__":
    main()
