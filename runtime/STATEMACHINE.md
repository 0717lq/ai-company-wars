# AI Company Wars — 最小状态机设计

> 版本：v1.1
> 更新日期：2026-05-18（第 9 轮：Judge 全局化修正）
> 性质：设计文档（已实现）

---

## 一、状态层级总览

```
Round 级状态  ─── 整轮比赛的阶段门禁
    │
    ├── Team 级状态  ─── 红队/蓝队各自进展
    │       │
    │       └── Agent 级状态  ─── 单个角色执行记录
    │
    └── (Team 之间独立，不互相阻塞)
```

**核心原则**：
- Round 级状态基于 Team 级状态的汇总判断
- Team 级状态基于 Agent 级执行结果的汇总判断
- 红队和蓝队的 Team 级状态独立演进
- Judge 是 **全局角色**，不在 per-team roles 中。Judge 的状态由 `round.json` 的 `judge_status` 字段单独管理
- Judge 等待双方 Team 状态到达 `promoting_complete` 后再执行

---

## 二、Round 级状态

### 状态列表

```
ROUND_CREATED
    │  [所有 team 的 product 进入 pending]
    ▼
PLANNING           ← Product 窗口
    │  [所有 team 的 product == completed]
    ▼
DEVELOPMENT        ← Dev 窗口
    │  [所有 team 的 dev == completed]
    ▼
RELEASING          ← DevOps 窗口
    │  [所有 team 的 devops == completed]
    ▼
PROMOTING          ← Growth 窗口
    │  [所有 team 的 growth == completed]
    ▼
JUDGING            ← Judge 窗口
    │  [judge == completed]
    ▼
ROUND_CLOSED       ← 本轮结束
```

| 状态 | 含义 | 推进条件（前进一步的必要条件） |
|------|------|-----------------------------|
| `ROUND_CREATED` | 本轮已创建，等待 Product 开始 | 任意 team 的 product ≥ in_progress → 自动推进到 PLANNING |
| `PLANNING` | Product Agent 窗口开放 | 所有 team 的 product == completed |
| `DEVELOPMENT` | Dev Agent 窗口开放 | 所有 team 的 dev == completed |
| `RELEASING` | DevOps Agent 窗口开放 | 所有 team 的 devops == completed |
| `PROMOTING` | Growth Agent 窗口开放 | 所有 team 的 growth == completed |
| `JUDGING` | Judge 窗口开放 | judge == completed |
| `ROUND_CLOSED` | 本轮结束 | — |

> **注意**：Round 状态是"门禁"而非"自动推进"。每个阶段窗口开放后，Agent 在对应时间段执行，完成后更新 team 状态。Round 状态在条件满足后，由 runner 或 cronjob 的下一个调度 tick 推进。

### 推进判断逻辑

```
round.current_state = PLANNING
    → 检查 red.product_status == completed AND blue.product_status == completed
      → 如果成立：round.current_state = DEVELOPMENT
      → 如果不成立：保持 PLANNING

特殊情况：如果某个 team 的 product == failed，可否推进？
→ 推进条件是"不处于 in_progress"。failed 或 skipped 也算"结束"，
   不阻塞 Round 推进。但 failed 的 team 在该轮该角色无产出。
```

---

## 三、Team 级状态

### 每个角色的状态

每个 Agent（product / dev / devops / growth）的状态：

```
pending         ← 未开始
in_progress     ← 正在执行
completed       ← 成功完成
failed          ← 执行失败（有错误）
skipped         ← 被跳过（本轮该角色不需要执行）
blocked         ← 被阻塞（前置条件不满足）
```

### Team 整体的聚合状态

| 聚合状态 | 含义 | 判断逻辑 |
|---------|------|---------|
| `pending` | 尚未开始本轮 | 所有角色 == pending |
| `in_progress` | 至少有一个角色在执行 | 任意角色 == in_progress |
| `completed` | 所有角色已完成 | 所有角色 == completed/skipped，无 failed |
| `failed` | 至少有一个角色失败 | 任意角色 == failed |
| `blocked` | 至少有一个角色被阻塞 | 任意角色 == blocked |

