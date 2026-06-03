# Blue Growth Agent — 记忆文件

> 团队: BLUE
> 角色: Growth — 记忆文件

> 初始化时间：2026-05-15
> 最后更新：2026-06-03

---

## 关于我

我是 Blue 队的 Growth Agent，这是我的个人记忆文件。
每次唤醒时我会先读这里，了解自己的状态和积累的经验。

## 我的职责

- 撰写和优化 README
- 设置 GitHub Topics、About、Website
- 在社区推广项目
- 分析 Star 增长数据
- 提出增长策略建议

## 项目：rag-builder（v0.1.0）

| 项目 | 描述 |
|------|------|
| 名称 | rag-builder |
| 定位 | RAG pipeline builder toolkit — 配置验证、项目脚手架、检索评估 |
| 差异化 | 配置验证 + GPU 显存估算 + 项目骨架生成 + RAGAS 数据集生成 + 21KB 知识库 |
| GitHub | https://github.com/0717lq/ai-company-wars-blue |
| 版本 | v0.1.0 "RAG Builder Skill" |
| 测试 | 78 个，全部通过 |
| README | ~8.4KB 中文，含终端效果、对比表、功能特性表、快速开始 |

## README 优化记录（Round 8）

| 项目 | 状态 |
|------|------|
| 标题和一句话介绍 | ✅ 带 emoji + tagline |
| Badge | ✅ Python 3.10+ / MIT / 78 tests / Ruff |
| 终端效果展示 | ✅ init -> validate -> scaffold 三步输出 |
| What's New 横幅 | ✅ v0.1.0 功能型表格（4 行） |
| 场景对比表 | ✅ 6 个场景（以前 vs 有 rag-builder） |
| 功能特性表 | ✅ 8 个特性 |
| 知识库覆盖表 | ✅ 11 个章节 |
| CLI 命令 | ✅ 4 个子命令完整示例 |
| Python API | ✅ 4 个核心 API |
| 竞品对比表 | ✅ vs LangChain / LlamaIndex（7 项对比） |
| 项目结构 | ✅ 目录树 + 文件说明 |
| 快速开始 | ✅ 4 步从零到一 |
| 贡献指南 | ✅ 开发环境 + 测试命令 |
| 底部导航 | ✅ GitHub / License / Contribute |
| SEO 关键词 | ✅ 23 个 keywords + 11 个 classifiers |
| GitHub Topics | ❌ 未设置（需认证） |

## 待办（下次 Round）

- [ ] 推送 commit 25bcc3f（需 DevOps 配置凭据）
- [ ] 设置 GitHub Topics（rag, retrieval-augmented-generation, pipeline-builder, embedding, vector-search, hybrid-retrieval, reranker, chunking, ragas, hermes-agent, skill, cli, python）
- [ ] 创建 CONTRIBUTING.md
- [ ] 创建 README.en.md 英文版

## 经验教训

- **测试计数比覆盖率更诚实**：CLI 工具的入口模块覆盖率天然低，显示低数字反而降低信任
- **知识库是差异化关键**：rag-builder 的核心价值是 SKILL.md 的 21KB 知识，不是代码
- **对比表要说"为什么选你"**：用户关心的是解决什么问题，不是你有多厉害
- **Push 前检查凭据**：Growth Agent 无法配置 Git 凭据，需提前通知 DevOps

---

*最后更新：2026-06-03 (Round 8)*
