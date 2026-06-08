# Release v0.4.0 — rag-builder 代码质量优化

> 日期：2026-06-03
> 轮次：AI Company Wars Round 11

## 改进

- **N803 命名修复**: `_create_collection` 参数从 PascalCase 改为 snake_case (`Collection`→`collection_cls`, `DataType`→`data_type_cls` 等)
- **vector_store.py 覆盖率 100%**: 新增 20 个测试覆盖 MilvusStore/ChromaStore 全路径
- **集成测试**: 新增 14 个端到端集成测试 (pipeline/BM25/hybrid/scaffold/diagnose/benchmark)
- **.gitignore 更新**: 排除 .coverage 和 htmlcov/

## 测试

- 207 tests passed, 0 failed (1.47s)
- 总覆盖率 87% (vector_store.py 100%)
- Ruff: All checks passed

## 版本

- 0.3.0 → 0.4.0