### 角色状态流转

```
pending ──→ in_progress ──→ completed
                 │
                 ├──→ failed ──→ pending (允许重跑，切换后重试)
                 │
                 └──→ blocked ──→ pending (条件满足后自动切换)
```

---

## 四、Agent 执行状态（执行日志）

用于 `last-run.json`，记录单次执行结果：

| 状态 | 含义 |
|------|------|
| `not_started` | 从未执行过 |
| `running` | 正在执行中 |
| `succeeded` | 执行成功 |
| `failed` | 执行失败 |
| `skipped` | 因条件不满足被跳过 |

> **注意**：Judge 是全局角色，不在 per-team 的 `roles` 中。Judge 的状态由 `round.json` 的 `judge_status` 字段管理（`pending` / `in_progress` / `completed` / `failed`）。
> 
> 试跑中发现的 Bug（已修复）：原先 Judge 被建模为 per-team 角色，导致红蓝两队都需要 judge=completed 才能关闭 Round。现在 Judge 只写入 `round.json` 的 `judge_status`，一次执行即可推进 `JUDGING → ROUND_CLOSED`。

---

## 五、各角色进入/退出/失败规则

### Product Agent

| 场景 | 规则 |
|------|------|
| **进入条件** | round.current_state ∈ [ROUND_CREATED, PLANNING]；且 team 的 product_status == pending |
| **前置条件** | 无（Product 是起始角色） |
| **何时推进 team 状态** | PRD 成功写入 → product_status = completed |
| **失败时** | product_status = failed，写入 `error` 字段 |
| **跳过条件** | 如果这是第二周且项目方向不变，可以跳过（不写新 PRD）→ product_status = skipped |
| **允许重跑？** | ✅ 允许，重跑时 product_status = pending → in_progress |
| **幂等保证** | 检查 `artifacts/prd/` 下是否有当前 round 的最新 PRD |

### Dev Agent

| 场景 | 规则 |
|------|------|
| **进入条件** | team 的 product_status == completed 或 skipped；且 dev_status == pending |
| **前置条件** | 需要 PRD（优先用最新的、未用过的 PRD）；如果没有 → blocked |
| **何时推进 team 状态** | 代码提交 + ready-for-deploy.md 写入 → dev_status = completed |
| **失败时** | dev_status = failed，写入错误原因 |
| **跳过条件** | 如果本轮没有新 PRD、没有新需求 → dev_status = skipped |
| **允许重跑？** | ✅ 允许。重跑时需注意：上次提交的代码需先 revert 或基于最新 commit 修改 |
| **幂等保证** | 检查 `project/` 下是否已有同轮次的代码；检查 `ready-for-deploy.md` 是否已存在 |

### DevOps Agent

| 场景 | 规则 |
|------|------|
| **进入条件** | team 的 dev_status == completed；且 devops_status == pending |
| **前置条件** | 需要 `ready-for-deploy.md` 存在；如果没有 → blocked |
| **何时推进 team 状态** | Release 创建成功 → devops_status = completed |
| **失败时** | devops_status = failed（如网络不可达 → 离线模式写入 manual steps） |
| **跳过条件** | 如果 dev_status == skipped（无新代码发什么版） → devops_status = skipped |
| **允许重跑？** | ✅ 允许。但需注意：同版本的 Release 不可重复创建。如果 tag 已存在，应创建新 tag |
| **幂等保证** | 检查 git tag 是否已存在；检查 `release-notes.md` 是否已写入 |

### Growth Agent

| 场景 | 规则 |
|------|------|
| **进入条件** | team 的 devops_status == completed 或 skipped；且 growth_status == pending |
| **前置条件** | 检查 `project/README.md` 是否存在（存在则可优化，不存在→blocked） |
| **何时推进 team 状态** | README 优化完成 + 文档更新 → growth_status = completed |
| **失败时** | growth_status = failed |
| **跳过条件** | 如果 dev 和 devops 都没有产出，README 优化可跳过 → growth_status = skipped |
| **允许重跑？** | ✅ 允许。README 优化幂等，重复执行无害 |
| **幂等保证** | README 更新本身幂等，不破坏已有内容 |

