#!/bin/bash
#
# init-workspace.sh — AI Company Wars Agent Workspace 初始化脚本
# 用法: ./scripts/init-workspace.sh
#

set -e

BASE_DIR="$(cd "$(dirname "$0")/.." && pwd)"
TEAMS_DIR="$BASE_DIR/teams"
DATE_NOW=$(date +%Y-%m-%d)

echo "🧹 清理已有 Agent 记忆目录..."
for team in red blue; do
    for role in product dev growth devops; do
        rm -rf "$TEAMS_DIR/$team/memory/$role"
    done
done

echo "🏗️  创建 Agent 记忆目录..."

gen_memory() {
    local team=$1 role=$2 dir="$TEAMS_DIR/$team/memory/$role"
    mkdir -p "$dir/diary"

    local cap_team="${team^}" cap_role="${role^}"

    {
        echo "# ${cap_team} ${cap_role} Agent — 记忆文件"
        echo ""
        echo "> 初始化时间：$DATE_NOW"
        echo "> 角色：${cap_team}队 - ${cap_role}"
        echo ""
        echo "---"
        echo ""
        echo "## 关于我"
        echo ""
        echo "我是 ${cap_team} 队的 ${cap_role} Agent，这是我的个人记忆文件。"
        echo "每次唤醒时我会先读这里，了解自己的状态和积累的经验。"
        echo ""
        echo "## 我的职责"
        echo ""

        case "$role" in
            product)
                echo "- 调研市场趋势和竞品动态"
                echo "- 制定产品方向和策略"
                echo "- 编写 PRD（产品需求文档）"
                echo "- 将任务拆分给 Dev Agent"
                echo "- 分析用户反馈，迭代产品方案"
                ;;
            dev)
                echo "- 根据 PRD 实现功能"
                echo "- 编写测试，保证质量"
                echo "- 修复 Bug"
                echo "- 优化性能和架构"
                echo "- 使用 convention 的 commit message 提交"
                echo "- 维护代码可读性和可维护性"
                ;;
            growth)
                echo "- 撰写和优化 README"
                echo "- 设置 GitHub Topics、About、Website"
                echo "- 在社区推广项目"
                echo "- 分析 Star 增长数据"
                echo "- 提出增长策略建议"
                ;;
            devops)
                echo "- 搭建和维护 CI/CD 流水线"
                echo "- GitHub Actions 配置"
                echo "- Release 发版管理"
                echo "- 环境监控和告警"
                echo "- 确保部署稳定性"
                ;;
        esac

        {
            echo ""
            echo "## 经验教训"
            echo ""
            echo "_（每次迭代后记录学到的教训）_"
            echo ""
            echo "## 技能清单"
            echo ""
            echo "_（记录自己掌握的技能和工具）_"
            echo ""
            echo "---"
            echo "*最后更新：$DATE_NOW*"
        }
    } > "$dir/MEMORY.md"

    echo "  ✅ ${cap_team} ${cap_role} → $dir"
}

for team in red blue; do
    for role in product dev growth devops; do
        gen_memory "$team" "$role"
    done
done

echo ""
echo "📋 为 Judge Agent 创建目录..."
mkdir -p "$BASE_DIR/shared/announcements"

if [ ! -f "$BASE_DIR/shared/announcements/README.md" ]; then
    cat > "$BASE_DIR/shared/announcements/README.md" << 'EOF'
# 通告索引

Judge Agent 在这里发布每周通告。

## 格式

YYYY-MM-DD-week-N.md
EOF
fi

echo "📊 创建空排行榜文件..."
cat > "$BASE_DIR/shared/leaderboard.md" << 'EOF'
# AI Company Wars — 排行榜

_等待第一轮评分..._

EOF

echo ""
echo "=========================================="
echo "✅ Workspace 初始化完成！"
echo "=========================================="
echo ""
echo "共创建了 8 个 Agent 的记忆空间："
echo "  🔴 红队: Product, Dev, Growth, DevOps"
echo "  🔵 蓝队: Product, Dev, Growth, DevOps"
echo "  ⚖️  Judge: shared/announcements/ + shared/leaderboard.md"
echo ""
echo "目录结构："
find "$TEAMS_DIR" -name "MEMORY.md" | sort
