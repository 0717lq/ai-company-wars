"""
executor.py 关键新函数单元测试：产物校验 + secret 扫描。
这两个是 P1 安全/正确性修复的核心，加测试防止回归。

运行：python3 -m pytest scripts/tests/ -v
"""

import importlib.util
import os
import subprocess
import time

import pytest

_HERE = os.path.dirname(os.path.abspath(__file__))
_EXEC_PATH = os.path.join(_HERE, "..", "executor.py")
_spec = importlib.util.spec_from_file_location("executor", _EXEC_PATH)
ex = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ex)


# ── secret 扫描 ────────────────────────────────────────────

def _init_repo(path):
    subprocess.run(["git", "init", "-q"], cwd=path, check=True)
    subprocess.run(["git", "config", "user.email", "t@t"], cwd=path, check=True)
    subprocess.run(["git", "config", "user.name", "t"], cwd=path, check=True)


def test_scan_staged_clean(tmp_path):
    d = str(tmp_path)
    _init_repo(d)
    (tmp_path / "clean.txt").write_text("hello world\nno secrets\n")
    subprocess.run(["git", "add", "clean.txt"], cwd=d, check=True)
    found, _ = ex.scan_staged_for_secrets(d)
    assert found is False


def test_scan_staged_detects_pat(tmp_path):
    d = str(tmp_path)
    _init_repo(d)
    # 运行时拼接，避免源文件本身出现连续 token 串（否则会被 secret 扫描误拦）
    fake = "github_" + "pat_" + "11ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    (tmp_path / "bad.txt").write_text(f"token={fake}\n")
    subprocess.run(["git", "add", "bad.txt"], cwd=d, check=True)
    found, detail = ex.scan_staged_for_secrets(d)
    assert found is True
    # 不能泄露完整 token，只回报前缀
    assert fake not in detail


def test_scan_staged_detects_ghp(tmp_path):
    d = str(tmp_path)
    _init_repo(d)
    fake = "ghp_" + "abcdefghijklmnopqrstuvwxyz0123456789"
    (tmp_path / "bad.txt").write_text(f"{fake}\n")
    subprocess.run(["git", "add", "bad.txt"], cwd=d, check=True)
    found, _ = ex.scan_staged_for_secrets(d)
    assert found is True


# ── 产物校验 verify_role_output ────────────────────────────

def _setup_team(tmp_path, team="red"):
    """构造一个临时 BASE_DIR 结构，返回 (base_dir, artifacts_dir)。"""
    base = tmp_path / "acw"
    art = base / "teams" / team / "artifacts"
    proj = base / "teams" / team / "project"
    art.mkdir(parents=True)
    proj.mkdir(parents=True)
    return base, art, proj


def test_verify_no_rule_role_passes(monkeypatch, tmp_path):
    base, _, _ = _setup_team(tmp_path)
    monkeypatch.setattr(ex, "BASE_DIR", str(base))
    ok, _ = ex.verify_role_output("red", "judge", time.time())
    assert ok is True  # judge 无校验规则，直接通过


def test_verify_product_missing_artifact_fails(monkeypatch, tmp_path):
    base, art, _ = _setup_team(tmp_path)
    monkeypatch.setattr(ex, "BASE_DIR", str(base))
    # 没有 handover-to-dev.md → 失败
    ok, detail = ex.verify_role_output("red", "product", time.time())
    assert ok is False
    assert "缺少产物" in detail


def test_verify_product_fresh_artifact_passes(monkeypatch, tmp_path):
    base, art, _ = _setup_team(tmp_path)
    monkeypatch.setattr(ex, "BASE_DIR", str(base))
    start = time.time()
    (art / "handover-to-dev.md").write_text("done")  # mtime 在 start 之后
    ok, _ = ex.verify_role_output("red", "product", start)
    assert ok is True


def test_verify_product_stale_artifact_fails(monkeypatch, tmp_path):
    base, art, _ = _setup_team(tmp_path)
    monkeypatch.setattr(ex, "BASE_DIR", str(base))
    (art / "handover-to-dev.md").write_text("old")
    # start 设在未来 → 产物相对“本次执行”是陈旧的 → 判定空转
    ok, detail = ex.verify_role_output("red", "product", time.time() + 9999)
    assert ok is False
    assert "未本次更新" in detail or "未更新" in detail


def test_verify_devops_glob_release_notes(monkeypatch, tmp_path):
    base, art, _ = _setup_team(tmp_path)
    monkeypatch.setattr(ex, "BASE_DIR", str(base))
    start = time.time()
    # devops 规则是 release-notes*.md，版本化命名也应匹配
    (art / "release-notes-v0.5.0.md").write_text("notes")
    ok, _ = ex.verify_role_output("red", "devops", start)
    assert ok is True
