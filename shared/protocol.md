# AI Company Wars — Agent 通信协议

> 最后更新：2026-05-18（第 2 轮审计后统一口径）
> 版本：v1.1

---

## 1. 目录结构约定（正式运行路径）

```
ai-company-wars/                        ← 主控仓库
├── orchestrator/                       # 调度脚本（手动配置）
├── teams/
│   ├── red/
│   │   ├── project/                    # 【正式运行】红队产品代码（独立 Git 仓库，推送到 GitHub）
│   │   │   ├── src/
│   │   │   ├── tests/
│   │   │   ├── README.md
│   │   │   └── pyproject.toml
│   │   ├── memory/                     # Agent 记忆（每个角色独立）
│   │   │   ├── product/MEMORY.md + diary/   # Product Agent
│   │   │   ├── dev/MEMORY.md + diary/       # Dev Agent
│   │   │   ├── devops/MEMORY.md + diary/     # DevOps Agent
│   │   │   └── growth/MEMORY.md + diary/    # Growth Agent
│   │   └── artifacts/                  # 产出文档
│   │       ├── prd/                    # PRD 文件（日期化命名）
│   │       ├── tasks.md                # 当前 Sprint 任务
│   │       ├── handover-to-dev.md      # Product → Dev 交接
│   │       ├── ready-for-deploy.md     # Dev → DevOps 交接
│   │       ├── release-notes.md        # DevOps 发版说明
│   │       ├── designs/                # 设计文档
│   │       └── reports/                # 其他报告
│   └── blue/                           # 蓝队，同上结构
│       ├── project/
│       ├── memory/
│       └── artifacts/
├── shared/                             # 共享区域（两队都可读）
│   ├── rules.md                        # 竞赛规则（Judge 维护）
│   ├── protocol.md                     # 本文件 — 通信协议
│   ├── leaderboard.md                  # 排行榜（Judge 更新）
│   ├── announcements/                  # 通告目录（Judge 写入）
│   │   └── README.md                   # 最新通告索引
│   └── judge/                          # Judge 记忆
│       ├── memory/MEMORY.md
│       └── diary/
├── scripts/                            # 工具脚本
│   └── init-workspace.sh
└── .gitignore
```

> **正式运行路径**：`teams/{color}/project/` 是唯一代码真源。
> `red-project/`、`blue-project/`（根目录）为镜像副本，非正式运行目录。

---

## 2. 文件命名规范

| 文件类型 | 命名格式 | 示例 |
|---------|---------|------|
| PRD | `YYYY-MM-DD-<project-name>-prd.md` | `2026-05-18-fclean-prd.md` |
| 日记 | `YYYY-MM-DD-<role>.md` | `2026-05-18-dev.md` |
| 通告 | `round-<N>.md` | `round-1.md` |
| Sprint 任务 | `tasks.md` | — |
| 交接文件 | `handover-to-<target>.md` | `handover-to-dev.md` |

---

## 3. Agent 通信方式

### 3.1 通过文件传递信息

Agent 之间不直接对话，通过约定的文件路径传递信息：

```
Product → Dev:       artifacts/prd/<prd>.md + artifacts/tasks.md + artifacts/handover-to-dev.md
Dev → DevOps:        artifacts/ready-for-deploy.md + project/ 下的 Git 提交
DevOps → Growth:     artifacts/release-notes.md + Git tags
Agent → Memory:      memory/<role>/diary/<YYYY-MM-DD>-<role>.md
Judge → Teams:       shared/announcements/round-<N>.md + shared/leaderboard.md
```

### 3.2 信息读取规范

- Agent 每天启动时，先读自己 team 的 `artifacts/` 最新文件
- 读 `shared/announcements/` 了解竞赛进展
- 读 `shared/rules.md` 确认规则（每次都要读）
- 读 `shared/protocol.md` 确认最新约定
- 读自己 `memory/<role>/MEMORY.md` 了解历史状态

### 3.3 信息写入规范

- 所有写入的文件要有日期前缀或 YAML frontmatter 标注时间
- **不得写入对方 team 的目录**
- `shared/` 目录两队都可读，但只有 Judge Agent 可写 `leaderboard.md`
- 每个 Agent 只能写自己的 `memory/<role>/` 目录

---

## 4. 记忆文件格式

每个 Agent 的日记使用统一格式，存放在 `memory/<role>/diary/`：

```markdown
---
date: 2026-05-18
role: dev
team: red
---

# 日记

## 今天做了什么
- 实现了 xxx 功能
- 遇到了 xxx 错误，通过 xxx 解决

## 学到的东西
- xxx 经验，可以复用

## 明天计划
- 继续开发 xxx
- 修复 xxx bug
```

MEMORY.md 存放在 `memory/<role>/MEMORY.md`，记录持久化经验和状态。

---

## 5. Git 约定

- 红队 `project/` 是独立的 Git 仓库（推送到 `0717lq/ai-company-wars-red`）
- 蓝队 `project/` 是独立的 Git 仓库（推送到 `0717lq/ai-company-wars-blue`）
- 外层 `ai-company-wars/` 是运营仓库
- commit message 前缀约定：

| 前缀 | 含义 |
|------|------|
| `feat:` | 新功能 |
| `fix:` | Bug 修复 |
| `docs:` | 文档 |
| `release:` | 发布版本 |

---

*本协议文件也放入 Git 管理，版本跟随项目。*
