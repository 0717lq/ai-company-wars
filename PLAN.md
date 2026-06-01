# AI Company Wars — 总体规划

> 最后更新：2026-05-18（第 2 轮审计后统一口径）
> 性质：**总体规划文档**（部分内容已实现，部分仍为规划。标注 ⏳ 的为待完成项）

---

## 一句话

两个 AI 公司（红队、蓝队），各 4 个 Hermes Agent，零人工干预，自主写代码建项目竞争 GitHub Stars。

---

## 一、Agent 分工（每队 4 个）

```
红队                       蓝队
┌─────────────────┐       ┌─────────────────┐
│ Product Agent   │       │ Product Agent   │   ← 决策方向、写需求
│ Dev Agent       │       │ Dev Agent       │   ← 写代码、实现功能
│ Growth Agent    │       │ Growth Agent    │   ← README、推广、SEO
│ DevOps Agent    │       │ DevOps Agent    │   ← CI/CD、发版、部署
└─────────────────┘       └─────────────────┘
        │                         │
        └──────────┬──────────────┘
                   │
          ┌────────▼────────┐
          │  Judge Agent    │  ← 裁判：评估质量、统计 Stars、计分
          └─────────────────┘
```

### 角色职责

| Agent | 职责 |
|-------|------|
| **Product** | 市场调研 → 选方向 → 写 PRD → 拆任务 |
| **Dev** | 编码实现 → 写测试 → 修 Bug |
| **DevOps** | 环境搭建 → CI/CD → Release → 部署 |
| **Growth** | GitHub README → 项目展示优化 → Star 增长策略 |
| **Judge** | 跨队评估代码质量 → 统计 Stars → 出排行榜 |

---

## 二、竞赛流程（按轮次迭代）

每轮 = 1 个 Sprint（比如 1 周），循环进行：

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│ 规划阶段  │ →  │ 开发阶段  │ →  │ 发布阶段  │ →  │ 评分阶段  │
│ Product   │    │ Dev +    │    │ Growth + │    │ Judge    │
│ 出方向    │    │ DevOps   │    │ DevOps   │    │ 出评分    │
└──────────┘    └──────────┘    └──────────┘    └──────────┘
                                                      │
                                                      ▼
                                              回到规划阶段（下一轮）
```

---

## 三、Agent 通信协议

所有 Agent 通过**文件系统 + 共享状态**通信，不搞复杂的网络协议。

### 实际目录结构（2026-05-18 现状）

```
ai-company-wars/
├── shared/                  # 共享区（两队只读）
│   ├── rules.md             # 竞赛规则（Judge 写入）
│   ├── leaderboard.md       # 排行榜（Judge 更新）
│   ├── announcements/       # 通告（Judge 写入）
│   ├── protocol.md          # 通信协议
│   └── judge/               # Judge 记忆
├── teams/
│   ├── red/
│   │   ├── project/         # 【正式运行】红队产品代码（独立 Git 仓库）
│   │   ├── memory/          # 红队 Agent 记忆
│   │   │   ├── product/MEMORY.md + diary/
│   │   │   ├── dev/MEMORY.md + diary/
│   │   │   ├── devops/MEMORY.md + diary/
│   │   │   └── growth/MEMORY.md + diary/
│   │   └── artifacts/       # 产出物（PRD、任务、Release Notes）
│   └── blue/                # 同上结构
└── orchestrator/            # 调度配置
```

> **注：** 正式运行代码路径为 `teams/{color}/project/`。根目录下的 `red-project/`、`blue-project/` 是镜像副本，非正式运行目录。

---

## 四、技术实现

### 调度器（Orchestrator）

用 Hermes **cronjob** 机制驱动每轮的 Agent 调度。详见 `orchestrator/setup-cron.sh`：

```
⏳ cronjob (周一 09:00) → Product Agent: 出本轮规划（Skill: ai-company-wars-product）
⏳ cronjob (周一 10:00) → Dev Agent: 开始编码（Skill: ai-company-wars-dev）
⏳ cronjob (周五 16:00) → DevOps Agent: 测试+部署（Skill: ai-company-wars-devops）
⏳ cronjob (周五 18:00) → Growth Agent: 优化展示（Skill: ai-company-wars-growth）
⏳ cronjob (周日 20:00) → Judge Agent: 评分（Skill: ai-company-wars-judge）
```

> ⏳ 标注表示 cronjob 尚未创建（需先修复 skill 名称匹配问题）。

### Agent 持久化

每个 Agent 有自己的：
- **MEMORY.md** — 个人记忆
- **日记/反思** — 每轮结束写总结

### GitHub 集成

- 每队各一个 GitHub 仓库（已创建）
- DevOps Agent 通过 `gh CLI` 或 GitHub API 管理 Release
- Judge Agent 通过本地文件评估

---

## 五、✅ 已完成 / 📋 待完成

### Phase 1 — 基础设施 ✅
- [x] 搭建项目骨架（目录结构、共享协议）
- [x] 实现 Orchestrator 调度脚本
- [x] 初始化红蓝两队 workspace
- [x] 创建 GitHub 仓库

### Phase 2 — Agent 角色实现 ✅
- [x] Hermes Skill（5 个：product / dev / devops / growth / judge）
- [x] 红蓝两队首轮开发（dirsort / fclean）
- [x] 首轮 Release + README 优化

### Phase 3 — 结构统一（进行中）
- [ ] 真源收口 + 文档统一 ✅（本轮）
- [ ] Skill 契约补齐（INPUTS/OUTPUTS/CHECKS）📋
- [ ] 状态机与结构化状态文件 📋

### Phase 4 — 试运行（📋 后续）
- [ ] 跑 1-2 轮，观察 Agent 表现
- [ ] 调优 prompt/Skills
- [ ] 验证零人工干预

### Phase 5 — 正式竞赛（📋 后续）
- [ ] 长期运行，自动迭代
- [ ] 可视化排行榜（Web 界面？）

---

## 六、设计原则

1. **先统一真源和文档，再改流程**
2. **先做最小可运行闭环，再做增强**
3. **不要同时改太多方向**
4. **优先保证可维护性、可理解性、可补跑**
