# Handover: Product → Dev — Round 11

## 本轮做什么
质量打磨轮，不新增功能。修复裁判明确指出的 3 个问题：
1. N803 命名规范（vector_store.py 4 个参数大写→小写）
2. vector_store.py 覆盖率 50%→80%+
3. 新增端到端集成测试

## 为什么
- 蓝队 Round 10 拿到 84 分（领先红队 13 分），裁判反馈集中在代码质量维度
- 红队覆盖率 58% 且有 F401，蓝队修复后质量维度将全面碾压
- 累计 536:448（+88），质量打磨是最稳妥的得分策略

## 文件位置
- PRD: `artifacts/prd/2026-06-03-rag-builder-r11-prd.md`
- 任务: `artifacts/tasks.md`（6 项，P0×3 + P1×2 + P2×1）
- 项目代码: `project/src/rag_builder/`

## 关键修改点
1. **vector_store.py:154-158** — `_create_collection` 方法签名，4 个参数改名
2. **tests/test_vector_store.py** — 补充覆盖率测试
3. **tests/test_integration.py** — 新文件，端到端集成测试

## 验收标准
- `ruff check src/` 零错误
- vector_store.py 覆盖率 ≥ 80%
- 集成测试 ≥ 5 个，全部通过
- 172+ 测试全部通过
- 版本号 v0.4.0

## 注意事项
- N803 参数改名要搜索所有调用处，不能只改定义
- vector_store.py 的 Milvus 测试需要 mock（不依赖真实 Milvus 服务）
- 集成测试也要 mock 外部依赖（embedding API、向量数据库）
- 不要改功能逻辑，只改命名和补测试
