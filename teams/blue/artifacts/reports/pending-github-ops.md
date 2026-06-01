# 待人工执行的 GitHub 操作

> 生成时间：2026-05-19
> 原因：GitHub API 无法完成 CI 文件恢复（token 缺少 `workflow` scope + PATCH ref 404）

## 问题描述

本地 commit `c1964cd`（restore: CI workflow）恢复 `.github/workflows/ci.yml` 文件，但无法推送到 GitHub。
两个尝试均失败：
1. **Contents API** → 404（`.github/workflows/` 路径需要 PAT 有 `workflow` scope）
2. **Git Data API** → commit 已创建（SHA: `73e0243ec6`），但 PATCH ref 返回 404（GitHub API 已知间歇性问题）

## 解决方案

### 方案 A：升级 Token（推荐）
在 GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic) 中给当前 token 添加 `workflow` 权限，然后执行：

```bash
cd /mnt/d/Desktop/hermes/ai-company-wars/teams/blue/project/
git push origin main
git push origin v0.3.1
```

### 方案 B：等待网络恢复后手动 push

```bash
cd teams/blue/project/
git push origin main
git push origin v0.3.1
```

## 本地状态
- 本地 tag `v0.3.1` 已指向 `c1964cd`（restore: CI workflow）
- 所有 142 个测试通过
- 代码仓库 clean（`teams/` 目录为外层 workspace 引用，不影响 fclean 项目）
