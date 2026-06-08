#!/usr/bin/env python3
"""
api-sync.py — 经 GitHub API 同步主仓库（绕过被污染的 github.com 直连）

适用场景：
  github.com 被 DNS 污染 / 防火墙阻断，常规 `git push` 走不通，
  但 api.github.com 仍可访问时，用本脚本把「当前工作区的已跟踪文件状态」
  作为一个提交同步到远程默认分支。

原理（Git Data API）：
  1. 读远程 HEAD 及其 tree
  2. 对比本地 `git ls-files -s` 与远程 tree，算出新增/修改/删除
  3. 为变更文件创建 blob（base64），基于远程 tree 建新 tree（含删除）
  4. 创建提交（父 = 远程 HEAD），更新分支 ref

注意：
  - 同步的是「已跟踪文件的 HEAD/index 版本」，未提交的工作区改动不会被推送。
  - 远程历史会多出一个「快照式」提交，与本地多提交历史不一致（内容一致）。
  - push 前会扫描待同步内容是否含疑似 token，命中即中止。

用法：
  python3 scripts/api-sync.py                       # 同步到 origin 默认分支
  python3 scripts/api-sync.py --branch master       # 指定分支
  python3 scripts/api-sync.py --repo owner/name     # 指定仓库（默认从 origin 解析）
  python3 scripts/api-sync.py --dry-run             # 只算变更，不提交
  python3 scripts/api-sync.py -m "自定义提交信息"
"""

import argparse
import base64
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 疑似 token 模式（push 前扫描）
SECRET_PATTERNS = [
    re.compile(r"github_pat_[A-Za-z0-9_]{20,}"),
    re.compile(r"ghp_[A-Za-z0-9]{20,}"),
    re.compile(r"gho_[A-Za-z0-9]{20,}"),
]


def get_token() -> str:
    """按优先级获取 GitHub token：环境变量 → ~/.hermes/.env → Windows 用户环境变量。"""
    tok = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if tok:
        return tok.strip()

    env_file = os.path.expanduser("~/.hermes/.env")
    if os.path.exists(env_file):
        for line in open(env_file, encoding="utf-8"):
            if line.startswith("GITHUB_TOKEN=") and not line.startswith("#"):
                return line.strip().split("=", 1)[1].strip()

    # WSL：从 Windows 用户环境变量读
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


def detect_repo() -> str:
    """从 origin remote URL 解析 owner/name。"""
    try:
        url = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            capture_output=True, text=True, timeout=10, cwd=BASE_DIR,
        ).stdout.strip()
    except Exception:
        return ""
    # 去掉可能内嵌的 token，提取 owner/repo
    m = re.search(r"github\.com[/:]([^/]+/[^/.]+)(?:\.git)?", url)
    return m.group(1) if m else ""


class GitHubAPI:
    def __init__(self, repo: str, token: str):
        self.api = f"https://api.github.com/repos/{repo}"
        self.token = token

    def call(self, path: str, method: str = "GET", body: dict | None = None) -> dict:
        data = json.dumps(body).encode() if body is not None else None
        req = urllib.request.Request(self.api + path, data=data, method=method)
        req.add_header("Authorization", f"token {self.token}")
        req.add_header("Accept", "application/vnd.github+json")
        if data:
            req.add_header("Content-Type", "application/json")
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                return json.load(resp)
        except urllib.error.HTTPError as e:
            detail = e.read().decode(errors="replace")[:300]
            raise SystemExit(f"❌ API {method} {path} 失败: HTTP {e.code} {detail}")


def local_files() -> dict:
    """返回 {path: (mode, sha)}，基于 git index/HEAD。"""
    out = subprocess.run(
        ["git", "ls-files", "-s"], capture_output=True, text=True, cwd=BASE_DIR
    ).stdout
    result = {}
    for line in out.splitlines():
        meta, path = line.split("\t", 1)
        parts = meta.split()
        result[path] = (parts[0], parts[1])  # mode, sha
    return result


def scan_secrets(paths: list[str]) -> str | None:
    """扫描给定文件内容是否含疑似 token，命中返回描述，否则 None。"""
    for p in paths:
        full = os.path.join(BASE_DIR, p)
        try:
            with open(full, "rb") as f:
                content = f.read()
        except (OSError, IsADirectoryError):
            continue
        try:
            text = content.decode("utf-8", errors="ignore")
        except Exception:
            continue
        for pat in SECRET_PATTERNS:
            m = pat.search(text)
            if m:
                return f"{p} 疑似含 token（前缀 {m.group(0)[:8]}…）"
    return None


