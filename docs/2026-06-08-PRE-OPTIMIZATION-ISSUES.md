# AI Company Wars — 优化前问题诊断报告

> 诊断日期：2026-06-08
> 诊断范围：`ai-company-wars/`（核心调度器 executor.py + 状态机 run-round.py + 协议/配置/文档）
> 诊断方式：通读源码 + 运行时状态核对 + 全仓 secret 扫描
> 性质：**优化前现状快照**，对应的修复见 `OPTIMIZATION-PLAN-AND-RESULTS.md`

---

## 一、系统概况

AI Company Wars 是基于 Hermes Agent 的红蓝对抗多 Agent 系统，核心是状态机驱动的自动流水线：

```
ROUND_CREATED → PLANNING → DEVELOPMENT → RELEASING → PROMOTING → JUDGING → ROUND_CLOSED
                 product      dev          devops      growth      judge
```

- `scripts/executor.py`（约 1010 行）：调度器。扫描 round 状态 → 红蓝双队 `ThreadPoolExecutor` 并行跑同阶段 → 调 `hermes chat -s <skill>` 执行角色 → 熔断/卡住检测 → 自动 push → 自动开下一轮。
- `scripts/run-round.py`（约 764 行）：状态机。前置检查 → 标记 `in_progress` → 完成回写 → 推进轮次。
- 状态分层：`runtime/round.json`（全局轮次）+ `teams/{red,blue}/runtime/status.json`（每队角色状态）。
- Agent 间不直接对话，通过 `artifacts/` 下约定文件传递（PRD → handover → ready-for-deploy → release-notes）。

设计清晰、文档完整，已运行 11 轮。以下为发现的问题，按严重性分级。

---

## 二、🔴 P0 — 安全（最高优先级）

### P0-1　真实 GitHub token 进入 git 仓库

| 项 | 详情 |
|----|------|
| 现象 | `tmp/token.txt`、`tmp/fg_token.txt` 明文存放 `github_pat_` fine-grained token；`tmp/push_tag.ps1`、`tmp/push_r10.ps1` 把 token 硬编码进 URL 字符串 |
| 跟踪状态 | 被 `git ls-files` 跟踪，出现在 `Round 2026-round-10/11 自动同步` 等本地提交中 |
| 根因链 | ① token 明文存进仓库目录 → ② `.gitignore` 无 `tmp/`/token 规则 → ③ `executor.py` 的 `_sync_main_repo` 用 `git add -A` 全量暂存 → ④ 自动 commit + 自动 push 无人工复核 |
| 放大因素 | 系统设计为"零人工干预"，提交前"瞄一眼 diff"的天然防线被去掉，疏漏会每轮稳定复发 |

> 补充发现（优化中暴露）：token 还藏在另外 3 处 —— `~/.hermes/.env`、`~/.bashrc` 的 `GITHUB_TOKEN`/`GH_TOKEN` 硬编码、`origin` remote URL 内嵌（push 失败未还原残留）。

---

## 三、🟠 P1 — 正确性 Bug

### P1-1　熔断器名实不符
README/注释宣称"QA 连续失败 3 次熔断"，但 `executor.py` 实际只在 `role == "dev"` 且 hermes 进程**退出码非 0** 时累加，根本没有 QA/测试结果概念。Agent 写出烂代码但进程正常退出时，计数器恒为 0 —— 熔断形同虚设。

### P1-2　退出码 ≠ 任务成功
`run_role` 仅凭 `returncode == 0` 判定 `completed`，完全不校验是否真的产出 PRD / 代码 / `ready-for-deploy.md`。**Agent 空转一遍也会被记成功。**

### P1-3　状态脱节已实际发生
诊断时实测：`round.json` 已是 `ROUND_CLOSED` + `judge_status: completed`，但 `red/status.json` 的 judge 仍停在 `in_progress`、`current_state` 也是 `in_progress`。root 原因：Judge 是全局角色，完成时只更新 `round.json`，不回写两队 team status。

### P1-4　`_start_ms` 污染状态文件
`run-round.py` 把临时计时字段 `_start_ms` 写进持久化的 `status.json`，靠 complete 时 `pop` 清理。一旦 complete 未走到（如 judge 分支），就永久残留 —— red 队当时即残留该字段。

### P1-5　主仓库 push 分支名硬编码 `master`
`_sync_main_repo` 写死 `git push origin master`，但队伍 project 用 `main`。主仓库若为 `main` 分支则永远 push 失败。

---

## 四、🟡 P2 — 设计 / 可维护性

| 编号 | 问题 |
|------|------|
| P2-1 | **轮次方向硬编码**：`ROUND_CONTEXT` 字典把每轮项目方向写死在 `executor.py` 源码里，每开一轮要改代码 |
| P2-2 | **token 逻辑重复 3 份**：`check_github_token`、`_get_token` 及 push 内联，且耦合 `powershell.exe`（Windows/WSL） |
| P2-3 | **魔法值散落**：`max_iterations=20`、超时 1800s、卡住阈值 30min 等常量分散各处，无集中配置 |
| P2-4 | **零单元测试**：两个核心脚本逻辑密集（状态机、聚合、前置条件）却无任何测试，回归风险高 |
| P2-5 | **Judge 触发方式别扭**：`run_judge` 写死 `run_role("red", "judge", ...)`，全局角色挂在 red 队上 |

---

## 五、🟢 P3 — 文档 / 体验

| 编号 | 问题 |
|------|------|
| P3-1 | README 战绩停在 Round 7（fclean/dirsort），实际已到 Round 11（rag-decompose/rag-builder），项目早已转型 RAG 技能 |
| P3-2 | `skills/dev-agent-draft.md` 为历史草稿，引用已废弃的 `PRD.md`/`current-sprint.md` 路径，易误导 |

---

## 六、问题清单速查

| 编号 | 等级 | 一句话 |
|------|:---:|--------|
| P0-1 | 🔴 | GitHub token 明文进仓库 + 自动管道无门禁 |
| P1-1 | 🟠 | 熔断器只看进程退出码，名实不符 |
| P1-2 | 🟠 | 退出码 0 即记成功，不校验产物（Agent 可空转） |
| P1-3 | 🟠 | Judge 完成后 round/team 状态脱节 |
| P1-4 | 🟠 | `_start_ms` 残留污染状态文件 |
| P1-5 | 🟠 | 主仓库 push 分支名硬编码 master |
| P2-1 | 🟡 | 轮次方向硬编码进源码 |
| P2-2 | 🟡 | token 逻辑 3 处重复 |
| P2-3 | 🟡 | 常量魔法值散落 |
| P2-4 | 🟡 | 核心脚本零测试 |
| P2-5 | 🟡 | Judge 触发挂在 red 队 |
| P3-1 | 🟢 | README 战绩/轮次过时 |
| P3-2 | 🟢 | 历史草稿 skill 引用废弃路径 |
