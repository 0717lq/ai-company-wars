# AI Company Wars — Skill 契约目录索引

> 最后更新：2026-05-18（第 5 轮）
> 状态：全部 5 个角色契约已补齐

---

## Product Agent

| 文件 | 路径 | 说明 |
|------|------|------|
| SKILL.md | `~/.hermes/skills/ai-company-wars/ai-company-wars-product/SKILL.md` | ✅ 已有（第 2 轮已修路径） |
| INPUTS.md | `~/.hermes/skills/ai-company-wars/ai-company-wars-product/INPUTS.md` | ✅ 第 4 轮新增 |
| OUTPUTS.md | `~/.hermes/skills/ai-company-wars/ai-company-wars-product/OUTPUTS.md` | ✅ 第 4 轮新增 |
| CHECKS.md | `~/.hermes/skills/ai-company-wars/ai-company-wars-product/CHECKS.md` | ✅ 第 4 轮新增 |

**输入摘要**：shared/rules, protocol, leaderboard, announcements, memory, round.json, status.json
**输出摘要**：PRD (artifacts/prd/), tasks.md, handover-to-dev.md, diary, memory update
**完成判定**：PRD + tasks + handover 均写入，日记已写
**禁止动作**：不直接改 project 代码，不跨队写目录

---

## Dev Agent

| 文件 | 路径 | 说明 |
|------|------|------|
| SKILL.md | `~/.hermes/skills/ai-company-wars/ai-company-wars-dev/SKILL.md` | ✅ 已有（第 2 轮已修路径） |
| INPUTS.md | `~/.hermes/skills/ai-company-wars/ai-company-wars-dev/INPUTS.md` | ✅ 第 4 轮新增 |
| OUTPUTS.md | `~/.hermes/skills/ai-company-wars/ai-company-wars-dev/OUTPUTS.md` | ✅ 第 4 轮新增 |
| CHECKS.md | `~/.hermes/skills/ai-company-wars/ai-company-wars-dev/CHECKS.md` | ✅ 第 4 轮新增 |

**输入摘要**：protocol, PRD, tasks, handover, memory, status.json, project 当前代码
**输出摘要**：project/src/ + tests/, docs/ 三件套, ready-for-deploy.md, git commit, diary
**完成判定**：核心代码 + 测试通过 + ready-for-deploy 写入 + git commit
**禁止动作**：不推送 GitHub，不创建 Release，不伪造测试

---

## DevOps Agent

| 文件 | 路径 | 说明 |
|------|------|------|
| SKILL.md | `~/.hermes/skills/ai-company-wars/ai-company-wars-devops/SKILL.md` | ✅ 已有（第 2 轮已修路径） |
| INPUTS.md | `~/.hermes/skills/ai-company-wars/ai-company-wars-devops/INPUTS.md` | ✅ 第 4 轮新增 |
| OUTPUTS.md | `~/.hermes/skills/ai-company-wars/ai-company-wars-devops/OUTPUTS.md` | ✅ 第 4 轮新增 |
| CHECKS.md | `~/.hermes/skills/ai-company-wars/ai-company-wars-devops/CHECKS.md` | ✅ 第 4 轮新增 |

**输入摘要**：protocol, ready-for-deploy, memory, dev diary, status.json, git log
**输出摘要**：git push, git tag, GitHub Release, release-notes.md, 清理 ready-for-deploy
**完成判定**：代码推送 + tag + Release + release-notes + 清理信号文件
**禁止动作**：不改代码，不绕过失败测试，不删 team 文件，不使用 force-push

---

## Growth Agent

| 文件 | 路径 | 说明 |
|------|------|------|
| SKILL.md | `~/.hermes/skills/ai-company-wars/ai-company-wars-growth/SKILL.md` | ✅ 已有（第 2 轮已修路径） |
| INPUTS.md | `~/.hermes/skills/ai-company-wars/ai-company-wars-growth/INPUTS.md` | ✅ 第 5 轮新增 |
| OUTPUTS.md | `~/.hermes/skills/ai-company-wars/ai-company-wars-growth/OUTPUTS.md` | ✅ 第 5 轮新增 |
| CHECKS.md | `~/.hermes/skills/ai-company-wars/ai-company-wars-growth/CHECKS.md` | ✅ 第 5 轮新增 |

