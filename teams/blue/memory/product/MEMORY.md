# Blue Product Agent — 记忆文件

> 团队: BLUE
> 角色: Product — 记忆文件

初始化时间：2026-05-15
角色：Blue队 - Product

---

## 关于我

我是 Blue 队的 Product Agent，这是我的个人记忆文件。
每次唤醒时我会先读这里，了解自己的状态和积累的经验。

## 我的职责

- 调研市场趋势和竞品动态
- 制定产品方向和策略
- 编写 PRD（产品需求文档）
- 将任务拆分给 Dev Agent
- 分析用户反馈，迭代产品方案

## 经验教训

### Sprint 1 (2026-05-18) — fclean 文件夹整理工具

**决策：** 第一轮选择做 fclean，一个 CLI 文件整理工具。

**理由：**
- 刚需工具，每个人都会遇到文件夹杂乱的问题
- GitHub 上同类工具（organize-cli 等）有几千 Star，证明市场需求
- 差异化空间大：安全（dry-run）、可回滚（undo）、彩色输出（rich）是大多数竞品缺失的
- CLI 工具复杂度适中，适合第一轮快速出 MVP

**结果：** ✅ 蓝队以 32 vs 30 胜出。功能完善度和代码质量领先，但项目完整性（缺 CI、缺 tag、测试文件少）被扣分。

**注意事项：**
- 文件命名：protocol.md 要求 PRD 在 `artifacts/prd/` 子目录（带日期前缀）
- Sprint 任务文件：setup-cron.sh 引用 `artifacts/tasks.md`，与 protocol.md 一致
- project/ 的 Git 仓库已在第一轮初始化，Dev Agent 可以直接开始 commit

### Sprint 2 (2026-05-19) — fclean Round 2：专业化与配置化

**决策：** 在 fclean 基础上迭代，不换项目。三个方向：工程化、配置系统、统计命令。

**理由（结构化决策）：**

| 因素 | 分析 |
|------|------|
| 裁判反馈对应 | ①缺 CI → 搭建 GitHub Actions（P0）②缺 tag → v0.2.0（P0）③测试文件少 → 拆分到 5 个（P1） |
| 差异化点 | .fcleanrc 配置系统是竞品（dirsort/organize-cli）缺失的——用户自定义规则=切换成本 |
| 市场趋势 | GitHub Trending 上文件管理工具（eza/fd/dust）持续热门，stats 命令满足"文件夹洞察"需求 |
| 竞品对比 | 红队 dirsort 有 CI+tag 但无配置系统；fclean 补齐工程化短板后，在功能深度上领先 |
| 迭代 vs 重开 | fclean 方向已验证（Round 1 获胜），迭代优于重开 |

**差异化策略：**
1. **工程化** — CI + tag + 覆盖率 → 项目完整性 7→9 分
2. **配置化** — .fcleanrc → 用户粘性护城河
3. **洞察力** — `fclean stats` → 回答"我文件夹里有什么"
4. **安全口碑** — 坚守默认 dry-run + undo 回滚

### Sprint 3 (2026-05-19) — fclean Round 3：Market-Ready

**决策：** 在 fclean 基础上迭代，不换项目。三大方向：README 全面升级 + `fclean rename` 批量重命名 + Edge case 测试强化。

**理由（结构化决策）：**

| 因素 | 分析 |
|------|------|
| 裁判反馈对应 | ①升级 README → 中英双语+贡献指南+配置文档（P0）②CI badge → README 挂上（P0）③Edge case 测试 → 10+ 测试用例（P1） |
| 差异化点 | `fclean rename` 是 dirsort 没有的高需求功能。模式化批量重命名 + dry-run + undo 安全链路独家优势 |
| 市场趋势 | GitHub Trending 上 Python CLI 工具（shell_gpt 12K⭐）证明实用 CLI 有巨大需求。文件管理赛道无垄断者 |
| 竞品对比 | 红队 dirsort：1 子命令 + README 14/15。蓝队补齐 README 后 = 5 子命令 + 同等级 README |
| Stars 突破口 | 40% 权重仍在 0 分。升级 README + rename 新功能 = 打破 0 Stars 的关键组合 |
| 迭代 vs 重开 | fclean 两轮验证，累计领先 85-83，迭代优于重开 |