### Judge Agent

| 场景 | 规则 |
|------|------|
| **进入条件** | Round 状态到达 JUDGING（所有 team 至少已完成或失败） |
| **前置条件** | 至少一个 team 有可评估的产出 |
| **何时推进** | leaderboard.md + round-N.md 写入 + 日记写入 → judge_status = completed |
| **失败时** | judge_status = failed |
| **跳过条件** | 无（Judge 每轮必须执行） |
| **允许重跑？** | ✅ 允许。重新评分后覆盖 leaderboard.md |
| **幂等保证** | 按 round_id 检查 `shared/announcements/round-N.md` 是否已存在 |

---

## 六、状态流转总图

```
                          ROUND_CREATED
                               │
                     [cronjob 触发 Product]
                               │
                               ▼
┌─────────────────── PLANNING ───────────────────┐
│  [红队] pending ──→ in_progress ──→ completed  │
│  [蓝队] pending ──→ in_progress ──→ completed  │
│  (任一方失败: failed, 不阻塞 Round 推进)        │
└───────────────────────┬─────────────────────────┘
                        │ 所有 product 已结束
                        ▼
┌───────────────── DEVELOPMENT ──────────────────┐
│  [红队] pending ──→ in_progress ──→ completed  │
│  [蓝队] pending ──→ in_progress ──→ completed  │
│  依赖 PRD 存在，否则 blocked                      │
└───────────────────────┬─────────────────────────┘
                        │ 所有 dev 已结束
                        ▼
┌────────────────── RELEASING ───────────────────┐
│  [红队] pending ──→ in_progress ──→ completed  │
│  [蓝队] pending ──→ in_progress ──→ completed  │
│  依赖 ready-for-deploy.md，否则 blocked           │
└───────────────────────┬─────────────────────────┘
                        │ 所有 devops 已结束
                        ▼
┌────────────────── PROMOTING ───────────────────┐
│  [红队] pending ──→ in_progress ──→ completed  │
│  [蓝队] pending ──→ in_progress ──→ completed  │
└───────────────────────┬─────────────────────────┘
                        │ 所有 growth 已结束
                        ▼
┌─────────────────── JUDGING ─────────────────────┐
│  Judge 读取两队状态和产出                         │
│  评分 → leaderboard.md → announcement           │
└───────────────────────┬─────────────────────────┘
                        │ Judge 完成
                        ▼
                     ROUND_CLOSED
```

---

## 七、重跑/跳过规则总结

### 允许重跑的角色（全部允许，但有约束）

| 角色 | 重跑约束 | 幂等策略 |
|------|---------|---------|
| Product | 覆盖旧 PRD 的轮次标记 | 按 round_id 去重 |
| Dev | 先 revert 或基于最新提交修改 | 检查 `ready-for-deploy.md` |
| DevOps | 不可重复使用同版本 tag | 检查 tag 是否存在 |
| Growth | 无约束 | README 更新幂等 |
| Judge | 覆盖 leaderboard.md | 按 round_id 写通告 |

### 什么叫"幂等可重跑"

同一角色在同一 round 中重复执行：
- 不会产生重复的副作用（多个 PRD、多个 tag、双倍计分）
- 第二次执行的输出与第一次一致（或修正了 Bug 后输出更正确）
- 不会因重复触发而阻塞下一次执行

### 什么叫"必须阻塞"

以下情况不应自动执行，应标记为 `blocked` 并报告：
- Dev 没有 PRD 可读
- DevOps 没有 `ready-for-deploy.md`
- Judge 时双方 team 都无任何产出（全部为 failed/skipped）
- 角色还在 `in_progress` 时再次触发（应检查状态后跳过）

---

*本设计文档应与 `runtime/` 目录下的状态文件 schema 配套使用。*
