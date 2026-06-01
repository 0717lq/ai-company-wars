# AI Company Wars — 试跑记录与问题清单

> 试跑日期：2026-05-18
> 试跑轮次：`2026-week-trial` + `2026-week-trial-b`
> 对应版本：runner v2.0

---

## 场景 A：正常最小链路

### 执行步骤

| 步骤 | 操作 | 预期 | 实际 | 状态 |
|------|------|------|------|------|
| A-1 | `init-round.py --round 2026-week-trial` | 4 个状态文件创建 | 同上 | ✅ |
| A-2 | 红队 Product pre-check | CAN_RUN | CAN_RUN | ✅ |
| A-3 | 红队 Product --complete | in_progress → completed | 同上 | ✅ |
| A-4 | 蓝队 Product pre-check | CAN_RUN | CAN_RUN | ✅ |
| A-5 | 蓝队 Product --complete | Round 推进 | ROUND_CREATED→PLANNING→DEVELOPMENT | ✅ |
| A-6 | 红队 Dev pre-check（Round=DEVELOPMENT） | CAN_RUN | CAN_RUN | ✅ |
| A-7 | 红队 Dev --complete | completed | completed | ✅ |
| A-8 | 蓝队 Dev --complete | Round 推进到 RELEASING | ✅ | ✅ |
| A-9 | 红队 DevOps pre-check（无 ready-for-deploy） | BLOCKED | BLOCKED | ✅ |
| A-10 | 创建 dummy ready-for-deploy 后重试 | CAN_RUN | CAN_RUN | ✅ |
| A-11 | 红队/蓝队 DevOps --complete | Round 推进到 PROMOTING | ✅ | ✅ |
| A-12 | 红队/蓝队 Growth --complete | Round 推进到 JUDGING | ✅ | ✅ |
| A-13 | 红队 Judge --complete | completed | completed | ✅ |
| A-14 | 蓝队 Judge --complete | Round 推进到 ROUND_CLOSED | ✅ | ✅ |

### 验证点

| 验证项 | 结果 |
|--------|------|
| 幂等：重复调用已完成角色 → 自动跳过 | ✅ SKIPPED (已完成) |
| blocked 写入：前置条件不满足 → status=blocked + error | ✅ |
| last-run.json 记录：result / duration_ms | ✅ 84ms |
| Round 连续推进：一次 complete 推进多阶 | ✅ ROUND_CREATED→PLANNING→DEVELOPMENT |

---

## 场景 B：失败恢复

### 执行步骤

| 步骤 | 操作 | 预期 | 实际 | 状态 |
|------|------|------|------|------|
| B-1 | 模拟 dev=failed 后前置检查 | BLOCKED，提示 --retry | BLOCKED (Round 级别) | ⚠️ |
| B-2 | `--retry` 重置 | blocked → pending | ✅ | ✅ |
| B-3 | 重置后前置检查 | CAN_RUN | CAN_RUN | ✅ |
| B-4 | `--complete --result failed --error-code TEST_FAILED` | 结构化错误信息写入 | completed | ✅ |

> ⚠️ B-1 显示 BLOCKED (Round 级别) 是因为 Round 状态 ROUND_CREATED 不允许 dev 执行，而非因为 dev failed。实际 failed 检测在 check_preconditions 中（"已失败，需要先 --retry 重置"），但 Round 检查优先级更高。

### 验证点

| 验证项 | 结果 |
|--------|------|
| `--retry` 重置 failed/blocked → pending | ✅ |
| `--complete --result failed` 写入错误 | ✅ |
| `error.code` + `error.message` 在 last-run.json 中 | ✅ |
| `duration_ms` 正确记录 | ✅ 3990ms |
| 下游角色（devops）因 dev failed 而 blocked | ✅ |

---

## 发现问题清单

### Bug #1（已修复）：advance_round 检查全部角色而非当前阶段

- **症状**：Product 完成后 Round 不推进到 DEVELOPMENT，因为 `advance_round` 检查的是 team 的整体状态（所有角色），而非当前阶段对应的角色（product）
- **修复**：改为只检查当前阶段对应的角色（PLANNING→检查 product，DEVELOPMENT→检查 dev 等）
- **修复后效果**：Product 完成后 Round 自动推进 ROUND_CREATED → PLANNING → DEVELOPMENT（两阶）

### 发现 #2：Round 状态检查先于 failed 检测

- **描述**：当 Round 状态不匹配时，check_preconditions 中的 failed/blocked 检测不会被执行
- **影响**：低。Round 状态错误本身就是阻塞原因，不执行角色状态检测不影响决策
- **建议**：在 round 检查通过后，failed 检测会正确触发

### 发现 #3：Judge 角色需要两队都标记 completed

- **描述**：Judge 在 team 的 roles 中是一个 per-team 角色。但 Judge 是全局角色，只应执行一次
- **当前做法**：红队 Judge 完成后，蓝队 Judge 也需要标记为 completed 才能推进 round 到 ROUND_CLOSED
- **建议**：后续可以将 Judge 从 per-team roles 中移出，改为 round.json 中的 judge_status 单独控制。当前做法（两队都过）没大的副作用

---

## Cron 接入前置条件

| 条件 | 当前状态 | 是否需要本轮解决？ |
|------|---------|-----------------|
| 完整链路已验证通过 | ✅ 已通过 | 否 |
| runner 可判断 blocked/skipped/completed/failed | ✅ 已支持 | 否 |
| --retry 可重置失败角色 | ✅ 已支持 | 否 |
| last-run.json 结构化记录完整 | ✅ 已支持 | 否 |
| setup-cron.sh 已修正 skill 名称 | ✅ 第 2 轮已修正 | 否 |
| 运行手册已就绪 | ✅ OPERATIONS.md + init-round.py | 否 |
| Judge 的 per-team 问题需要解决 | ⚠️ 已知但可绕过（两队都过） | **建议解决后再上 cron** |
| 试跑中发现了其他问题 | ✅ 已记录 | 否 |

### 建议的 cron 接入前处理顺序

1. 解决 Judge 的 per-team 问题（将 judge 从 team roles 中移出，用 round.json 的 judge_status 控制）
2. 再次快速验证一次完整链路
3. 运行 `setup-cron.sh` 创建 cronjob
4. 观察第一轮自动执行
