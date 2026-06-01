# Round 6 — Product → Dev 交接

> 日期: 2026-05-30
> 版本: dirsort v0.6.0 "Extensible Platform"

## 本轮做什么

**两大新功能**:
1. **插件系统** — 让用户用 Python 扩展 dirsort 的分类和报告逻辑
2. **Stats 增强** — ASCII 图表可视化 + 大文件 Top-N

## 为什么选这个

- Round 5 纯质量迭代导致功能维度被蓝队反超（52 vs 56）
- 裁判明确要求"下一轮必须产出新功能"
- 插件系统是**平台级差异化**，蓝队 fclean 和 organize(3K⭐) 都没有
- Stats 图表有视觉冲击力，适合 README 和社交媒体展示

## 文件在哪里

| 文件 | 路径 |
|------|------|
| PRD | `teams/red/artifacts/prd/2026-05-30-dirsort-v6-prd.md` |
| 任务 | `teams/red/artifacts/tasks.md` |
| 项目代码 | `teams/red/project/` |
| 插件示例 | `teams/red/project/plugins/` |

## 验收标准

1. `dirsort plugin list/install/create/info` 四个子命令可用
2. 插件 classify hook 能覆盖内置分类规则
3. 插件异常不影响主流程（安全隔离）
4. `dirsort stats --chart` 显示 ASCII 图表
5. `dirsort stats --top N` 显示大文件排行
6. `--json` 输出包含 metadata.version/plugins 字段
7. 全部新旧测试通过
8. Ruff lint 通过

## 注意事项

- **不要动现有功能的接口** — sort/dupes/rename/tui/undo 保持不变
- **插件目录默认 `~/.dirsort/plugins/`** — 首次运行自动创建
- **ASCII 图表不依赖外部库** — 纯 Python 字符画，保持零依赖策略
- **先跑测试再提交** — 避免 Round 5 的"测试中断"问题
- **英文 README 同步** — 这是裁判指出的短板，必须修


---

## 2026-05-31 补充 — 执行状态

### Dev 已开始实现
Git status 显示以下文件已创建但未提交：
- `src/dirsort/plugin_base.py` — 插件基类
- `src/dirsort/plugin_system.py` — 插件加载引擎
- `src/dirsort/stats_enhanced.py` — 增强统计
- `tests/test_plugin_system.py` — 插件测试
- `tests/test_stats_enhanced.py` — 统计测试
- `plugins/` — 示例插件目录

版本号已升至 0.6.0。

### 蓝队竞态提醒
蓝队 v0.5.0 已推进到 Production Pipeline（PyPI/Docker/Pre-commit/watch）。
**红队插件系统是唯一未被追赶的独家功能**，实现质量必须到位。

### 遗留问题
- `=0.3` 是残留文件，应在 .gitignore 或删除
- README.md 已修改但未确认内容