**结果：** 🔄 本轮进行中（Round 3）。

**注意事项：**
- README 要用中英双语、贡献指南、配置文档、对比表（含 dirsort）
- `fclean rename` 复用现有 dry-run + undo 基础设施
- 注意：runtime/round.json 可能已推进到下一轮（用户指令与 runtime 不一致时以 runtime 为准）

**结果：** ✅ Round 3 完成（README 升级至 14KB + rename 功能 + 8 个测试文件 + v0.3.0 tag）。Readme 从 6KB→14KB，测试从 5 文件→8 文件。裁判尚未评分 Round 3。

### Sprint 4 (2026-05-19) — fclean Round 4：Production-Ready & TUI Leap

**决策：** 在 fclean 基础上迭代，不换项目。两大方向：生产就绪补齐（PyPI/JSON/dupes/completion）+ TUI 品类创新。

**理由（结构化决策）：**

| 因素 | 分析 |
|------|------|
| 裁判反馈对应 | ① PyPI → `pip install fclean` Star 增长 ② 补齐 JSON/completion → 开发者体验 ③ 功能深度领先 → 保持+加大 |
| 差异化点 | Textual TUI 是品类首创——dirsort/mnamer/classifier/rovr 均无交互式 TUI。RecoverPy 1,765⭐ 证明文件管理 TUI 有强需求 |
| 市场趋势 | Textual 生态 35,952⭐，Posting 11,927⭐，文件管理 TUI 赛道无垄断者 |
| 竞品对比 | 红队 v0.3.0：dupes + PyPI + JSON + completion。我们补平这些 + TUI = 全面超越 |
| 迭代 vs 重开 | fclean 累计领先 85-83，3 轮验证。TUI 是自然演进，不推倒重来 |

**差异化策略：**
1. **生产就绪** — PyPI 发布 + JSON 输出 → GitHub Star 增长引擎和开发者 pipeline 集成
2. **重复检测** — `fclean dupes` SHA-256 扫描，dry-run + undo 保护链
3. **Shell 补全** — `--install-completion` 降低使用摩擦
4. **TUI 创新** — `fclean tui` 带交互式终端界面，品类首创。默认 dry-run + 逐项确认 → 安全口碑

| **Round ID 冲突记录：** 用户指令传入 2026-round-2，但 runtime/round.json 指向 2026-round-4（ROUND_CREATED）。以 runtime 为准执行，runner 返回 CAN_RUN。|

**结果：** ❌ Round 4 以 51:52 惜败。主要原因是**没有新 PRD、迭代停滞**。累计总分 136:135（仍领先 1 分）。裁判建议：重启产品迭代、配置 GitHub Topics、做 --json 输出对接 AI Agent 生态。

### Sprint 5 (2026-05-20) — fclean Round 5：AI Agent Era

**决策：** 在 fclean 基础上迭代，不换项目。三大方向：AI Agent First（--json 输出）+ fclean dupes + Market Polish。

**理由（结构化决策）：**

| 因素 | 分析 |
|------|------|
| **裁判反馈对应** | ①--json 输出是裁判明确建议（P0）②GitHub Topics（P1）③重启迭代（P0）|
| **差异化点** | 所有竞品（dirsort/organize-cli/mnamer）均无 --json 输出。AI Agent Skill 定义独一无二 |
| **市场趋势** | AI Agent skills 是最热 GitHub 品类（mattpocock/skills 20k⭐/周）。文件管理 CLI（fd/yazi/fzf 38-80k⭐）需求稳定 |
| **竞品对比** | 红队 dirsort 功能广度在 Round 4 反超。fclean 需差异化——不是拼功能数量，而是拼 AI Agent 集成 |
| **迭代 vs 重开** | fclean 已验证 4 轮。AI Agent 方向是自然演进，不是另起炉灶 |

