# AI Company Wars — 第 13 轮：环境稳定化 + 调度接入定稿

> 日期：2026-05-19
> 目标：解决 WSL GitHub 卡住问题，收敛正式调度接入方式

---

## 一、WSL GitHub 卡住根因分析

### 1.1 发现

第 12 轮红队 DevOps Agent 两次尝试 GitHub Release 操作均超时卡死。
蓝队 DevOps 首次成功，但后续也出现 error。

### 1.2 根因

**iKuuuVPN 的 DNS 劫持 + SSL 代理导致 GitHub HTTPS 连接失败。**

```
DNS 劫持:
  github.com     → 198.18.0.65  (✗ 不是真实 GitHub IP)
  api.github.com → 198.18.0.47  (✗)
  google.com     → 198.18.0.18  (✗)
  baidu.com      → 198.18.0.19  (但能正常访问 — 说明代理对国内域名兼容性好)

SSL 错误:
  api.github.com — SSL: UNEXPECTED_EOF_WHILE_READING
  github.com     — SSL: UNEXPECTED_EOF_WHILE_READING

受影响范围:
  从 WSL 和 Windows PowerShell 出发的所有 GitHub HTTPS 连接
  git 协议 (github.com:22/443) 同样受影响
```

**结论：这不是 WSL 独有的问题，是 Windows 系统级网络问题。** WSL 和 Windows 原生网络都走同一个 DNS + 路由路径。

### 1.3 为什么蓝队 DevOps 第一次成功了

蓝队 DevOps 第 12 轮第一次触发时（01:17 → 01:27，耗时 613 秒 ≈ 10 分钟）成功完成了 Release。此时 iKuuuVPN 可能处于不同的连接状态（未连接/已连接但路由不同）。后续再触发时 VPN 已启用，因此失败。

即：**该操作的成功与否取决于 iKuuuVPN 的实时状态。**

### 1.4 解决方案选项

#### 方案 A：关闭 VPN 时执行 DevOps 操作 ⭐ 推荐

| 优点 | 缺点 |
|------|------|
| 简单可靠，无需改网络配置 | 需要人工确认 VPN 状态 |
| 不涉及额外工具链 | 无法完全自动化 |

**实施方式：**
- DevOps Agent 启动时先检测 GitHub 连通性
- 如果不可达，跳过 GitHub 操作，记录为 `pending-for-manual`
- 人工确认 VPN 关闭后，手动触发 DevOps

**连通性检测脚本**（给 DevOps Skill 用）：

```bash
timeout 5 curl -sf https://api.github.com > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "GitHub unreachable - VPN may be active"
    # 记录状态，跳过 GitHub 操作
fi
```

#### 方案 B：使用 GitHub CLI（gh）替代 git/curl

| 优点 | 缺点 |
|------|------|
| gh CLI 可能有不同的网络栈处理 | 需要配置 gh auth login |
| 支持 PAT、OAuth、SSH 多种认证 | 仍然受同一网络环境影响 |
| 命令行简洁 `gh release create` | |

**验证结果：** `gh` 已安装但未登录。且 gh 同样走系统网络栈，大概率同样受影响。

#### 方案 C：WSL 使用独立 DNS 绕过 VPN 劫持

在 WSL 内配置 `/etc/resolv.conf` 使用公共 DNS（如 8.8.8.8 或 114.114.114.114），绕过 Windows 的 DNS 劫持。

```bash
# 在 WSL 中
sudo sh -c 'echo "nameserver 8.8.8.8" > /etc/resolv.conf'
```

**风险：** 这会关闭 WSL 的自动 DNS 生成（/etc/wsl.conf 需配置 `generateResolvConf = false`），且可能影响 VPN 的正常路由。

#### 方案 D：在 DevOps Skill 中添加网络检测 + 优雅降级

**推荐方案 —— DevOps Agent 增加网络健康检测：**

```python
def check_github_connectivity():
    """检测 GitHub 是否可达，返回 'ok' | 'vpn_blocked' | 'dns_hijacked'"""
    import socket, json, urllib.request
    try:
        # 检测 DNS 是否被劫持
        ips = socket.getaddrinfo('api.github.com', 443)
        for ip in ips:
            if ip[4][0].startswith('198.18.'):
                return 'dns_hijacked'
        # 检测 HTTPS 连通性
        r = urllib.request.urlopen('https://api.github.com', timeout=5)
        return 'ok' if r.status == 200 else f'unexpected_status:{r.status}'
    except Exception as e:
        return f'unreachable:{type(e).__name__}'
```

当检测到不可达时：
- 创建 `artifacts/reports/pending-github-ops.md`
- 标记 DevOps 状态为 `completed`（本地操作完成）+ outputs 中注明 GitHub 操作待人工执行
- 不卡死，不超时

---

## 二、正式调度接入方式定稿

### 2.1 问题回顾

第 12 轮发现 `setup-cron.sh` 有多个问题：

