# AI Company Wars — 正式运行模型说明

> 版本：v1.0
> 更新日期：2026-05-18（第 2 轮审计后）
> 性质：**当前正式运行模型**（非规划）

---

## 1. 正式真源路径

**唯一正式运行代码路径**：

| 队伍 | 代码真源 | GitHub 仓库 |
|------|---------|------------|
| 🔴 红队 | `ai-company-wars/teams/red/project/` | `0717lq/ai-company-wars-red` |
| 🔵 蓝队 | `ai-company-wars/teams/blue/project/` | `0717lq/ai-company-wars-blue` |

每个 `project/` 是**独立 Git 仓库**，有自己的 commit、tag、remote，与外层运营仓库无关。

---

## 2. 非正式目录定位

| 路径 | 性质 | 说明 |
|------|------|------|
| `/mnt/d/Desktop/hermes/red-project/` | 📦 镜像副本 | 无 Git 仓库，代码子集，**不是正式运行目录** |
| `/mnt/d/Desktop/hermes/blue-project/` | 📦 镜像副本 | 同上 |
| `ai-company-wars/skills/dev-agent-draft.md` | 📜 历史草稿 | 已被 Hermes 系统 Skill 取代 |
| `skills/` 目录 | 📜 历史 | 不再作为正式 skill 存放位置 |

---

## 3. Hermes 系统 Skill

| Agent | 真实 Skill 名 | 路径参考 | 状态 |
|-------|-------------|---------|------|
| Product Agent | `ai-company-wars-product` | `teams/{颜色}/project/` | ✅ 已创建、路径已修正 |
| Dev Agent | `ai-company-wars-dev` | `teams/{颜色}/project/` | ✅ 已创建、路径已修正 |
| DevOps Agent | `ai-company-wars-devops` | `teams/{颜色}/project/` | ✅ 已创建、路径已修正 |
| Growth Agent | `ai-company-wars-growth` | `teams/{颜色}/project/` | ✅ 已创建、路径已修正 |
| Judge Agent | `ai-company-wars-judge` | `teams/` 根目录 | ✅ 已创建、路径已修正 |

---

## 4. 正式运行链路（一轮 Sprint）

```
周一 09:00  Product → 写 PRD → artifacts/prd/ + tasks.md + handover-to-dev.md
周一 10:00  Dev → 编码 → teams/{颜色}/project/src/ + tests/
周五 16:00  DevOps → 发版 → git push + tag + artifacts/release-notes.md
周五 18:00  Growth → README优化 → teams/{颜色}/project/README.md
周日 20:00  Judge → 评分 → shared/leaderboard.md + announcements/round-N.md
```

上下环节通过 artifacts/ 下的约定文件衔接。

---

## 5. 当前文档口径状态（第 2 轮修正后）

| 文件 | 原问题 | 修正内容 | 状态 |
|------|--------|---------|------|
| `DOCS.md` | 目录图为根目录 `red-project/` | 改为 `teams/{color}/project/` | ✅ 已统一 |
| `PLAN.md` | 结构差一层 `teams/` | 目录图修正，新增✅/📋标记 | ✅ 已统一 |
| `shared/protocol.md` | memory 缺 role 子目录 | 补充 per-role memory 结构 | ✅ 已统一 |
| `orchestrator/schedule.md` | Skill 名称为旧名 | 改为 `ai-company-wars-*` | ✅ 已统一 |
| `orchestrator/setup-cron.sh` | Skill 名称检测全面失效 | `check_skill` + `--skill` 全修正 | ✅ 已统一 |
| Hermes Skills (5个) | 硬编码旧镜像路径 | 全部改为 `teams/{color}/project/` | ✅ 已统一 |

---

## 6. Artifacts 命名标准

**选定标准**（沿用蓝队已有格式）：

| 文件 | 路径 | 格式 |
|------|------|------|
| PRD | `artifacts/prd/` | `YYYY-MM-DD-<project>-prd.md` |
| Sprint 任务 | `artifacts/tasks.md` | 固定文件名 |
| 交接 | `artifacts/handover-to-<target>.md` | 固定文件名 |
| 待部署 | `artifacts/ready-for-deploy.md` | 固定文件名 |
| 发版说明 | `artifacts/release-notes.md` | 固定文件名 |

**历史文件处理**：红队的旧格式文件（`PRD.md`、`current-sprint.md`）本轮不动，后续写入一律按新格式。

---

## 7. 现状 / 规划 / 历史残留 边界

| 类别 | 内容 |
|------|------|
| **现状 (✅)** | 目录结构、protocol.md、rules.md、Hermes Skills、红蓝两队代码、leaderboard |
| **规划 (📋)** | cronjob 实际创建、Skill 契约补齐（INPUTS/OUTPUTS/CHECKS）、状态机、结构化状态文件 |
| **历史残留 (📦/📜)** | 根目录 `red-project/` `blue-project/` 镜像、`skills/dev-agent-draft.md` |

---

*本模型应与 `DOCS.md`、`shared/protocol.md` 保持一致。如果用户/Agent 发现新的结构冲突，优先更新本模型。*