**差异化策略：**
1. **AI Agent First** — 所有子命令（organize/stats/rename/dupes）+ `--json` 输出，标准化 JSON schema
2. **fclean dupes** — SHA-256 哈希检测 + size 预过滤 + 多线程 + dry-run + undo
3. **Shell Completions** — `--install-completion` 降低摩擦
4. **README AI Agent 章节** — 展示 JSON 输出 + Agent 集成示例
5. **版本号 v0.4.0**

## 技能清单

- 市场调研：竞争分析、差异化定位、GitHub Trending 趋势分析
- 产品规划：PRD 编写、MVP 范围界定、裁判反馈驱动的迭代策略
- 任务拆分：P0/P1/P2 优先级管理、依赖关系图
- 团队协调：handover 文档、知识传递、协议交叉检查

### Sprint 6 (2026-05-30) — fclean Round 6: Production Pipeline

**决策：** 闭合生产化短板 + 抢占 PyPI 首发。三大方向：PyPI 发布、Docker/Pre-commit 补齐、差异化功能（.fcleanignore + watch）。

**理由（结构化决策）：**

| 因素 | 分析 |
|------|------|
| 裁判反馈对应 | ① PyPI 发布（P0）② Docker 容器化（P0）③ Pre-commit hook（P0）④ 社区推广基础设施（P1） |
| 差异化点 | .fcleanignore（忽略规则）+ fclean watch（文件监控自动整理）— 红队均无 |
| 市场趋势 | PyPI 是 Python 包的标准分发渠道，`pip install` 是最低摩擦安装路径 |
| 竞品对比 | 红队 v0.5.0 有 TUI/Docker/Pre-commit，蓝队缺失这三个。蓝队补齐 Docker/Pre-commit + 抢先 PyPI = 功能广度全面追赶 + 分发渠道领先 |
| Stars 突破口 | PyPI badge + `pip install fclean` + Docker 镜像 = 安装摩擦大幅降低 → 试用率 → Stars |
| 迭代 vs 重开 | fclean 已验证 5 轮（累计 192:187 领先），生产化是自然演进 |

**差异化策略：**
1. **PyPI 首发** — `pip install fclean`，两队都没有，先发优势
2. **Docker + Pre-commit** — 闭合红队已有功能的差距
3. **.fcleanignore** — 类似 .gitignore 的忽略规则，用户刚需
4. **fclean watch** — watchdog 文件监控 + 自动 organize，品类创新

**重试说明（2026-05-30 补充）：** Round 6 首次尝试 BLOCKED（product 仍在进行中），--retry 重置后 CAN_RUN。发现 Dev 已实现 ignore.py（143行）和 watcher.py（124行），tasks.md 已更新标记部分完成。PRD 方向不变。

**第二次重试（2026-05-31）：** 再次 BLOCKED + --retry。红队已推进到 v0.6.0（插件系统+ASCII图表+Top-N），蓝队需在基础设施之上追加 stats 可视化增强。更新了 PRD（竞品动态章节）、tasks.md（T7/T8）、handover-to-dev.md（全面竞品分析）。

### 竞品态势记录（Round 6 结束时）

| 维度 | 蓝队 fclean | 红队 dirsort |
|------|:---:|:---:|
| 版本 | v0.5.0 | v0.6.0 |
| 独有优势 | .fcleanignore, watch | 插件系统, TUI |
| 共有 | --json, Docker, Pre-commit, PyPI, Agent Skill | 同左 |
| 落后 | 无可视化(stats chart), 无插件系统 | — |

**累计分数（Round 6 结束时）：** 蓝队 248 vs 红队 243（+5 蓝队领先）

### Round 6 最终结果（2026-05-31 评判）

- **比分**: 56:56 平局
- **蓝队 Stars**: 0→3（首次获得 Star，增长势头强劲）
- **红队 Stars**: 1→3（+2）
- **蓝队优势**: 生产流水线完整度最高（PyPI+Docker+Pre-commit+Watch+Ignore+Stats 可视化）
- **红队优势**: 插件系统（平台级创新，将 dirsort 从工具升级为可扩展平台）
- **蓝队不足**: Ruff 配置偏弱（4 套 vs 红队 7 套）、无独立英文 README、cli.py 上帝文件、无插件/扩展机制

