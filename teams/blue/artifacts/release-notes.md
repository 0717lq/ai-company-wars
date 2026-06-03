# Release v0.1.0 — RAG Builder Skill

> Blue Team — Round 8 | 2026-06-03

## 亮点

完整的 RAG (Retrieval-Augmented Generation) pipeline 构建指南 + Python 工具包，作为 Hermes Agent 技能发布。

## 产出物

- **SKILL.md** (21KB) — 12 章节覆盖 RAG 全链路的 Agent 技能文件
- **rag_builder Python 包** — 配置验证、项目脚手架、检索评估工具
- **78 个 pytest 测试** — 全部通过

## 功能清单

| 功能 | 模块 |
|------|------|
| 配置 schema + 验证 | config_schema.py |
| GPU 显存估算 | config_schema.py |
| 项目骨架生成 | scaffold.py |
| 检索质量评估 (Recall@K, NDCG@K) | benchmark.py |
| RAGAS 数据集生成 | benchmark.py |
| CLI (init/validate/scaffold/benchmark) | cli.py |

## SKILL.md 覆盖范围

- 文档解析（pymupdf / MinerU / Markdown）
- 分块策略（4 种 + 参数经验值）
- 嵌入模型选择（5 个模型对比）
- 向量存储（Milvus / Chroma / FAISS / Qdrant）
- 混合检索（BM25 + 向量 + RRF 融合）
- Reranker 精排（bge-reranker + 显存管理）
- 查询分解（3 种策略）
- RAGAS 评估（v0.2+ API）
- 13 个常见陷阱
- 嵌入模型微调指南

## 安装

```bash
# 作为 Hermes Agent 技能
cp SKILL.md ~/.hermes/skills/rag-builder/SKILL.md

# 作为 Python 包
pip install -e ".[dev]"
python -m rag_builder init
```
