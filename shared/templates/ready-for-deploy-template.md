---
round_id: ""        # 必填
created_at: ""      # 必填，ISO 时间戳
team: ""            # "red" 或 "blue"
author: "dev"
source_prd: ""      # 对应的 PRD 文件名
---

# Ready for Deploy — {round_id}

## 本轮已实现内容
{列出本轮实现的功能和改动}

- {功能1}
- {功能2}
- {Bug 修复}

## 测试结果

```
# pytest 运行结果示例
$ python -m pytest -v
============================= test session starts =============================
collected 15 items

tests/test_cli.py::test_basic ... PASSED                                   [6%]
tests/test_cli.py::test_sort ... PASSED                                    [13%]
...
============================= 15 passed in 2.34s =============================
```

- 总用例数：{N}
- 通过：{N}
- 失败：{0}
- 覆盖率：{N%}

## 已知问题
{如果有的话，列出已知问题或限制}

- {问题1 — 严重程度: 低/中/高}
- {问题2 — 严重程度: 低/中/高}

## 发布建议
- **版本号建议**: {例如：v0.1.0 → v0.2.0}
- **是否建议阻塞发布**: {是 / 否}
- **阻塞原因**: {如果有的话}

## Release Notes 要点
{建议 DevOps 在 release notes 中强调的内容}

## 检查清单
- [ ] 所有 P0 任务已完成
- [ ] 测试全部通过
- [ ] 已知问题已记录
- [ ] docs/ 已更新
- [ ] 代码已本地 commit
