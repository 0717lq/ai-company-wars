# fclean v0.6.0 — Plugin System + CLI Architecture Refactor

> 日期：2026-06-01
> 轮次：AI Company Wars Round 7
> 团队：Blue

## 新功能

### 🔌 插件系统 (P0)
- **PluginBase** 抽象基类：`classify`（必须）+ `transform`（可选）+ `summarize`（可选）
- **PluginManager**：加载/注册/执行/安装/卸载/列出插件
- CLI 子命令：`fclean plugin list/install/create/info/uninstall`
- 所有 plugin 子命令支持 `--json` 输出
- **差异化 hook**：`transform`（自定义移动目标）和 `summarize`（自定义报告）是红队没有的能力

### 📐 CLI 架构重构 (P1)
- `cli.py` 从 1331 行拆分为 3 个模块：
  - `cli.py` (~447 行): 参数解析 + main()
  - `commands.py` (~689 行): 命令执行逻辑
  - `formatters.py` (~380 行): 输出格式化
- 消除上帝文件，职责清晰分离

### ⚙️ Ruff 配置升级 (P1)
- 4 套规则 → 7 套（新增 N/命名规范、UP/pyupgrade、B/bugbear）
- 修复所有 B904/B007/UP015 问题

## 测试

- **总测试数**: 273 个（全部通过）
- **新增**: 35 个（test_plugin.py）
- **测试文件**: 13 个
- **Ruff**: All checks passed!

## 变更清单

```
新增: src/fclean/plugin.py (84行)
新增: src/fclean/plugin_manager.py (275行)
新增: src/fclean/commands.py (689行)
新增: src/fclean/formatters.py (380行)
重写: src/fclean/cli.py (1331→447行, 拆分)
修改: src/fclean/__init__.py (版本号 0.5.0→0.6.0)
修改: src/fclean/dupes.py (B904/B007 修复)
修改: src/fclean/organizer.py (B904 修复)
修改: src/fclean/stats_viz.py (B007 修复)
修改: pyproject.toml (版本号 + Ruff 7套规则)
新增: tests/test_plugin.py (35个测试)
修改: tests/test_cli.py (版本号断言更新)
修改: CHANGELOG.md (v0.6.0 条目)
新增: docs/STRUCTURE.md, docs/FILES.md, docs/CODE.md
```

## 已知问题

- CI workflow 文件（ci.yml、publish.yml）因 PAT 缺少 `workflow` scope 无法推送到远程，本地已恢复待后续推送
- PyPI 发布需配置 Trusted Publisher
