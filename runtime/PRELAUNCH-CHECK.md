# AI Company Wars — 长跑前最终验收

> 日期：2026-05-19
> 轮次：第 14 轮
> 对应 Round：2026-round-2（测试轮）
> 文档类型：正式验收 / go-no-go 判定

---

## 验收总结

**最终结论：✅ Conditional Go — 可进入小规模受控长期运行**

本轮验收基于第 11~13 轮的全部准备工作，包括链路补齐、环境分析、调度定稿。

---

## 一、双边一致性检查

| 检查项 | 状态 | 证据 |
|--------|------|------|
| 红队完整链路成立 | ✅ 通过 | Product→Dev→DevOps→Growth 全部 completed |
| 蓝队完整链路成立 | ✅ 通过 | Product→Dev→DevOps→Growth 全部 completed |
| 红蓝状态推进一致 | ✅ 通过 | 两队在 ROUND_CREATED→DEVELOPMENT→RELEASING→PROMOTING→JUDGING→ROUND_CLOSED 全程同步推进 |
| 各角色 completed 语义一致 | ✅ 通过 | `--complete` 后状态文件结构一致 |
| 产物结构一致 | ✅ 通过 | artifacts/prd/、tasks.md、handover-to-dev.md、ready-for-deploy.md、release-notes.md 红蓝结构相同 |

**结论：红蓝在系统逻辑层已完全对称。**

---

## 二、Runner 稳定性

| 检查项 | 状态 | 说明 |
|--------|------|------|
| run-round.py 正常执行 | ✅ 通过 | Product→Dev→DevOps→Growth→Judge 全程验证 |
| CAN_RUN 判定 | ✅ 通过 | 依赖 Round 阶段 + 角色前置条件 |
| BLOCKED 语义 | ✅ 通过 | Round 级别和角色级别正确区分 |
| SKIPPED 语义 | ✅ 通过 | 已 completed 后重复触发正确返回 SKIPPED |
| failed 写回 | ✅ 通过 | `--complete --result failed` 参数已验证 |
| retry 逻辑 | ✅ 通过 | `--retry` 将 failed/blocked 重置为 pending |
| advance_round | ✅ 通过 | 自动推进：ROUND_CREATED→PLANNING→DEVELOPMENT→RELEASING→PROMOTING→JUDGING→ROUND_CLOSED |
| Judge 全局化 | ✅ 通过 | Judge 作为全局角色（非 per-team），通过 round.json `judge_status` 管理 |

**结论：Runner 已具备生产级稳定性。**

---

## 三、调度接入

| 检查项 | 状态 | 说明 |
|--------|------|------|
| 正式调度路径 | ✅ 定稿 | cronjob 工具 API（`cronjob action='create'`） |
| 创建 cronjob 成功 | ✅ 通过 | 9 个 cronjob 全部创建成功 |
| 自动触发 → 拉起 Agent | ✅ 通过 | 已验证 |
| Agent → runner 判断 → 写回 | ✅ 通过 | 已验证 |
| workdir 正确 | ✅ 通过 | 所有 cronjob 设置 workdir=项目根 |
| skill 正确加载 | ✅ 通过 | 5 个 skill 均正确关联 |
| 弃用路径明确 | ✅ 完成 | setup-cron.sh 标记弃用，文档注明正式路径 |
| 旧 CLI 路径已弃用 | ✅ 完成 | oracle: 参数解析 bug，prompt 被 `-z` 干扰 |

**结论：调度接入已收敛到稳定路径。**

---

## 四、环境前置条件

| 检查项 | 状态 | 说明 |
|--------|------|------|
| check-github.py 可用 | ✅ 已实现 | `scripts/check-github.py` exit 0=正常, 1=DNS劫持, 2=不可达 |
| GitHub 不可达时的优雅降级 | ✅ 已实现 | DevOps Skill Step 0：离线模式 → 只做本地操作 → 记录 pending-github-ops.md |
| VPN/DNS 劫持列为环境风险 | ✅ 已文档化 | 详见 `ENVIRONMENT-NOTES.md` |
| 外部发布动作受环境约束 | ✅ 明确 | GitHub Release/Push 只在 `check-github.py` 返回 OK 时执行 |
| DevOps 不卡死 | ✅ 已验证 | 优雅降级确保 DevOps Agent 完成 `--complete` 回写 |

**结论：环境风险已识别，降级方案已落实。**

---

## 五、Acceptance 收尾

