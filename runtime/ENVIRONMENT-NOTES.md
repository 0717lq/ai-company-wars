# AI Company Wars — 环境层分析 & 正式接入定稿

> 日期：2026-05-19
> 对应轮次：第 13 轮
> 状态：定稿

---

## 一、WSL GitHub / Release 卡住问题分析

### 1.1 现象

第 12 轮双边自动运行验证中，DevOps Agent 执行 GitHub Release 操作时：

| 队伍 | 轮次 | 结果 |
|------|------|------|
| 蓝队 DevOps | 第 1 次触发 | ✅ completed（613s） |
| 蓝队 DevOps | 第 2 次触发 | ❌ last_status=error |
| 红队 DevOps | 第 1 次触发 | ❌ in_progress 卡死 >30min |
| 红队 DevOps | 第 2 次触发 | ❌ 同样超时卡死 |

### 1.2 根因

**iKuuuVPN（Windows VPN 客户端）的 DNS 劫持导致 GitHub HTTPS 连接失败。**

DNS 劫持证据：
```
github.com     → 198.18.0.65   (RFC 2544 保留段，非真实 IP)
api.github.com → 198.18.0.47   (同上)
google.com     → 198.18.0.18   (同上)
baidu.com      → 198.18.0.19   (代理兼容，能正常访问)
```

HTTPS 失败证据：
```
api.github.com — SSL: UNEXPECTED_EOF_WHILE_READING
github.com     — SSL: UNEXPECTED_EOF_WHILE_READING
```

### 1.3 关键结论

| 问题 | 答案 |
|------|------|
| 卡住步骤 | `git push` / `gh release create` / `curl` 到 GitHub HTTPS |
| 是否 WSL 特有 | ❌ **不是。** 从 Windows PowerShell 同样失败 |
| 是否稳定复现 | ✅ **是。** iKuuuVPN 启用时 100% 复现 |
| 是否 Windows 原生环境可规避 | ❌ **不能。** Windows 原生网络走同一 DNS + 路由路径 |
| 根本原因 | VPN 客户端 DNS 劫持 + SSL 代理不兼容 GitHub |

### 1.4 为什么蓝队第一次成功了

iKuuuVPN 在第 12 轮执行过程中可能处于**不同的连接状态**（未连接 / 已连接但路由不同）。
成功的那次（613s ≈ 10min）发生在 VPN 未启用时，后续 VPN 启用后全部失败。

---

## 二、DevOps 正式执行环境建议

### 2.1 方案对比

| 方案 | 可行性 | 稳定性 | 复杂度 | 推荐 |
|------|--------|--------|--------|------|
| **A: WSL 内优雅降级** | ✅ | ✅（不卡死） | 低 | ⭐ **推荐** |
| B: DevOps 改 Windows 原生执行 | ⚠️ | ❌（同样受 VPN 影响） | 高 | ❌ |
| C: 发布动作独立为单独层 | ✅ | ✅ | 中 | ✅ 备选 |
| D: 关闭 VPN 再操作 | ✅ | ✅（人工确认） | 低 | ✅ 补充 |

### 2.2 推荐方案：WSL 内优雅降级（方案 A）

**原则：DevOps Agent 不因外部网络问题而卡死。**

执行流程：

```
DevOps Agent 启动
    │
    ├─ python3 scripts/check-github.py
    │
    ├─ exit 0 (GitHub 可达)
    │   ├─ 运行测试
    │   ├─ git push / gh release create
    │   └─ runner --complete
    │
    └─ exit 1 (DNS 劫持/不可达)
        ├─ 运行测试（本地操作正常执行）
        ├─ 记录待办到 artifacts/reports/pending-github-ops.md
        ├─ 跳过 GitHub 操作
        └─ runner --complete (outputs注明"GitHub ops pending")
```

**人工补充执行：**
用户关闭 VPN 后，参考 `pending-github-ops.md` 手动执行 Release：

```bash
cd teams/red/project/
git push origin main --tags
gh release create v0.2.0 --title "v0.2.0" --notes "$(cat ../../artifacts/release-notes.md)"
```

### 2.3 备选：Windows 原生环境执行发布

如果后续需要完全自动化且 VPN 问题已解决，可以将 DevOps 的 Release 步骤改为通过 `powershell.exe` 调用 Windows 原生 `gh` CLI：

```bash
# 从 WSL 调用 Windows gh
TOKEN=$(powershell.exe -Command "[Environment]::GetEnvironmentVariable('GITHUB_TOKEN_Classic', 'User')")
powershell.exe -Command "gh auth login --with-token < echo $TOKEN"
powershell.exe -Command "gh release create v0.2.0 --repo 0717lq/ai-company-wars-red --title ..."
```

但这并不能解决 VPN 层的问题（Windows PowerShell 同样受 iKuuuVPN 影响），所以**不是根本解决方案**。

---

## 三、正式调度接入方式定稿

### 3.1 正式路径（Stable Path）

**Hermes cronjob 工具 API**（`cronjob` 工具，非 CLI）。

这是唯一经过第 12 轮完整验证的稳定方式。所有 9 个 cronjob 均通过此方式创建并验证运行。