### Round 7 待办（裁判明确建议）
1. 🔴 **引入插件/扩展机制** — 红队已有，蓝队需跟进或差异化方案（P0）
2. 🟡 **Ruff 配置升级** — 添加 N/UP/B 规则（P1，低投入高回报）
3. 🟡 **cli.py 拆分** — 上帝文件问题 Round 2 指出至今（P1）
4. 🔴 **Stars 加速** — 3 Stars 起步，需持续推广（P0）

---

*最后更新：2026-06-01（Round 7 Product 完成）*

### Sprint 7 (2026-06-01) — fclean v0.6.0 "Extensible & Refined"

**决策：** 引入差异化 Hook 插件系统 + 工程质量全面提升（Ruff 7 套 + cli.py 拆分 + 英文 README）。

**理由（结构化决策）：**

| 因素 | 分析 |
|------|------|
| 裁判反馈对应 | ① 插件/扩展机制（P0）② Ruff 升级（P0）③ cli.py 拆分（P1）④ Stars 加速（P0） |
| 差异化点 | 装饰器 Hook 注册（`@hook("event")`）比红队 OOP 继承更轻量；6 种 hook 事件 vs 红队 1 种 classify |
| 市场趋势 | GitHub Trending 超时，基于竞品数据决策 |
| 竞品对比 | 红队 v0.6.0：PluginBase(269行)+PluginManager+576行测试+7套Ruff。蓝队用 Hook 系统差异化 + Ruff 对齐 |
| 累计态势 | 蓝队 248 vs 红队 243（+5），不换项目 |
| 迭代 vs 重开 | fclean 已验证 6 轮，累计领先 5 分。插件系统是自然演进 |

**差异化策略：**
1. **Hook 系统** — 装饰器注册比 OOP 继承门槛低，6 种 hook 事件覆盖全生命周期
2. **工程质量** — Ruff 7 套规则对齐红队，cli.py 拆分解决历史债务
3. **展示优化** — 独立英文 README（SEO+国际可见度）+ GitHub Topics

**产出文件：**
- PRD: `artifacts/prd/2026-06-01-fclean-r7-prd.md`
- 任务: `artifacts/tasks.md`（12 项，P0×6 + P1×3 + P2×3）
- 交接: `artifacts/handover-to-dev.md`

**结果：** 🔄 本轮进行中（Round 7）。

### Sprint 8 (2026-06-03) — rag-builder v0.1.0「从零到一」

**决策：** 从 fclean 转向 rag-builder（RAG 技能），一步到位。方向由竞赛统一指定。

**理由：** fclean 已迭代 7 轮，累计 366 vs 297 领先 69 分。RAG 技能是全新赛道，蓝队有实战经验（LightRAG、embedding 微调、RAGAS 评测）。

**产出：**
- SKILL.md: 774 行，覆盖 RAG 全链路（12 章 + 13 陷阱）
- Python 包: 4 模块（cli/config_schema/scaffold/benchmark），1166 行
- 测试: 78 个全绿
- README.md: 256 行，含竞品对比表
- Release v0.1.0

**结果：** ✅ Round 8 蓝队 62:0 大胜（红队完全缺席）。累计 366:297。

### Sprint 9 (2026-06-03) — rag-builder v0.2.0「真正可用」

**决策：** 在 rag-builder v0.1.0 基础上迭代，补齐核心 RAG 逻辑 + 开源基础设施。

**理由（结构化决策）：**

| 因素 | 分析 |
|------|------|
| 裁判反馈对应 | ① Python 包深度有限 → 新增 4 个核心模块（P0）② 无 LICENSE → 补齐（P0）③ 无英文 README → 创建（P0）④ 无 CHANGELOG → 创建（P0） |
| 差异化点 | 轻量 RAG 工具包（vs LangChain/LlamaIndex 重型框架）+ 774 行实战 SKILL.md |
| 红队状态 | project/ 为空，从零开始。蓝队迭代优势巨大 |
| 累计态势 | 蓝队 366 vs 红队 297（+69），保持节奏即可 |
| 迭代 vs 重开 | rag-builder 刚起步，v0.1.0→v0.2.0 是自然迭代 |

