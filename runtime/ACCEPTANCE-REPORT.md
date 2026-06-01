# AI Company Wars — 第 10 轮自动化验收记录

> 测试日期：2026-05-18
> 测试类型：受控调度接入 + 首轮自动执行验证
> 调度后端：Hermes cron 内部调度器

---

## 一、调度接入方式确认

| 项目 | 结论 |
|------|------|
| 调度后端 | **Hermes cron**（`hermes cron create` + gateway 自动调度） |
| 替代方案 | 系统级 cron/WSL cron 均不适用——Hermes cron 已是原生方案 |
| setup-cron.sh 兼容性 | ❌ 存在一个 bug：`hermes skill list` → 应为 `hermes skills list`（**本轮已修复**） |
| 能否直接作为正式入口 | ✅ 修复后可以。手动创建已验证通过 |
| 最小替代方式 | `hermes cron create --name ... --skill ... --workdir ...` 手动创建 |

---

## 二、试跑记录

### 场景 1：Product Agent 自动触发

| 步骤 | 操作 | 结果 |
|------|------|------|
| 1 | 初始化 round `2026-week-trial-cron` | ✅ ROUND_CREATED, all pending |
| 2 | 创建 Product cronjob (`* * * * *`, skill + workdir) | ✅ job_id=f3c844f22ab1 |
| 3 | 等待自动触发 ~90s | ✅ agent 启动 |
| 4 | runner 前置检查 | ✅ CAN_RUN |
| 5 | Product 工作（写 PRD/tasks/handover） | ✅ 3 个文件全部落地 |
| 6 | runner --complete 回写 | ✅ product: pending → in_progress → completed |

**产物验证**：
- `artifacts/prd/2026-05-18-trial-prd.md` ✅
- `artifacts/tasks.md` ✅
- `artifacts/handover-to-dev.md` ✅
- `last-run.json`: result=completed, duration_ms=51155 ✅

### 场景 2：幂等验证（重复触发）

| 检查项 | 结果 |
|--------|------|
| product 状态被覆盖？ | ❌ 未覆盖，保持 completed |
| last-run.json 被破坏？ | ❌ 未破坏，保持原记录 |
| 重复产物？ | ❌ 未重复创建 |
| cron 持续触发 `last_status=ok` | ✅ 每次触发正常运行并跳过 |

### 场景 3：Dev Agent blocked 验证

| 步骤 | 操作 | 结果 |
|------|------|------|
| 1 | 创建 Dev cronjob（Round 仍在 ROUND_CREATED） | ✅ job_id=a7673382a0df |
| 2 | 等待自动触发 | ✅ agent 启动 |
| 3 | runner 前置检查 | ✅ **BLOCKED（Round 级别）** |
| 4 | Dev 状态 | 保持 `pending`，未被错误修改 |

### 场景 4：Dev Agent CAN_RUN 验证

| 步骤 | 操作 | 结果 |
|------|------|------|
| 1 | 手动完成 Blue Product，推进 Round 到 DEVELOPMENT | ✅ ROUND_CREATED→PLANNING→DEVELOPMENT |
| 2 | 等待 Dev cron 下一轮自动触发 | ✅ agent 启动 |
| 3 | runner 前置检查 | ✅ **CAN_RUN** |
| 4 | Dev 工作 + --complete | ✅ dev: pending → in_progress → completed |
| 5 | last-run.json | result=completed, duration_ms=98721 ✅ |

---

## 三、验证点总表

| 验证项 | 场景 | 结果 |
|--------|------|------|
| 调度能否成功触发 runner | Product + Dev | ✅ |
| runner 按状态机做前置检查 | Product(CAN_RUN), Dev(BLOCKED→CAN_RUN) | ✅ |
| 自动触发后 last-run.json 是否完整 | 含 result, duration_ms, error | ✅ |
| 自动触发后 team 状态是否正确推进 | pending→in_progress→completed | ✅ |
| blocked 在自动触发下正确区分 | Dev 在 ROUND_CREATED 下 BLOCKED | ✅ |
| skipped 在自动触发下正确区分 | Product 重复触发时 already_done | ✅ |
| retry 路径未被破坏 | 未在 cron 下测试，手动路径已验证 | ⚠️ |
| 手动运行路径仍然可用 | runner --dry-run 验证 | ✅ |

---

## 四、发现的问题

| # | 问题 | 严重度 | 是否已修复 |
|---|------|--------|----------|
| 1 | `setup-cron.sh` 中 `hermes skill list` 命令不存在，应为 `hermes skills list` | **中** | ✅ 本轮已修复 |
| 2 | `hermes cron run` 不立即执行，仅重新调度到下一 tick；需等待或使用 `tick` | **低** | 已知行为，非 bug |
| 3 | Dev cron 在被阻塞时 runner 不写任何状态文件（Round 级别检查在前） | **低** | 设计如此——Round 阻塞时不污染 team 状态 |

---

## 五、是否建议进入长期定时运行

**建议**：可以进入，但有前置条件。

| 条件 | 状态 |
|------|------|
| 单角色自动执行已验证 | ✅ Product + Dev |
| 幂等已验证 | ✅ |
| blocked 检查已验证 | ✅ |
| setup-cron.sh 已修复 | ✅ |
| 多角色完整链路（DevOps/Growth/Judge）未验证 | ⚠️ |
| 蓝队 cronjob 未验证 | ⚠️ |

**建议的进入方式**：
1. 先手动创建所有 cronjob（用 `hermes cron create`，暂不依赖 setup-cron.sh）
2. 先开 Product + Dev 两个角色
3. 观察 1-2 轮正常后再逐步开启 DevOps / Growth / Judge
4. 待所有角色稳定后再改用 `setup-cron.sh` 批量管理
