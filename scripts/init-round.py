#!/usr/bin/env python3
"""
init-round.py — 初始化一轮新的 Round

用法:
    python3 scripts/init-round.py --round 2026-week-22

参数:
    --round     轮次 ID（必填）
    --force     如果状态文件已存在，覆盖创建
    --dry-run   只看不写

效果:
    1. 创建 runtime/round.json（ROUND_CREATED 状态）
    2. 创建 teams/red/runtime/status.json（所有角色 pending）
    3. 创建 teams/blue/runtime/status.json（所有角色 pending）
    4. 清空 runtime/last-run.json
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEAM_ROLES = ["product", "dev", "devops", "growth"]  # per-team 角色（不含全局 Judge）


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def init_round(round_id, force=False, dry_run=False):
    """初始化一轮新比赛"""
    paths_to_create = []

    # 1. round.json
    round_path = os.path.join(BASE_DIR, "runtime", "round.json")
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
    paths_to_create.append((round_path, round_data))

    # 2. team status.json（红蓝两队）
    for team in ("red", "blue"):
        status_path = os.path.join(BASE_DIR, "teams", team, "runtime", "status.json")
        status_data = {
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
        paths_to_create.append((status_path, status_data))

    # 3. last-run.json（重置）
    last_run_path = os.path.join(BASE_DIR, "runtime", "last-run.json")
    last_run_data = {
        "round_id": round_id,
        "result": "not_started",
    }
    paths_to_create.append((last_run_path, last_run_data))

    # 检查冲突
    existing = [p for p, _ in paths_to_create if os.path.exists(p)]
    if existing and not force:
        print("❌ 以下状态文件已存在。使用 --force 覆盖：")
        for p in existing:
            print(f"   {p}")
        sys.exit(1)

    # 写入
    for path, data in paths_to_create:
        if dry_run:
            print(f"  [dry-run] 创建 {path}")
        else:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"  ✅ 创建 {path}")

    if dry_run:
        print("\n  [dry-run] 未写入任何文件")
    else:
        print(f"\n✅ Round {round_id} 初始化完成")
        print(f"   所有角色状态: pending")
        print(f"   当前 Round 状态: ROUND_CREATED")


def main():
    parser = argparse.ArgumentParser(description="AI Company Wars — Round 初始化工具")
    parser.add_argument("--round", required=True, help="轮次 ID，如 2026-week-22")
    parser.add_argument("--force", action="store_true", help="覆盖已存在的状态文件")
    parser.add_argument("--dry-run", action="store_true", help="只看不写")
    args = parser.parse_args()

    init_round(args.round, force=args.force, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
