# AI Company Wars — 最小治理边界

> 版本：v1.0
> 更新日期：2026-05-18
> 性质：治理规则摘要，不代替 `shared/rules.md`

---

## 一、Growth Agent 治理边界

### ✅ 允许（可自动执行）

| 动作 | 约束 |
|------|------|
| 编辑 README.md | 必须基于真实功能 |
| 创建/更新 LICENSE | MIT License，不覆盖已有自定义 License |
| 创建 CI workflow | `.github/workflows/ci.yml` |
| 更新 pyproject.toml metadata | description / keywords / classifiers / urls |
| 写外部推广文案草稿 | **只写入日记，不自动发布** |

### ⚠️ 灰区（需人工确认）

| 动作 | 原因 |
|------|------|
| 发布外部推广帖（Reddit/V2EX/Twitter） | 内容质量、时间、语气需要人判断 |
| 修改项目名或仓库设置 | 影响太广 |
| 移除/重写核心功能描述 | 可能误导用户 |
| 为项目申请 PyPI 发布 | 涉及外部账号权限 |

### ❌ 禁止

| 动作 | 说明 |
|------|------|
| 自动批量发帖 | 任何平台 |
| 自动评论其他项目 | 无论是正向还是负向 |
| 自动私信 | 拉人/宣传 |
| 刷 Star / Fork / Watch | 任何形式 |
| 修改对方队伍文件 | 违反规则 |
| 修改 `shared/rules.md` | 规则由 Judge 维护 |
| 发行 Release | 只读，不做 |

---

## 二、Judge Agent 治理边界

### ✅ 允许

| 动作 | 约束 |
|------|------|
| 读取两队代码/测试/文档 | 基于本地文件 |
| 更新 leaderboard.md | 每轮更新 |
| 写通告到 announcements/ | 含亮点和不足 |
| 标记队伍状态 | failed / completed / N/A |
| 使用 GitHub API 读 Stars | （如果有 token） |

### 失败队伍处理

| 场景 | 处理方式 |
|------|---------|
| 一队完成，一队 failed | ✅ 正常评分。failed 队伍各维度记 0 分，点评中说明原因 |
| 一队完成，一队 skipped | ✅ 正常评分。skipped 队伍用上轮数据或标注「本轮跳过」 |
| 一队完成，一队 blocked | ✅ 正常评分。blocked 队伍标注阻塞原因 |
| 两队均 failed | ❌ 无法评分，round 标记异常，建议离青介入 |

### ❌ 禁止

| 动作 | 说明 |
|------|------|
| 修改 `shared/rules.md` 评分权重 | 规则修改需离青确认 |
| 偏袒某一队伍 | 评分必须有依据 |
| 不验证输出内容 | 必须 read_file 确认 |
| 修改 teams/ 下文件 | 只写 shared/ |
| 基于幻觉数据评分 | 数据必须实际读取 |
| 修改 `runtime/` 下文件 | 由 runner 维护 |

---

## 三、团队间边界

### 数据隔离

| 内容 | 读权限 | 写权限 |
|------|--------|--------|
| 本队 project/ | 本队全部角色 | 本队 Product + Dev + Growth |
| 本队 memory/ | 本队全部角色 | 本队各角色各自 |
| 本队 artifacts/ | 本队全部角色 + Judge | Product + Dev + DevOps |
| 对方队伍目录 | ❌ 禁止 | ❌ 禁止 |
| shared/ (除 rules/leaderboard) | 全部 | Judge |
| runtime/ | 全部 | Runner（未实现） |

---

## 四、Round 状态与治理的关系

```
PLANNING:       只有 Product 写 artifacts/
DEVELOPMENT:    只有 Dev 写 project/src/ + tests/
RELEASING:      只有 DevOps 操作 Git/GitHub
PROMOTING:      只有 Growth 写 README/docs/
JUDGING:        只有 Judge 写 shared/leaderboard + announcements
ROUND_CLOSED:   所有写入关闭
```

每个阶段的角色都只能在该阶段窗口内写入对应路径。越权即自动标记为违规。

---

*本摘要与 `shared/rules.md`、各角色 CHECKS.md 保持一致。*
