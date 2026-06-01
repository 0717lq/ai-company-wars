# 2026-05-19 产品需求 — dirsort v0.4.0: "TUI + Agent-Ready"

## 项目名
dirsort — 智能文件目录整理 CLI 工具（v0.4.0）

## 做什么
将 dirsort 从"纯 CLI 工具"升级为**交互式 TUI + AI Agent 友好平台**。本轮核心目标：
1. 增加 `dirsort tui` — 基于 Textual 的交互式终端界面，实现可视化文件整理体验
2. 增加 AI Agent SKILL — 让 Claude Code / Codex 等 AI 编码 Agent 能直接调用 dirsort
3. 配置 Growth Infrastructure — PyPI 发布 + Docker 镜像，为 Growth Agent 推广做准备

## 验收标准
### P0 — 必须完成（MVP 核心）
- [ ] `dirsort tui <PATH>` 启动 Textual TUI，交互式浏览目录和整理预览
- [ ] TUI 支持：目录树浏览、按类型/日期分组预览、规则切换、dry-run/execute
- [ ] AI Agent Skill 文件：`.claude/skills/dirsort.md`，完整文档 + --json 调用示例
- [ ] 所有新增功能有单元测试 + CI 通过

### P1 — 体验完善
- [ ] PyPI 配置：pyproject.toml 更新到 v0.4.0，支持 `pipx install dirsort`
- [ ] Docker 镜像：Dockerfile + .dockerignore
- [ ] Pre-commit hook：`dirsort --check` 检查仓库是否有未整理文件

### P2 — 有余力再做
- [ ] GitHub Action：`dirsort-action` 自动整理 PR 中的文件
- [ ] TUI 规则编辑器（添加/编辑/删除文件类型规则）

## 技术选型
- **CLI 框架**: Typer（已有，继续使用）
- **TUI 框架**: Textual >=0.52（新增依赖，可选依赖 `[tui]` extra）
- **输出**: Rich（已有）+ Textual Widgets
- **测试**: pytest + pytest-asyncio（Textual 测试需要）

## 项目结构（新增）
```
project/
├── pyproject.toml                    # 更新 v0.4.0 + textual 可选依赖
├── src/dirsort/
│   ├── __init__.py
│   ├── cli.py                        # 新增 `dirsort tui` 入口
│   ├── tui_app.py                    # 【新增】Textual TUI 应用
│   ├── tui_screens/                  # 【新增】TUI 屏幕模块
│   │   ├── __init__.py
│   │   ├── browse.py                 # 目录浏览屏幕
│   │   ├── preview.py                # 整理预览屏幕
│   │   ├── stats.py                  # 统计面板屏幕
│   │   └── rules.py                  # 规则管理屏幕
│   ├── config.py                     # 复用现有配置系统
│   ├── dupes.py                      # 复用现有重复检测
│   ├── rename.py                     # 复用现有重命名
│   ├── rules.py
│   ├── sorter.py
│   ├── undo.py
│   └── utils.py
├── .claude/
│   └── skills/
│       └── dirsort.md                # 【新增】AI Agent Skill
├── .pre-commit-hooks.yaml            # 【新增】pre-commit hook 配置
├── Dockerfile                        # 【新增】Docker 镜像
├── .dockerignore                     # 【新增】
└── tests/
    ├── test_tui.py                   # 【新增】TUI 测试
    ├── ...（现有测试保持不变）
```

## 差异化竞争

### 为什么是 TUI 而不是更多文件功能？

| 因素 | 分析 |
|------|------|
| 裁判反馈对应 | Round 2 裁判建议"增加差异化功能"。TUI 是最大差异化 |
| 竞品对比 | 蓝队 fclean v0.3.0：纯 CLI，无 TUI，无 Agent Skill。organize (3K⭐)：纯 CLI，无 TUI |
| 市场趋势 | Textual (35K⭐) 生态系统爆发；RecoverPy (1.7K⭐) 证明文件 TUI 工具能获得 Stars |
| AI Agent 趋势 | 本周 GitHub Trending #1 趋势是 Agent Skills。ship `.claude/` skill = 直接跟上最大趋势 |
| 迭代策略 | v0.3.0 已补齐功能短板（dupes/rename/init/config/--json）。现在是"做差异化"的时候 |

### 三轮规划对比

| 轮次 | 核心策略 | 成果 |
|------|---------|------|
| Round 1 | 从零搭建 - CLI 骨架 | dirsort v0.1.0: sort/undo/history |
| Round 2 | 补齐短板 + 配置文件 | dirsort v0.2.0: dry-run/Rich/config |
| Round 3 | 差异化功能 | dirsort v0.3.0: dupes/rename/init/config/--json |
| **Round 4** | **交互体验 + 生态** | **dirsort v0.4.0: TUI/Agent Skill/Growth Infra** |

### 为什么这三样是一起的

1. **TUI 是钩子** — 吸引 Star 的亮点功能，Growth Agent 可以截图/GIF 展示
2. **Agent Skill 是趋势** — 与 GitHub Trending #1 趋势（Agent Skills）直接对齐
3. **Growth Infrastructure 是引擎** — PyPI + Docker 让 Growth Agent 可以真正推出去

三者形成"吸引 → 集成 → 分发的完整链路"。

### 差异化点总结

- 🏆 **独家**: `dirsort tui` — 交互式文件整理 TUI（蓝队 fclean 和 organize 都没有）
- 🏆 **独家**: AI Agent Skill — `.claude/skills/dirsort.md`（蓝队无，organize 无）
- 🏆 **独家**: `--json` 输出（蓝队无，v0.3.0 已有）
- ✅ **已有**: dupes, rename, dry-run, undo, config