def main():
    ap = argparse.ArgumentParser(description="经 GitHub API 同步主仓库")
    ap.add_argument("--repo", help="owner/name（默认从 origin 解析）")
    ap.add_argument("--branch", help="目标分支（默认远程默认分支）")
    ap.add_argument("-m", "--message", help="提交信息")
    ap.add_argument("--dry-run", action="store_true", help="只算变更不提交")
    args = ap.parse_args()

    token = get_token()
    if not token:
        raise SystemExit("❌ 未找到 GitHub token（GITHUB_TOKEN / ~/.hermes/.env / Windows 环境变量）")

    repo = args.repo or detect_repo()
    if not repo:
        raise SystemExit("❌ 无法确定仓库，请用 --repo owner/name 指定")

    gh = GitHubAPI(repo, token)
    print(f"🔗 仓库: {repo}")

    # 远程状态
    repo_info = gh.call("")
    branch = args.branch or repo_info.get("default_branch", "main")
    head = gh.call(f"/branches/{branch}")["commit"]["sha"]
    base_tree = gh.call(f"/git/commits/{head}")["tree"]["sha"]
    rt = gh.call(f"/git/trees/{base_tree}?recursive=1")
    if rt.get("truncated"):
        raise SystemExit("❌ 远程树过大被截断，本脚本暂不支持，请用常规 git push")
    # blob = 普通文件，commit = 子模块(gitlink)，两者都按 sha 比对，避免子模块误报变更
    remote = {e["path"]: e["sha"] for e in rt["tree"] if e["type"] in ("blob", "commit")}
    print(f"📡 远程 {branch} HEAD: {head[:8]}（{len(remote)} 文件）")

    # 本地对比
    local = local_files()
    changed = [p for p in local if local[p][1] != remote.get(p)]
    deleted = [p for p in remote if p not in local]
    print(f"📊 新增/修改 {len(changed)}，删除 {len(deleted)}")

    if not changed and not deleted:
        print("✅ 无差异，远程已是最新")
        return

    # secret 门禁
    hit = scan_secrets([p for p in changed if local[p][0] != "160000"])
    if hit:
        raise SystemExit(f"🛑 检测到疑似 secret，已中止同步: {hit}")
    print("🔒 secret 扫描通过")

    if args.dry_run:
        print("\n[dry-run] 变更文件:")
        for p in changed:
            print(f"  M {p}")
        for p in deleted:
            print(f"  D {p}")
        print("\n[dry-run] 未做任何远程改动")
        return

    # 建 blob + tree
    tree_items = []
    for i, p in enumerate(changed, 1):
        mode, sha = local[p]
        if mode == "160000":  # 子模块
            tree_items.append({"path": p, "mode": "160000", "type": "commit", "sha": sha})
            continue
        if mode == "120000":  # 符号链接
            content = os.readlink(os.path.join(BASE_DIR, p)).encode()
        else:
            with open(os.path.join(BASE_DIR, p), "rb") as f:
                content = f.read()
        blob = gh.call("/git/blobs", "POST",
                       {"content": base64.b64encode(content).decode(), "encoding": "base64"})
        tree_items.append({"path": p, "mode": mode, "type": "blob", "sha": blob["sha"]})
        if i % 15 == 0 or i == len(changed):
            print(f"  blob {i}/{len(changed)}")
    for p in deleted:
        tree_items.append({"path": p, "mode": "100644", "type": "blob", "sha": None})

    new_tree = gh.call("/git/trees", "POST", {"base_tree": base_tree, "tree": tree_items})

    msg = args.message or "sync: 经 GitHub API 同步当前文件状态（github.com 直连受阻）"
    commit = gh.call("/git/commits", "POST",
                     {"message": msg, "tree": new_tree["sha"], "parents": [head]})
    ref = gh.call(f"/git/refs/heads/{branch}", "PATCH",
                  {"sha": commit["sha"], "force": False})
    print(f"✅ {branch} 已更新 → {ref['object']['sha'][:8]}（提交 {commit['sha'][:8]}）")


if __name__ == "__main__":
    main()
