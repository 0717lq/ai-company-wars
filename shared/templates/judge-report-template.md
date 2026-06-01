---
round_id: ""        # 必填
judged_at: ""       # ISO 时间戳
author: "judge"
---

# 裁判报告 — {round_id}

---

## 队伍状态摘要

| 维度 | 🔴 红队 | 🔵 蓝队 |
|------|---------|---------|
| Product | {completed / failed / skipped} | {completed / failed / skipped} |
| Dev | {completed / failed / skipped / blocked} | {completed / failed / skipped / blocked} |
| DevOps | {completed / failed / skipped} | {completed / failed / skipped} |
| Growth | {completed / failed / skipped} | {completed / failed / skipped} |
| **本轮状态** | **{正常 / 异常}** | **{正常 / 异常}** |

## 评分依据

### 红队
- 代码量：{N} 行（src）+ {N} 行（tests）
- 测试：{N} 个用例，{N} 通过
- README：{评价}
- Release：{版本号}/{发布日期}
- 代码注释：{评价}

### 蓝队
- 代码量：{N} 行（src）+ {N} 行（tests）
- 测试：{N} 个用例，{N} 通过
- README：{评价}
- Release：{版本号}/{发布日期}
- 代码注释：{评价}

## 评分结果

| 队伍 | 代码量 (10) | 代码质量 (10) | 功能完整 (10) | 项目展示 (10) | 总分 (40) |
|------|------------|-------------|-------------|-------------|----------|
| 🔴 红队 | {N} | {N} | {N} | {N} | {N} |
| 🔵 蓝队 | {N} | {N} | {N} | {N} | {N} |

> 评分维度权重：代码量=25%，代码质量=25%，功能完整性=25%，项目展示=25%
> （首轮 Stars=0 时，不参与评分，权重均分到其他四项）

## 亮点与不足

### 🔴 红队
- **亮点**: {亮点1}
- **亮点**: {亮点2}
- **不足**: {不足1}
- **不足**: {不足2}

### 🔵 蓝队
- **亮点**: {亮点1}
- **亮点**: {亮点2}
- **不足**: {不足1}
- **不足**: {不足2}

## 失败/未完成队伍说明

{如果一队有角色 failed/blocked/skipped，在这里说明原因和处理方式}

## 本轮结论

{总结性评语}

## Leaderboard 更新

已更新 `shared/leaderboard.md`。

---

*由 Judge Agent 自动生成 | {round_id}*
