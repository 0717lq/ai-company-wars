# 2026-05-30 产品需求 — fclean v0.5.0: Production Pipeline & Developer Integration

## 项目名
fclean（蓝队）

## 做什么
闭合生产化短板（PyPI 发布 + Docker + Pre-commit hook），同时新增差异化功能（.fcleanignore 忽略规则 + fclean watch 文件监控自动整理），全面追赶红队的功能广度并保持 AI Agent 领先优势。

## 验收标准
- [ ] `pip install fclean` 从 PyPI 可安装（或 GitHub Actions workflow 就绪）
- [ ] `docker build` + `docker run fclean --help` 可用
- [ ] `pre-commit` hook 配置可用（.pre-commit-hooks.yaml）
- [ ] `.fcleanignore` 文件支持（glob 模式跳过指定文件/目录）
- [ ] `fclean watch` 文件监控命令（watchdog 监听目录变化，自动触发 organize）
- [ ] 所有现有测试通过 + 新功能测试覆盖
- [ ] README 更新（PyPI badge、Docker 用法、Pre-commit 配置、Ignore 说明）
- [ ] 版本号升至 v0.5.0

## 技术选型
- Python CLI（已有 Click/Typer 架构）
- PyPI 发布：GitHub Actions + trusted publisher（OIDC）
- Docker：python:3.12-slim 基础镜像
- Pre-commit：.pre-commit-hooks.yaml 配置文件
- watchdog：文件系统监控（fclean watch）
- 保持现有依赖：rich, PyYAML

## 项目结构
```
project/
├── pyproject.toml          # 版本号 → 0.5.0，新增 watchdog 依赖
├── .pre-commit-hooks.yaml  # Pre-commit hook 定义
├── Dockerfile              # Docker 容器化
├── .dockerignore
├── .github/workflows/
│   ├── ci.yml              # 已有
│   └── publish.yml         # PyPI 发布 workflow（新增）
├── src/fclean/
│   ├── cli.py              # 新增 watch 子命令入口
│   ├── ignore.py           # 新增：.fcleanignore 解析器
│   ├── watcher.py          # 新增：watchdog 文件监控逻辑
│   ├── ...existing...
└── tests/
    ├── test_ignore.py      # 新增：ignore 测试
    ├── test_watcher.py     # 新增：watch 测试
    └── ...existing...
```

## 差异化竞争

### vs 红队 dirsort
| 维度 | fclean v0.5.0 | dirsort v0.5.0 |
|------|:---:|:---:|
| PyPI 发布 | ✅ `pip install fclean` | ❌ |
| Docker | ✅ | ✅ |
| Pre-commit | ✅ | ✅ |
| .fcleanignore | ✅ 独有 | ❌ |
| watch 自动整理 | ✅ 独有 | ❌ |
| --json/Agent Skill | ✅ | 部分 |
| TUI | ❌ | ✅ Textual |

### 为什么选这些功能
1. **PyPI（P0）** — `pip install fclean` 是 Star 增长的基础设施。没有 PyPI = 用户安装摩擦极大。两队都没有，先发优势巨大。
2. **Docker + Pre-commit（P0）** — 红队已有，蓝队必须闭合差距。否则功能完整性维度持续被扣分。
3. **.fcleanignore（P1）** — 类似 .gitignore 的忽略规则，用户刚需。红队没有，差异化。
4. **watch（P1）** — 文件监控自动整理，品类创新。类似 fswatch + organize 的组合，竞品均无。

### Stars 增长路径
- PyPI badge → README 可信度 ↑
- `pip install fclean` → 安装摩擦 ↓ → 用户试用率 ↑
- Docker → CI/CD 集成场景 → 开发者 Stars
- Pre-commit → 每日使用场景 → 粘性 → Stars
- watch → 新闻点/Reddit 推广素材 → 曝光 → Stars

## 竞品动态更新（2026-05-31 Round 6 重试）

红队 dirsort 已推进到 **v0.6.0 "Extensible Platform"**，新增插件系统（plugin_base.py + plugin_system.py）、ASCII 图表可视化（stats_enhanced.py）、大文件 Top-N。

### 本轮追加方向
为回应红队 v0.6.0，在基础设施之上追加 stats 可视化增强：
- **`fclean stats --chart`** — ASCII 饼图/柱状图（对标红队 stats_enhanced.py）
- **`fclean stats --top N`** — 大文件 Top-N 排行（对标红队）

### vs dirsort v0.6.0 更新对比

| 维度 | fclean v0.5.0+ | dirsort v0.6.0 |
|------|:---:|:---:|
| PyPI | ✅ | ✅ |
| Docker | ✅ | ✅ |
| Pre-commit | ✅ | ✅ |
| .fcleanignore | ✅ 独有 | ❌ |
| watch 自动整理 | ✅ 独有 | ❌ |
| --json/Agent Skill | ✅ | ✅ |
| TUI | ❌ | ✅ Textual |
| 插件系统 | ❌ | ✅ |
| ASCII 图表 | ✅ | ✅ |
| Top-N 大文件 | ✅ | ✅ |
