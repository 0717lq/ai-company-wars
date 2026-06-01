# 2026-05-30 产品需求 — dirsort v0.6.0 "Extensible Platform"

## 项目名
dirsort — 智能文件目录整理 CLI 工具

## 版本
v0.6.0 — "Extensible Platform"

## 做什么

本轮在 v0.5.0 代码质量加固的基础上，推出**两大差异化功能**：

1. **插件系统 (`dirsort plugin`)** — 让用户通过 Python 插件扩展 dirsort 的分类逻辑、报告格式和操作行为。从"固定工具"升级为"可扩展平台"。
2. **增强统计 (`dirsort stats --chart`)** — 在现有 stats 命令基础上增加可视化图表（ASCII 饼图/柱状图）、存储分析（大文件 Top-N、重复文件占比）。

同时补齐 v0.5.0 遗留短板：英文 README 同步、--json 元数据增强。

## 验收标准

- [ ] `dirsort plugin list` — 列出已安装插件
- [ ] `dirsort plugin install <path>` — 安装自定义 Python 插件
- [ ] `dirsort plugin create <name>` — 生成插件模板脚手架
- [ ] 插件可以 hook 到 `classify` 阶段（自定义文件分类规则）
- [ ] 插件可以 hook 到 `report` 阶段（自定义报告格式）
- [ ] `dirsort stats --chart` — 显示 ASCII 饼图/柱状图
- [ ] `dirsort stats --top N` — 显示大文件 Top-N
- [ ] `--json` 输出增加 `metadata.version`、`metadata.plugins` 字段
- [ ] 英文 README 同步 v0.6.0 所有功能
- [ ] 全部测试通过（含新增插件测试 + stats 测试）
- [ ] CI 通过（含 Ruff lint）

## 技术选型

- **Python 3.10+** + Typer CLI（现有）
- **插件系统**: Python importlib + 抽象基类（PluginBase），无需外部依赖
- **图表**: 内置 ASCII 渲染（不依赖 rich.chart），保持零依赖策略
- **存储分析**: os.stat + pathlib（纯标准库）

## 项目结构

```
teams/red/project/
├── src/dirsort/
│   ├── __init__.py          (v0.6.0)
│   ├── __main__.py
│   ├── cli.py               (新增 plugin 子命令)
│   ├── config.py
│   ├── dupes.py
│   ├── rename.py
│   ├── rules.py
│   ├── sorter.py
│   ├── tui_app.py
│   ├── tui_screens/
│   ├── undo.py
│   ├── utils.py
│   ├── plugin_system.py     ← NEW: 插件加载/注册/执行引擎
│   ├── plugin_base.py       ← NEW: PluginBase 抽象基类
│   └── stats_enhanced.py    ← NEW: 增强统计（图表、Top-N）
├── tests/
│   ├── test_plugin_system.py  ← NEW
│   ├── test_stats_enhanced.py ← NEW
│   └── ...
├── plugins/                   ← NEW: 示例插件目录
│   └── example_classifier.py
├── README.md                  (同步 v0.6.0)
├── README.en.md               (同步 v0.6.0)
└── pyproject.toml             (v0.6.0)
```

## 差异化竞争

### 为什么是插件系统？

1. **蓝队 fclean 完全没有** — 这是平台级差异化，不是功能级
2. **竞品 organize(3057⭐) 也没有** — 纯配置规则，不可编程
3. **对接 GitHub Trending** — AI Agent 生态需要可扩展工具链（cli-anything-wps 102⭐ 模式）
4. **护城河深** — 插件系统一旦建立，用户有迁移成本，蓝队需要一整轮才能追赶
5. **开发者友好** — 吸引 Python 开发者写插件 = 免费功能扩展 + 社区贡献

### 为什么是 Stats 增强？

1. **现有 stats 命令已有基础** — 增量改进，风险低
2. **视觉冲击力强** — ASCII 图表截图可以直接放 README / 社交媒体
3. **蓝队 fclean stats 只有纯文本** — 我们的图表是差异化
4. **dust/du-dust 工具验证了存储分析需求** — 用户想知道"什么文件占空间"

### 竞品对比矩阵

| 功能 | dirsort v0.6.0 | fclean v0.4.0 | organize(3K⭐) |
|------|:-:|:-:|:-:|
| 插件系统 | ✅ | ❌ | ❌ |
| ASCII 图表 | ✅ | ❌ | ❌ |
| TUI | ✅ | ❌ | ❌ |
| Docker | ✅ | ❌ | ❌ |
| Pre-commit | ✅ | ❌ | ❌ |
| Agent Skill | ✅ | ✅ | ❌ |
| --json | ✅ | ✅ | ❌ |
| dupes | ✅ | ✅ | ❌ |
| 配置规则 | ✅ | ✅ | ✅ |

## Round 5 裁判反馈对照

| 裁判建议 | 本轮处理 |
|---------|---------|
| 必须产出新功能 | ✅ 插件系统 + Stats 增强 |
| Product Agent 优化子代理策略 | ✅ 本轮直接产出，不依赖子代理 |
| 英文 README 同步 | ✅ README.en.md 同步 v0.6.0 |
| GitHub 远程推送问题 | ⏳ DevOps 负责 |
| 启动社区推广 | ⏳ Growth 负责 |


---

## 2026-05-31 更新 — 竞态分析

### 蓝队最新动向 (v0.5.0)
蓝队 Round 6 方向为 **Production Pipeline + Developer Integration**：
- PyPI 发布 + GitHub Actions（trusted publisher OIDC）
- Docker 镜像（python:3.12-slim）
- Pre-commit hook（.pre-commit-hooks.yaml）
- `.fcleanignore` 忽略规则文件
- `fclean watch` 文件监控自动整理（watchdog 依赖）
- 新增模块：watcher.py、ignore.py

### 竞品对比更新

| 功能 | dirsort v0.6.0 | fclean v0.5.0 | organize(3K⭐) |
|------|:-:|:-:|:-:|
| 插件系统 | ✅ | ❌ | ❌ |
| ASCII 图表 | ✅ | ❌ | ❌ |
| TUI | ✅ | ❌ | ❌ |
| Docker | ✅ | ✅ | ❌ |
| Pre-commit | ✅ | ✅ | ❌ |
| Agent Skill | ✅ | ✅ | ❌ |
| --json | ✅ | ✅ | ❌ |
| dupes | ✅ | ✅ | ❌ |
| 配置规则 | ✅ | ✅ | ✅ |
| PyPI 发布 | ⏳ | ✅ | ❌ |
| 文件监控 | ❌ | ✅ | ❌ |
| 忽略规则 | ❌ | ✅ | ❌ |

### 差异化评估
蓝队补齐了 Docker/Pre-commit（与红队持平），新增 watch/ignore（红队没有）。
红队的 **插件系统 + ASCII 图表 + TUI** 仍然是独家优势，但蓝队在 DevOps 基础设施上反超。
红队需确保插件系统实现质量足够高，形成"可扩展平台"的叙事。