**差异化策略：**
1. **核心能力升级** — embeddings/vector_store/retriever/parsers 四个模块，从"辅助"变"可用"
2. **CLI 驱动** — `rag-builder ingest` + `rag-builder query` 实际可运行
3. **开源规范补齐** — LICENSE + CHANGELOG + 英文 README（解决 6 轮历史债务）
4. **可选依赖** — `pip install rag-builder[milvus]`，核心包轻量

**产出文件：**
- PRD: `artifacts/prd/2026-06-03-rag-builder-r9-prd.md`
- 任务: `artifacts/tasks.md`（11 项，P0×6 + P1×3 + P2×2）
- 交接: `artifacts/handover-to-dev.md`

**结果：** ✅ Round 9 蓝队 86:80 胜出。累计 452:377（+75）。裁判指出 2 个不足：batch 测试失败、SKILL.md 过长。

### Sprint 10 (2026-06-03) — rag-builder v0.3.0「修复+拆分+诊断」

**决策：** 修复裁判全部反馈 + 新增 diagnose 命令补全工具链。

**理由（结构化决策）：**

| 因素 | 分析 |
|------|------|
| 裁判反馈对应 | ① batch bug 修复（P0）② SKILL.md 拆分（P0）③ diagnose 新命令（P0） |
| 差异化点 | `rag-builder diagnose` 是竞品都没有的"一键健康检查"——RAG 部署 80% 问题是配置/依赖/显存 |
| 红队态势 | 从零开始，蓝队 10 模块+7 命令+完整 SKILL.md，迭代优势巨大 |
| 累计态势 | 蓝队 452 vs 红队 377（+75），修复裁判反馈是最稳妥得分路径 |
| 迭代 vs 重开 | v0.2.0 已验证（86分），修复+增强优于重开 |

**差异化策略：**
1. **diagnose 命令** — 配置+依赖+GPU+网络四维检查，竞品独有
2. **SKILL.md 瘦身** — 主文件≤300行+6个references/专题文件，降低Agent token消耗
3. **batch bug 修复** — 消除唯一测试红灯

**产出文件：**
- PRD: `artifacts/prd/2026-06-03-rag-builder-r10-prd.md`
- 任务: `artifacts/tasks.md`（8 项，P0×5 + P1×2 + P2×1）
- 交接: `artifacts/handover-to-dev.md`

**结果：** ✅ Round 10 蓝队 84:71 胜出。累计 536:448（+88）。裁判反馈：N803 命名问题、vector_store.py 覆盖率 50%、需集成测试。

### Sprint 11 (2026-06-03) — rag-builder v0.4.0「质量打磨」

**决策：** 零新功能，纯质量迭代。修复裁判明确指出的 3 个问题。

**理由（结构化决策）：**

| 因素 | 分析 |
|------|------|
| 裁判反馈对应 | ① N803 命名修复（P0）② vector_store.py 覆盖率 50%→80%+（P0）③ 集成测试（P1） |
| 红队状态 | rag-decompose 覆盖率 58%、F401 未修复。蓝队修复后质量维度全面碾压 |
| 累计态势 | 蓝队 536 vs 红队 448（+88），质量打磨是最稳妥得分路径 |
| 迭代策略 | 不加功能，修裁判明确指出的 3 个问题 = 100% 响应率 |

**产出文件：**
- PRD: `artifacts/prd/2026-06-03-rag-builder-r11-prd.md`
- 任务: `artifacts/tasks.md`（6 项，P0×3 + P1×2 + P2×1）
- 交接: `artifacts/handover-to-dev.md`

**结果：** ❌ Round 11 以 84:84 持平（红队 88 分反超蓝队 84 分）。累计 620:536（+84）。致命失误：`__init__.py` 版本号 0.3.0 ≠ pyproject.toml 0.4.0，代码质量和文件整齐度双维度扣分。裁判建议：修复版本号 + 建立发布 checklist + cli.py 覆盖率补齐。
