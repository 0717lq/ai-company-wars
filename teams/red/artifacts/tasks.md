# dirsort v0.6.0 — Sprint 任务

> 日期: 2026-05-30
> 轮次: Round 6
> PRD: `teams/red/artifacts/prd/2026-05-30-dirsort-v6-prd.md`

---

## P0 — 必须完成（MVP 核心）

### T1: 插件基类定义 [1h]
- **内容**: 创建 `src/dirsort/plugin_base.py`，定义 `PluginBase` 抽象基类
  - `classify(file_path: Path) -> Optional[str]` hook — 自定义分类规则
  - `generate_report(results: dict) -> str` hook — 自定义报告格式
  - `name` / `version` / `description` 属性
- **涉及文件**: `src/dirsort/plugin_base.py` (new)
- **验收**: PluginBase 可以被 import，抽象方法定义完整

### T2: 插件加载引擎 [2h]
- **内容**: 创建 `src/dirsort/plugin_system.py`，实现插件加载/注册/执行
  - 从 `~/.dirsort/plugins/` 加载 `.py` 文件
  - 使用 importlib 动态导入
  - 插件注册表（name -> instance）
  - `classify` hook 调用链：内置规则 → 插件链（first match wins）
  - `report` hook 调用链：默认报告 → 插件增强
  - 安全隔离：插件异常不影响主流程（try/except + 日志）
- **涉及文件**: `src/dirsort/plugin_system.py` (new), `src/dirsort/plugin_base.py`
- **验收**: 可以加载示例插件并执行 classify hook

### T3: CLI 插件子命令 [1.5h]
- **内容**: 在 `cli.py` 中新增 `plugin` 子命令组
  - `dirsort plugin list` — 列出已安装插件（名称、版本、描述）
  - `dirsort plugin install <path>` — 复制 .py 文件到插件目录
  - `dirsort plugin create <name>` — 生成插件模板脚手架
  - `dirsort plugin info <name>` — 显示插件详情
- **涉及文件**: `src/dirsort/cli.py` (modify)
- **验收**: 四个子命令均可执行，输出格式正确

### T4: 示例插件 [0.5h]
- **内容**: 创建示例插件 `plugins/example_classifier.py`
  - 演示 classify hook：按文件大小分类（small/medium/large）
  - 包含 docstring 说明如何编写插件
- **涉及文件**: `plugins/example_classifier.py` (new)
- **验收**: `dirsort plugin install plugins/example_classifier.py && dirsort plugin list` 能看到

### T5: 插件系统测试 [2h]
- **内容**: 全面测试插件系统
  - test_plugin_base: 抽象基类定义正确
  - test_plugin_load: 动态加载 .py 文件
  - test_plugin_classify: classify hook 被正确调用
  - test_plugin_report: report hook 被正确调用
  - test_plugin_error_handling: 插件异常不影响主流程
  - test_plugin_cli_list/install/create: CLI 子命令
- **涉及文件**: `tests/test_plugin_system.py` (new)
- **验收**: 全部测试通过

### T6: Stats 增强 — ASCII 图表 [1.5h]
- **内容**: 创建 `src/dirsort/stats_enhanced.py`
  - ASCII 饼图渲染器（纯标准库，不依赖 rich.chart）
  - ASCII 柱状图渲染器
  - `dirsort stats --chart` — 显示文件类型分布饼图
  - `dirsort stats --top N` — 显示大文件 Top-N（默认 10）
  - 集成到现有 stats 命令
- **涉及文件**: `src/dirsort/stats_enhanced.py` (new), `src/dirsort/cli.py` (modify)
- **验收**: `dirsort stats --chart` 显示 ASCII 图表，`--top 5` 显示大文件

### T7: Stats 增强测试 [1h]
- **内容**: 测试 stats 增强功能
  - test_ascii_pie_chart: 饼图渲染正确
  - test_ascii_bar_chart: 柱状图渲染正确
  - test_top_files: Top-N 排序正确
  - test_stats_chart_cli: CLI 集成测试
- **涉及文件**: `tests/test_stats_enhanced.py` (new)
- **验收**: 全部测试通过

### T8: --json 元数据增强 [0.5h]
- **内容**: --json 输出增加元数据字段
  - `metadata.version` — dirsort 版本号
  - `metadata.plugins` — 已加载插件列表
  - `metadata.engine` — "dirsort/0.6.0"
- **涉及文件**: `src/dirsort/cli.py` (modify), `src/dirsort/utils.py` (modify)
- **验收**: `dirsort sort --json .` 输出包含 metadata 字段

---

## P1 — 体验完善

### T9: 插件文档 [1h]
- **内容**: 编写插件开发指南
  - README 中新增 "Plugin System" 章节
  - 包含：插件结构、hook 说明、示例代码、安装方法
  - README.en.md 英文版同步
- **涉及文件**: `README.md`, `README.en.md`
- **验收**: 文档内容准确，中英文一致

### T10: 英文 README 同步 v0.6.0 [1h]
- **内容**: 将 v0.5.0 和 v0.6.0 的所有功能更新同步到 README.en.md
  - 插件系统、Stats 增强、--json 增强
  - 更新版本号、测试数、功能表
- **涉及文件**: `README.en.md` (modify)
- **验收**: README.en.md 内容与中文版一致

### T11: pyproject.toml + 版本更新 [0.5h]
- **内容**: 更新版本号到 0.6.0，更新 keywords/classifiers
  - 新增 keyword: "plugin", "extensible", "stats", "chart"
- **涉及文件**: `pyproject.toml`
- **验收**: `dirsort --version` 显示 0.6.0

---

## P2 — 锦上添花

### T12: 插件热重载 [1h]
- **内容**: `dirsort plugin reload` — 不重启 CLI 重新加载插件
- **涉及文件**: `src/dirsort/plugin_system.py`, `src/dirsort/cli.py`
- **验收**: 修改插件文件后 `reload` 生效

### T13: Stats JSON 输出 [0.5h]
- **内容**: `dirsort stats --json` — 统计数据以 JSON 格式输出
- **涉及文件**: `src/dirsort/stats_enhanced.py`
- **验收**: `dirsort stats --json` 输出合法 JSON

---

## 预估总工时

| 优先级 | 任务数 | 工时 |
|--------|--------|------|
| P0 | 8 | 11h |
| P1 | 3 | 2.5h |
| P2 | 2 | 1.5h |
| **合计** | **13** | **15h** |

## 开发顺序建议

1. T1 → T2 → T3 → T4 → T5（插件系统链路，先行验证）
2. T6 → T7（Stats 增强，独立模块）
3. T8（--json 增强，依赖 T2 插件信息）
4. T9 → T10 → T11（文档和版本更新）
5. T12 → T13（P2 可选）
