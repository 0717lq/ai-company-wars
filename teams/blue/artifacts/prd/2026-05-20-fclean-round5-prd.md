# 2026-05-20 产品需求 — fclean Round 5：AI Agent Era

## 项目名
**fclean** — 安全、好看的命令行文件整理工具

## 本轮定位：从「CLI 工具」到「AI Agent 原生工具」

### 背景

Round 4 蓝队以 51:52 惜败，累计总分为 136:135（仅领先 1 分）。裁判明确反馈：
1. **重启产品迭代** — Round 4 没有新 PRD，迭代停滞
2. **配置 GitHub Topics** — 提升项目可见性
3. **--json 输出** — 对接 AI Agent 生态

与此同时，GitHub 上 **AI Agent skills 类项目** 持续霸榜（mattpocock/skills 单周 20,361⭐），文件管理 CLI 生态（fd 43k⭐, fzf 80k⭐, yazi 38k⭐）需求稳定。

### 核心命题

**「为什么 AI Agent 会用 fclean？」**

答案不是「功能更多」—— 而是**「fclean 的输出可以被 AI Agent 读懂」**。

当 Hermes Agent / Claude Code / Cursor Agent 需要整理文件时，它不会调用 `fclean` 然后尝试解析彩色表格。它需要 `--json` —— 结构化、可编程、可 pipe 到 jq 的输出。这是从「给人类用的 CLI」到「也给 AI 用的工具」的关键转型。

### 做什么

**三大方向：**

---

### 1. 🤖 AI Agent First (P0) — 让 fclean 成为 AI Agent 的原生工具

所有子命令增加 `-j`/`--json` 输出模式，输出结构化 JSON 数据。每个命令的 JSON schema 标准化，附带 `tool_name`, `timestamp`, `summary` 字段，AI Agent 可直接解析决策。

#### 1a. `fclean --json [path]`
```json
{
  "tool": "fclean",
  "command": "organize",
  "timestamp": "2026-05-20T14:30:00Z",
  "path": "/home/user/Downloads",
  "status": "dry_run",
  "files_scanned": 42,
  "categories_found": {
    "images": {"count": 10, "size_bytes": 5242880},
    "documents": {"count": 8, "size_bytes": 2048000},
    "others": {"count": 4, "size_bytes": 102400}
  },
  "changes": [
    {"from": "photo.jpg", "to": "images/photo.jpg", "category": "images", "size": 1048576}
  ],
  "summary": "42 files scanned, 38 will be organized into 5 categories"
}
```

#### 1b. `fclean stats --json [path]`
```json
{
  "tool": "fclean",
  "command": "stats",
  "timestamp": "2026-05-20T14:30:00Z",
  "path": "/home/user",
  "total_files": 1500,
  "total_size_bytes": 1073741824,
  "categories": {
    "images": {"count": 300, "size_bytes": 268435456, "pct": 20.0},
    "documents": {"count": 500, "size_bytes": 536870912, "pct": 50.0}
  },
  "top_extensions": [
    {"ext": ".pdf", "count": 200, "size_bytes": 268435456},
    {"ext": ".jpg", "count": 150, "size_bytes": 134217728}
  ]
}
```

#### 1c. `fclean rename --json`
```json
{
  "tool": "fclean",
  "command": "rename",
  "timestamp": "2026-05-20T14:30:00Z",
  "status": "dry_run",
  "files_matched": 5,
  "renames": [
    {"from": "IMG_001.jpg", "to": "vacation_001.jpg"},
    {"from": "IMG_002.jpg", "to": "vacation_002.jpg"}
  ]
}
```

#### 1d. `fclean dupes --json` (见下方)
标准 JSON 输出，AI Agent 可解析并行决策。

#### 1e. fclean Agent Skill 文件
创建 `.hermes/skills/` 目录并放置 `fclean.md` skill 定义，让 Hermes Agent / Claude Code 能直接调用 fclean。

---

### 2. 🗂️ fclean dupes (P0) — 重复文件检测与清理

高频需求功能。SHA-256 哈希扫描，找出重复文件，安全清理。

**用户故事：** "我的 Downloads 文件夹有好多重复下载的文件，我想找出并清理掉，但不想误删。"

**设计：**
```
fclean dupes [path] [--min-size SIZE] [--delete] [--json] [--dry-run]
```

- 默认 dry-run：列出重复文件组，按 hash 分组展示
- `--min-size 1MB`：跳过小文件（小于 1MB 的重复不感兴趣）
- `--delete`：对每组重复，保留最新/最旧版本，删除其余
- `--delete --strategy newest|oldest|path`：保留策略
- 默认交互确认：每组重复显示并逐组确认
- undo 支持：删除记录到 undo 历史，可回滚
- --json 输出：结构化数据供 AI Agent 解析

**技术方案：**
- 使用 `hashlib.sha256()` 逐块哈希（避免大文件一次性加载到内存）
- 先按 size 分组（不同 size 不可能是重复），再哈希同 size 文件
- 并行哈希：使用 `concurrent.futures.ThreadPoolExecutor` 加速
- 进度条：`rich.progress` 显示扫描进度

---

### 3. 📦 Market Polish (P1) — 项目完整度提升

#### 3a. Shell Completions
添加 `--install-completion` 参数，支持 bash/zsh/fish 自动补全。
使用 `argparse` 的 `argparse.ArgumentParser` 原生 completion 能力或 `shtab`。

用户只需运行一次：
```bash
fclean --install-completion
```
自动检测当前 shell 并安装补全脚本。

#### 3b. GitHub Topics
在仓库设置中添加 Topics：
`fclean`, `file-organizer`, `cli`, `python`, `file-management`, `productivity`, `duplicate-files`, `batch-rename`, `dry-run`

