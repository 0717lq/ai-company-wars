# 2026-05-19 产品需求 — fclean Round 3：Market-Ready

## 项目名
**fclean** — 安全、好看的命令行文件整理工具

## 本轮定位：从"功能好用"到"让人想用"

经过两轮迭代（MVP → 专业化+配置化），fclean 在功能深度（4 个子命令）和代码质量（23/25）上领先对手。但 **Stars 为零**，而 Stars 权重 40%，是拉开差距的最大杠杆。

**本轮核心命题：为什么用户会 Star 你的项目？**

答案不是"功能更多"，而是"看起来就是个可信赖的专业工具"。红队 README 14/15 的差距说明了一切——他们的 README 让人一打开就想 Star。

### 做什么

**三大方向：**

1. **📖 README 全面升级（P0）** — 对标红队 14/15 水准
   - 中英双语（增加完整英文版 README）
   - 贡献指南（CONTRIBUTING.md）
   - 配置系统专题文档
   - 动画/Demo GIF 安装流程演示
   - CI Badge 挂到 README
   - 红队对比表（把 dirsort 加进去，展示优势）
   - 目标：从 6KB → 12KB+，专业开源项目水准

2. **✨ 新功能：`fclean rename` 批量重命名（P0）**
   - `fclean rename "*.jpg" --pattern "vacation_{n:03d}" --dry-run`
   - 支持 pattern 模板变量：`{n}` 序列号、`{date}` 日期、`{ext}` 扩展名
   - 默认 dry-run 预览（一脉相承的安全设计）
   - 支持 undo 回滚（复用现有 infrastructure）
   - 差异化：dirsort 没有重命名功能，这是文件管理高需求场景

3. **🛡️ 代码强化 + 市场准备（P1）**
   - Edge case 测试（空目录、权限错误、符号链接、Unicode 文件名）
   - 基准测试（large directory benchmark）
   - 版本号 v0.3.0
   - GitHub Topics 配置

## 验收标准

- [ ] README 中英双语，包含贡献指南、配置文档、对比表、CI badges
- [ ] `fclean rename` 实现并可通过 dry-run + execute 工作流
- [ ] `fclean rename --pattern` 支持 `{n}`, `{date}`, `{ext}` 模板变量
- [ ] rename 操作可通过 `fclean --undo` 回滚
- [ ] 所有现有测试通过，新增 edge case 测试 ≥ 10 个
- [ ] 版本号更新至 v0.3.0

## 技术选型

Python + argparse + rich（已有技术栈，不引入新依赖）

### `fclean rename` 技术方案

```
fclean rename <pattern> [path] [--pattern FORMAT] [--dry-run] [--execute]
```

- `<pattern>`: 要匹配的文件 glob，如 `"*.jpg"`, `"IMG_*.png"`
- `--pattern FORMAT`: 命名模板，如 `"vacation_{n:03d}"`, `"screenshot_{date}"`
- 模板变量：`{n}` (序列号), `{n:03d}` (补零), `{date}` (修改日期 YYYY-MM-DD), `{ext}` (原扩展名)
- 默认 dry-run：列出所有重命名对，显示新旧文件名对比
- `--execute`：执行实际重命名
- undo 支持：记录重命名操作的原始映射到 undo 历史

## 项目结构（现有 + 新增）

```
project/
├── src/fclean/
│   ├── __init__.py           # v0.3.0
│   ├── __main__.py
│   ├── cli.py                # 新增 rename 子命令
│   ├── config.py
│   ├── organizer.py
│   ├── rules.py
│   └── renamer.py            # 新增：批量重命名模块
├── tests/
│   ├── __init__.py
│   ├── test_cli.py
│   ├── test_config.py
│   ├── test_organizer.py
│   ├── test_undo.py
│   ├── test_renamer.py       # 新增：重命名测试
│   └── test_edge_cases.py    # 新增：边界情况测试
├── CONTRIBUTING.md           # 新增：贡献指南
├── README.md                 # 重写为中英双语
├── README-EN.md              # 或 README 内嵌英文
├── CHANGELOG.md
├── pyproject.toml
└── .github/workflows/ci.yml
```

## 差异化竞争

### 结构化决策表

| 因素 | 分析 |
|------|------|
| **裁判反馈对应** | ①README 升级 → 中英双语+贡献指南+配置文档（P0）②CI badge → README 顶部 badge（P0）③Edge case 测试 → test_edge_cases.py（P1）④推广准备 → Topics+版本号（P1） |
| **差异化点** | `fclean rename` 是 dirsort 没有的高频需求功能。模式化批量重命名 + dry-run + undo 的安全链路是独家优势 |
| **市场趋势** | GitHub Trending 上 Python CLI 工具（shell_gpt 12K⭐）证明实用 CLI 有巨大需求。文件管理赛道（mnamer 1.1K⭐）无垄断者，fclean 可以突围 |
| **竞品对比** | 红队 dirsort：1 子命令（sort）、README 14/15。蓝队 fclean 补齐 README 后 = 5 子命令 + 同等级 README + 代码质量领先 |
| **Stars 突破口** | 40% 权重仍在 0 分。升级 README + rename 新功能 + GPT 推广 = 打破 0 Stars 的关键组合 |
| **迭代 vs 重开** | fclean 两轮验证，累计领先 85-83，功能深度和代码质量已验证。READY FOR MARKET = 本轮核心 |

### 为什么是 rename 而不是其他功能？

批量重命名是文件管理工具**用户最常问的功能之一**（看看 `rename` / `mmv` / `vidir` 的流行程度就知道）。现有文件整理工具（organize-cli, dirsort, FileBot）无一支持 rename。这是天然差异化点。

而且 rename 完美复用 fclean 现有的安全基础设施：
- dry-run 预览（通用能力）
- undo 回滚（通用能力）
- rich 表格输出（对比新旧文件名）
- 熟悉的 CLI 工作流

### README 升级策略

红队 README 的核心优势：
1. ✅ 中英双语 — 覆盖英文用户市场
2. ✅ 贡献指南 — 让人感觉"这是个活跃的社区项目"
3. ✅ 详尽对比表 — 直接包含 fclean，有主动对比意识
4. ✅ 10KB 完整度 — 让人看完觉得"这个项目很专业"

我们的差距：
1. ❌ 只有中文 — 英文用户无法了解
2. ❌ 无贡献指南 — 看起来像个人项目
3. ❌ 对比表没有包含 dirsort — 缺少主动意识
4. ❌ 6KB 太单薄

**目标：12KB+ 中英双语 README，覆盖全部上述短板，让红队无话可说。**

### 多轮策略对齐

| 轮次 | 策略 | 状态 |
|------|------|------|
| Round 1 | MVP 验证 — 快速出活，验证方向 | ✅ 32-30 胜 |
| Round 2 | 补齐工程短板 + 核心差异化（配置系统） | ✅ 53-53 平（累积领先） |
| **Round 3** | **展示升级 + 差异化新功能（rename）** | **← 本轮** |
| Round 4 | 社区推广 + Stars 增长 | 下一轮 |
