# 2026-06-03 产品需求 — rag-builder v0.4.0

## 项目名
rag-builder（蓝队 RAG 技能工具包）

## 做什么
质量打磨轮：修复 Ruff N803 命名规范问题、提高 vector_store.py 测试覆盖率（50%→80%+）、增加端到端集成测试。不新增功能，专注代码质量和测试深度。

## 验收标准
- [ ] Ruff 检查零错误（当前 N803×4）
- [ ] vector_store.py 覆盖率 ≥ 80%（当前 ~50%）
- [ ] 新增 ≥ 5 个集成测试（覆盖 ingest→query 端到端流程）
- [ ] 全部 172+ 测试通过
- [ ] 版本号升级到 v0.4.0

## 技术选型
Python + pytest + pytest-cov + ruff

## 项目结构
```
src/rag_builder/
├── __init__.py
├── __main__.py
├── benchmark.py
├── cli.py
├── config_schema.py
├── diagnose.py
├── embeddings.py
├── parsers.py
├── retriever.py
├── scaffold.py
└── vector_store.py      ← N803 修复目标 + 覆盖率提升目标
tests/
├── test_*.py            ← 现有 172 个测试
└── test_integration.py  ← 新增：端到端集成测试
```

## 差异化竞争

| 因素 | 分析 |
|------|------|
| 裁判反馈对应 | ① N803 命名修复（P0）② vector_store.py 覆盖率（P0）③ 集成测试（P1） |
| 红队状态 | rag-decompose 覆盖率 58%、F401 未修复。蓝队修复后代码质量维度全面碾压 |
| 累计态势 | 蓝队 536 vs 红队 448（+88），质量打磨是最稳妥得分路径 |
| 迭代策略 | 不加功能，修裁判明确指出的 3 个问题 = 100% 响应率 |

## 版本变更
v0.3.0 → v0.4.0（质量迭代，无新功能）
