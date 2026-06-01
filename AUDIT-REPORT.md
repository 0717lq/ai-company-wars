# AI Company Wars — 第 1 轮审计报告

> 审计日期：2026-05-18
> 审计方式：文件扫描 + 文档对照，不动任何文件

---

## 一、项目结构图谱（现状）

### 1.1 实际目录结构（真实存在的文件）

```
ai-company-wars/
├── DOCS.md                  ← 总体目录说明
├── PLAN.md                  ← 总体规划
├── .gitignore
├── orchestrator/
│   ├── schedule.md          ← 调度时间表
│   └── setup-cron.sh        ← Cronjob 创建脚本
├── scripts/
│   └── init-workspace.sh    ← Workspace 初始化脚本
├── skills/
│   └── dev-agent-draft.md   ← 草稿（历史遗留）
├── shared/
│   ├── protocol.md          ← 通信协议
│   ├── rules.md             ← 竞赛规则
│   ├── leaderboard.md       ← 排行榜
│   ├── announcements/
│   │   ├── README.md
│   │   └── round-1.md
│   └── judge/               ← 空目录（judge/diary/ 和 judge/memory/）
│       ├── diary/           ← 空
│       └── memory/          ← 空
└── teams/
    ├── red/
    │   ├── artifacts/
    │   │   ├── PRD.md              ← 旧格式：单文件
    │   │   ├── current-sprint.md   ← 旧格式：sprint 任务
    │   │   ├── handover-to-dev.md
    │   │   └── release-notes.md
    │   ├── memory/
    │   │   ├── product/MEMORY.md + diary/
    │   │   ├── dev/MEMORY.md + diary/
    │   │   ├── devops/MEMORY.md + diary/
    │   │   └── growth/MEMORY.md + diary/
    │   └── project/                ← 独立 Git 仓库（已推送 GitHub）
    │       ├── src/dirsort/
    │       ├── tests/
    │       └── ...
    └── blue/
        ├── artifacts/
        │   ├── prd/                ← 新格式：日期化子目录
        │   │   └── 2026-05-18-fclean-prd.md
        │   ├── tasks.md            ← 新格式
        │   ├── handover-to-dev.md
        │   ├── ready-for-deploy.md
        │   ├── release-notes.md
        │   ├── designs/            ← 蓝队特有
        │   └── reports/            ← 蓝队特有
        ├── memory/                 ← 同红队结构
        └── project/                ← 独立 Git 仓库
            ├── src/fclean/
            ├── tests/
            └── ...

### 镜像目录（冗余）
/mnt/d/Desktop/hermes/
├── red-project/                   ← 无 .git，内容的子集
└── blue-project/                  ← 无 .git，内容的子集

### Hermes 系统技能
~/.hermes/skills/ai-company-wars/
├── ai-company-wars-product/SKILL.md
├── ai-company-wars-dev/SKILL.md
├── ai-company-wars-devops/SKILL.md
├── ai-company-wars-growth/SKILL.md
└── ai-company-wars-judge/SKILL.md
```

---

## 二、冲突点清单

### 🔴 冲突 1（严重）：三套 project 路径认知

| 来源 | 路径 | 状态 |
|------|------|------|
| 实际主数据 | `teams/red/project/` | ✅ 有完整数据、Git 历史 |
| Hermes Skill | `/mnt/d/Desktop/hermes/red-project/` | ❌ 指向镜像，无 Git |
| DOCS.md | `red-project/`（根目录） | ❌ 指向根目录 |

**影响**：Agent 启动后去 `/mnt/d/Desktop/hermes/red-project/` 干活，但代码实际在 `teams/red/project/` 里。Agent 要么找不到代码，要么在空的镜像目录里瞎忙。

---

### 🔴 冲突 2（严重）：Hermes Skill 名称不匹配

| 真实 Skill 名称 | schedule.md 引用名 | setup-cron.sh 检测名 |
|-----------------|-------------------|---------------------|
| `ai-company-wars-product` | `product-agent` | `product-agent` |
| `ai-company-wars-dev` | `dev-agent` | `dev-agent` |
| `ai-company-wars-devops` | `devops-agent` | `devops-agent` |
| `ai-company-wars-growth` | `growth-agent` | `growth-agent` |
| `ai-company-wars-judge` | `judge-agent` | `judge-agent` |

**影响**：`setup-cron.sh` 执行 `hermes skill list | grep "dev-agent"` 会找不到任何技能。所有 cronjob 都会跳过创建。

---

### 🔴 冲突 3（中）：红蓝两队 artifact 命名不一致

| 维度 | 红队（旧格式） | 蓝队（新格式） | 协议要求 |
|------|---------------|---------------|---------|
| PRD | `artifacts/PRD.md`（单文件，大写） | `artifacts/prd/2026-05-18-*-prd.md`（子目录+日期） | `artifacts/prd/YYYY-MM-DD-*-prd.md` |
| Sprint 任务 | `artifacts/current-sprint.md` | `artifacts/tasks.md` | 未明确规定 |
| 子目录 | 无 designs/、reports/ | 有 designs/、reports/ | 有 designs/、reports/ |

