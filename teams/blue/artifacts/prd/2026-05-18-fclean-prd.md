# 2026-05-18 产品需求 — fclean（Folder Clean CLI）

## 项目名
fclean — 又安全又好看的命令行文件整理工具

## 做什么
**一句话：** 一个 Python CLI 工具，扫描指定文件夹，按文件类型自动归类到子目录。

用户用一条命令就能把乱糟糟的桌面或下载文件夹整理得井井有条。核心卖点是 **安全**（默认 dry-run，先预览再执行）和 **可回滚**（支持 undo）。

## 为什么要做这个
- **刚需**：每个人电脑上都有需要整理的文件夹（桌面、下载、文档）
- **GitHub 上有成功先例**：`organize-cli`、`FileCleaner` 等都有几千 Star
- **可差异化**：GitHub 上同类工具的弱点：①没有 undo 功能 ②输出不够好看 ③不支持中文文件名 ④没有 dry-run 保护。fclean 把安全放在第一位
- **展示蓝队工程能力**：完善测试、类型注解、文档、GitHub Actions CI

## 验收标准

### P0 — MVP 核心功能
- [ ] 扫描指定目录，按文件类型分类（图片、文档、视频、压缩包、代码、音乐、其他）
- [ ] 支持 `--dry-run` 模式：只预览不操作，显示拟移动的文件列表
- [ ] 支持实际执行移动（`fclean /path/to/folder`）
- [ ] 支持 `--undo` 回滚上次整理操作
- [ ] 基本的分类规则（基于文件扩展名）

### P1 — 体验完善
- [ ] 彩色终端输出（rich 或 colorama），不同类型的文件显示不同颜色
- [ ] 统计信息：移动了多少文件、释放了多少空间提示
- [ ] 友好的错误处理：权限不足、路径不存在等
- [ ] 支持排除文件/文件夹（`--exclude` 参数）

### P2 — 锦上添花
- [ ] 自定义分类规则（`fclean --rules my-rules.json`）
- [ ] 进度条（大目录时有用）

## 技术选型
Python 3.9+ CLI 工具

| 组件 | 选择 | 理由 |
|------|------|------|
| CLI 框架 | `argparse`（标准库） | 零依赖，简单够用 |
| 彩色输出 | `rich` | 比 colorama 更好看，支持表格、进度条 |
| 测试 | `pytest` + `pyfakefs` | 文件操作测试用 fake filesystem |
| 打包 | `setuptools`（pyproject.toml） | 标准 Python 打包 |

## 项目结构
```
project/
├── pyproject.toml          # 包配置
├── README.md
├── .gitignore
├── src/
│   └── fclean/
│       ├── __init__.py     # 版本号
│       ├── __main__.py     # python -m fclean 入口
│       ├── cli.py          # CLI 参数解析 + 主入口
│       ├── organizer.py    # 核心：扫描 + 分类 + 移动逻辑
│       ├── rules.py        # 分类规则（扩展名 → 文件夹映射）
│       └── undo.py         # undo 逻辑（记录操作日志 + 回滚）
└── tests/
    ├── __init__.py
    ├── test_organizer.py   # 测试扫描和分类
    ├── test_rules.py       # 测试规则匹配
    └── test_undo.py        # 测试 undo 逻辑
```

## 差异化竞争要点
1. **安全第一**：默认 `--dry-run`，用户确认后才执行
2. **可回滚**：每次操作生成 undo 日志，随时回滚
3. **好看**：`rich` 表格输出，分类清晰
4. **中文友好**：支持中文目录名和文件名
5. **极致简单**：一条命令解决实际问题，无需学习复杂配置