**创建方式（在 Hermes Agent 会话中）：**
```
cronjob(action='create', name='...', schedule='...', 
        skills=['ai-company-wars-xxx'], 
        workdir='/mnt/d/Desktop/hermes/ai-company-wars',
        prompt='...')
```

**参数规范：**

| 参数 | 说明 | 示例 |
|------|------|------|
| `name` | 唯一标识 | `acw-red-product` |
| `schedule` | cron 表达式（单引号保护） | `'0 9 * * 1'` |
| `skills` | skill 列表 | `['ai-company-wars-product']` |
| `workdir` | 项目根绝对路径 | `/mnt/d/Desktop/hermes/ai-company-wars` |
| `prompt` | 含 runner 检查指令和 --complete 回写 | (见 AUTO-RUN-REPORT.md) |

### 3.2 弃用路径（Deprecated）

| 方式 | 状态 | 原因 |
|------|------|------|
| `setup-cron.sh` shell 脚本 | ❌ **弃用** | CLI 参数解析有多个 bug；`--schedule` 非命名参数；`*` 被 bash 展开；prompt 位置参数被 `-z` 干扰 |
| `hermes cron create` CLI | ❌ **弃用** | 同上原因，CLI 参数解析与帮助文档不一致 |
| 手动逐个调用 CLI | ⚠️ 不推荐 | 参数复杂易错，不适合批量操作 |

### 3.3 创建新 cronjob 的正式操作流程

当需要创建 cronjob 时，在当前会话中调用 cronjob 工具，**不依赖 shell 脚本**。

```python
# 参考模板
cronjob(
    action='create',
    name='acw-{team}-{role}',
    schedule='{cron_expression}',
    skills=[f'ai-company-wars-{role}'],
    workdir='/mnt/d/Desktop/hermes/ai-company-wars',
    prompt=f'''我是{{team_zh}} {{role_zh}}。{{context}}。

【先运行 runner 状态检查】
python3 scripts/run-round.py --team {team} --role {role} --round $ROUND_ID
如果返回 BLOCKED 或 SKIPPED，记录到日记后退出。

【如果 CAN_RUN】才继续以下步骤：
...（具体步骤）
最后运行完成回写:
python3 scripts/run-round.py --team {team} --role {role} --round $ROUND_ID --complete'''
)
```

---

## 四、已创建的 9 个 cronjob 清单

| # | 名称 | Skill | 调度 | 作用 |
|---|------|-------|------|------|
| 1 | acw-red-product | ai-company-wars-product | 周一 09:00 | 红队产品规划 |
| 2 | acw-blue-product | ai-company-wars-product | 周一 09:00 | 蓝队产品规划 |
| 3 | acw-red-dev | ai-company-wars-dev | 周一 10:00 | 红队开发 |
| 4 | acw-blue-dev | ai-company-wars-dev | 周一 10:00 | 蓝队开发 |
| 5 | acw-red-devops | ai-company-wars-devops | 周五 16:00 | 红队发布 |
| 6 | acw-blue-devops | ai-company-wars-devops | 周五 16:00 | 蓝队发布 |
| 7 | acw-red-growth | ai-company-wars-growth | 周五 18:00 | 红队推广 |
| 8 | acw-blue-growth | ai-company-wars-growth | 周五 18:00 | 蓝队推广 |
| 9 | acw-judge | ai-company-wars-judge | 周日 20:00 | 评分裁判 |

---

## 五、环境层 go / no-go 结论

### 长期运行的最大环境 blocker

**iKuuuVPN DNS 劫持导致的 GitHub 操作失败。** 这不是系统架构问题，是运行环境层的网络问题。

### go / no-go 判定

| 条件 | 状态 | 说明 |
|------|------|------|
| 调度系统 | ✅ go | cronjob 工具 API 已验证稳定 |
| 状态机 / runner | ✅ go | 红蓝对称已验证 |
| GitHub Release | ⚠️ **条件 go** | 需实现优雅降级后视为 go |
| DevOps 优雅降级实现 | ❌ 待完成 | 需更新 devops skill |

**结论：条件性 go。** 在 DevOps Skill 完成优雅降级改造后，即具备进入"监控 + 长跑前验收"的前提。

### 下一轮建议

1. **更新 `ai-company-wars-devops` Skill** — 加入 GitHub 连通性检测 + 优雅降级
2. **进入最小监控面板 + 长跑前最终验收**
   - 监控：cronjob last_status 可视化
   - 验收清单：确认全链路自动运行稳定
3. **确认新 round 启动方案**（用当前 2026-round-2 继续，或创建 round-3）

---

## 六、变更记录

| 文件 | 变更 | 说明 |
|------|------|------|
| `scripts/check-github.py` | 🆕 新增 | GitHub 连通性检测脚本 |
| `runtime/ENVIRONMENT-NOTES.md` | 🆕 新增 | 本文档 |
| `orchestrator/setup-cron.sh` | 📝 标记弃用 | 已加注释说明参考用途 |
| `ai-company-wars-devops` skill | 待更新 | 需加入优雅降级逻辑 |
