# AI Company Wars — 项目总目录说明

> 最后更新：2026-05-18（第 2 轮审计后统一口径）
> 状态：✅ 当前真实结构（非规划）

---

## 总览

AI Company Wars 是一个多 Agent 自治竞争系统。红蓝两队各 4 个 Hermes Agent（Product → Dev → DevOps → Growth），零人工干预，自主开发项目竞争 GitHub Stars。另有 1 个 Judge Agent 负责评分。

**正式运行路径**：`ai-company-wars/teams/{颜色}/` 下各角色独立工作，`project/` 为代码仓库。

---

## 目录结构（当前实现，2026-05-18）

```
ai-company-wars/                        ← 🏠 主控目录
│
├── DOCS.md                             ← 本文件
├── PLAN.md                             ← 总体规划文档
│
├── orchestrator/                       ← 调度配置
│   ├── schedule.md                     ←   调度时间表
│   └── setup-cron.sh                   ←   cronjob 创建脚本
│
├── scripts/
│   └── init-workspace.sh              ←   Agent 记忆目录初始化
│
├── shared/                             ← 共用资源（两队可读）
│   ├── rules.md                        ←   竞赛规则（Judge 维护）
│   ├── protocol.md                     ←   Agent 通信协议
│   ├── leaderboard.md                  ←   排行榜（Judge 更新）
│   ├── announcements/                  ←   轮次通告
│   │   └── round-1.md
│   └── judge/                          ←   Judge 记忆/日记
│       ├── memory/
│       └── diary/
│
└── teams/                              ← 🏠 正式比赛目录
    ├── red/
    │   ├── project/                    ← [正式运行] 红队代码仓库（独立 Git）
    │   │   ├── src/dirsort/
    │   │   ├── tests/
    │   │   ├── README.md
    │   │   └── pyproject.toml
    │   ├── memory/                     ← Agent 记忆
    │   │   ├── product/MEMORY.md + diary/
    │   │   ├── dev/MEMORY.md + diary/
    │   │   ├── devops/MEMORY.md + diary/
    │   │   └── growth/MEMORY.md + diary/
    │   └── artifacts/                  ← 产出物（PRD、任务、Release Notes）
    │       ├── prd/                    ← PRD 文件（子目录+日期前缀）
    │       ├── tasks.md
    │       ├── handover-to-dev.md
    │       ├── ready-for-deploy.md
    │       ├── release-notes.md
    │       ├── designs/
    │       └── reports/
    │
    └── blue/                           ← 同上结构
        ├── project/
        │   └── src/fclean/...
        ├── memory/
        └── artifacts/
```

---

## Agent 角色与正式目录关系

| Agent | 读取 | 写入 | 交接对象 |
|-------|------|------|---------|
| Product | `shared/announcements/`、`shared/leaderboard.md`、`teams/{color}/memory/product/MEMORY.md` | `teams/{color}/artifacts/prd/`、`tasks.md`、`handover-to-dev.md`；初始化 `project/` 骨架 | → Dev |
| Dev | `teams/{color}/artifacts/prd/`（最新）、`tasks.md`、`handover-to-dev.md`、`memory/dev/MEMORY.md` | `teams/{color}/project/src/`、`tests/`、`docs/`；写 `ready-for-deploy.md` | → DevOps |
| DevOps | `teams/{color}/artifacts/ready-for-deploy.md`、`memory/devops/MEMORY.md` | 推代码到 GitHub、创建 Release、写 `release-notes.md` | → Growth |
| Growth | `teams/{color}/project/README.md`、`release-notes.md`、`memory/growth/MEMORY.md` | `teams/{color}/project/README.md`、`LICENSE`、CI 工作流 | → 用户/社区 |
| Judge | 两队 `teams/{color}/project/`、`shared/rules.md` | `shared/leaderboard.md`、`shared/announcements/round-N.md`、`shared/judge/` | → 所有人 |

---

## 非正式/历史目录说明

以下目录**不是**正式比赛运行路径，仅作为示例、镜像或历史存档保留：

| 路径 | 性质 | 说明 |
|------|------|------|
| `/mnt/d/Desktop/hermes/red-project/` | 📦 镜像副本 | 无 Git 仓库，内容是 `teams/red/project/` 的子集 |
| `/mnt/d/Desktop/hermes/blue-project/` | 📦 镜像副本 | 同上 |
| `ai-company-wars/skills/` | 📜 历史草稿 | 仅含旧版 `dev-agent-draft.md`，已被 Hermes 系统 Skill 取代 |

---

## GitHub 仓库

| 仓库 | 用途 | 代码真源 |
|------|------|---------|
| `0717lq/ai-company-wars-red` | 红队项目代码 | `teams/red/project/` |
| `0717lq/ai-company-wars-blue` | 蓝队项目代码 | `teams/blue/project/` |
| `0717lq/ai-company-wars`（外层的运营仓库） | 规则、配置、调度 | `ai-company-wars/` 根目录 |

---

## 调度时间表（现状）

各 Agent 通过 Hermes cronjob 按 Sprint 节奏驱动。详见 `orchestrator/schedule.md`。

```
平日（周一至周五）：
  09:00  Product Agent → 出 PRD + 拆任务
  10:00  Dev Agent → 编码实现
  16:00  DevOps Agent → 发布 Release
  18:00  Growth Agent → 优化展示

周日：
  20:00  Judge Agent → 评分 + 排行榜
```

---

## 规范参考

- 文件命名规范：见 `shared/protocol.md`
- 竞赛规则：见 `shared/rules.md`
- 总体规划：见 `PLAN.md`