| 问题 | 详情 |
|------|------|
| `hermes cronjob create` 命令不存在 | 应为 `hermes cron create` |
| `--schedule` 不是命名参数 | schedule 是位置参数 |
| prompt 作为位置参数被系统级 `-z` 参数干扰 | CLI 不接受 prompt 位置参数 |
| `*` 被 bash 展开 | 需单引号保护 cron 表达式 |

### 2.2 正式接入路径（Stable Path）

**使用 Hermes cronjob 工具 API（而非 CLI）。**

这是唯一经过第 12 轮完整验证的稳定方式。工具 API 的所有参数都正常工作，没有任何 CLI 的参数解析问题。

```python
# 正式接入方式 — 通过 cronjob 工具 API
# 在 Hermes Agent 会话中，使用 cronjob 工具
# cronjob(action='create', name='...', schedule='...', skills=[...], workdir='...', prompt='...')
```

**参数说明：**

| 参数 | 必填 | 说明 |
|------|------|------|
| `name` | 推荐 | 人类可读的名称 |
| `schedule` | 是 | cron 表达式如 `'0 9 * * 1'` |
| `skills` | 否 | 要加载的 skill 列表 |
| `workdir` | 推荐 | 项目根目录绝对路径 |
| `prompt` | 否 | 任务指令 |
| `deliver` | 否 | 默认 local（不推送消息） |

**创建全部 9 个 cronjob 的参考命令（已验证）：**

详见第 12 轮创建记录，共创建 9 个 cronjob：
- acw-red-product / acw-blue-product（周一 09:00）
- acw-red-dev / acw-blue-dev（周一 10:00）
- acw-red-devops / acw-blue-devops（周五 16:00）
- acw-red-growth / acw-blue-growth（周五 18:00）
- acw-judge（周日 20:00）

### 2.3 弃用路径（Deprecated Path）

| 方式 | 状态 | 原因 |
|------|------|------|
| `setup-cron.sh` 脚本 | ❌ 弃用 | CLI 参数解析有多个 bug，不可靠 |
| `hermes cron create CLI` | ❌ 弃用 | prompt 位置参数被系统级 `-z` 参数干扰 |
| 手动 `hermes cron create ...` | ⚠️ 不推荐 | 参数复杂易错，不适合批量操作 |

**setup-cron.sh 保留但修改用途：** 改为**文档性质**的参考文件，记录每个 cronjob 的配置参数，不再作为可执行脚本。

### 2.4 DevOps Skill 修改建议

当前 DevOps Skill 的 prompt 中包含 GitHub Release 操作。建议增加网络检测步骤：

```
【DevOps Agent 执行流程】

Step 0: 检测 GitHub 连通性
  运行 python3 scripts/check-github.py
  输出: OK | DNS_HIJACKED | UNREACHABLE

Step 1: 如果 GitHub 不可达
  - 记录到 artifacts/reports/pending-github-ops.md
  - 跳过 GitHub 操作，只做本地操作（测试、文档）
  - 执行 runner --complete，outputs 注明待人工处理

Step 2: 如果 GitHub 可达
  - 正常执行 Release、Push 等操作
  - 执行 runner --complete
```

---

## 三、DevOps 正式执行环境方案

### 3.1 当前结论

DevOps Agent **可以在 WSL 内运行**，但 GitHub Release/Push 操作**受 iKuuuVPN 状态影响**。

### 3.2 推荐做法

1. **DevOps Agent 不依赖外部网络环境**
   - 本地操作（运行测试、创建 tag、生成 Release Notes）始终执行
   - GitHub Release 仅在连通性检测通过时执行
   - 不连通时记录到 `pending-github-ops.md`

2. **人工介入点**
   - 用户关闭 VPN 后，运行 `bash scripts/apply-pending-github-ops.sh` 批量执行未完成的 GitHub 操作
   - 或登录 gh CLI 后手动 `gh release create` 和 `git push`

3. **GitHub Token**
   - 当前 token 为 classic PAT，仅有 `repo` scope
   - 如需写入 `.github/workflows/`，需添加 `workflow` scope
   - 读取方式：`powershell.exe -Command "[Environment]::GetEnvironmentVariable('GITHUB_TOKEN_Classic', 'User')"`

---

## 四、变更记录

| 文件 | 变更 |
|------|------|
| `docs/ENVIRONMENT-NOTES.md` | 新增（本文档） |
| `orchestrator/setup-cron.sh` | 保留为文档参考，不再作为可执行入口 |

---

## 五、是否建议进入下一轮

**建议进入：最小监控面板 + 长跑前最终验收。**

前置条件：
- ✅ 红蓝调度对称性已验证
- ✅ runner / 状态机 / 判断层已可用
- ✅ 环境阻塞根因已定位
- ⚠️ DevOps GitHub 操作需优雅降级（建议在 DevOps Skill 中实现连通性检测）

下一轮重点：
1. 实现 DevOps Agent 的优雅降级（连通性检测 + 跳过 GitHub 操作）
2. 最小监控面板（cronjob last_status 可视化）
3. 长跑前最终验收清单
