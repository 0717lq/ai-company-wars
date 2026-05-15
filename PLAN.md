# AI Company Wars — 总体规划

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
| **Growth** | GitHub README → 项目展示优化 → Star 增长策略 |
| **DevOps** | 环境搭建 → CI/CD → Release → 部署 |
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

所有 Agent 通过**文件系统 + 共享状态**通信，不搞复杂的网络协议：

```
workspace/
├── shared/                  # 共享区
│   ├── rules.md             # 竞赛规则（裁判写入）
│   ├── leaderboard.md       # 排行榜（裁判更新）
│   └── announcements/       # 通告
├── red/
│   ├── project/             # 红队开发的产品代码
│   ├── memory/              # 红队记忆文件
│   │   ├── MEMORY.md
│   │   └── SKILLS/
│   └── artifacts/           # 产出物（PRD、设计文档）
└── blue/
    ├── project/
    ├── memory/
    └── artifacts/
```

---

## 四、技术实现

### 调度器（Orchestrator）

用 **cronjob** 机制驱动每轮的 Agent 调度：

```
cronjob 1 (每日 09:00) → Product Agent: 出本轮规划
cronjob 2 (每日 10:00) → Dev Agent: 开始编码
cronjob 3 (每日 16:00) → DevOps Agent: 测试+部署
cronjob 4 (每日 18:00) → Growth Agent: 优化展示
cronjob 5 (每周日 20:00) → Judge Agent: 评分
```

每个 cronjob 加载对应 Agent 的 Skills + 记忆，自主决策。

### Agent 持久化

每个 Agent 有自己的：
- **MEMORY.md** — 个人记忆
- **SKILL.md** — 积累的技能（通过 skill_manage 持久化）
- **日记/反思** — 每轮结束写总结

### GitHub 集成

- 每队各一个 GitHub 仓库（自动创建）
- DevOps Agent 通过 `gh CLI` 管理 PR、Release
- Judge Agent 通过 GitHub API 拉 Stars 数据

---

## 五、MVP 路线

### Phase 1 — 基础设施
- [ ] 搭建项目骨架（目录结构、共享协议）
- [ ] 实现 Orchestrator 调度脚本
- [ ] 初始化红蓝两队 workspace
- [ ] 创建 GitHub 仓库

### Phase 2 — Agent 角色实现
- [ ] Product Agent Skills（市场调研、写 PRD）
- [ ] Dev Agent Skills（编码、测试）
- [ ] Growth Agent Skills（README、SEO）
- [ ] DevOps Agent Skills（CI/CD、发版）
- [ ] Judge Agent Skills（评分算法）

### Phase 3 — 试运行
- [ ] 跑 1-2 轮，观察 Agent 表现
- [ ] 调优 prompt/Skills
- [ ] 验证零人工干预

### Phase 4 — 正式竞赛
- [ ] 长期运行，自动迭代
- [ ] 可视化排行榜（Web 界面？）

---

## 六、需要你确认的点

1. **每轮周期** — 建议 1 周一轮，还是更短（3 天）？
2. **项目类型** — 两队自己做同一类型的项目竞争，还是自由发挥？
3. **GitHub 账号** — 用你的账号还是单独创建机器人账号？
4. **Stars 目标** — 纯竞争看谁多，还是设具体的 KPI（比如四周内达到 100 Stars）？
