# AI Company Wars — 调度计划

> 最后更新：2026-05-18（第 2 轮审计后统一口径）
> Cronjob 时间表，驱动所有 Agent 按 Sprint 节奏运行
> 参考：shared/rules.md — Sprint 流程

---

## 时间表

| 时间 | Agent | 任务 | cron 表达式 |
|------|-------|------|-------------|
| 周一 09:00 | Product Agent (红队) | 市场调研 + 输出 PRD | `0 9 * * 1` |
| 周一 09:00 | Product Agent (蓝队) | 市场调研 + 输出 PRD | `0 9 * * 1` |
| 周一 10:00 | Dev Agent (红队) | 读取 PRD，开始编码 | `0 10 * * 1` |
| 周一 10:00 | Dev Agent (蓝队) | 读取 PRD，开始编码 | `0 10 * * 1` |
| 周五 16:00 | DevOps Agent (红队) | 测试、发布 Release | `0 16 * * 5` |
| 周五 16:00 | DevOps Agent (蓝队) | 测试、发布 Release | `0 16 * * 5` |
| 周五 18:00 | Growth Agent (红队) | 优化 README + 推广 | `0 18 * * 5` |
| 周五 18:00 | Growth Agent (蓝队) | 优化 README + 推广 | `0 18 * * 5` |
| 周日 20:00 | Judge Agent | 评分 + 排行榜 | `0 20 * * 0` |

---

## 已创建的 Skills

| Agent | Hermes Skill 名称 | 状态 |
|-------|-------------------|------|
| Product Agent | `ai-company-wars-product` | ✅ 已创建 |
| Dev Agent | `ai-company-wars-dev` | ✅ 已创建 |
| DevOps Agent | `ai-company-wars-devops` | ✅ 已创建 |
| Growth Agent | `ai-company-wars-growth` | ✅ 已创建 |
| Judge Agent | `ai-company-wars-judge` | ✅ 已创建 |

> ⚠️ **注意**：Skill 名称以 `ai-company-wars-` 为前缀，setup-cron.sh 和 cronjob 创建命令必须使用完整名称。

---

## 创建命令

Skills 就绪后，运行以下命令创建所有 cronjob（需要先修复 setup-cron.sh 中的 skill 名称匹配）：

```bash
bash orchestrator/setup-cron.sh
```

> **当前状态**：setup-cron.sh 中 skill 名称检测仍使用旧名（如 `product-agent`），与 Hermes 系统技能名（`ai-company-wars-product`）不匹配。需先修复脚本再运行。详见 `AUDIT-REPORT.md` 冲突 #2。
