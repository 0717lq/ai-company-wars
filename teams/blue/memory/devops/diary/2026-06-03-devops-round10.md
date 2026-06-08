---
date: 2026-06-03
role: devops
team: blue
round: 10
---

# Round 10 DevOps 日记

## 今天做了什么

### rag-builder v0.3.0 发版

1. **环境预检** — GitHub 在线模式（check-github.py exit 0）
2. **代码检查** — ready-for-deploy.md v0.3.0 存在，GitHub 最新 release 为 v0.1.0，确认为新代码
3. **测试运行** — 172 个测试全部通过（1.38s）
4. **代码推送** — 2 个 commit 推送到 origin/main（旧 classic token 失效，改用 fine-grained token）
5. **Tag 推送** — v0.3.0 tag 已存在于远程（之前 session 可能已推过）
6. **Release 创建** — v0.3.0 Release 已存在于 GitHub
7. **清理** — 清空 ready-for-deploy.md，恢复 remote URL（移除 token）

## 发版信息

- 版本: v0.3.0
- 内容: diagnose 命令、SKILL.md 拆分、batch bug 修复
- GitHub: https://github.com/0717lq/ai-company-wars-blue/releases/tag/v0.3.0

## 经验教训

- 经典 PAT (ghp_*) 持续不可用，fine-grained PAT 正常
- Git push 直接成功（在线模式），无需 PowerShell 桥接
