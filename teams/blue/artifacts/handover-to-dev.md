# Handover: Product → Dev（Round 9）

> 日期: 2026-06-03
> 项目: rag-builder v0.2.0
> 团队: Blue

---

## 本轮目标

将 rag-builder 从"配置验证 + 模板生成"升级为**可实际运行的 RAG 工具包**。

## 做什么

4 个新核心模块 + CLI 扩展 + 开源基础设施补齐：

1. **embeddings.py** — Embedding 抽象层（sentence-transformers 本地 + OpenAI 兼容 API 远程）
2. **vector_store.py** — 向量存储连接器（Milvus + Chroma，统一接口）
3. **parsers.py** — 文档解析器（PDF/Markdown）+ 分块器
4. **retriever.py** — 混合检索器（BM25 + 向量 RRF 融合）
5. **cli.py 扩展** — `ingest` 和 `query` 子命令
6. **开源基础设施** — LICENSE、CHANGELOG.md、README.en.md

## 文件位置

- PRD: `artifacts/prd/2026-06-03-rag-builder-r9-prd.md`
- 任务: `artifacts/tasks.md`
- 项目代码: `project/src/rag_builder/`

## 设计约束

1. **新模块必须有抽象基类** — 方便测试 mock，方便后续扩展（如加 Qdrant/FAISS）
2. **工厂函数模式** — `get_provider("st")` / `get_store("milvus")`，配置驱动
3. **所有外部依赖用 optional** — `pip install rag-builder[milvus]` / `rag-builder[chromadb]`，核心包不强制安装重型依赖
4. **现有 78 测试不能破坏** — 新功能是增量，不改现有模块接口
5. **版本号升至 0.2.0**

## 注意事项

- pymilvus 和 chromadb 是重型依赖，测试中必须 mock，不要在 CI 中实际连接数据库
- sentence-transformers 同理，测试中 mock embedding 返回值
- PDF 解析用 pymupdf（轻量），不要引入 marker-pdf 或 MinerU（太重）
- 混合检索的 RRF 公式：`score = 1/(k + rank_bm25) + 1/(k + rank_vector)`，k=60 是常用值
- CLI 的 `ingest` 命令需要进度显示（用 print 即可，不需要 tqdm）

## 验收标准

- `pip install -e .` 后 `rag-builder --help` 显示所有子命令
- `rag-builder init` 生成配置文件（已有功能，不破坏）
- `rag-builder validate` 验证配置（已有功能，不破坏）
- `rag-builder ingest --help` 和 `rag-builder query --help` 显示参数说明
- 全部测试通过（旧 78 + 新 ≥ 60 = ≥ 138）
- Ruff clean
