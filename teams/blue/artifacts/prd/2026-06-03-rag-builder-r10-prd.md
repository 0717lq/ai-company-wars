# 2026-06-03 产品需求 — rag-builder v0.3.0

## 项目名
rag-builder（RAG 流水线构建工具包）

## 做什么
在 v0.2.0 基础上做三件事：①修复测试 bug 消除红灯 ②拆分 SKILL.md 降低 token 消耗 ③新增 `rag-builder diagnose` 诊断命令，补全 RAG 工具链最后一环。版本升至 v0.3.0。

## 验收标准
- [ ] OpenAIProvider batch_processing 测试通过（修复 off-by-one bug）
- [ ] 全部 142+ 测试通过，0 failures
- [ ] SKILL.md 拆分为主文件（≤300 行）+ references/ 子文件（≥3 个专题文件）
- [ ] `rag-builder diagnose <config>` 命令可用：检查配置完整性、依赖可用性、GPU 显存、网络连通性
- [ ] diagnose 输出包含 JSON 格式（`--json` flag）
- [ ] CHANGELOG.md 更新 v0.3.0 条目
- [ ] 版本号升至 v0.3.0（pyproject.toml + __init__.py）
- [ ] 测试覆盖率 ≥ 80%

## 技术选型
沿用 v0.2.0 技术栈，不引入新依赖。diagnose 命令复用现有 config_schema.py + embeddings.py 模块。

## 项目结构（增量变化）

```
project/
├── pyproject.toml                    # v0.3.0
├── SKILL.md                          # 精简版（≤300行）
├── references/                       # 新增：SKILL.md 拆分出的专题文件
│   ├── pdf-parsing.md
│   ├── embedding-models.md
│   ├── chunking-strategies.md
│   ├── vector-stores.md
│   ├── retrieval-methods.md
│   └── pitfalls.md
├── CHANGELOG.md                      # 更新
├── src/rag_builder/
│   ├── cli.py                        # 新增 diagnose 子命令
│   └── embeddings.py                 # 修复 batch_processing bug
└── tests/
    ├── test_embeddings.py            # 修复测试
    └── test_diagnose.py              # 新增
```

## 差异化竞争

| 因素 | 分析 |
|------|------|
| 裁判反馈对应 | ① 测试失败修复（P0）② SKILL.md 拆分（P0）③ 工具链完整性——diagnose 填补"安装后第一步"的空白 |
| 差异化点 | `rag-builder diagnose` 是竞品（LangChain/LlamaIndex/Haystack）都没有的"一键健康检查"命令。RAG 系统部署前 80% 的问题是配置错误、依赖缺失、显存不足——diagnose 把这些全部自动化检测 |
| 红队态势 | 红队从零开始，蓝队 v0.3.0 已有 10 个源码模块 + 7 个 CLI 命令 + 完整 SKILL.md 知识库。迭代优势巨大 |
| 累计态势 | 蓝队 452 vs 红队 377（+75），保持节奏即可。修复裁判指出的全部不足是最稳妥的得分路径 |
| 迭代 vs 重开 | rag-builder v0.2.0 已验证（R9 86分），修复+增强优于重开 |

## 与上轮裁判反馈的逐条对应

| 裁判建议 | 本轮处理 | 优先级 |
|---------|---------|--------|
| 测试 1 个失败（batch off-by-one） | 修复 embeddings.py batch 切割逻辑 | P0 |
| SKILL.md 过长（774行→建议拆分） | 拆分为主文件 + 6 个 references/ 专题文件 | P0 |
| 功能覆盖——diagnose 是自然延伸 | 新增 diagnose 命令（配置+依赖+GPU+网络检查） | P0 |
| CHANGELOG 更新 | v0.3.0 条目 | P0 |
