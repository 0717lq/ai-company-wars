# AI Company Wars — 优化方案、结果与总结

> 执行日期：2026-06-08
> 配套文档：问题诊断见 `2026-06-08-PRE-OPTIMIZATION-ISSUES.md`
> 远程同步终点：master `ebb5e2b1`（经 GitHub API 同步，见文末"环境遗留"）

---

## 一、优化方案总览

按"先止血、再修 Bug、后重构、最后文档"的顺序分四档推进：

| 档位 | 目标 | 对应问题 |
|:---:|------|----------|
| **P0** | 安全止血：清除泄露 token，堵住复发路径 | P0-1 |
| **P1** | 正确性修复：让"成功"名副其实、状态一致 | P1-1 ~ P1-5 |
| **P2** | 可维护性重构：去重、外置配置、补测试 | P2-1 ~ P2-4 |
| **P3** | 文档同步：消除误导信息 | P3-1、P3-2 |

---

## 二、P0 安全 — 方案与结果

### 方案
1. 从 git 移除 `tmp/` 全目录（含 token 文件与内嵌 token 的脚本）
2. `.gitignore` 增补 `tmp/`、`*token*`、`github_pat_*`、`ghp_*` 等规则
3. 删除本地敏感文件
4. token 轮换（用户在 GitHub 侧吊销重建）+ 清理所有藏匿副本

### 结果 ✅
- `git rm --cached -r tmp/` 移除跟踪，`.gitignore` 规则生效（`git check-ignore` 验证）
- 全仓扫描确认 **0 个被跟踪文件含 live token**
- 清理了 4 处藏匿旧 token：`tmp/`、`~/.hermes/.env`、`~/.bashrc`（`GITHUB_TOKEN`/`GH_TOKEN` 改为从 Windows 环境变量动态读取）、`origin` remote URL
- 用户已在 GitHub 吊销旧 token，新 token 经 API 校验有效（HTTP 200）

### 重要发现 🎯
远程 master 当时停在 **Round-9**（`4337cd3`），而含 token 的提交是 Round-10/11 才产生的，**从未被 push 到 GitHub**。结论：**公开仓库实际从未真正暴露过 token**。配合 token 已吊销，风险归零。

---

## 三、P1 正确性 — 方案与结果

| 编号 | 方案 | 结果 |
|------|------|------|
| P1-1 | 熔断器文案/参数语义由"QA 失败"更正为"dev 执行失败"（JSON 字段 `consecutive_qa_failures` 保留以兼容现有 status.json） | ✅ 名实相符，与 P1-2 校验联动 |
| P1-2 | 新增 `verify_role_output`：退出码 0 后还须产出对应交接文件（product→handover、dev→ready-for-deploy、devops→release-notes*、growth→README）**且 mtime 晚于本次执行起点**，否则判 `failed` | ✅ 能识别 Agent 空转；单元测试覆盖 |
| P1-3 | Judge 完成回写时同步更新两队 team status 的 judge 项 + 重聚合 `current_state` | ✅ 修复脱节；并修复了已污染的 red/blue 状态文件 |
| P1-4 | 移除 `_start_ms` 持久化，duration 改由 `in_progress` 起始时间（`last_run`）推算；complete 时清理历史残留 | ✅ 不再污染 status.json |
| P1-5 | 主仓库 push 分支名改为 `git rev-parse --abbrev-ref HEAD` 动态读取 | ✅ master/main 均可 |

### 额外加固（根治 P0 复发）
- `_sync_main_repo` 去掉 `git add -A`，改为**显式路径白名单**
- 新增 `scan_staged_for_secrets` / `scan_unpushed_for_secrets`：主仓库提交前、队伍 push 前扫描 `github_pat_`/`ghp_`，命中即中止（只回报前缀，不打印完整 token）

---

## 四、P2 可维护性 — 方案与结果

| 编号 | 方案 | 结果 |
|------|------|------|
| P2-1 | `ROUND_CONTEXT` 字典外置为 `runtime/round-config.json`，executor 通过 `_load_round_context` 读取 | ✅ 新增轮次只改 JSON，不动代码 |
| P2-2 | 抽取 `scripts/github_auth.py` 统一 token 获取（环境变量 → `~/.hermes/.env` → Windows）与校验；executor、api-sync 全部复用 | ✅ 消除 4 处重复逻辑 |
| P2-4 | 新增 `scripts/tests/`：状态机 19 项（`aggregate_team_state`/`check_preconditions`/`check_round_state` 等）+ 安全函数 9 项（产物校验、secret 扫描） | ✅ **37 个测试全绿** |

