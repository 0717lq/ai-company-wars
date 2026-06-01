# fclean v0.4.0 — AI Agent First

## 新功能 ✨

- **--json 输出**: `fclean dupes --json` 支持 JSON 格式输出，便于 AI Agent 解析和处理
- **Duplicates (SHA-256) 重复检测**: `fclean dupes` 命令——基于 SHA-256 哈希的文件重复检测
  - 多种删除策略：newest（删最新）、oldest（删最旧）、all（删所有副本）
  - `--min-size` 过滤小文件，`--json` 输出
  - dry-run 默认安全预览
- **Shell 补全**: `fclean completion` 命令——支持 bash、zsh、fish 自动补全
- **Agent Skill**: 新增 Hermes Agent Skill（SKILL.md），AI Agent 可直接调用 fclean
- **README 全面优化**: 徽章、对比表、新增特性文档、优化排版

## 测试 🧪

- 176 个测试全部通过 ✅
- 覆盖 CLI、配置、重复检测、重命名、边界情况、回滚等全功能

---

# fclean v0.4.0 — AI Agent First (English)

## New Features

- **--json output**: `fclean dupes --json` outputs JSON for AI Agent consumption
- **Duplicates (SHA-256) detection**: `fclean dupes` command - SHA-256 based duplicate file detection
  - Delete strategies: newest, oldest, all
  - `--min-size` filtering, `--json` output
  - dry-run safe preview by default
- **Shell completion**: `fclean completion` - bash, zsh, fish auto-completion
- **Agent Skill**: Hermes Agent SKILL.md - AI agents can invoke fclean directly
- **README overhaul**: badges, comparison tables, new feature docs, optimized layout

## Tests

- 176 tests all passed ✅
- Full coverage: CLI, config, dupes, rename, edge cases, undo
