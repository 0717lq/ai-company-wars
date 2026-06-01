# GitHub Trending Analysis - File-Management CLI Signals
**Date:** 2026-05-19
**Team:** RED (dirsort project)
**Round:** AI Company Wars - Round 3

---

## Part 1: Raw Trending Data

### Source A: GitHub Trending Python (Weekly)
| # | Repo | Description | Total Stars | Weekly Stars | Language |
|---|------|-------------|-------------|-------------|----------|
| 1 | CloakHQ/CloakBrowser | Stealth Chromium bot detection | 15,406 | 9,124 | Python |
| 2 | Imbad0202/academic-research-skills | Research Skills for Claude Code | 12,162 | 4,402 | Python |
| 3 | anthropics/financial-services | Agent skills for finance | 25,477 | 5,259 | Python |
| 4 | HKUDS/AI-Trader | Automated Agent-Native Trading | 18,112 | 2,020 | Python |
| 5 | BigBodyCobain/Shadowbroker | OSINT platform | 7,805 | 1,376 | Python |
| 6 | anthropics/skills | Public Agent Skills repo | 137,120 | 4,818 | Python |
| 7 | K-Dense-AI/scientific-agent-skills | Scientific Agent Skills | 24,479 | 3,640 | Python |
| 8 | github/spec-kit | Spec-Driven Development toolkit | 102,254 | 6,476 | Python |
| 9 | MervinPraison/PraisonAI | 24/7 AI Workforce | 7,826 | 722 | Python |
| 10 | roboflow/supervision | Computer vision tools | 39,203 | 747 | Python |
| 11 | joeseesun/qiaomu-anything-to-notebooklm | Content processor for NotebookLM | 3,879 | 2,262 | Python |
| 12 | bytedance/UI-TARS | Automated GUI Interaction | 10,645 | 218 | Python |
| 13 | MemoriLabs/Memori | Agent-native memory infrastructure | 14,601 | 319 | Python |
| 14 | AIDC-AI/Pixelle-Video | AI Short Video Engine | 18,158 | 3,000 | Python |
| 15 | yichuan-w/LEANN | RAG on Everything, 97% storage savings | 11,441 | 455 | Python |

### Source B: GitHub Trending All Languages (Weekly)
| # | Repo | Description | Language | Total Stars | Weekly Stars |
|---|------|-------------|----------|-------------|-------------|
| 1 | CloakHQ/CloakBrowser | Stealth Chromium | Python | 15,407 | 9,124 |
| 2 | rohitg00/agentmemory | Persistent memory for AI agents | TypeScript | 13,046 | 7,830 |
| 3 | oven-sh/bun | Fast JS runtime/bundler/PM | Rust | 91,958 | 2,350 |
| 4 | Imbad0202/academic-research-skills | Research Skills for Claude Code | Python | 12,162 | 4,402 |
| 5 | yikart/AiToEarn | Use AI to Earn | TypeScript | 15,253 | 4,851 |
| 6 | anthropics/financial-services | Financial agent skills | Python | 25,477 | 5,259 |
| 7 | mattpocock/skills | Skills for Real Engineers | Shell | 92,159 | 20,361 |
| 8 | ruvnet/RuView | WiFi spatial intelligence | Rust | 59,990 | 7,217 |
| 9 | millionco/react-doctor | Catches bad React code | TypeScript | 10,190 | 2,453 |
| 10 | colbymchenry/codegraph | Code knowledge graph for agents | TypeScript | 5,107 | 2,690 |
| 11 | apernet/hysteria | Censorship resistant proxy | Go | 21,266 | 1,254 |
| 12 | facebook/pyrefly | Fast Python type checker | Rust | 6,221 | 481 |
| 13 | bytedance/UI-TARS-desktop | Multimodal AI Agent Stack | TypeScript | 34,663 | 1,939 |

### Source C: Established File-Management/CLI Ecosystem (Stars Baseline)
| Tool | Stars | Language | Category |
|------|-------|----------|----------|
| fzf (junegunn/fzf) | 80,300 | Go | Fuzzy finder / CLI |
| ripgrep (BurntSushi/ripgrep) | 63,900 | Rust | File search |
| bat (sharkdp/bat) | 58,900 | Rust | File viewer |
| fd (sharkdp/fd) | 43,000 | Rust | File finder |
| yazi (sxyazi/yazi) | 38,200 | Rust | Terminal file manager |
| eza (eza-community/eza) | 21,800 | Rust | ls replacement |

---

## Part 2: Signal Analysis Framework

### 1. FILE_CLI_TRENDS - File management CLI has stable demand

Signals and Implications:
- fd (43k), ripgrep (63.9k), bat (58.9k): Sustained massive popularity - top Rust projects.
  Implication: Modern Unix CLI replacement market is proven and growing.
- yazi (38.2k) terminal file manager: Blazing fast Rust TUI, very active development.
  Implication: Terminal-based file management has thriving audience. Users want interactive, visual terminal file mgmt.
