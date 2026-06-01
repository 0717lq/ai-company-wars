# AI Company Wars — 最小运行手册

> 版本：v1.0
> 更新日期：2026-05-18
> 用途：手动/半自动模式下的系统操作指南（cron 接入前）

---

## 一、快速开始：手动跑一轮

### 前置条件

- 当前目录：`ai-company-wars/`
- `scripts/run-round.py` 存在且可执行
- 红蓝两队 `teams/{color}/project/` 目录已存在（有代码）

### 步骤概览

```
第 1 步: 初始化 round
    ↓
第 2 步: Product Agent 执行
    ↓
第 3 步: Dev Agent 执行
    ↓
第 4 步: DevOps Agent 执行
    ↓
第 5 步: Growth Agent 执行
    ↓
第 6 步: Judge 评分
    ↓
第 7 步: 查看结果
```

---

## 二、初始化一轮 Round

### 2.1 创建 round.json

创建 `runtime/round.json`，内容：

```json
{
  "round_id": "2026-week-NN",
  "created_at": "2026-05-25T09:00:00+08:00",
  "current_state": "ROUND_CREATED",
  "teams": {
    "red": { "status": "pending" },
    "blue": { "status": "pending" }
  },
  "judge_status": "pending",
  "updated_at": "2026-05-25T09:00:00+08:00"
}
```

> **注意**：`round_id` 建议格式 `YYYY-week-NN`，例如 `2026-week-22`。
> `current_state` 必须从 `ROUND_CREATED` 开始。

### 2.2（可选）重命名轮次

如果上一轮已运行，需要开新轮时，只需修改 `round.json` 中的 `round_id` 和 `current_state`：

```json
{
  "round_id": "2026-week-22",
  "current_state": "ROUND_CREATED",
  ...
}
```

不需要重建 `status.json`——它们会跟随新 round 自动创建。

### 2.3 验证初始化

```bash
python3 scripts/run-round.py --team red --role product --round 2026-week-22 --dry-run
```

预期结果：
```
BLOCKED (Round 级别)
```
这是因为 `round.json` 状态是 `ROUND_CREATED`，但 `check_round_state` 允许 Product 在 `ROUND_CREATED` 时执行，所以实际应该是 `CAN_RUN`。如果 round.json 不存在，runner 也会通过（跳过 Round 检查）。

> 如果 `round.json` 不存在，runner 会跳过 Round 检查直接允许 Product 执行。

---

## 三、手动运行各角色

### 通用命令格式

```bash
# 前置检查
python3 scripts/run-round.py --team <red|blue> --role <role> --round <round-id>

# 执行完成后回写（成功）
python3 scripts/run-round.py --team <red|blue> --role <role> --round <round-id> --complete

# 执行完成后回写（失败）
python3 scripts/run-round.py --team <red|blue> --role <role> --round <round-id> \
    --complete --result failed --error-code TEST_FAILED --error-message "reason"

# 查看检查结果（只看不写）
python3 scripts/run-round.py --team <red|blue> --role <role> --round <round-id> --dry-run
```

### 3.1 Product Agent

```bash
# 第 1 步：前置检查
python3 scripts/run-round.py --team red --role product --round 2026-week-22

# 预期：CAN_RUN（状态变为 in_progress）

# 第 2 步：Product 完成工作（写 PRD、tasks、handover）

# 第 3 步：回写完成
python3 scripts/run-round.py --team red --role product --round 2026-week-22 --complete
```

**检查产物**：
- `teams/red/artifacts/prd/*.md`
- `teams/red/artifacts/tasks.md`
- `teams/red/artifacts/handover-to-dev.md`

### 3.2 Dev Agent

```bash
# 第 1 步：前置检查
python3 scripts/run-round.py --team red --role dev --round 2026-week-22

# 预期：CAN_RUN（前提：product 已完成）

# 第 2 步：Dev 完成工作（编码、测试、ready-for-deploy）

# 第 3 步：回写完成
python3 scripts/run-round.py --team red --role dev --round 2026-week-22 --complete
```

**检查产物**：
- `teams/red/project/src/` 下代码改动
- `teams/red/project/tests/` 下测试
- `teams/red/artifacts/ready-for-deploy.md`

### 3.3 DevOps Agent

```bash
# 第 1 步：前置检查
python3 scripts/run-round.py --team red --role devops --round 2026-week-22

# 预期：CAN_RUN（前提：ready-for-deploy.md 存在，dev 已完成）

# 第 2 步：DevOps 完成工作（push、tag、release-notes）

# 第 3 步：回写完成
python3 scripts/run-round.py --team red --role devops --round 2026-week-22 --complete
```

### 3.4 Growth Agent

```bash
# 第 1 步：前置检查
python3 scripts/run-round.py --team red --role growth --round 2026-week-22

# 预期：CAN_RUN 或 SKIPPED（取决于 devops 是否有产出）

# 第 2 步：Growth 完成工作（README 优化等）

# 第 3 步：回写完成
python3 scripts/run-round.py --team red --role growth --round 2026-week-22 --complete
```

### 3.5 Judge Agent（全局角色）

```bash
# 前置检查（不需要指定 --team，但参数仍需传）
python3 scripts/run-round.py --team red --role judge --round 2026-week-22

# 回写完成
python3 scripts/run-round.py --team red --role judge --round 2026-week-22 --complete
```

