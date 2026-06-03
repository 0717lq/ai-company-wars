# 2026-06-03 产品需求 — rag-builder v0.2.0

## 项目名
rag-builder（RAG 流水线构建工具包）

## 做什么
将 rag-builder 从"配置验证 + 模板生成"的辅助工具升级为**可实际运行的 RAG 工具包**。新增 embedding 抽象层、向量存储连接器、混合检索器、文档解析器，让 `rag-builder ingest` 和 `rag-builder query` 真正可用。同时补齐 LICENSE、英文 README、CHANGELOG 等开源基础设施。

## 验收标准
- [ ] `rag-builder ingest <dir>` 能解析文档 → 分块 → 向量化 → 存入 Milvus/Chroma
- [ ] `rag-builder query "问题"` 能检索 → rerank → 返回结果
- [ ] Embedding 抽象层支持 sentence-transformers 和 OpenAI 兼容 API（如 MIMO/DashScope）
- [ ] 向量存储连接器支持 Milvus 和 Chroma，统一接口
- [ ] 混合检索器实现 BM25 + 向量 RRF 融合
- [ ] LICENSE 文件存在（MIT）
- [ ] CHANGELOG.md 存在（Keep a Changelog 格式）
- [ ] README.en.md 英文独立 README 存在
- [ ] 测试覆盖率 ≥ 80%，全部通过
- [ ] 版本号升至 v0.2.0

## 技术选型
- Python 3.10+，CLI via argparse
- sentence-transformers（本地 embedding）
- OpenAI SDK（远程 embedding API 兼容）
- pymilvus（Milvus 客户端）
- chromadb（Chroma 客户端）
- rank-bm25（BM25 检索）
- pymupdf（PDF 解析）

## 项目结构

```
project/
├── pyproject.toml                    # v0.2.0, 新增依赖
├── README.md                         # 更新
├── README.en.md                      # 新增：英文 README
├── LICENSE                           # 新增：MIT
├── CHANGELOG.md                      # 新增：Keep a Changelog
├── SKILL.md                          # 更新：新增 3 章
├── docs/
│   ├── STRUCTURE.md
│   ├── FILES.md
│   └── CODE.md
├── src/rag_builder/
│   ├── __init__.py                   # v0.2.0
│   ├── __main__.py
│   ├── cli.py                        # 更新：新增 ingest/query 子命令
│   ├── config_schema.py              # 保持
│   ├── scaffold.py                   # 保持
│   ├── benchmark.py                  # 保持
│   ├── embeddings.py                 # 新增：Embedding 抽象层
│   ├── vector_store.py               # 新增：向量存储连接器
│   ├── retriever.py                  # 新增：混合检索器
│   └── parsers.py                    # 新增：文档解析器
└── tests/
    ├── test_benchmark.py             # 保持
    ├── test_cli.py                   # 更新
    ├── test_config_schema.py         # 保持
    ├── test_scaffold.py              # 保持
    ├── test_embeddings.py            # 新增
    ├── test_vector_store.py          # 新增
    ├── test_retriever.py             # 新增
    └── test_parsers.py               # 新增
```

## 差异化竞争

### vs Round 8（自身迭代）
| 维度 | v0.1.0 | v0.2.0 |
|------|--------|--------|
| 核心能力 | 配置验证 + 模板生成 | 完整 RAG pipeline（ingest/query） |
| Embedding | 无 | 抽象层（本地 + API） |
| 向量存储 | 无 | Milvus + Chroma 连接器 |
| 检索 | 无 | 混合检索 BM25+Vector RRF |
| 文档解析 | 无 | PDF + Markdown 解析器 |
| 代码行数 | 1166 | ~2500（目标） |
| 开源规范 | 缺 LICENSE/CHANGELOG/英文 README | 全部补齐 |

### vs 红队（竞品对比）
红队 Round 9 从零开始。蓝队已在 Round 8 建立 774 行 SKILL.md + 1166 行代码基础，迭代速度远超从零搭建。

### vs LangChain/LlamaIndex
| 维度 | rag-builder | LangChain | LlamaIndex |
|------|------------|-----------|------------|
| 定位 | 轻量工具包 | 重型框架 | RAG 框架 |
| 安装 | pip install，无重依赖 | 依赖链复杂 | 依赖链复杂 |
| 上手 | CLI 一行命令 | 需学 API | 需学 API |
| 可定制 | 低耦合，可单独用模块 | 高耦合 | 中耦合 |
| SKILL.md | 774 行实战知识库 | 无 | 无 |

**核心差异化：轻量 + 实战知识库 + CLI 驱动。** 不做重型框架，做 RAG 开发者的"瑞士军刀"。

## 裁判 Round 8 反馈对应

| 反馈 | 本轮处理 | 优先级 |
|------|---------|--------|
| Python 包深度有限 | 新增 4 个核心模块（embeddings/vector_store/retriever/parsers） | P0 |
| 无 LICENSE | 补齐 MIT LICENSE | P0 |
| 无英文 README | 创建 README.en.md | P0 |
| 无 CHANGELOG | 创建 CHANGELOG.md | P0 |
| SKILL.md 知识深度不匹配代码 | 代码行数翻倍，新增实际 RAG 逻辑 | P0 |
| 测试中 mock 较多 | 新增模块设计为可 mock + 集成测试 | P1 |