- eza (21.8k) modern ls replacement: Still actively maintained. File listing has room for modern alternatives.
- No trending file-management CLIs this week on either page.
  Implication: GAP/OPPORTUNITY - no new entrant capturing weekly buzz. Rust dominates. Python differentiates via being accessible/extensible.

### 2. TECH_TREND - Users expect interactive terminal experience

Signals and Implications:
- Rust CLI ecosystem (eza, yazi, bat) uses rich output: colors, icons, Git indicators.
  Implication: dirsort MUST have rich terminal output. Colors, icons (nerd font), preview mode.
- fzf (80k) proves users want fuzzy search + interactivity; yazi proves full TUI browsing.
  Implication: Consider TUI mode (dirsort interactive) using Textual (Python TUI framework).
- AI/Agent ecosystem DOMINANT: 7/15 Python trending repos are AI agent skills.
  mattpocock/skills got 20,361/week - #1 across ALL languages.
  Implication: dirsort could provide a Claude Code skill / agent skill for file organization.

### 3. SPEED_DEMAND - Python tools need perceived speed

Signals and Implications:
- Every top file CLI (fd, rg, bat, eza, yazi) is Rust. bun (Rust) is top infra tool.
  Implication: Users expect CLI tools to be instant. Python has perception problem.
- spec-kit (102k) and supervision (39k) prove Python CAN succeed in CLI space.
  Implication: Python wins with: (1) rich progress bars (Rich/Textual), (2) async I/O, (3) fast startup via lazy imports.
- agentmemory (TypeScript, 13k, 7,830/week): Speed matters for agent tool calling.
  Implication: If dirsort called by AI agent repeatedly, sub-100ms latency is critical. Consider daemon mode.

### 4. ECOSYSTEM - Tools should integrate into shell pipelines

Signals and Implications:
- fzf+fd+rg pipeline: Holy trinity of shell productivity - pipe fd into fzf into rg into bat.
  Implication: dirsort must be pipe-friendly. Accept stdin/stdout, work as filter in pipeline.
- Shell completions: All major CLI tools ship bash/zsh/fish completions.
  Implication: Must ship shell completions.
- Config file trends: TOML/YAML preferred over JSON for human-editable config.
  Implication: Use TOML for dirsort config files.
- Agent/tool-calling ecosystem: Skills repos trending massively.
  Implication: Expose machine-readable output (JSON/JSONL). Add --json flag.

---

## Part 3: Strategic Recommendations for dirsort

### Immediate Opportunities (Low Effort, High Impact)

1. Add --json / --output-format=json output
   - AI-agent-friendly, pipe chaining with jq/fzf
   - Trivial with Typer + Pydantic

2. Ship shell completions
   - Typer supports natively
   - Required for serious CLI credibility

3. Rich terminal output with icons
   - Use rich library, Nerd Font support
   - Show sizes, dates, counts

4. Publish a CLI Skill for Claude Code / AI agents
   - Create .claude directory with dirsort skill definition
   - Could drive massive adoption given current trends

### Medium-Term Features (Competitive Differentiation)

5. Interactive TUI mode with Textual
   - dirsort interactive: browse dirs, preview sorting rules, see results live

6. Rule-based auto-sorting daemon
   - dirsort watch /path/ - watches dir and auto-sorts new files
   - Uses watchdog + async I/O

7. Pipeline integration examples
   - Document: fd + dirsort + fzf pipeline

8. Configuration as TOML
   - ~/.config/dirsort/config.toml with pattern-to-directory rules

### Long-Term Vision (Market Leadership)

9. AI-powered sorting suggestions
   - Local LLM (Ollama) or API for content-aware sorting

10. Cross-platform file tagging
    - macOS extended attributes, Windows ADS, Linux xattr

11. Plugin system
    - Python plugins for custom sorting logic, community repo of rules

---

## Part 4: Competitive Landscape

| Tool | Strength | Weakness | dirsort Angle |
|------|----------|----------|---------------|
| fd | Blazing fast (Rust), simple | Only finds, doesnt sort/organize | Complementary - dirsort sorts and moves |
| fzf | Universal fuzzy finder | Not file-management focused | Integrate fzf as backend for interactive mode |
| eza | Beautiful ls replacement | Read-only listing | dirsort shows what would happen, then does it |
| yazi | Full TUI file manager | Heavy, Rust-only, opinionated | Lighter, Python-interoperable, sorting-first |
| Hazel (macOS) | Auto-rule file organizer | macOS-only, paid, GUI-only | Cross-platform, CLI-first, free/OSS |
| ranger/lf | File managers | Navigation-focused | Sorting automation is primary goal |

---

## Part 5: Key Numbers for the Pitch

- 80k+ stars for fzf - fuzzy interaction is proven
- 63.9k stars for ripgrep - file search/CLI tools have massive audiences
- 38.2k stars for yazi - terminal file management is exploding
- 21.8k stars for eza - people want modern replacements for basic Unix tools
- 20,361/week for mattpocock/skills - THE trend is AI agent tooling
- 0 file-management CLIs on this weeks trending pages - market gap

---

Report generated by RED Team subagent - May 19, 2026