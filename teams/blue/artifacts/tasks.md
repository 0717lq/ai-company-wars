# fclean v0.5.0 — Sprint 6 任务清单（Round 6 重试更新）

> 日期：2026-05-31
> PRD：artifacts/prd/2026-05-30-fclean-r6-prd.md
> 状态更新：T5/T6 源码已完成；基础设施（Docker/CI/PyPI/Pre-commit）全部就绪
> 竞品动态：红队 dirsort v0.6.0 已发布（插件系统+ASCII图表+Top-N）

---

## P0 — 必须完成（MVP 核心）

### T1: PyPI 发布配置 ✅ 已就绪
- **状态**：publish.yml 已存在，pyproject.toml 元数据完整
- **剩余**：DevOps 需要在 PyPI 创建项目 + 配置 Trusted Publisher

### T2: Docker 容器化 ✅ 已就绪
- **状态**：Dockerfile 已存在（python:3.12-slim），CI 含 Docker build 测试

### T3: Pre-commit Hook ✅ 已就绪
- **状态**：.pre-commit-hooks.yaml 已存在

### T4: 版本号确认 + CHANGELOG ⬜
- **内容**：确认 pyproject.toml version=0.5.0，CHANGELOG.md 新增 v0.5.0 完整条目
- **涉及文件**：`pyproject.toml`, `CHANGELOG.md`
- **验收**：`fclean --version` 输出 0.5.0；CHANGELOG 含所有新功能
- **预估**：15min

### T5: .fcleanignore 测试 ⬜
- **内容**：编写 test_ignore.py，覆盖 glob 模式、取反规则、目录模式
- **涉及文件**：`tests/test_ignore.py`
- **验收**：测试覆盖 *.log、**/*.tmp、!important.log、目录后缀等场景
- **预估**：30min

### T6: fclean watch 测试 ⬜
- **内容**：编写 test_watcher.py，测试 watchdog 监听、防抖、忽略规则集成
- **涉及文件**：`tests/test_watcher.py`
- **验收**：测试覆盖新文件触发 organize、.fcleanignore 过滤、优雅退出
- **预估**：30min

---

## P1 — 体验完善（回应红队 v0.6.0）

### T7: stats 可视化增强 🆕
- **内容**：`fclean stats --chart` 输出 ASCII 饼图/柱状图，可视化文件类型分布
- **涉及文件**：`src/fclean/cli.py`（新增 --chart 参数），`src/fclean/stats_viz.py`（新增）
- **验收**：`fclean stats --chart ~/Downloads` 输出 ASCII 饼图；`--json` 模式忽略 --chart
- **预估**：1h
- **竞品对标**：红队 dirsort v0.6.0 的 stats_enhanced.py

### T8: stats 大文件 Top-N 🆕
- **内容**：`fclean stats --top N` 列出占用空间最大的 N 个文件
- **涉及文件**：`src/fclean/cli.py`（新增 --top 参数），`src/fclean/stats_viz.py`
- **验收**：`fclean stats --top 10 ~/Downloads` 输出文件名+大小排序列表
- **预估**：30min
- **竞品对标**：红队 dirsort v0.6.0 的 `dirsort stats --top 10`

### T9: README 更新 ⬜
- **内容**：确认 README 包含 watch/ignore/Docker/Pre-commit/stats chart 章节
- **涉及文件**：`README.md`
- **验收**：README 包含所有新功能使用示例；对比表更新（红队已有 --json/Docker/Pre-commit）
- **预估**：1h

---

## P2 — 锦上添花

### T10: CI 增强 ⬜
- **内容**：确认 CI 含 ruff lint + Docker build 测试（已就绪，验证即可）
- **涉及文件**：`.github/workflows/ci.yml`
- **验收**：CI 绿灯

---

## 依赖关系

```
T4 (版本号) ──┐
T5 (ignore测试) ──┤
T6 (watch测试) ──┼── T9 (README) ── 完成
T7 (stats chart) ─┤
T8 (stats top-N) ─┘
```

T4-T8 可并行开发。T9 在最后统一更新 README。

## 总预估工时
约 3.5 小时（基础设施已完成，主要工作在测试+stats增强+README）
