# 2026-06-03 产品需求 — rag-decompose

## 项目名
rag-decompose — RAG 查询分解 CLI 工具

## 做什么
创建一个 RAG 查询分解工具，将复杂用户问题拆分为多个子查询，提升检索召回率。提供 4 种分解策略（simple/multihop/atomic/llm），支持 CLI 和 Python API，所有规则策略零依赖。

## 验收标准
- [x] 4 种分解策略实现（simple/multihop/atomic/llm）
- [x] CLI 4 个命令（decompose/batch/bench/strategies）
- [x] `--json` 输出支持
- [x] Python API（QueryDecomposer 类 + benchmark 函数）
- [x] 测试全部通过（34 个测试）
- [x] MIT LICENSE
- [x] CHANGELOG.md
- [x] README.md + README.en.md
- [x] SKILL.md（Hermes Agent 技能定义）
- [x] docs/ 三件套

## 技术选型
- Python 3.10+ + 标准库（核心零依赖）
- argparse CLI（无外部 CLI 框架依赖）
- openai（可选，仅 LLM 策略需要）
- pytest + pytest-cov + ruff（开发依赖）

## 项目结构
```
rag-decompose/
├── pyproject.toml
├── README.md / README.en.md
├── LICENSE / CHANGELOG.md
├── SKILL.md
├── docs/
├── src/rag_decompose/
│   ├── cli.py          # CLI 入口
│   ├── decomposer.py   # 核心分解器
│   ├── models.py       # 数据模型
│   └── strategies.py   # 4 种策略
└── tests/
```

## 差异化竞争

### 与蓝队 rag-builder 的关系
rag-decompose 专注查询分解，rag-builder 专注流水线构建。互补而非竞争。

### 独家卖点
1. **零依赖核心** — 3 种规则策略纯标准库，安装即可用
2. **多策略选择** — 4 种策略覆盖不同场景（simple/multihop/atomic/llm）
3. **CLI + Python API 双入口** — 既能命令行用也能代码集成
4. **内置基准测试** — `bench` 命令对比策略效果
5. **Hermes Agent 技能** — SKILL.md 含 7 个常见陷阱和 RAG 集成示例

### 与竞品对比
| 特性 | rag-decompose | 其他工具 |
|------|:---:|:---:|
| 零依赖核心 | ✅ | ❌ |
| 多策略选择 | 4 种 | 1-2 种 |
| CLI + Python API | ✅ | 仅 API |
| 内置基准测试 | ✅ | ❌ |
| Hermes Agent Skill | ✅ | ❌ |
