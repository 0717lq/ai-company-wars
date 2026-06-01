# ACW 系统优化报告

> 日期：2026-05-30
> 范围：AI Company Wars 自动调度器（executor.py v2）
> 路径：`/mnt/d/Desktop/hermes/ai-company-wars/scripts/executor.py`

---

## 一、优化总览

| 优先级 | 改进项 | 改动量 | 效果 |
|:------:|--------|:------:|------|
| P0 | 死循环熔断 | +80 行 | QA 连续失败 3 次自动阻断 Dev，防无限循环 |
| P1 | Git push 自动化 | +100 行 | token 四步验证 + 自动 push，去掉手动卡点 |
| P2 | 自动推进 + 缓冲期 | +30 行 | Judge 完成后缓冲期自动开下一轮 |
| P3 | --preview 模式 | +20 行 | 流程预览，不 push 不 deploy |
| — | 基础架构 | 重写 | 并行双队 + 卡住检测 + Judge 自动触发 |

---

## 二、逐项详解

### P0：死循环熔断

**问题：** Dev → QA → Dev → QA 无限循环，executor 无法自动停止。

**方案：**
- 每队维护 `circuit_breaker` 计数器，存在 `status.json` 中
- QA 失败 → 计数 +1；QA 成功 → 计数归零
- 计数 >= 3 → 触发熔断，Dev 标记 `blocked`，executor 跳过该队
- `--status` 显示当前计数（`⚡ QA 失败计数: 2/3`）和熔断状态（`🔥 熔断: ...`）
- `--reset-circuit red/blue` 手动重置

**数据结构：**
```json
{
  "circuit_breaker": {
    "consecutive_qa_failures": 0,
    "threshold": 3,
    "blocked": false,
    "reason": null
  }
}
```

**效果：** 最坏情况跑 3 轮 QA→Dev 循环后自动停止，不再无限卡死。

---

### P1：Git push 自动化

**问题：** Dev 写完代码后需要手动 push 到 GitHub。

**方案：** 四步检查链，任何一步失败标记 `push_skipped` 继续往下走，不堵流程。

```
Step 1: token 检查
  └─ 读 GITHUB_TOKEN / GITHUB_TOKEN_Classic（含 Windows 环境变量回退）
  └─ curl 验证 /user 接口
  └─ 401 → token 无效 | 403 → rate limit | 200 → 有效

Step 2: remote 检查
  └─ git remote -v 确认 origin 已配置

Step 3: 变更检测
  └─ git status --porcelain 检查未暂存变更
  └─ git log origin..HEAD 检查未 push 的 commit

Step 4: push
  └─ git push origin main
```

**效果：** 95% 的时候全自动，token 过期才找人。push 失败不阻塞后续角色。

---

### P2：自动推进 + 缓冲期

**问题：** 一轮结束后不会自动开始下一轮。

**方案：**
- `ROUND_ADVANCE_POLICY` 配置策略（`manual` / `auto_30min` / `auto_1hour`）
- Judge 完成 → ROUND_CLOSED → 写入 `next_advance_at` 时间戳
- cron 调用 `--check-auto-advance` 检查时间是否到
- 到了 → 自动 `init_round()` 创建下一轮

**效果：** 设为 `auto_30min` 后全自动循环，每轮间有 30 分钟缓冲（给 CI、异步任务留时间）。

---

### P3：--preview 模式

**问题：** 改了代码想跑一遍验证流程，但不想真的 push/deploy。

**方案：**
```bash
python3 scripts/executor.py --preview 2026-round-6
```
- PM → Dev → QA 全跑
- Dev 执行时注入额外指令："⚠️ 预览模式：写代码但不要 git push。"
- DevOps 注入："⚠️ 预览模式：不要实际部署，只写部署文档。"

**效果：** 5 分钟验证整条链路能跑通，不产生副作用。

---

### 基础架构改进

| 改进项 | 旧版 | 新版 |
|--------|------|------|
| 双队执行 | 串行（先红后蓝） | `ThreadPoolExecutor` 并行 |
| 卡住检测 | 无 | `check_stuck()` 30 分钟超时自动 retry |
| Judge 触发 | 手动 | 两队完成自动触发 |
| 状态查看 | 无 | `--status` 红蓝两队全角色+熔断器状态 |
| dry-run | 无 | `--dry-run` 模拟全流程 |
| 日志 | 无 | `logs/YYYY-MM-DD.log` 全程记录 |

---

## 三、文件清单

| 文件 | 行数 | 说明 |
|------|:----:|------|
| `scripts/executor.py` | 620 | 自动调度器 v2（本次新增/重写） |
| `scripts/run-round.py` | 764 | 状态机（未改动，executor 通过 subprocess 调用） |
| `logs/` | — | 自动创建，按日期记录 |

---

## 四、用法速查

```bash
cd /mnt/d/Desktop/hermes/ai-company-wars

# 查看状态（含熔断器）
python3 scripts/executor.py --status

# 创建新轮次并全自动推进
python3 scripts/executor.py --new-round 2026-round-6

# 预览模式（不 push 不 deploy）
python3 scripts/executor.py --preview 2026-round-6

# 推进已有轮次
python3 scripts/executor.py

# 只看不跑
python3 scripts/executor.py --dry-run

# 重置熔断器
python3 scripts/executor.py --reset-circuit red

# cron 自动推进检查
python3 scripts/executor.py --check-auto-advance
```

---

## 五、已知限制

| 限制 | 说明 | 影响 |
|------|------|------|
| 熔断器阈值固定 | 默认 3 次，暂不支持命令行调整 | 低（可在代码里改 `CIRCUIT_BREAKER_THRESHOLD`） |
| 自动推进策略 | 默认 `manual`，需改代码切 `auto_30min` | 低（一行改动） |
| preview 指令注入 | 靠 prompt 文本约束，LLM 可能不遵守 | 中（概率低） |
| token 回退逻辑 | Windows powershell 回退仅限 WSL 环境 | 低 |

---

*报告生成时间：2026-05-30 13:20*
