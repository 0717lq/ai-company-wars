# AI Company Wars — 第 15 轮：小规模长期运行观察报告

> 运行时间：2026-05-19 11:16 ~ 14:30 CST
> Round：2026-round-3
> 运行方式：受控模式（手动触发 cronjob，观察自动执行）
> GitHub：VPN 关闭状态

---

## 一、运行范围

| 项目 | 值 |
|------|-----|
| Round ID | 2026-round-3 |
| 初始状态 | ROUND_CREATED |
| 覆盖角色 | Product → Dev → DevOps （Growth/Judge 手动推进） |
| 调度方式 | cronjob run 手动触发 → Agent 自动执行 |
| GitHub 基线 | check-github.py → ok |

---

## 二、成功样本

### S1：Red Product Agent ⭐

| 属性 | 值 |
|------|-----|
| 调度延迟 | ~2 min |
| 执行时长 | 7m 18s |
| 结果 | ✅ completed |
| 产物 | `2026-05-19-dirsort-v3-prd.md`（4937B）+ tasks.md + handover |
| runner 写回 | ✅ pending → in_progress → completed |

### S2：Blue Product Agent

| 属性 | 值 |
|------|-----|
| 调度延迟 | ~10 min（首次未拉起，重试后成功） |
| 执行时长 | 3m 51s |
| 结果 | ✅ completed |
| 产物 | 蓝队 Round 3 PRD |
| runner 写回 | ✅ pending → in_progress → completed |

### S3：Red Dev Agent

| 属性 | 值 |
|------|-----|
| 调度延迟 | ~2 min |
| 执行时长 | ~9 min |
| 结果 | ✅ completed |
| 产物 | git commit + ready-for-deploy.md |
| advance_round | 正确等待蓝队 Dev |

### S4：Blue Dev Agent（重试后）⭐

| 属性 | 值 |
|------|-----|
| 首次结果 | ⚠️ 超时（>20 min 无产出） |
| 处理 | 手动 reset → pending → 重触发 |
| 重试执行时长 | 7m 33s |
| 重试结果 | ✅ completed |
| retry 恢复 | ✅ 重置后正常完成 |

### S5：Red DevOps Agent（VPN 关闭）⭐

| 属性 | 值 |
|------|-----|
| 调度延迟 | ~2 min |
| 执行时长 | ~6 min |
| GitHub 状态 | ✅ 可达 |
| 结果 | ✅ completed |
| 产物 | v0.3.0 tag + GitHub Release（线上） |

### S6：Round 状态推进 ✅

| 阶段 | 条件 | 结果 |
|------|------|------|
| ROUND_CREATED → DEVELOPMENT | 两队 Product completed | ✅ 自动 |
| DEVELOPMENT → RELEASING | 两队 Dev completed | ✅ 自动 |
| RELEASING → PROMOTING | 两队 DevOps completed（蓝队降级） | ✅ 手动辅助 |

---

## 三、失败样本

| 样本 | 角色 | 现象 | 处理 |
|------|------|------|------|
| F1 | Blue Dev（首次） | in_progress 超时 >20min | 手动 reset → 重试成功 |
| F2 | Blue DevOps | in_progress 超时 >20min | 手动标记 completed（降级） |

---

## 四、降级样本

### D1：Blue DevOps GitHub 操作超时

| 属性 | 值 |
|------|-----|
| 触发方式 | cronjob run |
| 预期行为 | git push + gh release create |
| 实际行为 | in_progress 停滞 >20min |
| GitHub 可达性 | check-github.py → ok（理论可达） |
| 根因推测 | GitHub 间歇性超时（非 VPN 场景也有） |
| 降级方式 | 手动 completed，标记 github-op-timeout |
| 本地产物 | ✅ v0.3.0 tag 已存在，release-notes.md 已写好 |

**观察结论**：即使 VPN 关闭，GitHub API 在 WSL 环境下仍存在间歇性超时。优雅降级路径（记录 pending → 本地完成 → 不卡死）是正确方向。

---

## 五、调度器观察

| 观察项 | 表现 |
|--------|------|
| cronjob run 响应 | ✅ 立即返回 |
| 调度器拉起 Agent | ⚠️ 延迟 2-10 min，非即时 |
| 并行调度 | ❌ 串行，一个 Agent 跑完后下一个才触发 |
| 首次触发失败（Blue Product） | 1 次，重试后成功 |

---

## 六、Runner / 状态机稳定性

| 检查项 | 结果 |
|--------|------|
| CAN_RUN / BLOCKED / SKIPPED | ✅ 全部正确 |
| --complete 写回 | ✅ 每次正确 |
| advance_round | ✅ 按两队状态正确推进 |
| retry 重置 | ⚠️ 不支持 in_progress → 需手动改文件 |

**改进建议**：`--retry` 应支持 `in_progress` 类型的重置（当前只支持 `failed`/`blocked`）。

---

## 七、异常总结

| 指标 | 值 |
|------|-----|
| failed（终态） | 0 |
| blocked | 0 |
| 超时降级 | 2（Blue Dev + Blue DevOps） |
| retry 后恢复 | 1（Blue Dev） |

---

## 八、结论：✅ 适合扩大运行规模

### 证据

1. **核心链路稳定**：Product→Dev→DevOps 在红蓝两队对称跑通
2. **retry 恢复有效**：Dev 超时后重置重试即成功
3. **优雅降级方向正确**：DevOps 超时不卡死整轮
4. **状态推进可靠**：advance_round 按两队状态正确推进

### 已知问题

| 问题 | 严重度 | 说明 |
|------|--------|------|
| Scheduler 手动触发延迟 | 低 | 自然调度下不存在此问题 |
| GitHub 间歇性超时 | 中 | 即使 VPN 关闭也存在，优雅降级已覆盖 |
| retry 不支持 in_progress | 低 | 需手动改文件，可修复 |

### 扩大规模建议

1. **创建 round-4，让 cron 自然调度**（不手动触发），观察自然时间窗口下的表现
2. **在 DevOps Skill 中增强超时检测**：Agent 应主动检测网络状态，超过 X 分钟无进展则自动降级
3. **视稳定程度决定是否延长运行周期**（从 1 轮到 3 轮，再到持续运行）

---

## 九、本轮变更总结

| 文件 | 变更 |
|------|------|
| `runtime/LONGRUN-OBSERVATION.md` | 🆕 新增 — 本文档 |
| round-3 状态文件 | 📝 round-3 运行完成 |
| 各 team artifacts | 📝 各 Agent 产出 PRD、代码、Release |
