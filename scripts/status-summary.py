#!/usr/bin/env python3
"""
status-summary.py — AI Company Wars 状态汇总脚本

用法:
    python3 scripts/status-summary.py           # 默认输出（可读文本）
    python3 scripts/status-summary.py --json     # JSON 输出
    python3 scripts/status-summary.py --verbose  # 详细模式

数据来源:
    runtime/round.json
    teams/{red,blue}/runtime/status.json
    runtime/last-run.json
"""

import json
import os
import sys
from datetime import datetime, timezone

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEAMS = ["red", "blue"]
TEAM_LABELS = {"red": "🔴 红队", "blue": "🔵 蓝队"}
ROLE_LABELS = {
    "product": "Product",
    "dev": "Dev",
    "devops": "DevOps",
    "growth": "Growth",
    "judge": "Judge",
}
STATUS_ICONS = {
    "completed": "✅",
    "in_progress": "⏳",
    "pending": "⬜",
    "failed": "❌",
    "blocked": "🔒",
    "skipped": "⏭️",
}


def read_json(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def ts_display(ts):
    """ISO 时间戳转可读格式"""
    if not ts:
        return "-"
    try:
        dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        local = dt.astimezone()
        return local.strftime("%m-%d %H:%M")
    except (ValueError, AttributeError):
        return ts[:16] if ts else "-"


def dur_display(ms):
    """毫秒转可读时长"""
    if not ms:
        return "-"
    total_s = ms / 1000
    if total_s < 60:
        return f"{total_s:.0f}s"
    return f"{int(total_s // 60)}m {int(total_s % 60)}s"


class StatusSummary:
    def __init__(self, verbose=False, as_json=False):
        self.verbose = verbose
        self.as_json = as_json
        self.round_data = read_json(os.path.join(BASE_DIR, "runtime", "round.json"))
        self.last_run = read_json(os.path.join(BASE_DIR, "runtime", "last-run.json"))
        self.team_data = {}
        for team in TEAMS:
            path = os.path.join(BASE_DIR, "teams", team, "runtime", "status.json")
            self.team_data[team] = read_json(path)

    def build(self):
        return {
            "round": self._round_info(),
            "teams": self._teams_info(),
            "last_run": self._last_run_info(),
            "anomalies": self._anomalies(),
        }

    def _round_info(self):
        if not self.round_data:
            return {"error": "round.json not found"}
        return {
            "round_id": self.round_data.get("round_id", "?"),
            "current_state": self.round_data.get("current_state", "?"),
            "judge_status": self.round_data.get("judge_status", "?"),
            "updated_at": ts_display(self.round_data.get("updated_at")),
        }

    def _teams_info(self):
        result = {}
        for team in TEAMS:
            data = self.team_data.get(team)
            if not data:
                result[team] = {"error": "status.json not found"}
                continue
            roles = data.get("roles", {})
            role_info = {}
            for role_key in ["product", "dev", "devops", "growth"]:
                r = roles.get(role_key, {})
                role_info[role_key] = {
                    "status": r.get("status", "pending"),
                    "last_run": ts_display(r.get("last_run")),
                    "error": r.get("error"),
                }
            result[team] = {
                "team_state": data.get("current_state", "?"),
                "roles": role_info,
            }
        return result

    def _last_run_info(self):
        if not self.last_run or self.last_run.get("result") == "not_started":
            return None
        return {
            "team": self.last_run.get("team", "?"),
            "role": self.last_run.get("role", "?"),
            "result": self.last_run.get("result", "?"),
            "duration_ms": self.last_run.get("duration_ms"),
            "error": self.last_run.get("error"),
        }

    def _anomalies(self):
        anomalies = {"failures": [], "blocks": []}
        for team in TEAMS:
            data = self.team_data.get(team)
            if not data:
                continue
            roles = data.get("roles", {})
            for role_key, r in roles.items():
                status = r.get("status")
                if status == "failed":
                    anomalies["failures"].append({
                        "team": team,
                        "role": role_key,
                        "error": r.get("error"),
                        "last_run": r.get("last_run"),
                    })
                if status == "blocked":
                    anomalies["blocks"].append({
                        "team": team,
                        "role": role_key,
                        "error": r.get("error"),
                    })
        # 排序：最近的在前
        anomalies["failures"].sort(key=lambda x: x.get("last_run") or "", reverse=True)
        return anomalies

    def render_text(self, data):
        lines = []
        r = data["round"]

        # ── 标题 ──
        lines.append("=" * 52)
        lines.append("  AI Company Wars — 状态汇总")
        lines.append("=" * 52)
        lines.append("")

        # ── Round 概览 ──
        lines.append("── Round 概览 ──────────────────────────────")
        if "error" in r:
            lines.append(f"  ⚠️  {r['error']}")
        else:
            lines.append(f"  轮次:       {r['round_id']}")
            lines.append(f"  阶段:       {r['current_state']}")
            lines.append(f"  Judge:      {r['judge_status']}")
            lines.append(f"  更新于:     {r['updated_at']}")
        lines.append("")

        # ── 队伍状态 ──
        lines.append("── 队伍状态 ────────────────────────────────")
        for team in TEAMS:
            t = data["teams"].get(team, {})
            label = TEAM_LABELS[team]
            if "error" in t:
                lines.append(f"  {label}: ⚠️ {t['error']}")
                continue
            roles = t.get("roles", {})
            team_state = t.get("team_state", "?")
            states = []
            for rk in ["product", "dev", "devops", "growth"]:
                info = roles.get(rk, {})
                s = info.get("status", "?")
                icon = STATUS_ICONS.get(s, "❓")
                label_r = ROLE_LABELS.get(rk, rk)
                last = info.get("last_run", "")
                states.append(f"    {icon} {label_r}: {s}  {last}")

            lines.append(f"  {label}  (队伍状态: {team_state})")
            lines.extend(states)
            lines.append("")
        lines.append("")

        # ── 最近执行 ──
        lr = data["last_run"]
        lines.append("── 最近执行 ────────────────────────────────")
        if lr:
            team_label = TEAM_LABELS.get(lr.get("team", ""), lr.get("team", "?"))
            role_label = ROLE_LABELS.get(lr.get("role", ""), lr.get("role", "?"))
            icon = STATUS_ICONS.get(lr.get("result"), "❓")
            dur = dur_display(lr.get("duration_ms"))
            lines.append(f"  {icon} {team_label} {role_label}: {lr['result']} ({dur})")
            err = lr.get("error")
            if err:
                code = err.get("code", "")
                msg = err.get("message", "")
                if code or msg:
                    lines.append(f"     错误: [{code}] {msg[:80]}")
        else:
            lines.append("  (无最近执行记录)")
        lines.append("")

        # ── 异常摘要 ──
        anom = data["anomalies"]
        lines.append("── 异常摘要 ────────────────────────────────")
        fail_count = len(anom["failures"])
        block_count = len(anom["blocks"])
        lines.append(f"  ❌ 失败: {fail_count}   🔒 阻塞: {block_count}")

        if fail_count > 0:
            f = anom["failures"][0]
            lines.append(f"  最近失败: {TEAM_LABELS.get(f['team'], f['team'])} {ROLE_LABELS.get(f['role'], f['role'])}")
            if f.get("error"):
                lines.append(f"    原因: {f['error'][:80]}")
        if block_count > 0:
            b = anom["blocks"][0]
            lines.append(f"  最近阻塞: {TEAM_LABELS.get(b['team'], b['team'])} {ROLE_LABELS.get(b['role'], b['role'])}")
            if b.get("error"):
                lines.append(f"    原因: {b['error'][:80]}")
        lines.append("")

        if self.verbose and fail_count > 0:
            lines.append("── 全部失败详情 ───────────────────────────")
            for f in anom["failures"]:
                team = TEAM_LABELS.get(f["team"], f["team"])
                role = ROLE_LABELS.get(f["role"], f["role"])
                err = f.get("error", "-")
                lines.append(f"  {team} {role}: {err}")
            lines.append("")

        lines.append("=" * 52)
        return "\n".join(lines)

    def render_json(self, data):
        return json.dumps(data, ensure_ascii=False, indent=2)


def main():
    verbose = "--verbose" in sys.argv or "-v" in sys.argv
    as_json = "--json" in sys.argv or "-j" in sys.argv

    ss = StatusSummary(verbose=verbose, as_json=as_json)
    data = ss.build()

    if as_json:
        print(ss.render_json(data))
    else:
        print(ss.render_text(data))


if __name__ == "__main__":
    main()
