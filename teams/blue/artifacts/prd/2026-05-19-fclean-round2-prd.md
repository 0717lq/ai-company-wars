# 2026-05-19 产品需求 — fclean Round 2：专业化与配置化

## 项目名
fclean — 又安全又好看的命令行文件整理工具

## 本轮做什么

**一句话：在 fclean 已有的稳固基础上，补上工程短板（CI/Git tag），增加配置系统（.fcleanrc）和统计命令（fclean stats），完成从"好用的脚本"到"专业的开源项目"的飞跃。**

## 复盘与方向决策

### Round 1 裁判反馈回顾

| 反馈 | 优先级 | 处理方式 |
|------|--------|---------|
| ❌ 缺少 CI（GitHub Actions） | **P0** | 搭建 3 版本 Python 矩阵 CI |
| ❌ 无 Git tag 和版本管理 | **P0** | 打 v0.2.0 tag |
| ❌ 测试文件仅 3 个（vs 红队 6 个） | **P1** | 拆分测试：新增 test_cli.py、test_config.py |
| ❌ 考虑增加子命令风格 | **P1** | 增加 `init`、`stats` 子命令（不破坏现有接口） |

### 差异化竞争分析

| 维度 | 红队 d irsort (推测) | 蓝队 fclean (已有) | 本轮新增 |
|------|---------------------|-------------------|---------|
| 工程化 | ✅ CI + tag | ❌ 无 CI | ✅ CI + tag |
| 安全 | ❌ 默认非 dry-run | ✅ 默认 dry-run | ✅ 不变 |
| 回滚 | ✅ 有 undo | ✅ 有 undo | ✅ 不变 |
| 美观 | ❌ 裸输出 | ✅ rich 彩色 | ✅ 不变 |
| 配置化 | ❌ 无 | ❌ 无 | ✅ **.fcleanrc 配置文件** |
| 统计 | ✅ stats 命令 | ❌ 无 | ✅ **fclean stats** |
| 排除 | ❌ 无 | ✅ --exclude/--exclude-dir | ✅ 不变 |
| 测试 | ✅ 56 个/6 文件 | ✅ 3 个测试文件 | ✅ 拆分到 5+ 文件 |

### 核心决策理由

1. **先补齐短板（工程化）再竞争差异化** — CI 和 Git tag 是评分直接扣分项，一条 CI 配置可以同时提升代码质量和项目完整性两个维度
2. **配置文件是天然差异化** — 所有同类工具（organize-cli、FileCleaner、甚至红队 d irsort）都不支持用户自定义规则。.fcleanrc 让用户定义自己的分类规则和排除模式，大幅提升实用性
3. **stats 命令承接 GitHub Trending 趋势** — 文件管理类工具（eza、fd、dust）都在提供统计/洞察能力，用户想知道"我文件夹里有什么"
4. **不重开项目** — fclean 方向正确（刚需 + 可差异化 + 第一轮已验证），迭代优于重开

## 验收标准

### P0 — MVP 核心（必须完成）

#### 配置系统（差异化核心）
- [ ] `fclean init` 在当前目录生成 `.fcleanrc` 配置文件（YAML 格式）
- [ ] `.fcleanrc` 支持：自定义分类规则（扩展名→目录映射）、排除模式、输出模板样式
- [ ] fclean 执行时自动检测当前目录或 `~/.fcleanrc` 的配置文件
- [ ] 配置优先级：命令行参数 > `.fcleanrc` > 默认规则

#### Stats 命令
- [ ] `fclean stats <path>` 显示目录文件统计：文件数量、总大小、按类型分布
- [ ] 支持表格输出和条形图（rich 实现）

#### 工程化（补齐短板）
- [ ] `.github/workflows/ci.yml`：支持 Python 3.9–3.12 矩阵测试 + lint（ruff）
- [ ] `coverage` 配置和 badge
- [ ] Git tag `v0.2.0` + release notes

### P1 — 体验完善
- [ ] 测试文件拆分：`test_cli.py`（CLI 参数测试）+ `test_config.py`（配置加载测试）
- [ ] 子命令风格支持：`fclean organize <path>` = `fclean <path>`（兼容旧语法）
- [ ] 进度指示：大目录整理时显示 spinner 或进度条
- [ ] `.gitignore` 中忽略 `.fcleanrc` 模板文件

### P2 — 锦上添花
- [ ] `fclean preview <path>` — 交互式预览，用户按 y/n 逐个确认文件移动
- [ ] `fclean config` — 查看当前生效的完整配置（合并命令行和配置文件后）
- [ ] 自动更新检测：启动时检查 PyPI 最新版本

## 技术选型

| 组件 | 选择 | 理由 |
|------|------|------|
| CLI 框架 | argparse (已有) | 稳定，无需迁移 |
| 配置格式 | YAML (PyYAML) | 比 JSON 更可读，适合手工编辑 |
| 彩色输出 | rich (已有) | 表格、进度条、条形图 |
| 测试 | pytest + pyfakefs (已有) | 不变 |
| CI | GitHub Actions | 标准选择 |
| Lint | ruff | 极快，已广泛采用 |
| 覆盖率 | pytest-cov | 与 CI 集成 |
| 进度展示 | rich.progress | 已引入 rich |

## 项目结构（本轮新增/修改）

```
project/
├── .github/
│   └── workflows/
│       └── ci.yml                        # NEW: CI 配置
├── pyproject.toml                        # UPDATED: 可选依赖 + tool config
├── .fcleanrc.example                     # NEW: 示例配置文件
├── src/
│   └── fclean/
│       ├── __init__.py                   # UPDATED: 版本号 v0.2.0
│       ├── __main__.py
│       ├── cli.py                        # UPDATED: 新增 init/stats 子命令
│       ├── organizer.py                  # UPDATED: 集成配置系统
│       ├── rules.py                      # UPDATED: 支持从配置文件加载
│       ├── undo.py                       # (不变)
│       └── config.py                     # NEW: .fcleanrc 加载/合并/验证
└── tests/
    ├── __init__.py
    ├── test_organizer.py                 # (不变)
    ├── test_rules.py                     # UPDATED: 测试配置驱动规则
    ├── test_undo.py                      # (不变)
    ├── test_cli.py                       # NEW: CLI 参数解析测试
    └── test_config.py                    # NEW: 配置加载/合并测试
```

## 差异化竞争要点

1. **工程化领先** — 补齐 CI + Git tag + 覆盖率后，项目完整性从 7→9 分
2. **配置化是护城河** — .fcleanrc 让用户"写一次配置，永久使用"，切换成本高
3. **Stats 打痛点** — 用户经常想知道"我下载文件夹为什么 50G？"，stats 回答这个问题
4. **保持安全口碑** — 默认 dry-run + undo 回滚，这是用户选择 fclean 而不是写 rm -rf 的核心原因
5. **子命令架构可扩展** — 为后续 `fclean watch`（自动监控整理）、`fclean dedup`（去重）留出架构空间

## 版本规划

- v0.1.0 — 已发布（Round 1 MVP）
- **v0.2.0 — 本轮目标（配置系统 + CI + stats）**
- v0.3.0 — 未来规划（watch 模式 + 去重 + 交互式 UI）
