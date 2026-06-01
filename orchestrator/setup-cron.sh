#!/bin/bash
#
# ⚠️ 注意：此脚本已弃用，仅作参考。
#
# 正式调度接入方式请使用 Hermes cronjob 工具 API（cronjob action='create'），
# 详见 runtime/ENVIRONMENT-NOTES.md 第三节"正式调度接入方式定稿"。
#
# 弃用原因：
# 1. hermes cron create CLI 不接受 --schedule 命名参数（schedule 是位置参数）
# 2. prompt 作为位置参数被系统级 -z 参数干扰
# 3. * 被 bash 展开，需单引号保护
# 4. 已验证的稳定路径是 cronjob 工具 API
#
# 本脚本保留为文档参考，记录每个 cronjob 的完整配置参数。
# 不保证能成功执行。
#
# setup-cron.sh — AI Company Wars Cronjob 创建脚本（参考用）
# 
# 先决条件: Phase 2 的 Skills 已就绪
# 定义 9 个 cronjob 的配置参数，按 schedule.md 时间表驱动 Agent

set -e

BASE_DIR="$(cd "$(dirname "$0")/.." && pwd)"
ROUND_ID=$(python3 -c "import json; print(json.load(open('$BASE_DIR/runtime/round.json'))['round_id'])" 2>/dev/null || echo "UNKNOWN")

echo "=========================================="
echo "🤖 AI Company Wars — 创建 Cronjob 调度"
echo "=========================================="
echo ""
echo "Base dir: $BASE_DIR"
echo "Round ID: $ROUND_ID"
echo ""

# 确保 Skills 存在
check_skill() {
    local full_name="ai-company-wars-$1"
    if ! hermes skills list 2>/dev/null | grep -q "$full_name"; then
        echo "  ⚠️  Skill '$full_name' 尚未创建，跳过相关 cronjob"
        return 1
    fi
    return 0
}

# ============================================
# Product Agent (红队) — 周一 09:00
# ============================================
if check_skill "product"; then
    echo "  🔴 创建 Product Agent (红队) cronjob..."
    hermes cron create \
        "0 9 * * 1" \
        --name "acw-red-product" \
        --skill "ai-company-wars-product" \
        --workdir "$BASE_DIR" \
        "我是红队 Product Agent。今天周一，本周 Sprint 开始了。

【先运行 runner 状态检查】
python3 scripts/run-round.py --team red --role product --round $ROUND_ID
如果返回 BLOCKED 或 SKIPPED，记录到日记后退出。

【如果 CAN_RUN】才继续以下步骤：
1. 读取 teams/red/memory/product/MEMORY.md 了解我的记忆
2. 搜索 GitHub Trending 了解当前热点
3. 制定本周产品方向，输出 PRD 到 teams/red/artifacts/prd/
4. 将开发任务拆分，写入 teams/red/artifacts/tasks.md
5. 写日记到 teams/red/memory/product/diary/
6. 运行完成回写: python3 scripts/run-round.py --team red --role product --round $ROUND_ID --complete"
fi

# ============================================
# Product Agent (蓝队) — 周一 09:00
# ============================================
if check_skill "product"; then
    echo "  🔵 创建 Product Agent (蓝队) cronjob..."
    hermes cron create \
        "0 9 * * 1" \
        --name "acw-blue-product" \
        --skill "ai-company-wars-product" \
        --workdir "$BASE_DIR" \
        "我是蓝队 Product Agent。今天周一，本周 Sprint 开始了。

【先运行 runner 状态检查】
python3 scripts/run-round.py --team blue --role product --round $ROUND_ID
如果返回 BLOCKED 或 SKIPPED，记录到日记后退出。

【如果 CAN_RUN】才继续以下步骤：
1. 读取 teams/blue/memory/product/MEMORY.md 了解我的记忆
2. 搜索 GitHub Trending 了解当前热点
3. 制定本周产品方向，输出 PRD 到 teams/blue/artifacts/prd/
4. 将开发任务拆分，写入 teams/blue/artifacts/tasks.md
5. 写日记到 teams/blue/memory/product/diary/
6. 运行完成回写: python3 scripts/run-round.py --team blue --role product --round $ROUND_ID --complete"
fi