**影响**：产品/开发流程断档。Red 的 Dev Agent 去 artifacts/ 下找 `tasks.md` 找不到。

---

### 🔴 冲突 4（中）：DOCS.md 与实际结构严重脱节

DOCS.md 目录树中写的是：
```
red-project/    ← 根目录下直接放
blue-project/   ← 根目录下直接放
```
但实际是：
```
teams/red/project/
teams/blue/project/
```
DOCS.md 甚至没有出现 `teams/` 目录名。

---

### 🔴 冲突 5（中）：PLAN.md 与 protocol.md 结构描述不符

PLAN.md（第 61-76 行）描述的结构：
```
workspace/
├── shared/
├── red/          ← 无 teams/ 前缀
│   ├── project/
│   ├── memory/
│   └── artifacts/
└── blue/
```
protocol.md（第 10-36 行）描述的结构：
```
ai-company-wars/
├── teams/
│   ├── red/      ← 有 teams/ 前缀
│   └── blue/
```

两套目录结构差一层 `teams/`。

---

### 🔴 冲突 6（中）：Hermes Skill 中硬编码的旧路径

5 个 Hermes Skill 全部在 prompt 中写死了 `/mnt/d/Desktop/hermes/red-project/` 和 `/mnt/d/Desktop/hermes/blue-project/`，但实际代码在 `teams/` 下。

---

### 🔴 冲突 7（低）：Judge 目录准备不完整

protocol.md 和 Judge Skill 引用 `shared/judge/memory/MEMORY.md` 和 `shared/judge/diary/`，但这两个目录虽然存在，内容是空的。没有 MEMORY.md 文件。

---

### 🔴 冲突 8（低）：`skills/dev-agent-draft.md` 孤立

`ai-company-wars/skills/dev-agent-draft.md` 是一个旧版的 Dev Agent 草稿，未被任何系统引用。其内容和 Hermes 系统里的 `ai-company-wars-dev/SKILL.md` 重复且更简略。

---

## 三、现状 vs 规划 辨识

| 文件 | 描述的是 |
|------|---------|
| `shared/protocol.md` | ✅ **现状**（约定当前结构） |
| `shared/rules.md` | ✅ **现状**（当前竞赛规则） |
| `shared/leaderboard.md` | ✅ **现状**（已有 Round 1 数据） |
| `orchestrator/setup-cron.sh` | ❌ **规划**（Skill 名称错了没法用） |
| `orchestrator/schedule.md` | ⚠️ **混合**（时间表是现状，Skill 名称是过时规划） |
| `DOCS.md` | ❌ **规划/过时**（目录结构图与实际不符） |
| `PLAN.md` | ✅ **规划**（本来就是总体设计文档） |
| Hermes Skills | ✅ **现状**（在用了）但路径指向是错的 |

---

## 四、真源统一建议

### 4.1 正式运行路径

**决定采用**：`ai-company-wars/teams/{color}/project/`

理由：
- 这里已有完整的代码、Git 历史、.venv
- 与 `shared/protocol.md` 约定一致
- 与 `setup-cron.sh` 中的 prompt 引用一致
- 文档齐全，结构清晰

### 4.2 镜像目录处理

`/mnt/d/Desktop/hermes/red-project/` 和 `blue-project/` 建议：
- 明确标记为 **示例/存档**（不是正式运行目录）
- 在所有 Skill、文档中指向 `teams/{color}/project/`

### 4.3 红队 artifact 格式

统一为蓝队已经使用的格式：
- `artifacts/prd/YYYY-MM-DD-*-prd.md`（子目录+日期前缀）
- `artifacts/tasks.md`（而非 `current-sprint.md`）
- `artifacts/ready-for-deploy.md`（红队缺失）
- 补上 `designs/` 和 `reports/` 子目录

---

## 五、需修改的文件清单

| 文件 | 需修改内容 | 优先级 |
|------|-----------|--------|
| `DOCS.md` | 目录树改为 `teams/red/project/` + 补全 teams 结构 | P0 |
| Hermes Skills (5 个) | 路径从 `/mnt/d/Desktop/hermes/{color}-project/` 改为 `teams/{color}/project/` | P0 |
| `orchestrator/setup-cron.sh` | Skill 名称检测从 `dev-agent` 改为 `ai-company-wars-dev` | P1 |
| `orchestrator/schedule.md` | Skill 名称表修正 | P1 |
| `shared/protocol.md` | memory 目录图补充 role 子目录 | P2 |
| 红队 artifacts | 迁至新命名规范 | P2 |
| `skills/dev-agent-draft.md` | 删除（已被 Hermes Skill 取代） | P3 |

---

## 六、下一轮工作建议

按你设定的 10 步流程，第 1 轮（审计）已完成。建议第 2 轮：

1. **先改 P0**：修正所有文档和 Skill 中的路径，将真源锁定为 `teams/{color}/project/`
2. **统一 artifact 命名**：红队 artefact 迁至新规范
3. **修 setup-cron.sh**：Skill 名称匹配
4. **再确认**：DOCS.md → protocol.md → Skill prompt 三处口径一致

要开始改吗？
