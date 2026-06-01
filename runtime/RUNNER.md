# Runner 执行流程与状态更新说明

> 对应脚本：`scripts/run-round.py`
> 版本：v2.0（第 7 轮更新：支持失败回写、结构化日志、幂等、补跑）

---

## 一、调用方式

```bash
# 前置检查（默认）
python3 scripts/run-round.py --team red --role product --round 2026-week-21

# 执行完成——成功
python3 scripts/run-round.py --team red --role dev --round 2026-week-21 --complete

# 执行完成——失败（含结构化和错误信息）
python3 scripts/run-round.py --team red --role dev --round 2026-week-21 --complete \
    --result failed --error-code TEST_FAILED --error-message "3/15 tests failed"

# 补跑：重置失败/阻塞角色
python3 scripts/run-round.py --team blue --role dev --round 2026-week-21 --retry

# 只看不写
python3 scripts/run-round.py --team blue --role devops --round 2026-week-21 --dry-run
```

### 参数说明（v2.0 新增加粗标出）

| 参数 | 必填 | 说明 |
|------|------|------|
| `--team` | ✅ | `red` 或 `blue` |
| `--role` | ✅ | `product` / `dev` / `devops` / `growth` / `judge` |
| `--round` | ✅ | 轮次 ID，如 `2026-week-21` |
| `--complete` | 否 | 执行完成后调用，更新状态 |
| **`--result`** | 否 | 执行结果（仅 `--complete` 模式）：`completed` / `failed` / `skipped`。默认 `completed` |
| **`--error-code`** | 否 | 错误码（仅 `--result failed` 时使用）。预定义：`INPUT_MISSING` / `PRECONDITION_FAILED` / `NETWORK_ERROR` / `TEST_FAILED` / `GITHUB_RATE_LIMIT` / `POLICY_BLOCKED` / `IMPLEMENTATION_FAILED` / `PRD_MISSING` / `READY_FOR_DEPLOY_MISSING` / `UNKNOWN_ERROR` |
| **`--error-message`** | 否 | 错误描述（仅 `--result failed` 时使用） |
| **`--retry`** | 否 | 重跑模式：重置 failed/blocked → pending |
| `--dry-run` | 否 | 只检查不写文件 |
| `--verbose` | 否 | 详细日志 |

---

## 二、执行流程

### 2.1 前置检查模式（默认）

```
读取命令参数
    │
    ▼
读取 runtime/round.json
    │
    ├── 检查 Round 状态是否允许当前 role
    │   ├── 不允许 → BLOCKED (Round 级别)
    │   └── 允许 → 继续
    │
    ▼
读取 teams/{color}/runtime/status.json
    │
    ├── 不存在 → 创建初始状态文件
    │
    ▼
⏱  幂等检查：同 round 同角色已 completed → SKIPPED
    │
    ▼
检查前置条件
    │
    ├── 终态 (completed/skipped) ────────→ SKIPPED (已完成)
    ├── 已 failed（非重跑模式）──────────→ BLOCKED（提示 --retry）
    ├── 前置角色尚未开始 ────────────────→ BLOCKED
    ├── 前置角色失败 ───────────────────→ BLOCKED（Judge 除外）
    ├── 前置角色被阻塞 ────────────────→ BLOCKED
    ├── 前置角色运行中 ────────────────→ BLOCKED
    ├── 可跳过条件满足 ────────────────→ SKIPPED
    │
    └── 全部满足 → CAN_RUN
         │
         ▼
    设置 role_status = in_progress
    记录 start_ms（用于 duration 计算）
    写入 last-run.json (result: "running", started_at)
    输出提示信息
```

### 2.2 执行完成回写模式（--complete）

```
读取 team 状态
    │
    ▼
读取当前 role 状态
    │
    ▼
计算结果 duration_ms = now_ms - start_ms
    │
    ▼
根据 --result 参数写回（默认 completed）
    │
    ├── completed → role_status = completed, error = null
    ├── failed → role_status = failed, error = {code, message}
    └── skipped → role_status = skipped
    │
    ▼
写入增强版 last-run.json:
  - started_at / finished_at / duration_ms
  - result / error (code + message)
  - inputs / outputs
    │
    ▼
尝试推进 Round 状态
    ├── 检查两队所有角色是否都已结束
    │   ├── 全部结束 → 推进到下一阶段
    │   └── 未结束 → 保持当前阶段
```

### 2.3 重跑模式（--retry）

```
读取 team 状态
    │
    ▼
检查当前 role 状态
    │
    ├── 终态 (completed/skipped) → ❌ 不允许重跑
    ├── failed/blocked → ✅ 允许重置
    │   │
    │   ▼
    │   role_status = pending（清除 error、outputs、last_run）
    │   写入 last-run.json (result: "skipped", 备注: 重跑前重置)
    │
    ├── pending → ℹ️ 无需重置，直接执行前置检查
    └── in_progress → ⚠️ 角色正在执行，先等它完成
```

---

## 三、last-run.json 字段说明（v2.0 增强版）

```json
{
  "round_id": "2026-week-21",
  "team": "red",
  "role": "dev",
  "started_at": "2026-05-25T10:00:00.123456+00:00",
  "finished_at": "2026-05-25T10:45:30.987654+00:00",
  "duration_ms": 2730864,
  "result": "failed",
  "error": {
    "code": "TEST_FAILED",
    "message": "3/15 tests failed: test_sort, test_undo, test_cli"
  },
  "inputs": [
    "teams/red/artifacts/prd/2026-05-25-update-prd.md",
    "teams/red/artifacts/tasks.md"
  ],
  "outputs": [
    "teams/red/project/src/ (4 files changed)",
    "teams/red/project/tests/ (2 files added)"
  ]
}
```