# ============================================
# Dev Agent (红队) — 周一 10:00
# ============================================
if check_skill "dev"; then
    echo "  🔴 创建 Dev Agent (红队) cronjob..."
    hermes cron create \
        "0 10 * * 1" \
        --name "acw-red-dev" \
        --skill "ai-company-wars-dev" \
        --workdir "$BASE_DIR" \
        "我是红队 Dev Agent。新的一周开始了！

【先运行 runner 状态检查】
python3 scripts/run-round.py --team red --role dev --round $ROUND_ID
如果返回 BLOCKED 或 SKIPPED，记录到日记后退出。

【如果 CAN_RUN】才继续以下步骤：
1. 读取 teams/red/memory/dev/MEMORY.md 了解我的记忆
2. 读取 teams/red/artifacts/prd/ 下最新的 PRD
3. 在 teams/red/project/ 中开始编码实现
4. 使用 conventional commit 提交代码
5. 写日记到 teams/red/memory/dev/diary/
6. 运行完成回写: python3 scripts/run-round.py --team red --role dev --round $ROUND_ID --complete"
fi

# ============================================
# Dev Agent (蓝队) — 周一 10:00
# ============================================
if check_skill "dev"; then
    echo "  🔵 创建 Dev Agent (蓝队) cronjob..."
    hermes cron create \
        "0 10 * * 1" \
        --name "acw-blue-dev" \
        --skill "ai-company-wars-dev" \
        --workdir "$BASE_DIR" \
        "我是蓝队 Dev Agent。新的一周开始了！

【先运行 runner 状态检查】
python3 scripts/run-round.py --team blue --role dev --round $ROUND_ID
如果返回 BLOCKED 或 SKIPPED，记录到日记后退出。

【如果 CAN_RUN】才继续以下步骤：
1. 读取 teams/blue/memory/dev/MEMORY.md 了解我的记忆
2. 读取 teams/blue/artifacts/prd/ 下最新的 PRD
3. 在 teams/blue/project/ 中开始编码实现
4. 使用 conventional commit 提交代码
5. 写日记到 teams/blue/memory/dev/diary/
6. 运行完成回写: python3 scripts/run-round.py --team blue --role dev --round $ROUND_ID --complete"
fi

# ============================================
# DevOps Agent (红队) — 周五 16:00
# ============================================
if check_skill "devops"; then
    echo "  🔴 创建 DevOps Agent (红队) cronjob..."
    hermes cron create \
        "0 16 * * 5" \
        --name "acw-red-devops" \
        --skill "ai-company-wars-devops" \
        --workdir "$BASE_DIR" \
        "我是红队 DevOps Agent。周五了，该发版了！

【先运行 runner 状态检查】
python3 scripts/run-round.py --team red --role devops --round $ROUND_ID
如果返回 BLOCKED 或 SKIPPED，记录到日记后退出。

【如果 CAN_RUN】才继续以下步骤：
1. 读取 teams/red/memory/devops/MEMORY.md
2. 检查 teams/red/project/ 代码状态
3. 运行测试，确保通过
4. 创建 GitHub Release
5. 写日记到 teams/red/memory/devops/diary/
6. 运行完成回写: python3 scripts/run-round.py --team red --role devops --round $ROUND_ID --complete"
fi

# ============================================
# DevOps Agent (蓝队) — 周五 16:00
# ============================================
if check_skill "devops"; then
    echo "  🔵 创建 DevOps Agent (蓝队) cronjob..."
    hermes cron create \
        "0 16 * * 5" \
        --name "acw-blue-devops" \
        --skill "ai-company-wars-devops" \
        --workdir "$BASE_DIR" \
        "我是蓝队 DevOps Agent。周五了，该发版了！

