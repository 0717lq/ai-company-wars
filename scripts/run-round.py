#!/usr/bin/env python3
"""
run-round.py — AI Company Wars 统一 Runner 入口 (v2.0)

统一调用方式：
    # 前置检查（默认）
    python3 scripts/run-round.py --team red --role product --round 2026-week-21

    # 执行完成——成功
    python3 scripts/run-round.py --team red --role dev --round 2026-week-21 --complete

    # 执行完成——失败
    python3 scripts/run-round.py --team red --role dev --round 2026-week-21 --complete \\
        --result failed --error-code TEST_FAILED --error-message "3/15 tests failed"

    # 补跑：重置角色状态为 pending
    python3 scripts/run-round.py --team blue --role dev --round 2026-week-21 --retry

参数：
    --team              red | blue
    --role              product | dev | devops | growth | judge
    --round             轮次 ID，例如 2026-week-21
    --complete          执行完成后调用，更新状态（默认：前置检查模式）
    --result            completed | failed | skipped（仅 --complete 模式）
    --error-code        错误码（仅 --result failed 时使用）
    --error-message     错误描述（仅 --result failed 时使用）
    --retry             重跑模式：重置 failed/blocked → pending
    --dry-run           只检查不写文件
    --verbose           详细输出
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone

# ── 路径常量 ──────────────────────────────────────────────

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROUND_JSON = os.path.join(BASE_DIR, "runtime", "round.json")
LAST_RUN_JSON = os.path.join(BASE_DIR, "runtime", "last-run.json")

VALID_TEAMS = {"red", "blue"}
VALID_ROLES = {"product", "dev", "devops", "growth", "judge"}
TEAM_ROLES = {"product", "dev", "devops", "growth"}  # per-team 角色（不含全局 Judge）
VALID_RESULTS = {"completed", "failed", "skipped"}

# 已知错误码列表
KNOWN_ERROR_CODES = {
    "INPUT_MISSING",      # 必读输入缺失
    "PRECONDITION_FAILED", # 前置条件不满足
    "NETWORK_ERROR",      # 网络不通
    "TEST_FAILED",        # 测试失败
    "GITHUB_RATE_LIMIT",  # GitHub API 限流
    "POLICY_BLOCKED",     # 策略禁止该行为
    "IMPLEMENTATION_FAILED",  # 实现错误
    "PRD_MISSING",        # 缺少 PRD
    "READY_FOR_DEPLOY_MISSING",  # 缺少 ready-for-deploy
    "UNKNOWN_ERROR",      # 未知错误
}

# ── 工具函数 ──────────────────────────────────────────────


def team_status_path(team):
    """获取 team 状态文件路径"""
    return os.path.join(BASE_DIR, "teams", team, "runtime", "status.json")


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def now_ms():
    return int(time.time() * 1000)


def read_json(path):
    """读取 JSON 文件，不存在则返回 None"""
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path, data, dry_run=False):
    """写入 JSON 文件（自动创建目录）"""
    if dry_run:
        print(f"  [dry-run] 写入 {path}")
        return
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ── 角色列表与阶段映射 ────────────────────────────────────

ROUND_STATE_FOR_ROLE = {
    "product":   "PLANNING",
    "dev":       "DEVELOPMENT",
    "devops":    "RELEASING",
    "growth":    "PROMOTING",
    "judge":     "JUDGING",
}

ALLOWED_ROUND_STATES = {
    "product":   {"ROUND_CREATED", "PLANNING"},
    "dev":       {"DEVELOPMENT"},
    "devops":    {"RELEASING"},
    "growth":    {"PROMOTING"},
    "judge":     {"JUDGING"},
}

PREREQUISITE_ROLES = {
    "product":   [],
    "dev":       ["product"],
    "devops":    ["dev"],
    "growth":    ["devops", "dev"],
    # judge 是全局角色，不由 per-team 前置条件控制
}


# ── 状态判断核心函数 ──────────────────────────────────────


def is_role_ended(status_value):
    """角色是否已结束（不再需要执行）"""
    return status_value in ("completed", "failed", "skipped")


def is_role_ended_terminal(status_value):
    """角色是否处于终态（不可自动恢复）"""
    return status_value in ("completed", "skipped")


def check_preconditions(team_status, role, verbose, is_retry=False):
    """
    检查前置条件。
    返回: (decision, reason)
    decision: "can_run" | "skipped" | "blocked" | "already_done"
    """
    # ── Judge 是全局角色：前置条件由 round 级状态控制 ──
    if role == "judge":
        # Judge 的 per-team 检查不由这里控制，由 round_state 处理。
        # 只要不是 already_done 就允许
        role_data = team_status.get("roles", {}).get(role, {})
        current_status = role_data.get("status", "pending")
        if is_role_ended_terminal(current_status):
            return ("already_done", f"Judge 已经是 {current_status} 状态")
        return ("can_run", None)

    roles_dict = team_status.get("roles", {})
    role_data = roles_dict.get(role, {})
    current_status = role_data.get("status", "pending")

    # ── 幂等检查：已 completed/skipped → 无需重复执行 ──
    if is_role_ended_terminal(current_status):
        return ("already_done", f"{role} 已经是 {current_status} 状态，无需重复执行")

    # ── failed 状态：非重跑模式下 blocked ──
    if current_status == "failed" or current_status == "in_progress":
        if not is_retry:
            if current_status == "failed":
                return ("blocked", f"{role} 已失败，需要先 --retry 重置")
            if current_status == "in_progress":
                return ("blocked", f"{role} 仍在进行中")

    # ── 检查前置角色 ──
    prereqs = PREREQUISITE_ROLES.get(role, [])
    for prereq in prereqs:
        prereq_status = roles_dict.get(prereq, {}).get("status", "pending")

        if prereq_status == "failed":
            if role == "judge":
                if verbose:
                    print(f"  [info] Judge 允许在前置角色 failed 的情况下执行")
                continue
            return ("blocked", f"前置角色 {prereq} 已失败，本轮无接力条件")

        if prereq_status == "blocked":
            return ("blocked", f"前置角色 {prereq} 被阻塞")

        if prereq_status == "in_progress":
            return ("blocked", f"前置角色 {prereq} 仍在进行中")

        if prereq_status in ("pending", None):
            # 特殊规则
            if role == "devops" and prereq == "dev":
                return ("skipped", "Dev 未执行，DevOps 无需发布")
            if role == "growth" and prereq == "devops":
                return ("skipped", "DevOps 未执行，Growth 无需优化")
            return ("blocked", f"前置角色 {prereq} 尚未开始")

    # ── 额外检查：DevOps ──
    if role == "devops":
        rfd_path = os.path.join(
            BASE_DIR, "teams", team_status.get("team", ""), "artifacts", "ready-for-deploy.md"
        )
        if not os.path.exists(rfd_path):
            dev_status = roles_dict.get("dev", {}).get("status", "pending")
            if dev_status in ("skipped", None, "pending"):
                return ("skipped", "Dev 已跳过，无需部署")
            return ("blocked", f"缺少 ready-for-deploy.md（期望路径: {rfd_path}）")

    # ── 额外检查：Growth ──
    if role == "growth":
        devops_status = roles_dict.get("devops", {}).get("status", "pending")
        if devops_status in ("failed", "skipped", None, "pending"):
            readme_path = os.path.join(
                BASE_DIR, "teams", team_status.get("team", ""), "project", "README.md"
            )
            if not os.path.exists(readme_path):
                return ("blocked", "项目没有 README，Growth 无法优化")

    return ("can_run", None)


def check_round_state(round_data, role, verbose):
    """检查 Round 级状态是否允许当前角色执行。返回 (ok, message)"""
    if round_data is None:
        return (True, "无 round.json，跳过 Round 级检查")

    current_state = round_data.get("current_state", "")
    allowed = ALLOWED_ROUND_STATES.get(role, set())

    if role == "judge":
        for team_name in ("red", "blue"):
            team_info = round_data.get("teams", {}).get(team_name, {})
            team_state = team_info.get("status", "pending")
            if team_state == "in_progress":
                return (False, f"{team_name} 队伍仍在进行中，Judge 不能开始")

    if current_state not in allowed:
        if role == "product" and current_state == "ROUND_CREATED":
            return (True, "Round 刚创建，Product 可执行")
        return (False, f"Round 状态 {current_state} 不允许 {role} 执行（需要 {allowed}）")

    return (True, None)


# ── 状态更新函数 ──────────────────────────────────────────


def set_role_status(team_status, role, new_status, error=None, outputs=None):
    """更新 team 状态中指定角色的状态"""
    if "roles" not in team_status:
        team_status["roles"] = {}
    if role not in team_status["roles"]:
        team_status["roles"][role] = {"status": "pending", "last_run": None, "error": None, "outputs": []}

    team_status["roles"][role]["status"] = new_status
    team_status["roles"][role]["last_run"] = now_iso()
    if error:
        team_status["roles"][role]["error"] = error
    if outputs is not None:
        team_status["roles"][role]["outputs"] = outputs

    team_status["current_state"] = aggregate_team_state(team_status["roles"])
    team_status["updated_at"] = now_iso()


def reset_role_status(team_status, role):
    """将角色状态重置为 pending（补跑用）"""
    if "roles" not in team_status:
        return
    if role not in team_status["roles"]:
        return
    team_status["roles"][role] = {"status": "pending", "last_run": None, "error": None, "outputs": []}
    team_status["current_state"] = aggregate_team_state(team_status["roles"])
    team_status["updated_at"] = now_iso()


def aggregate_team_state(roles):
    """根据各角色状态聚合得到 team 当前状态"""
    statuses = [r.get("status", "pending") for r in roles.values()]

    if any(s == "in_progress" for s in statuses):
        return "in_progress"
    if any(s == "blocked" for s in statuses):
        return "blocked"
    if any(s == "failed" for s in statuses):
        return "failed"
    if all(s == "pending" for s in statuses):
        return "pending"
    if all(is_role_ended(s) for s in statuses):
        return "completed"
    return "in_progress"


# ── last-run.json 写入（增强版） ─────────────────────────


def write_last_run(
    round_id, team, role,
    result,
    error_code=None,
    error_message=None,
    inputs=None,
    outputs=None,
    started_at=None,
    finished_at=None,
    duration_ms=None,
    dry_run=False,
):
    """写入增强版 last-run.json"""
    entry = {
        "round_id": round_id,
        "team": team,
        "role": role,
        "started_at": started_at,
        "finished_at": finished_at,
        "duration_ms": duration_ms,
        "result": result,
    }

    # 错误信息：只有 failed 时才有意义
    if error_code or error_message:
        entry["error"] = {
            "code": error_code,
            "message": error_message,
        }
    else:
        entry["error"] = None

    entry["inputs"] = inputs or []
    entry["outputs"] = outputs or []

    write_json(LAST_RUN_JSON, entry, dry_run=dry_run)
    return entry


# ── Round 推进 ────────────────────────────────────────────


def _check_phase_complete(round_data, phase_state):
    """检查 Round 当前阶段是否完成"""
    # ── JUDGING 阶段：检查 round.json 的 judge_status（全局角色）──
    if phase_state == "JUDGING":
        judge_status = round_data.get("judge_status", "pending")
        return is_role_ended(judge_status)

    # ── 其他阶段：检查每队对应的 per-team 角色 ──
    PHASE_TO_ROLE = {
        "ROUND_CREATED": "product",
        "PLANNING": "product",
        "DEVELOPMENT": "dev",
        "RELEASING": "devops",
        "PROMOTING": "growth",
    }
    role_to_check = PHASE_TO_ROLE.get(phase_state)
    if role_to_check is None:
        return False

    teams = round_data.get("teams", {})
    for team_name in teams:
        ts_path = os.path.join(BASE_DIR, "teams", team_name, "runtime", "status.json")
        ts = read_json(ts_path)
        if ts is None:
            return False
        role_info = ts.get("roles", {}).get(role_to_check, {})
        role_status = role_info.get("status", "pending")
        if not is_role_ended(role_status):
            return False
    return True


def advance_round(round_data, team, dry_run=False):
    """检查 Round 状态是否可以推进。连续推进直到无法再推进。"""
    if round_data is None:
        return

    state_order = ["ROUND_CREATED", "PLANNING", "DEVELOPMENT", "RELEASING", "PROMOTING", "JUDGING", "ROUND_CLOSED"]

    advanced = False
    while True:
        current = round_data.get("current_state", "ROUND_CREATED")
        try:
            current_idx = state_order.index(current)
        except ValueError:
            return

        # 检查当前阶段是否完成
        if not _check_phase_complete(round_data, current):
            break

        # 推进到下一阶段
        if current_idx >= len(state_order) - 1:
            break

        next_state = state_order[current_idx + 1]
        round_data["current_state"] = next_state
        round_data["updated_at"] = now_iso()
        write_json(ROUND_JSON, round_data, dry_run=dry_run)
        print(f"  ✅ Round 推进: {current} → {next_state}")
        advanced = True

    if not advanced:
        return


# ── 子命令：前置检查 ──────────────────────────────────────


def cmd_check(args):
    """前置检查模式：判断是否允许执行"""
    team = args.team
    role = args.role
    round_id = args.round
    dry_run = args.dry_run
    verbose = args.verbose

    print(f"\n{'='*50}")
    print(f"🏁  Runner 前置检查")
    print(f"   Team: {team} | Role: {role} | Round: {round_id}")
    print(f"{'='*50}\n")

    # 1. Round 状态检查
    round_data = read_json(ROUND_JSON)
    if round_data is None and verbose:
        print("  [info] round.json 不存在，跳过 Round 级检查")
    elif verbose:
        print(f"  Round 状态: {round_data.get('current_state', 'N/A')}")

    round_ok, round_msg = check_round_state(round_data, role, verbose)
    if not round_ok:
        print(f"  ❌ Round 检查未通过: {round_msg}")
        print(f"\n  📋 结论: BLOCKED (Round 级别)")
        return

    if verbose and round_msg:
        print(f"  ✅ Round 检查通过: {round_msg}")

    # 2. Team 状态
    status_path = team_status_path(team)
    team_status = read_json(status_path)

    if team_status is None:
        print(f"  [info] team 状态文件不存在，将创建")
        team_status = {
            "round_id": round_id,
            "team": team,
            "current_state": "pending",
            "roles": {
                r: {"status": "pending", "last_run": None, "error": None, "outputs": []}
                for r in TEAM_ROLES
            },
            "latest_artifacts": {},
            "updated_at": now_iso(),
        }
        if not dry_run:
            write_json(status_path, team_status)

    # 3. 幂等验证：同 round 已完成则跳过
    stored_round = team_status.get("round_id")
    if stored_round and stored_round != round_id:
        if verbose:
            print(f"  [info] 状态文件记录的 round ({stored_round}) 与当前 round ({round_id}) 不同")

    # 4. 前置条件
    decision, reason = check_preconditions(team_status, role, verbose)

    if decision == "already_done":
        print(f"  ℹ️  {role} 已经是 {team_status['roles'].get(role, {}).get('status', 'N/A')}，无需重复执行")
        print(f"\n  📋 结论: SKIPPED (已完成)")
        return

    if decision == "blocked":
        print(f"  ❌ 前置条件不满足: {reason}")
        if not dry_run:
            set_role_status(team_status, role, "blocked", error=reason)
            write_json(status_path, team_status, dry_run=dry_run)
            write_last_run(
                round_id, team, role, "skipped",
                error_code="PRECONDITION_FAILED",
                error_message=reason,
                dry_run=dry_run,
            )
        print(f"\n  📋 结论: BLOCKED")
        print(f"  原因: {reason}")
        return

    if decision == "skipped":
        print(f"  ℹ️  可跳过: {reason}")
        if not dry_run:
            set_role_status(team_status, role, "skipped")
            write_json(status_path, team_status, dry_run=dry_run)
            write_last_run(round_id, team, role, "skipped", dry_run=dry_run)
        print(f"\n  📋 结论: SKIPPED")
        if reason:
            print(f"  原因: {reason}")
        return

    # 5. CAN_RUN
    if decision == "can_run":
        print(f"  ✅ 前置条件全部满足，允许执行")
        started_at = now_iso()

        if not dry_run:
            # set_role_status 会把 last_run 记为本时刻，供 complete 时计算 duration，
            # 无需额外持久化 _start_ms（避免污染 status.json 且 complete 未走到时残留）
            set_role_status(team_status, role, "in_progress")
            write_json(status_path, team_status, dry_run=dry_run)
            write_last_run(
                round_id, team, role, "running",
                started_at=started_at,
                dry_run=dry_run,
            )

        print(f"\n  📋 结论: CAN_RUN")
        print(f"  状态已更新为 in_progress")
        print(f"  请在 {role} 执行完成后调用:")
        print(f"    python3 scripts/run-round.py --team {team} --role {role} --round {round_id} --complete")

    if dry_run:
        print(f"\n  [dry-run] 未写入任何文件")


# ── 子命令：重跑 ──────────────────────────────────────────


def cmd_retry(args):
    """重跑模式：将 failed/blocked 角色重置为 pending"""
    team = args.team
    role = args.role
    round_id = args.round
    dry_run = args.dry_run

    print(f"\n{'='*50}")
    print(f"🔄  Runner 重跑模式")
    print(f"   Team: {team} | Role: {role} | Round: {round_id}")
    print(f"{'='*50}\n")

    status_path = team_status_path(team)
    team_status = read_json(status_path)

    if team_status is None:
        print(f"  ❌ 错误: 状态文件不存在，无法重置")
        return

    role_data = team_status.get("roles", {}).get(role, {})
    current_status = role_data.get("status", "pending")

    print(f"  当前 {role} 状态: {current_status}")

    # 哪些状态允许重跑
    RETRY_ALLOWED_FROM = {"failed", "blocked"}
    # completed/skipped 是终态，不允许自动重跑
    TERMINAL_STATES = {"completed", "skipped"}

    if current_status in TERMINAL_STATES:
        print(f"  ❌ {role} 处于终态 ({current_status})，不允许自动重跑")
        print(f"     如需强制重跑，请手动修改状态文件后重试")
        return

    if current_status not in RETRY_ALLOWED_FROM:
        print(f"  ℹ️  {role} 状态为 {current_status}，无需重置")
        if current_status == "pending":
            print(f"     提示: 角色尚未开始，直接执行前置检查即可")
        return

    # 允许重置的角色
    RETRY_ALLOWED_ROLES = {"product", "dev", "devops", "growth"}
    if role not in RETRY_ALLOWED_ROLES:
        print(f"  ℹ️  {role} 不支持自动重跑（Judge 可在下一轮重新评分）")
        return

    # 执行重置
    if not dry_run:
        reset_role_status(team_status, role)
        write_json(status_path, team_status, dry_run=dry_run)
        write_last_run(
            round_id, team, role, "skipped",
            error_message=f"重跑前手动重置: {current_status} → pending",
            dry_run=dry_run,
        )

    print(f"  ✅ 已重置: {current_status} → pending")
    print(f"  请执行前置检查确认是否可以重新开始:")
    print(f"    python3 scripts/run-round.py --team {team} --role {role} --round {round_id}")
    print(f"\n  ⚠️  重跑前确认：")
    print(f"     - Product: 旧 PRD 是否仍适用？")
    print(f"     - Dev: 是否需要先 revert 上次提交？")
    print(f"     - DevOps: 旧 tag 是否需要清理？")


# ── 子命令：完成回写（增强版） ──────────────────────────


def cmd_complete(args):
    """执行完成模式：更新最终状态"""
    team = args.team
    role = args.role
    round_id = args.round
    result = args.result or "completed"
    error_code = args.error_code
    error_message = args.error_message
    dry_run = args.dry_run

    print(f"\n{'='*50}")
    print(f"🏁  Runner 执行完成回写")
    print(f"   Team: {team} | Role: {role} | Round: {round_id} | Result: {result}")
    print(f"{'='*50}\n")

    # ── Judge 是全局角色：更新 round.json 的 judge_status ──
    if role == "judge":
        round_data = read_json(ROUND_JSON)
        if round_data is None:
            print(f"  ❌ 错误: round.json 不存在，无法完成 Judge 回写")
            sys.exit(1)

        round_data["judge_status"] = result
        round_data["updated_at"] = now_iso()

        finished_at = now_iso()
        error_data = None
        if result == "failed":
            if not error_code:
                error_code = "UNKNOWN_ERROR"
            if not error_message:
                error_message = "评分执行失败"
            error_data = {"code": error_code, "message": error_message}

        if not dry_run:
            write_json(ROUND_JSON, round_data, dry_run=dry_run)
            write_last_run(
                round_id, team, role, result,
                error_code=error_code,
                error_message=error_message,
                finished_at=finished_at,
                dry_run=dry_run,
            )
            # Judge 是全局角色：同步回写两队 team status 的 judge 项，
            # 避免 team 级 status 卡在 in_progress、current_state 与 round 脱节
            for tm in ("red", "blue"):
                tpath = team_status_path(tm)
                tstat = read_json(tpath)
                if tstat is None:
                    continue
                tstat.pop("_start_ms", None)
                set_role_status(tstat, "judge", result, error=error_message)
                write_json(tpath, tstat)
            print(f"  ✅ Judge 状态已更新: → {result}（含两队 team status 同步）")
            if result == "failed" and error_data:
                print(f"  ❌ 错误: [{error_data['code']}] {error_data['message']}")
            advance_round(round_data, team, dry_run=dry_run)
        else:
            print(f"  [dry-run] 将更新 Judge → {result}")
        return

    # 读取当前 team 状态
    status_path = team_status_path(team)
    team_status = read_json(status_path)

    if team_status is None:
        print(f"  ❌ 错误: team 状态文件不存在，无法完成回写")
        sys.exit(1)

    role_data = team_status.get("roles", {}).get(role, {})
    current_status = role_data.get("status", "pending")

    if current_status != "in_progress":
        print(f"  ⚠️  当前角色状态是 {current_status}，不是 in_progress")
        print(f"     这可能是幂等检查后的正常跳过，或状态文件已被修改")

    # 清理历史遗留的 _start_ms（旧版本污染，complete 未走到时会残留）
    team_status.pop("_start_ms", None)

    # 计算 duration：基于 in_progress 起始时间（role.last_run），不再依赖 _start_ms
    finished_at = now_iso()
    duration_ms = None
    if current_status == "in_progress":
        started_iso = role_data.get("last_run")
        if started_iso:
            try:
                started_dt = datetime.fromisoformat(started_iso)
                delta = datetime.now(timezone.utc) - started_dt
                duration_ms = int(delta.total_seconds() * 1000)
            except ValueError:
                duration_ms = None

    # 错误信息（仅 failed）
    error_data = None
    if result == "failed":
        if not error_code:
            error_code = "UNKNOWN_ERROR"
        if not error_message:
            error_message = "执行失败（未提供详细错误信息）"
        error_data = {"code": error_code, "message": error_message}

    # 回写
    if not dry_run:
        set_role_status(team_status, role, result, error=error_message)
        write_json(status_path, team_status, dry_run=dry_run)

        write_last_run(
            round_id, team, role, result,
            error_code=error_code,
            error_message=error_message,
            started_at=role_data.get("last_run") if current_status == "in_progress" else None,
            finished_at=finished_at,
            duration_ms=duration_ms,
            dry_run=dry_run,
        )

        print(f"  ✅ 状态已更新: {current_status} → {result}")
        if duration_ms:
            print(f"  ⏱  耗时: {duration_ms}ms")

        if result == "failed" and error_data:
            print(f"  ❌ 错误: [{error_data['code']}] {error_data['message']}")

        # Round 推进
        round_data = read_json(ROUND_JSON)
        if round_data:
            advance_round(round_data, team, dry_run=dry_run)
    else:
        print(f"  [dry-run] 将更新 {role}: {current_status} → {result}")


# ── 主入口 ────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(
        description="AI Company Wars — 统一 Runner 入口 (v2.0)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 前置检查（默认模式）
  python3 scripts/run-round.py --team red --role product --round 2026-week-21

  # 执行完成——成功
  python3 scripts/run-round.py --team red --role dev --round 2026-week-21 --complete

  # 执行完成——失败
  python3 scripts/run-round.py --team red --role dev --round 2026-week-21 --complete \\
      --result failed --error-code TEST_FAILED --error-message "3/15 tests failed"

  # 补跑：重置失败角色
  python3 scripts/run-round.py --team blue --role dev --round 2026-week-21 --retry

  # 只看不写
  python3 scripts/run-round.py --team blue --role devops --round 2026-week-21 --dry-run
        """,
    )
    parser.add_argument("--team", required=True, choices=sorted(VALID_TEAMS), help="队伍: red / blue")
    parser.add_argument("--role", required=True, choices=sorted(VALID_ROLES), help="角色")
    parser.add_argument("--round", required=True, help="轮次 ID，如 2026-week-21")
    parser.add_argument("--complete", action="store_true", help="执行完成后回写状态")
    parser.add_argument("--retry", action="store_true", help="重跑模式：重置 failed/blocked → pending")
    parser.add_argument("--result", choices=sorted(VALID_RESULTS), help="执行结果（仅 --complete 模式）")
    parser.add_argument("--error-code", help="错误码（仅 --result failed 时使用）")
    parser.add_argument("--error-message", help="错误描述（仅 --result failed 时使用）")
    parser.add_argument("--dry-run", action="store_true", help="只检查不写文件")
    parser.add_argument("--verbose", action="store_true", help="详细输出")

    args = parser.parse_args()

    # 参数校验
    if args.complete and args.retry:
        print("❌ 错误: --complete 和 --retry 不能同时使用")
        sys.exit(1)

    if args.complete and args.result == "failed":
        if not args.error_code:
            # 允许不传，自动补充 UNKNOWN_ERROR
            pass

    if args.retry:
        cmd_retry(args)
    elif args.complete:
        cmd_complete(args)
    else:
        cmd_check(args)


if __name__ == "__main__":
    main()
