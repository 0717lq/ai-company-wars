# 2026-06-03 产品需求 — rag-decompose v0.2.0

## 项目名
rag-decompose — RAG 查询分解 CLI 工具

## 做什么
优化迭代 rag-decompose v0.1.0：修复测试覆盖率（58%→80%+）、清理所有 Ruff 问题（19→0）、提升代码质量和工程规范。

## 验收标准
- [ ] 测试覆盖率 ≥ 80%（当前 58%）
- [ ] Ruff 检查零错误（当前 19 个）
- [ ] cli.py 覆盖率 > 0%（当前 0%，至少覆盖主路径和 --json 输出）
- [ ] strategies.py 覆盖率 ≥ 85%（当前 72%，补 LLM 策略测试）
- [ ] CHANGELOG.md 丰富化（记录 v0.2.0 变更详情）
- [ ] 所有现有测试仍然通过

## 技术选型
- Python 3.10+（不变）
- pytest + pytest-cov + ruff（开发依赖）
- unittest.mock（mock LLM 调用，补 LLM 策略测试）

## 项目结构
```
rag-decompose/
├── src/rag_decompose/
│   ├── __init__.py
│   ├── __main__.py       # 0% → 需要测试
│   ├── cli.py            # 0% → P0 补测试
│   ├── decomposer.py     # 100% ✅
│   ├── models.py         # 96% → 补 2 行
│   └── strategies.py     # 72% → 补 LLM 策略测试
├── tests/
│   ├── test_cli.py       # 补充 CLI 测试
│   ├── test_strategies.py # 补充 LLM 策略测试
│   └── ...               # 其他测试保持
└── pyproject.toml
```

## 差异化竞争

### 核心策略
本轮不新增功能，纯质量迭代。蓝队 rag-builder 覆盖率 82%，红队只有 58%——这是上轮评分差距的主要原因（代码质量 23 vs 30）。补齐覆盖率差距 = 直接追 7 分。

### 与蓝队对比
| 维度 | 红队当前 | 蓝队当前 | 本轮目标 |
|------|---------|---------|---------|
| 测试覆盖率 | 58% | 82% | 80%+ |
| Ruff 错误 | 19 | N803 | 0 |
| 测试数量 | 34 | 172 | 50+ |
| 版本 | v0.1.0 | v0.3.0 | v0.2.0 |
