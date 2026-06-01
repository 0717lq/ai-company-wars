# 2026-05-19 产品需求 — dirsort v0.2.0

## 项目名
**dirsort** — 智能文件目录整理 CLI 工具（第2轮迭代）

## 做什么
在 Round 1 的 dirsort v0.1.0 基础上，根据裁判评分反馈进行关键功能迭代，增加差异化特性：

1. **默认 dry-run 模式** — 安全优先：`dirsort ~/Downloads` 默认只预览，添加 `--execute` 才执行
2. **文件排除功能** — `--exclude "*.tmp"` 和 `--exclude-dir "node_modules"` 跳过特定文件/目录
3. **Rich 美化输出** — 表格预览、颜色高亮、进度条、对齐格式化输出
4. **配置文件系统** — `dirsort --config rules.yaml` 支持用户自定义分类规则（**差异化卖点**）
5. **错误处理增强** — PermissionError/OSError 捕获、优雅降级

## 验收标准
- [ ] `dirsort <path>` 默认只预览（dry-run），使用 `--execute` 才真正执行移动
- [ ] `--exclude "*.log"` 排除匹配模式的文件
- [ ] `--exclude-dir "node_modules"` 排除匹配名称的目录
- [ ] Rich 表格显示整理预览，含颜色高亮和格式对齐
- [ ] `--config rules.yaml` 从自定义规则文件加载分类规则
- [ ] 默认规则文件 `~/.config/dirsort/rules.yaml` 自动加载（如存在）
- [ ] PermissionError / OSError 捕获，显示友好错误信息
- [ ] 原有功能（sort/undo/history/stats/--by-date）完全兼容
- [ ] 全部 56+ 个测试通过，新增功能有测试覆盖
- [ ] rich 降级处理（无 rich 环境仍可工作）

## 技术选型
Python 3.10+ · Typer CLI · Rich（美化输出） · PyYAML（配置文件解析） · pytest + pytest-cov（测试）

**新增依赖**：`rich`, `pyyaml`

## 项目结构
```
project/
├── src/dirsort/
│   ├── __init__.py
│   ├── __main__.py
│   ├── cli.py         # 子命令 + 新增参数（--execute, --exclude, --config 等）
│   ├── sorter.py      # 核心整理逻辑（排除过滤 + 配置规则加载）
│   ├── rules.py       # 默认分类规则（扩展：支持 YAML 覆盖）
│   ├── undo.py        # 回滚管理（不变/增强）
│   ├── config.py      # [新] 配置文件加载与合并逻辑
│   └── utils.py       # 工具函数
├── tests/
│   ├── test_cli.py
│   ├── test_sorter.py
│   ├── test_sorter_extra.py
│   ├── test_undo.py
│   ├── test_undo_extra.py
│   ├── test_utils.py
│   └── test_config.py # [新] 配置系统测试
├── pyproject.toml      # 版本升至 0.2.0，新增 rich/pyyaml 依赖
└── README.md
```

## 差异化竞争

### 为什么继续做 dirsort 而非新项目？
- Round 1 只落后蓝队 2 分（30 vs 32），项目基础扎实
- 裁判明确给出了 4 条可执行建议，快速修复=快速得分
- 文件整理工具是已验证的市场（竞品 `organize-cli` ~3k⭐，`mnamer` ~1.1k⭐）
- 持续迭代比频繁换方向更符合"真实产品"逻辑

### 和蓝队 fclean 的差异
| 特性 | 🔴 dirsort v0.2.0 | 🔵 fclean (Round 1) |
|------|-------------------|---------------------|
| 默认 dry-run | ✅ **新增** | ✅ 已有 |
| --exclude | ✅ **新增** | ✅ 已有 |
| Rich 美化输出 | ✅ **新增** | ✅ 已有 |
| 配置文件系统 | ✅ **独家** | ❌ 无 |
| 项目完整性(CI/Git/tag) | ✅ 已有 | ❌ 缺 |
| GitHub CI 测试矩阵 | ✅ 已有 | ❌ 无 |

### 核心差异化：配置文件系统
蓝队 fclean 没有配置文件功能。`dirsort --config rules.yaml` 让用户可以通过 YAML 自定义：
- 文件类型到分类目录的映射（如 `.pdf → Documents/PDFs`）
- 正则表达式规则
- 不同目录使用不同配置
- 配置可分享为 dotfiles

这是文件整理工具从"玩具"升级为"真正生产力工具"的分水岭。`organize-cli` 的核心卖点就是配置文件。

### GitHub Star 竞争策略
- **安全优先**：默认 dry-run 减少误操作风险，降低用户心理门槛
- **可配置性**：配置文件吸引开发者/重度用户群体（GitHub Star 主力）
- **完整工程**：CI 徽章、PyPI 发布、贡献指南 — 专业感吸引 Star
