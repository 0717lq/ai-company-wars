# rag-decompose v0.2.0 — Sprint 任务

## P0（必须完成）

### T1: 清理 Ruff 错误（19→0）
- **内容**: 删除未使用导入（F401）、修复类型注解（UP045）、修复 f-string（F541）、修复 zip 严格参数（B905）、修复 assert False（B011）
- **涉及文件**: `src/rag_decompose/cli.py`, `decomposer.py`, `models.py`, `strategies.py`, `tests/test_cli.py`, `tests/test_decomposer.py`, `tests/test_strategies.py`
- **验收**: `ruff check src/ tests/` 零错误

### T2: 补充 CLI 测试（cli.py 0%→60%+）
- **内容**: 测试 decompose/batch/bench/strategies 四个子命令的主路径和 --json 输出
- **涉及文件**: `tests/test_cli.py`
- **验收**: cli.py 覆盖率 ≥ 60%

### T3: 补充 strategies.py 测试（72%→85%+）
- **内容**: 补充 LLM 策略测试（mock openai 调用）、覆盖策略工厂缺失分支
- **涉及文件**: `tests/test_strategies.py`
- **验收**: strategies.py 覆盖率 ≥ 85%

### T4: 补充 models.py 测试（96%→100%）
- **内容**: 覆盖 line 84 和 93 的缺失分支
- **涉及文件**: `tests/test_strategies.py` 或新增 `tests/test_models.py`
- **验收**: models.py 覆盖率 100%

## P1（体验完善）

### T5: 版本号升级 + CHANGELOG 丰富化
- **内容**: pyproject.toml 版本升至 0.2.0，CHANGELOG.md 增加详细变更记录
- **涉及文件**: `pyproject.toml`, `CHANGELOG.md`
- **验收**: CHANGELOG 有完整 v0.2.0 记录

### T6: 总体覆盖率验证
- **内容**: `pytest --cov=rag_decompose` 确认总体覆盖率 ≥ 80%
- **验收**: TOTAL ≥ 80%

## P2（锦上添花）

### T7: README 更新
- **内容**: 更新 README 中的版本号和覆盖率数据
- **涉及文件**: `README.md`, `README.en.md`
