# rag-decompose v0.2.0 — Quality & Coverage Release

> 2026-06-03 | Round 11

## Summary

rag-decompose 从 MVP (v0.1.0) 迭代到生产就绪 (v0.2.0)，核心改进是测试覆盖率和代码质量。

## Changes

### Ruff Lint Cleanup (19 → 0 violations)
- Removed 7 unused imports (F401)
- Fixed 3 type annotations (UP045: Optional → X | None)
- Fixed 7 empty f-strings (F541)
- Fixed 1 zip missing strict parameter (B905)
- Fixed 1 assert False (B011)
- Fixed import sorting (I001)

### Test Coverage (58% → 98%)
- **cli.py**: 0% → 100% (38 tests, direct function calls)
- **strategies.py**: 72% → 98% (37 tests, with LLM mocks)
- **models.py**: 96% → 100% (8 tests)
- **Total**: 34 → 91 tests

### Version Bump
- pyproject.toml: 0.2.0
- __init__.py: 0.2.0
- CHANGELOG.md: v0.2.0 entry added

## Test Results
- 91 tests passed (1.12s)
- Ruff: All checks passed
- Coverage: 98% (292 statements, 5 misses)

## Notes
- No functional changes — pure quality release
- All existing features preserved
- LLM strategy tests use mocked API calls
