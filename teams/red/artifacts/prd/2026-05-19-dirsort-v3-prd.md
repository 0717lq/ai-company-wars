# 2026-05-19 产品需求 — dirsort v0.3.0

## 项目名
dirsort — 智能文件整理 CLI 工具

## 本轮做什么
在 Round 2 基础上补齐蓝队的子命令短板，同时通过差异化功能（重复文件检测、批量重命名）实现弯道超车。

**核心变更：**
- `dirsort init` / `dirsort config` — 配置文件管理体验（对标蓝队 fclean）
- `dirsort dupes <path>` — 重复文件检测（蓝队没有，差异化）
- `dirsort rename <pattern> <template>` — 批量重命名（蓝队没有，差异化）
- `--json` 输出 — AI agent 集成友好（市场趋势驱动）
- Shell 自动补全 — 专业 CLI 标配

## 验收标准
- [ ] `dirsort init` — 创建默认配置文件 ~/.config/dirsort/rules.yaml
- [ ] `dirsort config` — 查看/编辑当前配置
- [ ] `dirsort dupes <path>` — 按 MD5/SHA256 检测重复文件，支持 dry-run
- [ ] `dirsort rename "*.jpg" "photo_%04d"` — 批量重命名，支持预览
- [ ] `--json` 标志 — 所有命令支持 JSON 输出
- [ ] `--install-completion` — Shell 自动补全
- [ ] 所有新功能有单元测试覆盖
- [ ] 持续集成通过

## 技术选型
Python + Typer CLI + Rich 美化 + hashlib（重复检测，零外部依赖）

| 功能 | 技术方案 |
|------|---------|
| CLI 框架 | Typer（已有）增量扩展 |
| 内容输出 | Rich（已有） |
| 重复检测 | hashlib.md5（块读取，大文件友好） |
| 配置 | PyYAML（已有） |
| JSON 输出 | Typer 原生 JSON 支持 |
| 补全 | Typer 原生 `--install-completion` |

## 项目结构（已有，本轮新增文件标注）
```
project/
├── pyproject.toml
├── README.md
├── src/
│   └── dirsort/
│       ├── __init__.py
│       ├── __main__.py
│       ├── cli.py          ← 修改：增加 init/config/dupes/rename 子命令
│       ├── config.py       ← 修改：增加 init, config 命令
│       ├── rules.py        ← 修改：支持自定义重命名模式
│       ├── sorter.py       ← 修改：支持内容 hash 排序
│       ├── undo.py
│       ├── utils.py        ← 修改：增加 JSON 输出格式化
│       └── dupes.py        ← 新增：重复文件检测模块
│       └── rename.py       ← 新增：批量重命名模块
└── tests/
    ├── __init__.py
    ├── test_cli.py         ← 扩展
    ├── test_config.py      ← 扩展
    ├── test_sorter.py
    ├── test_dupes.py       ← 新增
    ├── test_rename.py      ← 新增
    ├── test_undo.py
    └── test_utils.py       ← 扩展
```

## 决策依据

| 因素 | 分析 |
|------|------|
| 裁判反馈对应 | ① `init`/`config` 子命令（直接回应"配置系统不如蓝队"）② 差异化功能（"尝试差异化功能"） |
| 差异化点 | 重复文件检测 + 批量重命名 — 蓝队 fclean 没有此功能 |
| 市场趋势 | AI agent 工具主导 Trending（20k+/week），`--json` 输出让 dirsort 可被 AI agent 调用 |
| 竞品对比 | 蓝队 fclean v0.2.0：4 子命令（organize/init/config/stats/undo/history），配置系统完善。我们没有 init/config 子命令 |
| 迭代 vs 重开 | 迭代——dirsort 已有完整骨架（8 源文件 + 9 测试文件 + CI + README），裁判认可用力追分 |

## 差异化竞争

**为什么选 dirsort 而非换项目？**
- Round 2 平局（53-53），差距仅 2 分，持续迭代是最快追分路径
- 文件整理市场需求已验证（organize-cli ~3k⭐, mnamer ~1.1k⭐）
- 重复文件检测是"文件整理"功能的自然延伸——整理完目录后自然需要查重
- 批量重命名让 dirsort 从"排序工具"升级为"全功能文件管理工具"

**差异化 vs 蓝队 fclean：**
| 功能 | 红队 dirsort v0.3.0 | 蓝队 fclean v0.2.0 |
|------|-------------------|-------------------|
| 文件整理 | ✅ sort（默认） | ✅ organize |
| 配置文件 | ✅ init + config | ✅ init + config |
| 重复检测 | ✅ **dupes（独有）** | ❌ 无 |
| 批量重命名 | ✅ **rename（独有）** | ❌ 无 |
| Undo 回滚 | ✅ | ✅ |
| --json 输出 | ✅ **（独有）** | ❌ 无 |
| Shell 补全 | ✅ **（独有）** | ❌ 无 |
| Stats | ✅ 增强版 | ✅ 已有 |
| README 质量 | ✅ 10KB 双语 | ✅ 6KB |

**GitHub Stars 策略：**
- 差异化功能（dupes + rename）是目录整理工具中用户高频搜索的功能
- `--json` 输出适用于 CI/CD 和 AI agent 场景——对接当前最大市场趋势
- 完善子命令体系后，dirsort 将成为"最全面的文件管理 CLI 工具"定位

**AI Agent 生态（市场趋势最大信号）：**
- GitHub Trending #1: mattpocock/skills 单周 20,361⭐
- 提供 `--json` 输出让 AI agent 可以直接调用 dirsort
- 可配合 Claude Code / Cursor / Copilot 使用
- 未来可发布 AI agent skill 定义文件
