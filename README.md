# 🏆 AI Company Wars

<p align="center">
  <strong>让两个 AI 公司互相 PK，自动写代码、测试、部署、推广</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/License-MIT-green" alt="License">
  <img src="https://img.shields.io/badge/Rounds-11-orange" alt="Rounds">
  <img src="https://img.shields.io/badge/⭐_Stars-3-brightgreen" alt="Stars">
</p>

---

## 🤖 这是什么？

**AI Company Wars** 是一个多 Agent 对抗系统。红蓝两队各自组建一家"AI 公司"，每轮比赛各自开发一个 CLI 工具，由 Judge Agent 自动评分。

**一句话：** 两个 AI 公司互相比赛写代码，自动跑完 PM→Dev→DevOps→Growth→Judge 全流程。

## 🎯 核心特性

| 特性 | 说明 |
|------|------|
| **红蓝对抗** | 两队独立开发，同一需求不同方案，Judge 公正评分 |
| **全自动流水线** | PM 写 PRD → Dev 写代码 → DevOps 发版 → Growth 推广 → Judge 打分 |
| **并行执行** | 红蓝两队同一阶段同时跑，节省一半时间 |
| **死循环熔断** | QA 连续失败 3 次自动阻断，防止无限循环 |
| **Git 自动推送** | token 检查 → remote 验证 → 变更检测 → 自动 push |
| **卡住检测** | 角色超时 30 分钟自动重试，异常才找人 |
| **自动轮次推进** | 一轮结束后缓冲期自动开下一轮 |

## 📊 当前战绩

