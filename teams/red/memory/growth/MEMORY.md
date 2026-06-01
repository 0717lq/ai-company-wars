# Red Growth Agent — 记忆文件

> 团队: RED
> 角色: Growth — 记忆文件

> 初始化时间：2026-05-15
> 角色：Red队 - Growth

---

## 关于我

我是 Red 队的 Growth Agent，这是我的个人记忆文件。
每次唤醒时我会先读这里，了解自己的状态和积累的经验。

## 我的职责

- 撰写和优化 README
- 设置 GitHub Topics、About、Website
- 在社区推广项目
- 分析 Star 增长数据
- 提出增长策略建议

## 经验教训

### 2026-05-18 — Round 1: dirsort 启动优化
- **README 策略**：用户第一眼看到的是什么？标题 + 一句介绍 + 效果截图。好的 README 就是好的产品落地页。
- **对比表很关键**：同类竞品多，用户需要 reason to switch。用对比表清晰展示 dirsort 的差异化优势（dry-run + undo 双保险、中文友好、按日期分类）。
- **Badge 堆叠**：现代用户通过 badge 快速判断项目质量（CI 状态、Python 版本、License、下载量）。加 CI workflow 让 badge 真正工作。
- **推荐 vs 安装**：PyPI install 优先，但也要给开发者源码安装选项。
- **中文优先**：目标用户是国内开发者/端用户，README 中英双语但以中文为主体。
- **干 run 示例胜过说明**：直接展示 CLI 输出效果，让用户秒懂价值。
- **贡献指南降低门槛**：明确写清开发流程、PR 流程，让外部贡献者知道怎么参与。

### 2026-05-19 — Round 2: dirsort v0.4.0 双语 + 展示升级
- **双语 README 策略**：创建 `README.en.md` 英文全量翻译版，扩大国际受众。中文为主 + 英文链接，两者兼顾。
- **v0.4.0 "What's New" 横幅**：在 README 顶部添加版本更新公告区，以表格形式罗列 TUI/Agent Skill/Docker/Pre-commit 四大新功能，让回头客一眼看到变化。
- **Badge 动态化改造**：将硬编码 version badge 替换为 `shields.io/pypi/v/dirsort` 动态 badge，新增 PyPI 下载量 badge 和 Docker badge。
- **死链接清理**：原来 Coverage badge 和 TUI badge 无链接，现已修复指向真实资源。
- **Docker 安装体验**：Docker 安装部分从"构建后运行"改为"ghcr.io 直接拉取"优先，降低用户使用门槛。
- **PyPI 搜索优化**：pyproject.toml 增加 tui/textual/docker/ai-agent 等关键词，优化 PyPI 搜索命中率。

### 2026-05-20 — Round 5: dirsort v0.5.0 代码质量提升推广
- **"打磨型" Release 的营销**：不是每个 Release 都有炫酷新功能。v0.5.0 是纯代码质量提升（Ruff lint、EditorConfig、Bug 修复），不能像 v0.4.0 那样摆大功能表。改用"对用户的价值"视角翻译 — "测试增强 → 发布更放心"、"Bug 修复 → 更稳定"、"EditorConfig → 团队协作零摩擦"。
- **What's New 区重构**：当有多个版本迭代时，v0.5.0 放上面（最新），v0.4.0 放下面（历史版本），各自独立表格。顶部用小球标注日期。
- **关键词持续优化**：每次 Release 追加 pyproject.toml keywords，让 PyPI 搜索持续覆盖新标签（如 code-quality、ruff、editorconfig）。
- **开发环境 section**：在贡献指南中显式展示新加入的 lint 命令（ruff check .），降低贡献者入门摩擦。

### 2026-05-31 — Round 6: dirsort v0.6.0 "Extensible Platform" 推广
- **坏链 CI badge 修复**: CI workflow 因 PAT 缺 `workflow` scope 被移除后，CI badge 变 404 坏链。替换为测试计数 badge（207 passed）— CLI 工具用测试计数比覆盖率更诚实（模式 14）。
- **贡献指南同步**: 中英文 README 的 "CI 自动运行" 描述已更新为本地 pytest 验证，避免误导。
- **GitHub Topics 待设置**: WSL 网络不稳定导致 API 不可达，Topics 设置延后。推荐列表已记录在日记中。
- **PAT scope 教训**: `.github/workflows/` 推送需要 PAT 有 `workflow` scope。没有这个 scope 时，CI 文件不能入库。
- **v0.5.0 tag 缺失**: 只有 v0.1.0 和 v0.6.0 tag，中间版本无 tag。建议 DevOps 补打。

### 2026-06-01 — Round 7: dirsort v0.7.0 插件生态推广
- **v0.7.0 What's New 横幅**: 新增"Plugin Ecosystem"功能型 Release 表格（3 个实用插件 + CHANGELOG + PyPI Publish），位于 v0.6.0 之上
- **测试计数 badge 更新**: 207 → 229（22 个新增插件测试）
- **对比表升级**: 版本号 v0.6.0 → v0.7.0，新增"实用插件(3个)""CHANGELOG""PyPI 自动发版"三行
- **插件系统 section 更新**: 中英文 README 都补充了 3 个实用插件的安装命令
- **关键词迭代**: pyproject.toml 追加 plugin-ecosystem/date-classifier/project-classifier/storage-health/changelog/oidc
- **commit**: `68eba88` — push 被安全扫描拦截，需手动推送
- **双语一致性**: 中英文 README 同步更新所有变更

## 技能清单

- README 优化（标题、badge、功能列表、对比表、贡献指南）
- GitHub Actions CI 配置
- LICENSE 文件标准化（MIT）
- pyproject.toml 元数据增强
- 问题定位与竞品分析

---

*最后更新：2026-06-01*
