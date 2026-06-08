#!/usr/bin/env python3
"""
github_auth.py — GitHub token 统一获取与校验（共享模块）

所有需要 GitHub token 的脚本统一从这里取，避免逻辑分散、口径不一。

获取优先级：
  1. 环境变量 GITHUB_TOKEN / GH_TOKEN / GITHUB_TOKEN_Classic
  2. ~/.hermes/.env 中的 GITHUB_TOKEN= 行（仓库外，安全）
  3. WSL 下从 Windows 用户环境变量读（powershell.exe）

⚠️ 安全约定：token 绝不硬编码进代码或仓库内文件。
"""

import os
import subprocess


def get_token() -> str:
    """按优先级返回 GitHub token；找不到返回空串。"""
    for var in ("GITHUB_TOKEN", "GH_TOKEN", "GITHUB_TOKEN_Classic"):
        val = os.environ.get(var)
        if val and val.strip():
            return val.strip()

    env_file = os.path.expanduser("~/.hermes/.env")
    if os.path.exists(env_file):
        try:
            for line in open(env_file, encoding="utf-8"):
                if line.startswith("GITHUB_TOKEN=") and not line.lstrip().startswith("#"):
                    return line.strip().split("=", 1)[1].strip()
        except OSError:
            pass

    # WSL：Windows 用户环境变量
    try:
        proc = subprocess.run(
            ["powershell.exe", "-Command",
             "[Environment]::GetEnvironmentVariable('GITHUB_TOKEN','User')"],
            capture_output=True, text=True, timeout=10,
        )
        tok = proc.stdout.strip().replace("\r", "").replace("\n", "")
        if tok:
            return tok
    except Exception:
        pass

    return ""


def validate_token(token: str, timeout: int = 15) -> tuple[bool, str]:
    """调用 GitHub API 校验 token 有效性。返回 (ok, message)。"""
    if not token:
        return False, "未提供 token"
    try:
        proc = subprocess.run(
            ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}",
             "-H", f"Authorization: token {token}", "https://api.github.com/user"],
            capture_output=True, text=True, timeout=timeout,
        )
        code = proc.stdout.strip()
        if code == "200":
            return True, "有效"
        if code == "401":
            return False, "token 无效 (401 Unauthorized)"
        if code == "403":
            return False, "rate limit 或权限不足 (403)"
        return False, f"GitHub API 返回 {code}"
    except Exception as e:
        return False, f"校验失败: {e}"


def get_valid_token() -> tuple[str, str]:
    """获取并校验 token。返回 (token, message)；无效时 token 为空串。"""
    tok = get_token()
    if not tok:
        return "", "未找到 token（GITHUB_TOKEN / ~/.hermes/.env / Windows 环境变量）"
    ok, msg = validate_token(tok)
    return (tok if ok else ""), msg


if __name__ == "__main__":
    # 自检：python3 scripts/github_auth.py
    t, m = get_valid_token()
    if t:
        print(f"✅ token 有效（前缀 {t[:8]}…，长度 {len(t)}）")
    else:
        print(f"❌ {m}")