> Judge 是全局角色。`--complete` 时写入 `round.json` 的 `judge_status`，
> 而非 per-team 的 status.json。一次执行即可推进 `JUDGING → ROUND_CLOSED`。

---

## 四、查看执行结果

### 4.1 查看 round 整体状态

```bash
python3 -c "import json; d=json.load(open('runtime/round.json')); print(json.dumps(d, indent=2, ensure_ascii=False))"
```

关注字段：
- `current_state`：当前 Round 阶段
- `teams.red.status`：红队聚合状态
- `teams.blue.status`：蓝队聚合状态

### 4.2 查看某一队的所有角色状态

```bash
python3 -c "
import json
d = json.load(open('teams/red/runtime/status.json'))
print(f\"Team: {d['team']} | Round: {d['round_id']} | State: {d['current_state']}\")
for role, info in d['roles'].items():
    status = info['status']
    err = info.get('error') or ''
    print(f\"  {role}: {status}  {err}\")
"
```

### 4.3 查看最近一次执行记录

```bash
python3 -c "import json; d=json.load(open('runtime/last-run.json')); print(json.dumps(d, indent=2, ensure_ascii=False))"
```

### 4.4 查看 blocked 原因

如果 `status.json` 中某角色是 `blocked`，查看 `error` 字段：

```bash
python3 -c "
import json
d = json.load(open('teams/red/runtime/status.json'))
for role, info in d['roles'].items():
    if info['status'] == 'blocked':
        print(f'{role} BLOCKED: {info.get(\"error\", \"unknown\")}')
"
```

---

## 五、失败处理与恢复

### 5.1 角色 failed

```bash
# 1. 查看失败原因
python3 -c "
import json
d = json.load(open('teams/red/runtime/status.json'))
r = d['roles'].get('dev', {})
print(f'Status: {r.get(\"status\")}')
print(f'Error: {r.get(\"error\")}')
"

# 2. 修复问题

# 3. 重置为 pending
python3 scripts/run-round.py --team red --role dev --round 2026-week-22 --retry

# 4. 重新前置检查
python3 scripts/run-round.py --team red --role dev --round 2026-week-22

# 5. 重新执行并回写
# (...编码...)
python3 scripts/run-round.py --team red --role dev --round 2026-week-22 --complete
```

### 5.2 角色 blocked

```bash
# 查看哪些角色被阻塞
python3 -c "
import json
d = json.load(open('teams/red/runtime/status.json'))
for role, info in d['roles'].items():
    if info['status'] == 'blocked':
        print(f'{role}: {info.get(\"error\", \"\")}')
"

# blocked 的解除方式：
# - 如果是前置角色未完成 → 等前置角色完成后再检查
# - 如果是前置角色 failed → 前置角色 retry 完成后，当前角色自动变为 pending
# 不需要手动 --retry（但其实 --retry 也可以）
python3 scripts/run-round.py --team red --role devops --round 2026-week-22 --retry
```

### 5.3 角色 in_progress 但需要回滚

```bash
# 如果角色状态卡在 in_progress（脚本中断等意外）
# 手动重置为 pending
python3 scripts/run-round.py --team red --role dev --round 2026-week-22 --retry
```

---

## 六、判断 Round 是否推进

Round 推进需要**两队同一阶段的所有角色都已结束**。

例如，`PLANNING` → `DEVELOPMENT` 需要：
- 红队 product = completed/failed/skipped
- 蓝队 product = completed/failed/skipped

检查：

```bash
python3 -c "
import json

def team_done(team_name):
    d = json.load(open(f'teams/{team_name}/runtime/status.json'))
    return all(
        info['status'] in ('completed', 'failed', 'skipped')
        for info in d['roles'].values()
    )

print('红队全部结束:', team_done('red'))
print('蓝队全部结束:', team_done('blue'))
"
```

如果两队都结束而 Round 未推进，可能说明：
- 有角色是 `pending`（不是结束状态）
- round.json 的 `current_state` 与角色状态不匹配
- runner 的 `advance_round` 未被调用（例如直接改 status.json 而非通过 runner）

---

## 七、安全结束一次试跑

### 7.1 回滚到干净状态

删除状态文件（**谨慎操作，会丢失所有进度**）：

```bash
rm runtime/round.json
rm teams/red/runtime/status.json
rm teams/blue/runtime/status.json
rm runtime/last-run.json
```

### 7.2 保留产物但重置状态

删除状态文件但不删除 artifacts：

```bash
rm runtime/round.json
rm teams/red/runtime/status.json
rm runtime/last-run.json
# artifacts/ 下的 PRD、tasks、release-notes 会自动保留
```

---

## 八、命令速查表

| 操作 | 命令 |
|------|------|
| 前置检查 | `python3 scripts/run-round.py --team <t> --role <r> --round <id>` |
| 回写成功 | `... --complete` |
| 回写失败 | `... --complete --result failed --error-code X --error-message "..."` |
| 重置失败/阻塞 | `... --retry` |
| 只看不写 | `... --dry-run` |
| 查看 last-run | `python3 -c "import json; print(json.dumps(json.load(open('runtime/last-run.json')), indent=2))"` |
| 查看 team 状态 | `python3 -c "import json; d=json.load(open('teams/red/runtime/status.json')); ..."` |
| 查看 round 状态 | `python3 -c "import json; d=json.load(open('runtime/round.json')); ..."` |
