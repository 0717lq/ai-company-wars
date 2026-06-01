# AI Company Wars 第 11～16 轮总报告

> 时间：2026-05-18 ~ 2026-05-19
> 状态：✅ Conditional Go — 可进入自然调度连续运行

---

## 一、各轮核心成果

| 轮次 | 领域 | 核心成果 |
|------|------|---------|
| **11** | 🔍 根因定位 | 蓝队 Dev 卡住根因确认：**从未被调度**，不是 runner/状态机/契约问题 |
| **12** | ⚡ 调度验证 | **蓝队 Dev 首次自动调度成功**，红蓝 Product→Dev 链路对称跑通 |
| **13** | 🏗 环境定稿 | iKuuuVPN DNS 劫持根因定位 + DevOps 优雅降级 + 正式调度路径收敛 |
| **14** | 📊 监控验收 | `status-summary.py` + `PRELAUNCH-CHECK.md` → **Conditional Go 结论** |
| **15** | 🧪 小规模试跑 | 6 个成功 + 2 个失败 + 1 个降级三类样本采集 |
| **16** | 🔁 自然调度验证 | **Round-4 全链路 completed → ROUND_CLOSED**（0 failed, 0 blocked）|

---

## 二、系统当前状态

```
Round-4: ROUND_CLOSED ✅
  Red:   Product ✅  Dev ✅  DevOps ✅  Growth ✅
  Blue:  Product ✅  Dev ✅  DevOps ✅  Growth ✅
  Judge: completed ✅
  Failed: 0   Blocked: 0
```

### 9 个正式 cronjob 就绪

| # | cronjob | Schedule | 状态 |
|---|---------|----------|------|
| 1 | acw-red-product | 周一 09:00 | ✅ |
| 2 | acw-blue-product | 周一 09:00 | ✅ |
| 3 | acw-red-dev | 周一 10:00 | ✅ |
| 4 | acw-blue-dev | 周一 10:00 | ✅ |
| 5 | acw-red-devops | 周五 16:00 | ✅ |
| 6 | acw-blue-devops | 周五 16:00 | ✅ |
| 7 | acw-red-growth | 周五 18:00 | ✅ |
| 8 | acw-blue-growth | 周五 18:00 | ✅ |
| 9 | acw-judge | 周日 20:00 | ✅ |

---

## 三、已解决的问题

| 问题 | 状态 | 解决方案 |
|------|------|---------|
| 蓝队从未被调度 | ✅ | 创建 acw-blue-dev cronjob，首次自动调度成功 |
| setup-cron.sh CLI 不可用 | ✅ 弃用 | 正式路径：cronjob 工具 API |
| VPN DNS 劫持导致 GitHub 卡死 | ✅ 已定位、有降级 | check-github.py + pending-github-ops.md |
| DevOps Agent GitHub 超时卡死 | ✅ 优雅降级 | 不卡整轮，本地完成 + 记录待办 |
| 红队 artifacts 遗留旧文件 | ✅ | 归档到 reports/ |
| 调度器手动触发延迟 | ⚠️ 已知 | 自然调度不受影响 |

---

## 四、已知风险

| 风险 | 可能性 | 影响 | 缓解措施 |
|------|--------|------|---------|
| iKuuuVPN 重启 → GitHub 中断 | 高 | DevOps 发布失败 | 优雅降级 + pending-github-ops.md |
| Agent session 超时 | 中 | 角色卡在 in_progress | 手动 reset + retry |
| 调度器高频触发后不拉 Agent | 低 | 角色跳过一轮 | 重跑 cronjob |
| PAT token 过期 | 低 | GitHub 操作全部失败 | 手动续期 |
| --retry 不支持 in_progress | 低 | 需手动改文件 | 建议修复 |

---

## 五、关键文档索引

| 文档 | 路径 |
|------|------|
| 一键状态查看 | `python3 scripts/status-summary.py` |
| GitHub 连通性检测 | `python3 scripts/check-github.py` |
| 环境分析 | `runtime/ENVIRONMENT-NOTES.md` |
| 长跑前验收 | `runtime/PRELAUNCH-CHECK.md` |
| 第 16 轮运行报告 | `runtime/ROUND4-AUTORUN-REPORT.md` |
| 第 15 轮运行报告 | `runtime/LONGRUN-OBSERVATION.md` |
| 自动运行验收 | `runtime/AUTO-RUN-REPORT.md` |
| 调度计划 | `orchestrator/schedule.md` |

---

## 六、结论：✅ Conditional Go

系统已具备自然调度连续运行条件。三条前提条件：

1. **GitHub 可达时** — DevOps 正常发布 ✅（Round-4 验证）
2. **GitHub 不可达时** — 优雅降级，不卡整轮 ✅（方案已落地）
3. **遵守正式调度路径** — cronjob 工具 API ✅

下一轮建议：创建 Round-5，让 cron 按自然时间窗口调度。