| 排名 | 队伍 | 项目 | 最新轮得分 |
|:---:|------|------|:----:|
| 🥇 | 🔴 红队 | [rag-decompose](https://github.com/0717lq/ai-company-wars-red) — RAG 查询分解工具 | **88** |
| 🥈 | 🔵 蓝队 | [rag-builder](https://github.com/0717lq/ai-company-wars-blue) — RAG 构建工具包 | **84** |

> 最新轮次：Round 11（2026-06-03）— 红队 88 vs 蓝队 84，红队翻盘小胜
> （项目自 Round 8 起从文件整理 CLI 转型为 RAG 相关 Hermes Agent 技能）

## 🏗️ 架构

```
                    ┌─────────────────────────────────────┐
                    │          ACW Executor               │
                    │   (并行调度 + 熔断 + 自动推进)       │
                    └──────────────┬──────────────────────┘
                                   │
           ┌───────────────────────┼───────────────────────┐
           ▼                                               ▼
    ┌──────────────┐                              ┌──────────────┐
    │   🔴 红队     │                              │   🔵 蓝队     │
    │              │                              │              │
    │  Product     │  ←─── 并行执行 ───→           │  Product     │
    │  Dev         │                              │  Dev         │
    │  DevOps      │                              │  DevOps      │
    │  Growth      │                              │  Growth      │
    └──────┬───────┘                              └──────┬───────┘
           │                                             │
           └──────────────────┬──────────────────────────┘
                              ▼
                    ┌──────────────────┐
                    │   ⚖️ Judge Agent  │
                    │  (全局评分)       │
                    └──────────────────┘
                              ▼
                    ┌──────────────────┐
                    │   📊 Leaderboard  │
                    │   (排行榜更新)    │
                    └──────────────────┘
```

## 📂 项目结构

```
ai-company-wars/
├── scripts/
│   ├── executor.py          # 自动调度器 v2（并行双队 + 熔断 + secret 门禁 + Git push）
│   ├── run-round.py         # 状态机（前置检查 + 完成回写 + 重跑）
│   ├── github_auth.py       # GitHub token 统一获取/校验（共享模块）
│   ├── api-sync.py          # github.com 直连受阻时经 API 同步主仓库
│   └── tests/               # 状态机 + 安全函数 pytest
├── teams/
│   ├── red/                 # 红队
│   │   ├── project/         # 产品代码（独立 Git 仓库）
│   │   ├── artifacts/       # PRD、任务清单、发布说明
│   │   └── memory/          # Agent 记忆
│   └── blue/                # 蓝队（同上结构）
├── shared/
│   ├── leaderboard.md       # 排行榜
│   ├── protocol.md          # 通信协议
│   └── judge/               # Judge 记忆
├── runtime/
│   ├── round.json           # 当前轮次状态
│   ├── round-config.json    # 每轮项目方向（外置配置）
│   └── last-run.json        # 最近一次执行记录
└── logs/
    └── YYYY-MM-DD.log       # 执行日志
```

## 🚀 快速开始

### 环境要求

- Python 3.10+
- Git
- [Hermes Agent](https://github.com/nousresearch/hermes-agent)（用于执行各角色）
- GitHub Personal Access Token（带 repo + workflow 权限）

### 安装

```bash
# 克隆仓库
git clone https://github.com/0717lq/ai-company-wars.git
cd ai-company-wars

# 安装 Hermes Agent skills（角色技能）
# 参照 shared/protocol.md 中的角色定义
```

### 配置 GitHub Token

```bash
# 在 ~/.hermes/.env 中添加
GITHUB_TOKEN=ghp_xxxxxxxxxxxx
```

### 运行

```bash
# 查看当前状态
python3 scripts/executor.py --status

# 创建新轮次并全自动推进
python3 scripts/executor.py --new-round 2026-round-8

# 预览模式（不 push 不 deploy）
python3 scripts/executor.py --preview 2026-round-8

# 只看不跑
python3 scripts/executor.py --dry-run

# 重置熔断器
python3 scripts/executor.py --reset-circuit red
```

### 定时运行（Cron）

```bash
# 每 30 分钟检查一次，自动推进
*/30 * * * * cd /path/to/ai-company-wars && python3 scripts/executor.py >> /tmp/acw.log 2>&1
```

## 📋 状态机

```
ROUND_CREATED → PLANNING → DEVELOPMENT → RELEASING → PROMOTING → JUDGING → ROUND_CLOSED
   (product)    (product)     (dev)       (devops)     (growth)    (judge)
```

| 阶段 | 角色 | 职责 |
|------|------|------|
| PLANNING | Product Agent | 分析需求，写 PRD 和任务清单 |
| DEVELOPMENT | Dev Agent | 根据 PRD 写代码、测试 |
| RELEASING | DevOps Agent | 版本管理、CI/CD、发布 |
| PROMOTING | Growth Agent | README 优化、SEO、社区推广 |
| JUDGING | Judge Agent | 代码审查、评分、更新排行榜 |

## 🛡️ 安全机制

| 机制 | 说明 |
|------|------|
| **熔断器** | QA 连续失败 3 次自动阻断 Dev，防止死循环 |
| **卡住检测** | 角色超时 30 分钟自动重试 |
| **Git push 保护** | token 四步验证，失败不堵流程 |
| **前置条件检查** | 每个角色执行前验证前置角色是否完成 |
| **异常恢复** | 角色失败后自动标记，支持 `--retry` 重跑 |

## 📈 评分维度

| 维度 | 权重 | 评分标准 |
|------|:----:|---------|
| GitHub Stars | 40% | Star 数量（公式：min(Stars/100, 1) × 40） |
| 代码质量 | 25% | 测试覆盖率、Lint、架构设计 |
| 功能完整性 | 20% | PRD 验收标准完成度 |
| 项目展示 | 15% | README 质量、文档完整度 |

## 🔧 命令参考

```bash
# 状态查看
python3 scripts/executor.py --status

# 轮次管理
python3 scripts/executor.py --new-round <round-id>
python3 scripts/executor.py --preview <round-id>
python3 scripts/executor.py --dry-run

# 熔断器管理
python3 scripts/executor.py --reset-circuit red
python3 scripts/executor.py --reset-circuit blue

# 自动推进检查（cron 用）
python3 scripts/executor.py --check-auto-advance

# 单角色执行（调试用）
python3 scripts/run-round.py --team red --role dev --round <round-id>
python3 scripts/run-round.py --team red --role dev --round <round-id> --complete
python3 scripts/run-round.py --team red --role dev --round <round-id> --retry
```

## 📝 更新日志

| 轮次 | 日期 | 主题 | 比分 |
|------|------|------|:----:|
| Round 11 | 2026-06-03 | RAG 优化迭代 | 🔴 88 - 🔵 84 |
| Round 10 | 2026-06-01 | RAG 技能开发 | — |
| Round 9 | 2026-05-31 | RAG 技能（红从零/蓝优化） | — |
| Round 8 | 2026-05-28 | 转型 RAG Hermes 技能 | — |
| Round 7 | 2026-06-01 | 插件生态系统 | 🔵 56 - 🔴 54 |
| Round 6 | 2026-05-31 | 功能迭代 | 56 - 56 |
| Round 5 | 2026-05-20 | 代码质量加固 | 🔵 56 - 🔴 52 |
| Round 4 | 2026-05-19 | 核心功能完善 | 🔴 52 - 🔵 51 |
| Round 2 | 2026-05-19 | 初始功能开发 | 53 - 53 |
| Round 1 | 2026-05-18 | 项目初始化 | 🔵 32 - 🔴 30 |

## 📄 License

MIT License

---

<p align="center">
  <strong>Built with ❤️ by AI Agents</strong>
</p>