#### 3c. AI Agent README 章节
在 README 增加「AI Agent Integration」章节：
- `--json` 输出格式说明
- 示例：如何使用 jq 处理 JSON 输出
- 示例：如何在 Hermes Agent / Claude Code 中调用 fclean
- Agent Skill 引用位置

---

## 多轮策略对齐

| 轮次 | 策略 | 状态 |
|------|------|------|
| Round 1 | MVP 验证 | ✅ 32-30 胜 |
| Round 2 | 工程化 + 配置系统 | ✅ 53-53 平（累积领先）|
| Round 3 | 展示升级 + rename | ✅ v0.3.0 发布 |
| Round 4 | (停滞 — 无新 PRD) | ❌ 51-52 惜败 |
| **Round 5** | **AI Agent First + dupes** | **← 本轮** |

### 为什么是 AI Agent First 而不是 TUI？

Round 4 我们原本计划做 TUI，但执行不力导致失败。TUI 固然是品类创新，但：
1. **裁判明确建议做 --json** — 这是来自裁判的信号，必须优先响应
2. **AI Agent 生态是 GitHub 最热方向** — skills 类项目每周 20k+ stars，顺势而为
3. **JSON 输出相比 TUI 更轻量** — 不需要 Textual 框架，纯 Python 标准库即可实现
4. **Dupes 替代 TUI 作为功能亮点** — SHA-256 重复检测是高频需求，优先级高于 TUI

TUI 仍在我们 roadmap 上（Round 6），但本轮必须拿回 momentum。

### 差异化竞争

| 因素 | 分析 |
|------|------|
| **裁判反馈** | ①--json 输出（P0）②GitHub Topics（P1）③重启迭代（P0）|
| **差异化点** | - 所有竞品（dirsort/organize-cli/mnamer）均无 --json 输出<br>- AI Agent Skill 定义独一无二<br>- dupes 是高频需求但多数整理工具缺失 |
| **市场趋势** | AI Agent skills 是最热 GitHub 品类。文件管理 CLI（fd/yazi/fzf）需求稳定。`--json` + Agent Skill = 顺势而为 |
| **竞品对比** | 红队 dirsort 功能广度在 Round 4 反超。fclean 需差异化——不是拼功能数量，而是拼 AI Agent 集成 |
| **迭代 vs 重开** | fclean 已验证 4 轮。AI Agent 方向是自然演进 |

---

## 验收标准

- [ ] `fclean --json [path]` 输出结构化 JSON
- [ ] `fclean stats --json [path]` 输出结构化 JSON
- [ ] `fclean rename --json` 输出结构化 JSON
- [ ] `fclean dupes` 实现并可通过 dry-run → execute 工作流
- [ ] `fclean dupes --json` 输出结构化 JSON
- [ ] dupes 使用 SHA-256 逐块哈希 + size 预过滤
- [ ] dupes 支持 `--min-size` 参数
- [ ] dupes 操作可 undo 回滚
- [ ] `fclean --install-completion` 可用
- [ ] GitHub Topics 已配置
- [ ] README 中增加 AI Agent Integration 章节
- [ ] 所有现有测试通过
- [ ] 版本号更新至 v0.4.0

---

## 技术选型

- Python 标准库 `hashlib`（SHA-256）
- `concurrent.futures.ThreadPoolExecutor`（并行哈希）
- `rich.progress`（扫描进度条）
- `json` 标准库（JSON 输出）
- `pathlib`（路径操作）
- 不引入新依赖

### JSON 输出实现方案

在 cli.py 中为每个子命令添加 `--json`/`-j` 可选参数：
- 参数类型：`store_true`
- 内部创建一个 `to_json()` 辅助函数，将结果 dict 序列化为 JSON
- 当 `args.json` 为 True 时，不走 rich 表格渲染，直接 `print(json.dumps(result, indent=2, ensure_ascii=False))`

### fclean dupes 技术方案

```
fclean dupes [path] [--min-size SIZE] [--delete] [--dry-run] [--json] [--strategy newest|oldest|path]
```

1. 扫描目录，收集所有文件的 size + path
2. 按 size 分组，只对同 size 的文件进行哈希（大小不同必不重复）
3. 多线程 SHA-256 哈希（maximum 4 workers）
4. 按 hash 分组，`hash -> [path1, path2, ...]`
5. 过滤出 len(groups) > 1 的组（有重复）
6. 默认 dry-run：shown in rich table + file sizes
7. `--delete`：对每组保留一个，删除其余
8. `--strategy newest|oldest|path`：保留策略
9. undo 记录：删除操作映射到 undo 历史

## 项目结构（新增）

```
project/
├── src/fclean/
│   ├── __init__.py           # v0.4.0
│   ├── __main__.py
│   ├── cli.py                # 修改：所有命令添加 --json, 新增 dupes 子命令
│   ├── config.py
│   ├── organizer.py
│   ├── rules.py
│   ├── renamer.py
│   ├── undo.py
│   └── dupes.py              # 新增：重复文件检测模块
├── tests/
│   ├── __init__.py
│   ├── test_cli.py
│   ├── test_config.py
│   ├── test_organizer.py
│   ├── test_undo.py
│   ├── test_renamer.py
│   ├── test_edge_cases.py
│   └── test_dupes.py         # 新增：dupes 测试
├── .hermes/skills/
│   └── fclean.md             # 新增：Agent Skill 定义
├── README.md                 # 修改：增加 AI Agent Integration 章节
├── CHANGELOG.md
├── pyproject.toml
└── .github/workflows/ci.yml
```