【先运行 runner 状态检查】
python3 scripts/run-round.py --team blue --role devops --round $ROUND_ID
如果返回 BLOCKED 或 SKIPPED，记录到日记后退出。

【如果 CAN_RUN】才继续以下步骤：
1. 读取 teams/blue/memory/devops/MEMORY.md
2. 检查 teams/blue/project/ 代码状态
3. 运行测试，确保通过
4. 创建 GitHub Release
5. 写日记到 teams/blue/memory/devops/diary/
6. 运行完成回写: python3 scripts/run-round.py --team blue --role devops --round $ROUND_ID --complete"
fi

# ============================================
# Growth Agent (红队) — 周五 18:00
# ============================================
if check_skill "growth"; then
    echo "  🔴 创建 Growth Agent (红队) cronjob..."
    hermes cron create \
        "0 18 * * 5" \
        --name "acw-red-growth" \
        --skill "ai-company-wars-growth" \
        --workdir "$BASE_DIR" \
        "我是红队 Growth Agent。本周发布了新版本！

【先运行 runner 状态检查】
python3 scripts/run-round.py --team red --role growth --round $ROUND_ID
如果返回 BLOCKED 或 SKIPPED，记录到日记后退出。

【如果 CAN_RUN】才继续以下步骤：
1. 读取 teams/red/memory/growth/MEMORY.md
2. 检查 teams/red/project/ 的最新 Release
3. 优化 README（添加新功能说明、GIF demo）
4. 检查 GitHub Topics 和 About 设置
5. 写日记到 teams/red/memory/growth/diary/
6. 运行完成回写: python3 scripts/run-round.py --team red --role growth --round $ROUND_ID --complete"
fi

# ============================================
# Growth Agent (蓝队) — 周五 18:00
# ============================================
if check_skill "growth"; then
    echo "  🔵 创建 Growth Agent (蓝队) cronjob..."
    hermes cron create \
        "0 18 * * 5" \
        --name "acw-blue-growth" \
        --skill "ai-company-wars-growth" \
        --workdir "$BASE_DIR" \
        "我是蓝队 Growth Agent。本周发布了新版本！

【先运行 runner 状态检查】
python3 scripts/run-round.py --team blue --role growth --round $ROUND_ID
如果返回 BLOCKED 或 SKIPPED，记录到日记后退出。

【如果 CAN_RUN】才继续以下步骤：
1. 读取 teams/blue/memory/growth/MEMORY.md
2. 检查 teams/blue/project/ 的最新 Release
3. 优化 README（添加新功能说明、GIF demo）
4. 检查 GitHub Topics 和 About 设置
5. 写日记到 teams/blue/memory/growth/diary/
6. 运行完成回写: python3 scripts/run-round.py --team blue --role growth --round $ROUND_ID --complete"
fi

# ============================================
# Judge Agent — 周日 20:00
# ============================================
if check_skill "judge"; then
    echo "  ⚖️ 创建 Judge Agent cronjob..."
    hermes cron create \
        "0 20 * * 0" \
        --name "acw-judge" \
        --skill "ai-company-wars-judge" \
        --workdir "$BASE_DIR" \
        "我是 Judge Agent。周末了，该评分了！

【先运行 runner 状态检查】
python3 scripts/run-round.py --team red --role judge --round $ROUND_ID
如果返回 BLOCKED 或 SKIPPED，记录到日记后退出。

【如果 CAN_RUN】才继续以下步骤：
1. 读取 shared/rules.md 确认评分规则
2. 拉取红队 GitHub 仓库的 Stars + 代码数据
3. 拉取蓝队 GitHub 仓库的 Stars + 代码数据
4. 按评分维度打分，更新 shared/leaderboard.md
5. 写出本周评语到 shared/announcements/
6. 写日记
7. 运行完成回写: python3 scripts/run-round.py --team red --role judge --round $ROUND_ID --complete"
fi

echo ""
echo "=========================================="
echo "✅ Cronjob 创建完成！"
echo "=========================================="
echo ""
echo "运行 'hermes cron list' 查看所有调度任务"
