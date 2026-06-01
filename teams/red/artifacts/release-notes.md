# dirsort v0.7.0 — Plugin Ecosystem

> Release: 2026-06-01 | Team: Red | Round: 7

## Highlights

### 3 Practical Plugins (裁判要求"让插件系统产生实际价值")

| Plugin | Description | Hook |
|--------|-------------|------|
| `date-classifier` | 按修改日期分类（今天/本周/本月/更早） | classify |
| `project-classifier` | 按语言/项目类型分类（20+ 语言识别） | classify |
| `duplicate-reporter` | 存储健康报告（大文件检测 + 扩展名空间 Top-5） | report |

### Engineering Improvements

- **CHANGELOG.md**: 规范版本记录，覆盖 v0.1.0 ~ v0.7.0
- **PyPI publish workflow**: `.github/workflows/publish.yml` — OIDC Trusted Publisher
- **Version bump**: 0.6.0 → 0.7.0（`__init__.py` + `pyproject.toml` 一致）

### Quality

- 229 tests all passing (22 new plugin tests)
- Ruff lint: all checks passed
- Code changes: 13 files, +885 / -167

## Stats

| Metric | Value |
|--------|-------|
| Total tests | 229 |
| New tests | 22 |
| Files changed | 13 |
| Lines added | 885 |
| Lines removed | 167 |

## Known Limitations

- README.md / README.en.md v0.7.0 章节待 Growth Agent 更新
- 插件优先级/排序机制未实现（当前按字母序加载）
- `.github/workflows/*` 受 PAT workflow scope 限制，CI 文件需后续手动推送
