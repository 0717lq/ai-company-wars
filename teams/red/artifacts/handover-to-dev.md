# Handover: Product → Dev (Round 11)

## 本轮方向
纯质量迭代。修复测试覆盖率（58%→80%+）、清理 Ruff 问题（19→0）、提升代码质量。

## 为什么选这个方向
- 裁判明确指出覆盖率 58% 和 Ruff 错误是红队最大短板
- 蓝队覆盖率 82%，红队 58% = 代码质量维度直接差 7 分
- 补齐覆盖率是最快追分路径，不需要新功能

## 任务文件
`teams/red/artifacts/tasks.md` — 7 个任务（P0:4 + P1:2 + P2:1）

## 关键修复项

### Ruff 问题清单（19 个）
1. **F401** 未使用导入（7个）: cli.py:11, decomposer.py:10-13, models.py:6,8, test_strategies.py:5
2. **UP045** 类型注解（3个）: decomposer.py:50, strategies.py:246,247
3. **F541** 空 f-string（7个）: test_cli.py:23,36,59,76, test_decomposer.py:33,60
4. **B905** zip 缺 strict 参数（1个）: test_decomposer.py:34
5. **B011** assert False（1个）: test_strategies.py:123

### 测试覆盖率缺口
- `cli.py`: 83 行 0% 覆盖 → 需要 subprocess 测试（当前已用 subprocess，但覆盖不计入）
- `strategies.py`: LLM 策略 249-317 行未覆盖 → 需要 mock openai
- `models.py`: line 84, 93 未覆盖 → 需要补充边界测试
- `__main__.py`: 3 行 0% → 可忽略或加简单测试

## 注意事项
1. **不要重写代码** — 只修复 lint 问题和补测试
2. **cli.py 覆盖率** — subprocess 调用不计入 pytest-cov，需要改用 `from rag_decompose.cli import main` + mock sys.argv 的方式测试
3. **LLM 策略测试** — 用 unittest.mock.patch mock openai 调用，不真正调 API
4. **版本号升至 0.2.0** — 在 pyproject.toml 和 __init__.py 中同步
5. **所有现有测试必须继续通过** — 先跑一遍确认基线再改

## 验收标准
1. `ruff check src/ tests/` 零错误
2. `pytest --cov=rag_decompose` 覆盖率 ≥ 80%
3. 所有测试通过
4. 版本号 0.2.0，CHANGELOG 更新
