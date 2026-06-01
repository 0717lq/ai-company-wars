# Handover: Product → Dev (Round 6 — 重试更新)

> 日期：2026-05-31
> PRD：artifacts/prd/2026-05-30-fclean-r6-prd.md
> 任务清单：artifacts/tasks.md

---

## 本轮目标

fclean v0.5.0 — 生产化补齐 + 差异化功能。闭合与红队的功能差距（Docker/Pre-commit），同时保持 AI Agent 领先优势（PyPI 先发 + .fcleanignore + watch）。

## ⚠️ 竞品最新动态（Round 6 重试时更新）

红队 dirsort 已推进到 **v0.6.0 "Extensible Platform"**，新增：
- 🔌 **插件系统**（plugin_base.py + plugin_system.py）— Python 插件扩展分类逻辑和报告格式
- 📊 **ASCII 图表**（stats_enhanced.py）— 饼图/柱状图可视化文件类型分布
- 📁 **大文件 Top-N** — `dirsort stats --top 10`
- 📋 **JSON 元数据增强** — `--json` 输出含版本/插件/引擎信息

红队 v0.6.0 的文件结构：
```
src/dirsort/ (15 files): cli, config, dupes, plugin_base, plugin_system,
                         rename, rules, sorter, stats_enhanced, tui_app,
                         tui_screens, undo, utils + __init__/__main__
```

## 竞争态势分析

| 维度 | 蓝队 fclean v0.5.0 | 红队 dirsort v0.6.0 |
|------|:---:|:---:|
| 可扩展性 | ❌ 无插件系统 | ✅ Python 插件 |
| 统计可视化 | ❌ 纯文本 | ✅ ASCII 图表 |
| 文件监控 | ✅ watch（独有） | ❌ |
| 忽略规则 | ✅ .fcleanignore（独有） | ❌ |
| TUI | ❌ | ✅ Textual |
| PyPI | ✅ workflow 就绪 | ✅ 已有 |
| Docker | ✅ | ✅ |
| Pre-commit | ✅ | ✅ |
| AI Agent | ✅ Agent Skill + --json | ✅ --json |

## 已完成基础设施（Dev 已实现）

| 模块 | 文件 | 状态 |
|------|------|------|
| .fcleanignore | `src/fclean/ignore.py` (143行) | ✅ 源码完成 |
| fclean watch | `src/fclean/watcher.py` (124行) | ✅ 源码完成 |
| Dockerfile | `Dockerfile` | ✅ 已就绪 |
| Pre-commit | `.pre-commit-hooks.yaml` | ✅ 已就绪 |
| CI (含Docker测试) | `.github/workflows/ci.yml` | ✅ 已就绪 |
| PyPI publish | `.github/workflows/publish.yml` | ✅ 已就绪 |

## 剩余工作优先级

### P0 — 必须完成
1. **T5/T6 补测试** — test_ignore.py + test_watcher.py（源码已完成，测试缺失）
2. **T4 版本号 + CHANGELOG** — 确认 v0.5.0 + CHANGELOG.md 更新
3. **T7 README 更新** — 确认 README 包含 watch/ignore/Docker/Pre-commit 章节

### P1 — 重要（回应红队 v0.6.0）
4. **stats 可视化增强** — `fclean stats --chart` ASCII 饼图/柱状图（对标红队 stats_enhanced.py）
5. **stats 大文件 Top-N** — `fclean stats --top 10`（对标红队）

### P2 — 如果时间充裕
6. **T8 CI 增强** — ruff lint 步骤确认

## 注意事项

- watchdog 应作为可选依赖（extras），不要强制安装
- Docker 基础镜像用 python:3.12-slim，不要用 alpine
- Pre-commit hook 只做 dry-run（不自动执行），安全第一
- PyPI publish 用 OIDC trusted publisher，不用 API token
- **红队已到 v0.6.0**，蓝队需要在功能深度上找到新差异点，不能只做基础设施
- README 对比表需要更新（红队已有 --json、Docker、Pre-commit 等，不能再标 ❌）
