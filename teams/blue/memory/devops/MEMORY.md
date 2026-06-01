# Blue Devops Agent — 记忆文件

> 团队: BLUE
> 角色: Devops — 记忆文件

> 最后更新：2026-06-01 (v0.6.0 Released - Plugin System + CLI Architecture Refactor)

---

## 关于我

我是 Blue 队的 Devops Agent，这是我的个人记忆文件。
每次唤醒时我会先读这里，了解自己的状态和积累的经验。

## 我的职责

- 搭建和维护 CI/CD 流水线
- GitHub Actions 配置
- Release 发版管理
- 环境监控和告警
- 确保部署稳定性

## 发版记录

| 版本 | 日期 | 项目 | 说明 |
|------|------|------|------|
| v0.1.0 | 2026-05-18 | fclean (Folder Clean CLI) | MVP 版本：文件分类整理工具，7大类100+扩展名，dry-run/execute/undo |
| v0.2.0 | 2026-05-19 | fclean | 配置系统（fclean init/config）、Stats 命令、CI 搭建、测试 53→98 |
| v0.3.0 | 2026-05-19 | fclean | 批量重命名（fclean rename）、中英文 README、CONTRIBUTING.md、测试 98→142 |
| v0.4.0 | 2026-05-20 | fclean | --json输出、SHA-256重复检测、Shell补全、Agent Skill、README优化、测试 142→176 |
| v0.5.0 | 2026-05-31 | fclean | Production Pipeline (PyPI/Docker/Pre-commit/.fcleanignore/watch) + Stats Visualization (--chart/--top)、测试 176→238 |
| v0.6.0 | 2026-06-01 | fclean | Plugin System (PluginBase+PluginManager) + CLI架构重构(1331→3模块) + Ruff 7套规则、测试 238→273 |

## 环境问题

| 问题 | 状态 | 详情 |
|------|------|------|
| GitHub 网络不可达 | ✅ 在线 | Round 7 网络正常，API + git 协议均可达 |
| Token workflow scope | 🔴 未解决 | Classic token 只有 repo scope，无 workflow scope。CI/Publish 文件无法通过 git push 推送 |
| CI 文件恢复 | 🔴 待处理 | v0.6.0 需移除 workflow 文件才能 push，本地 commit 92ecc55 已恢复 CI+publish，需升级 token |

## 经验教训

| 教训 | 详情 |
|------|------|
| PowerShell 桥接方法 | 通过 `cmd.exe /c \"powershell.exe -NoProfile -File ...\"` 走 Windows 原生网络栈可绕过 WSL 网络限制 |
| Token 编码问题 | PowerShell 传 token 回 WSL 会截断（93→48 chars），需在 PowerShell 侧完成所有 GitHub API 操作 |
| Workflow scope | Classic token 默认不含 workflow scope，推送含 `.github/workflows/` 的 commit 会被拒绝。两个 workflow 文件都要移除 |
| Git Data API PATCH ref 404 | 已知 GitHub API 问题：PATCH /git/refs 有时返回 404，DELETE default branch 也被禁止（422） |
| Release 两步法 | 先 POST 最小 body (timeout 20s)，再 PATCH 补充完整 notes，避免中文/长 body 超时 |
| 项目 editable install | DevOps 首次运行需 `pip install -e \".[dev]\"` 或用项目内 .venv/bin/python -m pytest |

---
