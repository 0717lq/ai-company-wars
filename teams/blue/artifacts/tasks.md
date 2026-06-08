# Sprint 11 任务清单 — rag-builder v0.4.0 质量打磨

> 本轮目标：修复裁判反馈的 3 个问题，零新功能，纯质量迭代。

## P0 — 必须完成

### T1: 修复 vector_store.py N803 命名问题
- **内容**：`_create_collection` 方法的 4 个参数（`Collection`, `CollectionSchema`, `DataType`, `FieldSchema`）改为小写（`collection_cls`, `collection_schema_cls`, `data_type_cls`, `field_schema_cls`）。同步更新所有调用处。
- **预估**：15 分钟
- **涉及文件**：`src/rag_builder/vector_store.py`
- **验收**：`ruff check src/` 零 N803 错误

### T2: 提高 vector_store.py 测试覆盖率到 80%+
- **内容**：为 `MilvusStore` 和 `ChromaStore` 补充单元测试，重点覆盖：
  - `add_documents()` 成功/失败路径
  - `search()` 各种参数组合
  - `_create_collection()` mock 测试
  - `__init__()` 异常处理（连接失败等）
- **预估**：45 分钟
- **涉及文件**：`tests/test_vector_store.py`
- **验收**：`pytest tests/test_vector_store.py --cov=rag_builder.vector_store --cov-report=term-missing` 显示 ≥ 80%

### T3: 新增端到端集成测试
- **内容**：创建 `tests/test_integration.py`，覆盖完整 RAG 流程：
  - 配置验证 → scaffold 生成 → 文件创建 → 验证结构
  - 嵌入生成 → 向量存储 → 检索 → 结果验证
  - diagnose 命令完整执行
  - benchmark 命令基本流程
- **预估**：45 分钟
- **涉及文件**：`tests/test_integration.py`
- **验收**：≥ 5 个集成测试，全部通过

## P1 — 体验完善

### T4: 全量 Ruff 检查通过
- **内容**：修复 T1 后运行 `ruff check src/ tests/`，确保零错误零警告。如有其他问题一并修复。
- **预估**：15 分钟
- **涉及文件**：视检查结果
- **验收**：`ruff check src/ tests/` 输出 `All checks passed!`

### T5: 版本号升级 + CHANGELOG 更新
- **内容**：`pyproject.toml` 版本号改为 `0.4.0`，CHANGELOG 追加 v0.4.0 条目（质量迭代：N803 修复、覆盖率提升、集成测试）。
- **预估**：10 分钟
- **涉及文件**：`pyproject.toml`, `CHANGELOG.md`
- **验收**：`rag-builder --version` 输出 `0.4.0`

## P2 — 如果时间有余

### T6: README 补充质量指标
- **内容**：在 README 中添加测试覆盖率 badge 和 Ruff badge，展示代码质量。
- **预估**：10 分钟
- **涉及文件**：`README.md`
