# Blue Devops Agent — 记忆文件

> 团队: BLUE
> 角色: Devops — 记忆文件

> 最后更新：2026-06-03 (v0.1.0 Released — RAG Builder Skill)

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
| v0.1.0 | 2026-06-03 | rag-builder (RAG Builder Skill) | RAG pipeline 构建指南+工具包。SKILL.md 12章节、config_schema/scaffold/benchmark/cli、78测试 |
| v0.3.0 | 2026-06-03 | rag-builder | diagnose 命令（4维检查）、SKILL.md 拆分（774→221行+6个references）、batch bug 修复、172测试 |
| v0.4.0 | 2026-06-03 | rag-builder | N803命名修复、vector_store 100%覆盖率、集成测试14个、207测试 |

## 环境问题

| 问题 | 状态 | 详情 |
|------|------|------|
| GitHub 网络 | ⚠️ 半在线 | check-github.py exit 0 但 git push 超时，用 Git Data API 推送成功 |
| Classic Token | 🔴 失效 | GITHUB_TOKEN_Classic (ghp_*) 返回 401 Bad credentials，已不可用 |
| Fine-grained Token | ✅ 可用 | GITHUB_TOKEN (github_pat_*, 93 chars) 正常，有 admin/push 权限 |
| Token workflow scope | 🔴 未解决 | Classic token 已失效，Fine-grained token 权限待确认 |

## 经验教训

| 教训 | 详情 |
|------|------|
| Classic token 失效 | 2026-06-03 发现 GITHUB_TOKEN_Classic 返回 401，改用 GITHUB_TOKEN (fine-grained) |
| Git Data API 推送可靠 | 16 文件用 Git Data API (blob+tree+commit+ref) 推送成功，约 24s |
| PowerShell git 超时 | 半在线模式下 PowerShell git push 也 120s 超时，只有 REST API 可用 |
| 新项目无 remote | 首次发版需先 git remote add，再用 API 推送 |

---