| # | 问题 | 严重度 | 状态 |
|---|------|--------|------|
| 1 | setup-cron.sh skill list 命名错误 | blocker | ✅ 已修复 |
| 2 | setup-cron.sh 用 `hermes cronjob` 而非 `hermes cron` | blocker | ✅ 已修复 |
| 3 | setup-cron.sh 缺少 `--workdir` | important | ✅ 已修复 |
| 4 | setup-cron.sh CLI 参数 bug（--schedule + * 展开） | blocker | ✅ 已标记弃用，正式路径为工具 API |
| 5 | 红队 artifacts 遗留旧文件 | nice-to-have | ✅ 已归档 |
| 6 | 蓝队从未被调度 | blocker | ✅ 已验证修复（Blue Dev 自动完成） |
| 7 | WSL GitHub 卡死 | important | ✅ 根因定位+优雅降级落地 |
| 8 | 红队第一次 DevOps GitHub 超时 | environment | ✅ 环境风险已文档化 |

**结论：所有 blocker 已处理，important 问题有明确方案，可进入运行。**

---

## 六、最终运行建议

### 结论：✅ Conditional Go

### 运行条件

**条件 1：外部发布依赖 GitHub 可达**
- DevOps Agent 依赖 `check-github.py` 检测连通性
- GitHub 不可达时，Release/Push 操作记录到 `pending-github-ops.md`，需人工处理
- 不影响其他 role 的正常调度和运行

**条件 2：VPN/DNS 劫持环境下本地降级运行**
- iKuuuVPN 启用时，Product/Dev/Growth 的 web_search 可能会受影响
- 但 PRD 方向主要来自裁判反馈和团队记忆，不依赖实时网络数据
- 调度系统本身（cronjob、runner、状态机）完全不受网络影响

**条件 3：遵守正式调度路径**
- 使用 cronjob 工具 API 创建和管理 cronjob
- 不依赖 `setup-cron.sh` CLI 脚本
- 如需修改调度配置，在当前 Hermes 会话中执行

**条件 4：长跑初期保留人工观察窗口**
- 建议至少观察 1-2 轮完整调度周期（1-2 周）
- 每轮结束后运行 `python3 scripts/status-summary.py` 检查状态
- 发现异常时检查 `runtime/last-run.json` 和具体 role 的日记

### 建议的启动方式

```
1. 创建新 round：
   python3 scripts/init-round.py --round 2026-round-3 --force

2. 确认所有 cronjob 存在：
   (通过 cronjob action='list' 验证 9 个 cronjob)

3. 确认 DevOps 优雅降级：
   运行 python3 scripts/check-github.py
   返回 ok → 正常模式；返回 DNS 劫持 → 降级模式

4. 运行状态检查基线：
   python3 scripts/status-summary.py

5. 观察自然调度：
   Product: 周一 09:00
   Dev: 周一 10:00
   DevOps: 周五 16:00
   Growth: 周五 18:00
   Judge: 周日 20:00
```

---

## 七、已知风险清单

| 风险 | 可能性 | 影响 | 缓解措施 |
|------|--------|------|---------|
| iKuuuVPN 重启导致 GitHub 中断 | 高 | DevOps Release 失败 | 优雅降级，pending-github-ops.md |
| scheduler 高频触发后不拉 Agent | 低 | 角色跳过一轮 | rerun cronjob 即可 |
| Agent 超时卡死 | 低 | 角色停留在 in_progress | `--retry` 重置 |
| PAT 过期 | 低 | GitHub 操作全部失败 | 需人工更新 token |
| WSL 磁盘满 | 低 | 文件操作失败 | runner 在前置检查中检测 |

---

## 八、相关文档索引

| 文档 | 路径 |
|------|------|
| 状态查看（一条命令） | `python3 scripts/status-summary.py` |
| 连通性检测 | `scripts/check-github.py` |
| 环境分析 | `runtime/ENVIRONMENT-NOTES.md` |
| 自动运行验收 | `runtime/AUTO-RUN-REPORT.md` |
| 调度计划 | `orchestrator/schedule.md` |
| 通信协议 | `shared/protocol.md` |
| 竞赛规则 | `shared/rules.md` |
| 排行榜 | `shared/leaderboard.md` |

---

## 九、本轮变更总结

| 文件 | 变更 |
|------|------|
| `scripts/status-summary.py` | 🆕 新增 — 一键状态汇总 |
| `runtime/PRELAUNCH-CHECK.md` | 🆕 新增 — 本文档，长跑前验收 |

---

## 十、下一轮建议

1. **进入小规模长跑**：创建 round-3，按 schedule.md 时间表观察自然调度
2. **每轮用 `status-summary.py` 检查**：无需手动翻阅多个状态文件
3. **如有 DevOps pending 记录**：关闭 VPN 后人工执行
4. **稳定运行 1-2 轮后**：可考虑最小监控面板（持续观察 cronjob last_status）