| 字段 | 含义 | 写入时机 |
|------|------|---------|
| `round_id` | 轮次 ID | 总是 |
| `team` | 队伍 | 总是 |
| `role` | 角色 | 总是 |
| `started_at` | ISO 格式开始时间 | 前置检查（can_run）时写入 |
| `finished_at` | ISO 格式结束时间 | --complete 回写时写入 |
| `duration_ms` | 执行耗时（毫秒） | --complete 回写时写入 |
| `result` | 执行结果：`running` / `completed` / `failed` / `skipped` | 总是 |
| `error` | 错误信息（code + message）；null 代表无错误 | 仅 result=failed 时有值 |
| `inputs` | 读取的文件列表 | 总是 |
| `outputs` | 写入的文件列表 | 总是 |

**注意**：`last-run.json` 是单次执行记录，每次调用覆盖上一次。

---

## 四、错误码定义

| 错误码 | 适用场景 |
|--------|---------|
| `INPUT_MISSING` | 必读输入文件缺失 |
| `PRECONDITION_FAILED` | 前置条件不满足，无法开始 |
| `NETWORK_ERROR` | GitHub API 或其他网络连接失败 |
| `TEST_FAILED` | 单元测试/集成测试失败 |
| `GITHUB_RATE_LIMIT` | GitHub API 速率限制 |
| `POLICY_BLOCKED` | 策略禁止该行为 |
| `IMPLEMENTATION_FAILED` | 代码实现错误 |
| `PRD_MISSING` | 缺少 PRD 文档 |
| `READY_FOR_DEPLOY_MISSING` | 缺少 ready-for-deploy 信号文件 |
| `UNKNOWN_ERROR` | 其他未分类错误 |

---

## 五、幂等规则

### 已 completed → 跳过

前置检查中，如果 `role_status` 是 `completed` 或 `skipped`，runner 自动判定为 `already_done` 并跳过，不会重新执行。

### 同 round 同角色保护

前置检查时，如果 `round_id` 匹配且角色已结束（终态），不再重复执行。

### 各角色幂等保护（在 CHECKS.md 中定义）

| 角色 | 幂等形式 |
|------|---------|
| Product | 同一 round 不重复生成多份 PRD。检查 `artifacts/prd/` 下是否有同轮次 PRD |
| Dev | 检查 `ready-for-deploy.md` 的 round_id 是否匹配当前 round |
| DevOps | 检查 `git tag` 是否已存在，不允许重复创建同版本 tag |
| Growth | README 更新幂等，重复执行无害 |
| Judge | 按 round_id 检查 `announcements/round-N.md` 是否已存在 |

---

## 六、failed / blocked / skipped / completed 的区别

| 状态 | 含义 | Team 聚合 | 可恢复？ |
|------|------|----------|---------|
| `completed` | 角色成功完成，产出物完整 | 推进 Round | 终态，不可自动重跑 |
| `failed` | 角色执行失败，有错误信息 | 聚合为 failed | 可通过 `--retry` 重置为 pending |
| `blocked` | 前置条件不满足，无法开始 | 聚合为 blocked | 上游完成后自动可重试，也可 `--retry` |
| `skipped` | 条件满足但跳过执行 | 参与"已结束"判断 | 终态，不可自动重跑 |
| `in_progress` | 正在执行中 | 聚合为 in_progress | 等待完成 |
| `pending` | 等待开始 | 初始态 | — |

### 失败队伍处理（Judge 场景）

| 场景 | 处理 |
|------|------|
| 一队 completed，一队 failed | Judge 正常评分，failed 队伍记 0 分/N/A，点评说明原因 |
| 两队均 failed | Round 标记异常，Judge 无法评分 |

---

## 七、补跑 / 恢复规则

### 允许重跑的角色

| 角色 | 重跑方式 | 重跑前注意事项 |
|------|---------|--------------|
| Product | `--retry` 后执行前置检查 | 确认旧 PRD 是否仍适用 |
| Dev | `--retry` 后执行前置检查 | 是否需要 revert 上次提交？ |
| DevOps | `--retry` 后执行前置检查 | 旧 tag 是否需要清理？删除后重新创建 |
| Growth | `--retry` 后执行前置检查 | 重复优化无害 |
| Judge | 不支持 `--retry`，下一轮自然重评 | 上一轮的通告可覆盖写入 |

### 不允许自动重跑的角色状态

| 状态 | 原因 |
|------|------|
| `completed` | 终态，产物已发布 |
| `skipped` | 终态，条件是主动评估后作出的 |
| judge `failed` | 下一轮新的 round 自然覆盖 |

### 重跑命令示例

```bash
# 步骤 1：重置失败角色
python3 scripts/run-round.py --team blue --role dev --round 2026-week-21 --retry

# 步骤 2：前置检查确认
python3 scripts/run-round.py --team blue --role dev --round 2026-week-21

# 步骤 3：角色执行...

# 步骤 4：回写结果
python3 scripts/run-round.py --team blue --role dev --round 2026-week-21 --complete
```

---

## 八、状态文件更新摘要

| 文件 | 更新时机 | 写入内容 |
|------|---------|---------|
| `teams/{color}/runtime/status.json` | 前置检查 + retry + complete | role 状态、执行时间、错误信息 |
| `runtime/last-run.json` | 前置检查 + retry + complete | 完整结构化执行记录 |
| `runtime/round.json` | complete 回写后 | 检查并推进 Round 阶段 |

---

## 九、Round 推进规则

每次 `--complete` 回写后，runner 检查两队所有角色是否已不在进行中（in_progress），如果都结束了，Round 推进到下一阶段。

阶段顺序：
```
ROUND_CREATED → PLANNING → DEVELOPMENT → RELEASING → PROMOTING → JUDGING → ROUND_CLOSED
```
