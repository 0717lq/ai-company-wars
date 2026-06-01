# dirsort v0.5.0 — 代码质量提升

## 变更内容

### 代码质量
- 新增 Ruff 配置（pycodestyle, pyflakes, isort, pep8-naming, pyupgrade, flake8-bugbear）
- 自动修复 35+ 个 lint 问题
- 清理 `_format_bytes`/`_format_size` 代码重复 → 统一使用 `utils.format_bytes`
- 添加 `.editorconfig` 编码风格配置
- 添加 `ruff>=0.3` 到 dev 可选依赖

### Bug 修复
- 修复 `cli.py` 中 `chart` 未定义变量 Bug（stats 命令）
- 修复 `rename.py` 闭包捕获循环变量的 Bug
- 修复 `__init__.py` 版本号 0.3.0 → 0.5.0

### 测试
- 测试修复：`test_format_size` 适配重构后的 `format_bytes`
- 138 个测试全部通过

## 安装

```bash
pip install dirsort[all]
# 或从源码安装
pip install "dirsort[all] @ git+https://github.com/0717lq/ai-company-wars-red@v0.5.0"
```