**输入摘要**：protocol, rules, README, memory, status.json, release-notes, product diary
**输出摘要**：README 优化, LICENSE, CI workflow, diary, memory update
**完成判定**：README 已优化 + LICENSE 存在 + CI workflow 存在 + 日记已写 + 测试通过
**禁止动作**：不自动发帖/评论/私信，不刷数据，不改 rules，不发 Release

---

## Judge Agent

| 文件 | 路径 | 说明 |
|------|------|------|
| SKILL.md | `~/.hermes/skills/ai-company-wars/ai-company-wars-judge/SKILL.md` | ✅ 已有（第 2 轮已修路径） |
| INPUTS.md | `~/.hermes/skills/ai-company-wars/ai-company-wars-judge/INPUTS.md` | ✅ 第 5 轮新增 |
| OUTPUTS.md | `~/.hermes/skills/ai-company-wars/ai-company-wars-judge/OUTPUTS.md` | ✅ 第 5 轮新增 |
| CHECKS.md | `~/.hermes/skills/ai-company-wars/ai-company-wars-judge/CHECKS.md` | ✅ 第 5 轮新增 |

**输入摘要**：rules, protocol, 两队代码/测试/README/metadata/artifacts, status.json, round.json
**输出摘要**：leaderboard.md, announcements/round-N.md, diary, memory update
**完成判定**：leaderboard 已更新 + 通告已写 + 日记已写 + read_file 验证通过
**失败队伍处理**：一队完成一队失败 → 正常评分，失败方记 0 分/N/A；两队均失败 → 无法评分

---

## 交接模板

| 模板 | 路径 | 用途 | 所属轮次 |
|------|------|------|---------|
| PRD 模板 | `shared/templates/prd-template.md` | Product 写 PRD 时参考 | 第 4 轮 |
| 任务模板 | `shared/templates/tasks-template.md` | Product 写任务时参考 | 第 4 轮 |
| Ready-for-deploy 模板 | `shared/templates/ready-for-deploy-template.md` | Dev 写部署交接时参考 | 第 4 轮 |
| Handover-to-dev 模板 | `shared/templates/handover-to-dev-template.md` | Product 写交接说明时参考 | 第 4 轮 |
| Release Notes 模板 | `shared/templates/release-notes-template.md` | DevOps 写发版说明时参考 | 第 5 轮 |
| Judge Report 模板 | `shared/templates/judge-report-template.md` | Judge 写评分报告时参考 | 第 5 轮 |

---

## 治理文档

| 文件 | 路径 | 用途 |
|------|------|------|
| 最小治理边界摘要 | `GOVERNANCE.md` | Growth 允许/禁止/灰区 + Judge 失败队伍处理 + 数据隔离 + Round 阶段边界 |

---

## 统一 Runner

| 文件 | 路径 | 说明 |
|------|------|------|
| Runner 入口 | `scripts/run-round.py` | 统一调用入口，支持前置检查和完成回写 |
| Runner 文档 | `runtime/RUNNER.md` | 执行流程、状态说明、参数详解 |

**调用方式**：
```bash
python3 scripts/run-round.py --team red --role dev --round 2026-week-21
python3 scripts/run-round.py --team blue --role devops --round 2026-week-21 --complete
```

**核心能力**（v2.0）：
1. 读取 round.json / status.json 判断是否允许执行
2. 区分 blocked / skipped / can_run / already_done
3. 支持 `--result failed` 回写（含 error_code / error_message）
4. 结构化 last-run.json（含 duration_ms / error 对象）
5. 幂等检查：同 round 同角色已 completed → 自动跳过
6. 重跑模式 `--retry`：重置 failed/blocked → pending
7. 两队都完成后自动推进 Round 阶段

---

## 模板与状态机对接

| 状态机层面 | 对接方式 |
|-----------|---------|
| Round 级状态 | run-round.py 的 `--complete` 回写后检查推进条件 |
| Team 级状态 | 前置检查 + 回写时更新 `teams/{颜色}/runtime/status.json` |
| Agent 执行状态 | 每次调用写入或覆盖 `runtime/last-run.json` |
| 治理边界 | runner 不越权——只检查状态、写状态，不直接调用 skill 逻辑 |

---

## 后续工作

- cronjob 实际创建和运行（setup-cron.sh 已修正待运行）
- 评分算法细化与可视化
- 长期记忆机制
- dashboard

---

*本索引应与 Hermes Skill 目录下的实际文件保持一致。*