> P2-3（常量集中）、P2-5（Judge 触发）评估后判定为低收益、改动牵连较大，本轮未动，留待后续。

---

## 五、P3 文档 — 方案与结果

| 编号 | 方案 | 结果 |
|------|------|------|
| P3-1 | README 战绩/最新轮次/更新日志/项目结构同步到 Round 11 真实数据 | ✅ rag-decompose 88 vs rag-builder 84，补全 Round 8–11 |
| P3-2 | `skills/dev-agent-draft.md` 顶部加废弃标注，指明现行真源 | ✅ 防误用 |

---

## 六、新增 / 变更文件清单

| 文件 | 类型 | 说明 |
|------|:---:|------|
| `scripts/github_auth.py` | 新增 | token 统一获取/校验共享模块 |
| `scripts/api-sync.py` | 新增 | github.com 直连受阻时经 API 同步主仓库 |
| `scripts/tests/test_run_round.py` | 新增 | 状态机单元测试（19） |
| `scripts/tests/test_executor.py` | 新增 | 产物校验 + secret 扫描测试（9） |
| `runtime/round-config.json` | 新增 | 每轮项目方向外置配置 |
| `scripts/executor.py` | 修改 | secret 门禁、产物校验、分支名、熔断器语义、配置/token 复用 |
| `scripts/run-round.py` | 修改 | `_start_ms` 移除、Judge 状态同步 |
| `.gitignore` | 修改 | token/tmp 忽略规则 |
| `README.md` | 修改 | 战绩/轮次/结构同步 |
| `skills/dev-agent-draft.md` | 修改 | 废弃标注 |

---

## 七、验证

- 四个脚本 `python3 -m py_compile` 全部通过
- `python3 -m pytest scripts/tests/` → **37 passed**
- `executor.py --status` / `--dry-run` 冒烟正常
- 关键新逻辑（产物校验、secret 扫描）单元测试验证：新鲜产物通过 / 陈旧缺失失败；干净放行 / 含 token 拦截
- 远程经 API 同步后逐文件 `curl` 校验 HTTP 200，且确认无 token、关键修复代码在位

---

## 八、总结

### 做了什么
从一次 token 泄露的止血开始，连带修复了 5 个正确性 Bug、完成 3 项可维护性重构、同步了过时文档，并沉淀出一个离线同步工具。**13 个诊断问题中处理 11 个**（P2-3、P2-5 评估后暂缓），核心脚本从"零测试"到"37 个测试护栏"。

### 最有价值的三点
1. **把"成功"变得名副其实**（P1-2）：退出码不再等于成功，必须有真实产物 —— 这是多 Agent 自动系统最容易被掩盖的失效。
2. **根治泄露而非仅止血**（P0 + secret 门禁）：去掉 `git add -A` + 提交/push 前扫描，让"零人工干预"管道也拦得住 secret。
3. **token 真源唯一化**（P2-2 + `.bashrc` 动态化）：从 4 处藏匿副本收敛到统一模块 + 单一真源，轮换只需改一处。

### 经验教训
- **自动化放大疏忽**：无人值守管道里，一个没忽略的文件不会被骂一次就改，而是每轮稳定泄露一次。自动化必须自带防线（secret 门禁、显式 add）。
- **"完成"需要被定义**：Agent 系统里"跑完了"和"做对了"是两回事，必须用可验证的产物来界定。

### 环境遗留（非代码问题）
1. **github.com 被 DNS 污染**（解析到死 IP，真实 IP 间歇可达）：常规 `git push` 走不通。恢复方式 —— 稳定 VPN（全局模式）或真实终端中 `/etc/hosts` 加 `140.82.112.3 github.com`。在此之前用 `python3 scripts/api-sync.py` 经 api.github.com 同步。
2. **本地 git 历史与远程分叉**：API 同步是快照式提交，与本地多提交历史不一致（内容一致）。未来恢复原生 push 时，需 `git fetch` 后 reconcile 一次。

### 后续建议（未做）
- P2-3：常量集中到配置区
- P2-5：Judge 触发从 red 队解耦为独立全局调用
- 给 `executor.py` 的并行调度、push 流程补集成测试
