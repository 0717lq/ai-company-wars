# Sprint 9 任务清单 — rag-builder v0.2.0

> 更新时间：2026-06-03
> 项目：rag-builder
> 团队：Blue

---

## P0（必须完成 — MVP 核心）

### T1: Embedding 抽象层
- **文件**: `src/rag_builder/embeddings.py`（新增）
- **内容**: `EmbeddingProvider` 抽象基类 + `STProvider`（sentence-transformers）+ `OpenAIProvider`（OpenAI 兼容 API）+ `get_provider()` 工厂函数
- **接口**: `embed_texts(texts: list[str]) -> list[list[float]]`，支持 batch_size、normalize、device 参数
- **预估**: 150 行

### T2: 向量存储连接器
- **文件**: `src/rag_builder/vector_store.py`（新增）
- **内容**: `VectorStore` 抽象基类 + `MilvusStore` + `ChromaStore` + `get_store()` 工厂函数
- **接口**: `add(ids, texts, embeddings, metadata)` / `search(embedding, top_k)` / `delete(ids)` / `count()`
- **预估**: 200 行

### T3: 文档解析器
- **文件**: `src/rag_builder/parsers.py`（新增）
- **内容**: `parse_pdf(path)` → list[dict]（pymupdf）+ `parse_markdown(path)` → list[dict] + `parse_directory(path)` → list[dict] + `chunk_text(text, strategy, chunk_size, overlap)` 分块器
- **预估**: 150 行

### T4: 混合检索器
- **文件**: `src/rag_builder/retriever.py`（新增）
- **内容**: `HybridRetriever` 类，组合 BM25 + 向量检索，RRF 融合排序
- **接口**: `index(documents)` / `search(query, top_k)` → list[dict]，可选 reranker
- **预估**: 150 行

### T5: CLI 扩展 — ingest/query 子命令
- **文件**: `src/rag_builder/cli.py`（更新）
- **内容**: `rag-builder ingest <dir> --config <json>` 调用 parsers → embeddings → vector_store 完成入库；`rag-builder query "问题" --config <json>` 调用 retriever 完成检索
- **预估**: 100 行增量

### T6: 测试
- **文件**: `tests/test_embeddings.py`, `tests/test_vector_store.py`, `tests/test_retriever.py`, `tests/test_parsers.py`（新增）+ `tests/test_cli.py`（更新）
- **内容**: 每个新模块单元测试（mock 外部依赖），CLI 子命令集成测试
- **预估**: 4 个新测试文件，≥ 60 个测试用例

---

## P1（体验完善）

### T7: 开源基础设施
- **文件**: `LICENSE`（新增 MIT）、`CHANGELOG.md`（新增）、`README.en.md`（新增英文 README）
- **内容**: 标准 MIT LICENSE、Keep a Changelog v0.2.0 条目、完整英文 README（Installation/Quick Start/CLI Reference/Architecture）

### T8: SKILL.md 更新
- **文件**: `SKILL.md`（更新）
- **内容**: 新增"向量存储选型"、"Embedding 微调"、"生产部署"三章；更新快速决策树引用新 CLI 命令

### T9: pyproject.toml 更新
- **文件**: `pyproject.toml`（更新）
- **内容**: 版本号 0.1.0→0.2.0，新增 optional-dependencies（milvus/chromadb/sentence-transformers），更新 keywords/classifiers

---

## P2（锦上添花）

### T10: docs/ 更新
- **文件**: `docs/STRUCTURE.md`, `docs/FILES.md`, `docs/CODE.md`（更新）
- **内容**: 反映 v0.2.0 新增模块

### T11: 集成测试
- **文件**: `tests/test_integration.py`（新增）
- **内容**: 端到端测试：parse → chunk → embed（mock）→ store（mock）→ query → results
