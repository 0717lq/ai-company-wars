"""
run-round.py 状态机核心逻辑单元测试。

run-round.py 文件名带连字符，无法直接 import，用 importlib 按路径加载。
运行：python3 -m pytest scripts/tests/ -v
"""

import importlib.util
import os

import pytest

# ── 加载 run-round.py 模块 ──────────────────────────────────
_HERE = os.path.dirname(os.path.abspath(__file__))
_RUNNER_PATH = os.path.join(_HERE, "..", "run-round.py")
_spec = importlib.util.spec_from_file_location("run_round", _RUNNER_PATH)
rr = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(rr)


# ── aggregate_team_state ───────────────────────────────────

def _roles(**kw):
    """构造 roles dict，未指定的角色默认 pending。"""
    base = {r: {"status": "pending"} for r in ("product", "dev", "devops", "growth")}
    for k, v in kw.items():
        base[k] = {"status": v}
    return base


def test_aggregate_all_pending():
    assert rr.aggregate_team_state(_roles()) == "pending"


def test_aggregate_in_progress_wins():
    # 任一 in_progress → 整体 in_progress（优先级最高）
    s = rr.aggregate_team_state(_roles(product="completed", dev="in_progress"))
    assert s == "in_progress"


def test_aggregate_blocked_over_failed():
    # blocked 优先于 failed
    s = rr.aggregate_team_state(_roles(dev="failed", devops="blocked"))
    assert s == "blocked"


def test_aggregate_failed():
    s = rr.aggregate_team_state(_roles(product="completed", dev="failed"))
    assert s == "failed"


def test_aggregate_all_ended_completed():
    s = rr.aggregate_team_state(_roles(
        product="completed", dev="completed", devops="skipped", growth="completed"))
    assert s == "completed"


def test_aggregate_partial_progress():
    # 部分完成、其余 pending、无 in_progress/blocked/failed → in_progress
    s = rr.aggregate_team_state(_roles(product="completed"))
    assert s == "in_progress"


# ── is_role_ended ──────────────────────────────────────────

@pytest.mark.parametrize("status,expected", [
    ("completed", True), ("failed", True), ("skipped", True),
    ("pending", False), ("in_progress", False), ("blocked", False),
])
def test_is_role_ended(status, expected):
    assert rr.is_role_ended(status) is expected


@pytest.mark.parametrize("status,expected", [
    ("completed", True), ("skipped", True),
    ("failed", False), ("pending", False), ("in_progress", False),
])
def test_is_role_ended_terminal(status, expected):
    assert rr.is_role_ended_terminal(status) is expected


# ── check_preconditions ────────────────────────────────────

def _team_status(**role_statuses):
    return {
        "team": "red",
        "roles": {r: {"status": s} for r, s in role_statuses.items()},
    }


def test_precond_product_can_run_fresh():
    ts = _team_status(product="pending")
    decision, _ = rr.check_preconditions(ts, "product", verbose=False)
    assert decision == "can_run"


def test_precond_already_done():
    ts = _team_status(product="completed")
    decision, _ = rr.check_preconditions(ts, "product", verbose=False)
    assert decision == "already_done"


def test_precond_failed_blocks_without_retry():
    ts = _team_status(dev="failed", product="completed")
    decision, _ = rr.check_preconditions(ts, "dev", verbose=False, is_retry=False)
    assert decision == "blocked"


def test_precond_dev_blocked_when_product_pending():
    ts = _team_status(product="pending", dev="pending")
    decision, _ = rr.check_preconditions(ts, "dev", verbose=False)
    assert decision == "blocked"


def test_precond_dev_can_run_when_product_completed():
    ts = _team_status(product="completed", dev="pending")
    decision, _ = rr.check_preconditions(ts, "dev", verbose=False)
    assert decision == "can_run"


def test_precond_dev_blocked_when_product_failed():
    ts = _team_status(product="failed", dev="pending")
    decision, _ = rr.check_preconditions(ts, "dev", verbose=False)
    assert decision == "blocked"


def test_precond_devops_skipped_when_dev_pending():
    # dev 未执行 → devops 无需发布（skipped），优先于缺文件的 blocked
    ts = _team_status(product="completed", dev="pending", devops="pending")
    decision, reason = rr.check_preconditions(ts, "devops", verbose=False)
    assert decision == "skipped"


# ── check_round_state ──────────────────────────────────────

def test_round_state_product_on_created():
    ok, _ = rr.check_round_state({"current_state": "ROUND_CREATED"}, "product", False)
    assert ok is True


def test_round_state_dev_wrong_phase():
    ok, _ = rr.check_round_state({"current_state": "PLANNING"}, "dev", False)
    assert ok is False


def test_round_state_dev_right_phase():
    ok, _ = rr.check_round_state({"current_state": "DEVELOPMENT"}, "dev", False)
    assert ok is True


def test_round_state_judge_blocked_when_team_in_progress():
    rd = {
        "current_state": "JUDGING",
        "teams": {"red": {"status": "in_progress"}, "blue": {"status": "completed"}},
    }
    ok, _ = rr.check_round_state(rd, "judge", False)
    assert ok is False


def test_round_state_none_skips():
    ok, _ = rr.check_round_state(None, "dev", False)
    assert ok is True
