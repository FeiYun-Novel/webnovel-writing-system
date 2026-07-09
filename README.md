<a id="中文"></a>
**🌐 Language：中文 ｜ [English](#english)**

# 网文写作系统 · Webnovel Writing System

> 一套**跨会话的「AI 写小说」工程系统**——把「写作」当成一个可持续迭代的工程流程来做：跨会话状态、每章 SOP、分阶段检查表、可复用写作技法库、上下文水位管理、多子代理并行自检。
>
> 设计理念受 Claude Code 的 `webnovel-writing` skill（[Tomsawyerhu/Chinese-WebNovel-Skill](https://github.com/Tomsawyerhu/Chinese-WebNovel-Skill)）启发，但为**独立编写的工作流系统**（本仓库不包含该 skill 的任何语料、脚本或模块文件）。适用于多种长篇连载题材，**不绑定任何特定题材**。

> 👉 **第一次使用？先看 [QUICKSTART.md](./QUICKSTART.md)** —— 一份可执行清单：建目录 + 复制模板 + 填几样必填项，就能让 AI 用这套系统写第一章。

---

## 这是什么 / 解决什么问题

用 AI 写长篇小说，最大的痛点不是「写一段」，而是**跨会话失忆**和**越写越 AI 味**：

- 新开一个对话，AI 不记得前 20 章埋了什么伏笔、谁受了伤、谁的秘密还没揭穿；
- 写着写着人物 OOC、设定前后矛盾、文风漂移；
- AI 天生爱「替读者下结论」「升华点题」「工整排比」，越写越像说明书。

这套系统的核心思路：**所有状态不放在对话记忆里，全部落到 Markdown 文件**。新对话只要读几个状态文件就能无损接续。每章按固定 SOP + 检查表走，写前查技法、写后多路自检，把「不 AI 味」变成可执行的工程纪律，而不是靠运气。

## v2 更新（2026-07）：双机检闸门 + 分级审稿 + 单源制

经过一轮多 AI 交叉审计驱动的工程化改造，v2 新增：

- **文风机检闸门 `scripts/style_gate.py`**（写后必跑）：破折号/对照句式/明喻密度/单句成段/段内排比/符号配对/文件名一致等通用句式硬规则脚本化，另有禁用词/敏感词两个可配置槽位。立项实证：给 AI 立"破折号≤5"的文字规则，连续三章写了 18/9/6 处、多路 AI 审稿全放过——**LLM 靠读感数数不可靠，数值规则一律脚本核验**。
- **账本机检闸门 `scripts/consistency_gate.py`**（封存后必跑）：章号一致/伏笔表自洽/账本引语回正文核对/状态快照新鲜度/悬空指针/上下文水位七项。立项实证：状态文件手抄正文台词，抄错一个字能潜伏几十章；**手抄必漂移，一致性交给机器**。
- **分级审稿**：章计划里定"章型"——关键章全路数子代理审、过场章 3 路＋每 3 章一致性巡检兜底，省约三分之一审稿开销而不裂质量底线。
- **单源+指针制**：每条规则/事实的全文只存一个权威源，其他文件一律一行指针——从机制上消灭"改一处忘三处"。
- **文件三层模型**：活账本（强一致·机检红项）/ 活索引（警告级）/ 历史归档（排除）——覆盖面和维护成本的平衡点。

## 核心理念

| 理念 | 说明 |
|---|---|
| **状态即文件（Cross-session state as files）** | 章节进度、伏笔、人物状态、已发生事件、未解决问题全部存 Markdown。冷启动只读文件，不靠对话记忆。 |
| **Forward-only 封章** | 一章过了自检三关（结构/设定/历史错题）= 封存，不回头改。用「自检通过」代替「还不满意」，避免无限返工。 |
| **写前查技法，不是写完补** | 动笔前先把本章拆成几个场景，对照技法库给每场点名具体招式，产出「本章技法清单」——专治 AI 味。 |
| **上下文水位管理** | 三大累积文件定期量字数、报绿/黄/红灯，超阈值就归档，防止上下文膨胀拖垮质量与成本。 |
| **多子代理并行自检** | 关键章封存前，按「角色 + 维度」拆多个子 Agent 并行审稿，主 Agent 汇总去重定稿。见下方⭐。 |
| **机检闸门（v1.1 新增）** | 数值可判定的风格规则（破折号/对照句/明喻密度/单句段/排比）一律脚本核验——LLM 靠读感数数不可靠，多路审稿代理都可能读不出超标。写后第一步跑 `story_system/scripts/style_gate.py`，全绿才派审稿。 |
| **文风样本卡（v1.1 新增）** | 规则告诉模型"别写什么"，样本告诉模型"写成什么样"。把作者点头认可的正文选段按场景类型归档，写场景前先对同类样本——**换模型/换工具时靠它对齐文风**（抽象规则跨模型损耗大，具体范文几乎无损）。 |

## ⭐ 头牌特性：多子代理并行自检

单个 AI 审一整章容易「注意力稀释」、漏检。这套系统在关键章封存前，把审稿拆成**多路子 Agent 并行**（详见 `story_system/检查表/阶段4-写后自检.md`）：

- **按「角色 + 维度」拆路**：感情线/配角组、主角+(可选)系统组、写法/AI味组、剧情/设定组、**读者视角组**。
- **读者视角组**最特别：刻意**不给它任何设定文件**，只给本章正文 + 上一章末尾，让它以「第一次看这本书的读者」身份找——哪里逻辑跳跃、哪里作者旁白替读者下了结论、哪句读着卡壳。
- 每路用 **schema 强制结构化输出**（severity / location / issue / suggestion）；**多路命中同一处 = 高置信**，优先改。
- 机械项（错别字/标点计数/字数核对）主 Agent 自己 grep，不浪费 Agent。

## 目录结构

```text
webnovel-writing-system/
├── README.md              # 本文件
├── EXAMPLE.md             # 抽象示例：如何填槽位
├── CLAUDE.md / AGENTS.md  # 给 AI 的项目级指令模板（冷启动、格式规范、硬约束）
├── 00_AI_WIKI/            # 项目控制塔（空白模板：当前状态/下一步/文件地图/边界）
├── story_system/          # 系统核心
│   ├── README.md          # 冷启动读序、两层角色结构说明
│   ├── 写作流程.md         # 每章 SOP（阶段 0→5）
│   ├── 检查表/            # 每个阶段一份逐条核对清单（阶段0~5）
│   ├── 章节自检清单.md     # 写后自检总清单（结构六项 / 设定伏笔 / 历史错题）
│   ├── 上下文管理.md       # 上下文水位与归档策略
│   ├── 写作风格指南.md     # 腔调/大白话/信息可见性约定（模板版）
│   ├── 写前速览卡.md       # 动笔前一页速览（模板版）
│   ├── 写作技法/          # ★ 技法库「框架」：路由表 + 每类的占位指引（正文留白，自己填）
│   ├── scripts/style_gate.py  # ★ v1.1 机检闸门：五项数值风格检查（阈值可校准）
│   └── 模板/             # 各类活文档空白模板（人物状态/伏笔/事件/大纲/总结/文风样本卡…）
└── templates/角色卡/       # 角色卡空白模板
```

## 怎么用（快速上手）

1. **Clone 下来**，把 `story_system/` 和 `CLAUDE.md`、`00_AI_WIKI/` 放进你自己的小说项目文件夹。
2. **填槽位**：参考 `EXAMPLE.md`，把「主角 / 反派 / 感情线角色 / 势力」等通用槽位换成你自己的人物设定；用 `templates/` 和 `story_system/模板/` 的空白模板建你项目的活文档。
3. **冷启动**：新对话第一句话让 AI 读 `story_system/README.md`，按读序加载状态。
4. **每章照 SOP 走**：写前读状态 + 查技法库 → 出本章计划 → 写正文 → 阶段4 多路自检 → 更新活文档。逐阶段对照 `检查表/`。

> **关于写作技法库：** 本仓库提供的是技法库的**框架**——一张"什么场景翻哪份"的路由表 + 每类技法的**占位指引**（讲清这份该放什么方向、什么内容），但**不含具体招式正文**（那是各人自己积累的手艺，需自行填充）。怎么建见 `story_system/写作技法/如何建立你自己的技法库.md`。角色、设定、题材相关的东西也都做成了**空白槽位**，填成你自己的即可。

## 关于「示例项目」

系统里偶尔用抽象举例来演示某些机制怎么落地（比如「主角专属信息机制」可以是预知/读心/面板/信息外泄等，「角色专属反应特征」可以是小动作/口头禅/瞳色变化等）。这些都是**可选示例**，不是使用本系统的前提，也不指向任何具体作品——你完全可以换成任何你自己的设定。详见 `EXAMPLE.md`。

## 更新日志

### v2.1（2026-07）
- **阶段2「爽点门槛四答」消音自查新增第 5 类**：认知功劳被工具代劳——金手指/系统/军师类角色把关键推理结论直接讲给主角听，主角只负责提问和惊讶，读者感受到的是"工具很聪明"而不是"主角很聪明"。正确做法：工具只给原始信息/数据，推理结论由主角自己拼出来。（实证：审稿子代理曾指出某章"男主自己的算计能力被系统的全知代劳了"，属于消音四类之外的第五种常见失误。）

### v1.1（2026-07）
- **新增 `story_system/scripts/style_gate.py` 机检闸门**：破折号/「不是A是B」对照句/明喻密度/单句成段占比/段内排比五项数值检查，写后第一步先跑、全绿才进审稿。动机：实测 LLM（包括审稿子代理）靠读感数数不可靠，数值规则必须脚本核验。阈值集中在脚本头部 CONFIG，按自己书的文风校准。
- **新增「文风样本卡」机制**（`模板/文风样本卡-模板.md` ＋ 阶段3 首条）：把作者点头认可的正文选段按场景类型归档，写场景前先对同类样本。这是**跨模型/跨工具迁移文风**的关键——抽象规则迁移损耗大，具体范文几乎无损。
- **阶段2 新增「爽点门槛四答」**（男频/爽文向）：本章的赢/档位/憋放账/消音自查，动笔前答不出就打回计划。
- **阶段4 审稿编排升级**：新增可选第 6 路"体系一致性组"（打斗章查力量表现是否符合等级）；新增**跨环境降级说明**（Codex 需显式要求派子代理；无子代理环境按路分独立会话跑，关键是输入隔离）。
- **章节总结模板改限长四栏版**：总结也是每章要读的上下文，写长=成本逐章上涨。

### v1.0（2026-06）
- 初版：六阶段 SOP、检查表、多子代理并行自检、上下文水位管理、AI-Wiki 控制塔、技法库框架、活文档模板。

## 致谢与出处

- 设计理念受 **[Tomsawyerhu/Chinese-WebNovel-Skill](https://github.com/Tomsawyerhu/Chinese-WebNovel-Skill)**（Claude Code 的 `webnovel-writing` skill）启发——尤其是「模块化路由 + 本地语料检索 + 全程去 AI 味」的思路。
- 本仓库是**独立编写的工作流系统**，为作者自己的原创内容（SOP、检查表、技法库、控制塔等），**未包含也未再分发**上述 skill 的语料 / 脚本 / 模块等文件。
- 「控制塔 / PRD / issues / troubleshooting」的工程习惯参考了通用的 AI 长期项目管理实践。

> 注：上述 skill 原仓库当前未附带开源许可证；本仓库仅在思路层面致谢，不主张对其任何内容的再授权。

## License

本仓库自身的原创内容以 [MIT](./LICENSE) 授权 © 2026 FeiYun-Novel。

---
---

<a id="english"></a>
**🌐 Language: [中文](#中文) ｜ English**

# Webnovel Writing System · 网文写作系统

> A **cross-session engineering system for "AI-assisted novel writing"** — treating "writing" as a sustainable, iterative engineering process: cross-session state, per-chapter SOP, staged checklists, a reusable craft-technique library, context-budget management, and parallel multi-agent self-review.
>
> Design inspired by Claude Code's `webnovel-writing` skill ([Tomsawyerhu/Chinese-WebNovel-Skill](https://github.com/Tomsawyerhu/Chinese-WebNovel-Skill)), but this is an **independently written workflow system** (this repo contains none of that skill's corpus, scripts, or module files). Works across long-form serialized genres — **not tied to any specific genre**.

> 👉 **First time here? Start with [QUICKSTART.md](./QUICKSTART.md)** — an actionable checklist: create folders, copy templates, fill in a few required slots, and you can have an AI write your first chapter with this system.

---

## What this is / what problem it solves

The hardest part of writing a long novel with AI isn't "writing a paragraph" — it's **losing memory across sessions** and **drifting into AI-flavored prose**:

- Open a new conversation and the AI no longer remembers what foreshadowing was planted 20 chapters ago, who got hurt, or whose secret hasn't been revealed yet;
- Characters go out-of-character, worldbuilding contradicts itself, prose style drifts as the story goes on;
- AI has a built-in tendency to "draw conclusions for the reader," "sum up the theme," and "write in tidy parallel sentences" — the longer it writes, the more it reads like an instruction manual.

The core idea of this system: **no state lives in conversation memory — all of it lands in Markdown files**. A new conversation only needs to read a handful of state files to pick up seamlessly where the last one left off. Each chapter follows a fixed SOP + checklist: look up technique references before writing, run multi-pass self-review after writing. This turns "not sounding like AI" into an enforceable engineering discipline, not something left to luck.

## v2 Update (2026-07): Dual Machine-Checked Gates + Tiered Review + Single Source of Truth

After a round of engineering hardening driven by multi-AI cross-auditing, v2 adds:

- **Style machine-check gate `scripts/style_gate.py`** (must run after writing): hard-codes generic prose-pattern rules as a script — em-dash frequency, "not-A-but-B" contrast sentences, simile density, single-sentence-paragraph ratio, in-paragraph parallelism, bracket-pairing, filename consistency — plus two configurable slots for banned/sensitive words. Founding evidence: telling the AI "no more than 5 em-dashes" as a plain-text rule still produced 18/9/6 violations across three consecutive chapters, and multiple AI reviewers all missed it — **LLMs can't reliably count by "feel"; numeric rules must be verified by script.**
- **Ledger machine-check gate `scripts/consistency_gate.py`** (must run after archiving): seven checks — chapter-number consistency, foreshadowing-table self-consistency, ledger quotes matching the actual prose, state-snapshot freshness, dangling pointers, and context-budget level. Founding evidence: a state file once hand-copied a line of dialogue from the prose and got one character wrong — that error could lie dormant for dozens of chapters; **hand-copying inevitably drifts, so consistency-checking is handed off to a machine.**
- **Tiered review**: the chapter plan now declares a "chapter type" — key chapters get the full multi-pass agent review, transitional chapters get a lean 3-pass review plus a consistency sweep every 3 chapters as a safety net — cutting review cost by roughly a third without breaking the quality floor.
- **Single source + pointer discipline**: every rule/fact has exactly one authoritative full-text source; every other file holds only a one-line pointer to it — structurally eliminating the "fixed it in one place, forgot the other three" failure mode.
- **Three-tier file model**: living ledger (strict consistency, machine-check red-flag level) / living index (warning level) / historical archive (excluded from active reads) — a deliberate balance between coverage and maintenance cost.

## Core Principles

| Principle | Description |
|---|---|
| **Cross-session state as files** | Chapter progress, foreshadowing, character states, event log, and open questions all live in Markdown. A cold start only reads files — it never relies on conversation memory. |
| **Forward-only sealing** | Once a chapter clears the three-gate self-review (structure / worldbuilding / recurring-mistake history), it's sealed and never revisited. "Passed self-review" replaces "still not satisfied," preventing infinite rework loops. |
| **Look up technique before writing, not patch it in after** | Before drafting, break the chapter into scenes and match each one to a specific move from the technique library, producing a "this chapter's technique checklist" — the direct antidote to AI-flavored prose. |
| **Context-budget management** | Three cumulative files are periodically measured by character count and flagged green/yellow/red; once a threshold is crossed, older content gets archived — preventing context bloat from degrading quality and inflating cost. |
| **Parallel multi-agent self-review** | Before a key chapter is sealed, review is split across multiple sub-agents by "role + dimension," running in parallel; the main agent merges, deduplicates, and finalizes. See ⭐ below. |
| **Machine-check gate (added in v1.1)** | Any style rule that can be judged numerically (em-dashes, contrast sentences, simile density, single-sentence paragraphs, parallelism) is verified by script — LLMs are unreliable at counting by feel, and even multi-pass review agents can miss an overage. Run `story_system/scripts/style_gate.py` as the first step after writing; only dispatch review agents once every check is green. |
| **Style sample cards (added in v1.1)** | Rules tell the model "what not to write"; samples show it "what good looks like." File author-approved prose excerpts by scene type, and reference the matching samples before writing a similar scene — **this is what keeps style consistent when you switch models or tools** (abstract rules degrade a lot across models; concrete reference prose barely degrades at all). |

## ⭐ Headline Feature: Parallel Multi-Agent Self-Review

A single AI reviewing an entire chapter is prone to "attention dilution" and missed issues. Before a key chapter is sealed, this system splits the review into **multiple parallel sub-agents** (full details in `story_system/检查表/阶段4-写后自检.md`):

- **Split by "role + dimension"**: a romance/supporting-cast group, a protagonist + (optional) system-mechanic group, a craft/AI-flavor group, a plot/worldbuilding-consistency group, and a **reader's-eye-view group**.
- The **reader's-eye-view group** is the most distinctive: it is deliberately given **no worldbuilding files at all** — only this chapter's prose plus the tail of the previous chapter — and asked to review as "a reader seeing this book for the first time": where's the logic jump, where does the narrator draw a conclusion the reader should have drawn themselves, which line makes a reader stumble.
- Every pass is forced into **structured output via schema** (severity / location / issue / suggestion); **when multiple passes flag the same spot, that's high-confidence** and gets fixed first.
- Mechanical items (typos, punctuation counts, word-count checks) are grepped by the main agent directly — no need to burn an agent call on them.

## Directory Structure

```text
webnovel-writing-system/
├── README.md               # This file (Chinese + English, in one page)
├── EXAMPLE.md               # Abstract example: how to fill in the slots
├── CLAUDE.md / AGENTS.md    # Project-level instruction templates for the AI (cold start, formatting rules, hard constraints)
├── 00_AI_WIKI/              # Project control tower (blank templates: current state / next action / file map / boundaries)
├── story_system/            # The system core
│   ├── README.md            # Cold-start read order, explanation of the two-tier role structure
│   ├── 写作流程.md           # Per-chapter SOP (Stage 0 → 5)
│   ├── 检查表/              # One checklist per stage (Stage 0–5)
│   ├── 章节自检清单.md       # Post-writing master checklist (6 structural items / worldbuilding & foreshadowing / recurring-mistake history)
│   ├── 上下文管理.md         # Context-budget levels and archiving policy
│   ├── 写作风格指南.md       # Voice / plain-language / information-visibility conventions (template version)
│   ├── 写前速览卡.md         # One-page pre-writing cheat sheet (template version)
│   ├── 写作技法/            # ★ Technique library "framework": routing table + placeholder guidance per category (body text left blank, fill in your own)
│   ├── scripts/style_gate.py   # ★ v1.1 machine-check gate: five numeric style checks (thresholds configurable)
│   └── 模板/                # Blank templates for all living documents (character state / foreshadowing / events / outline / summary / style sample cards…)
└── templates/角色卡/          # Blank character-card templates
```

## Getting Started

1. **Clone the repo**, then drop `story_system/`, `CLAUDE.md`, and `00_AI_WIKI/` into your own novel project folder.
2. **Fill in the slots**: use `EXAMPLE.md` as a reference and replace generic slots like "protagonist / antagonist / romance-line characters / factions" with your own cast; use the blank templates in `templates/` and `story_system/模板/` to build your project's living documents.
3. **Cold start**: in a new conversation, have the AI read `story_system/README.md` first and load state in the documented read order.
4. **Follow the SOP for every chapter**: read state + look up technique references → produce this chapter's plan → write the prose → run the Stage-4 multi-pass self-review → update the living documents. Cross-check each stage against `检查表/`.

> **On the technique library:** what this repo provides is the **framework** of the technique library — a routing table ("which scene type maps to which file") plus **placeholder guidance** per category (what direction and content each file should hold), but **not the actual move write-ups themselves** (that's craft you accumulate yourself and fill in). See `story_system/写作技法/如何建立你自己的技法库.md` for how to build it. Characters, worldbuilding, and genre-specific content are all **blank slots** — fill them in with your own.

## About the "Example Project"

The system occasionally uses abstract examples to illustrate how a mechanism plays out in practice (e.g., a "protagonist-exclusive information mechanic" could be precognition / mind-reading / a status panel / involuntary information leakage; a "character-exclusive reaction trait" could be a tic, a catchphrase, a change in eye color, etc.). These are all **optional illustrations**, not a prerequisite for using this system, and they don't point to any specific published work — you're free to swap in whatever fits your own worldbuilding. See `EXAMPLE.md` for details.

## Changelog

### v2.1 (2026-07)
- **Added a 5th failure category to Stage 2's "payoff-threshold four-question" desensitization self-check**: cognitive credit outsourced to a tool — a cheat-mechanic / system / strategist-type character hands the key deductive conclusion straight to the protagonist, leaving the protagonist to just ask questions and react with surprise; the reader ends up feeling that "the tool is clever," not that "the protagonist is clever." Correct approach: the tool supplies only raw information/data, and the protagonist works out the conclusion themselves. (Evidence: a review sub-agent once flagged a chapter where "the protagonist's own scheming ability had been outsourced to the system's omniscience" — a fifth common failure mode beyond the original four desensitization categories.)

### v1.1 (2026-07)
- **Added the `story_system/scripts/style_gate.py` machine-check gate**: five numeric checks — em-dash frequency, "not-A-but-B" contrast sentences, simile density, single-sentence-paragraph ratio, in-paragraph parallelism — run as the very first step after writing; only proceed to review once every check is green. Motivation: testing showed LLMs (including review sub-agents) can't reliably count by feel; numeric rules must be script-verified. Thresholds are centralized in a CONFIG block at the top of the script — calibrate them to your own book's style.
- **Added the "style sample card" mechanism** (`模板/文风样本卡-模板.md` + the first item of Stage 3): file author-approved prose excerpts by scene type, and reference the matching samples before writing a similar scene. This is the key to **carrying your style across models/tools** — abstract rules degrade a lot in translation between models, but concrete reference prose barely degrades at all.
- **Added the "payoff-threshold four-question" to Stage 2** (for male-lead-driven / power-fantasy-oriented projects): this chapter's win / payoff tier / tension-saved-vs-released ledger / desensitization self-check — if you can't answer the plan is bounced back before writing starts.
- **Upgraded the Stage 4 review lineup**: added an optional 6th pass, a "system-consistency group" (for combat chapters, checks whether power displays match the stated power tier); added **cross-environment degradation notes** (Codex needs to be explicitly told to dispatch sub-agents; environments without sub-agents should run each pass as a separate session, with input isolation being the key thing to preserve).
- **Rewrote the chapter-summary template as a length-capped four-column version**: the summary is also context that gets read every chapter — writing it long means cost climbing chapter after chapter.

### v1.0 (2026-06)
- Initial release: the six-stage SOP, checklists, parallel multi-agent self-review, context-budget management, the AI-Wiki control tower, the technique-library framework, and blank living-document templates.

## Credits & Provenance

- Design inspired by **[Tomsawyerhu/Chinese-WebNovel-Skill](https://github.com/Tomsawyerhu/Chinese-WebNovel-Skill)** (Claude Code's `webnovel-writing` skill) — particularly its approach of "modular routing + local corpus retrieval + de-AI-flavoring throughout."
- This repository is an **independently written workflow system** — original content by its author (SOP, checklists, technique-library framework, control tower, etc.) — and **does not include or redistribute** any corpus, script, or module file from the skill above.
- The engineering habits around "control tower / PRD / issues / troubleshooting" draw on general-purpose AI long-running-project management practice.

> Note: the original skill repo above does not currently ship with an open-source license; this repo credits it only at the level of ideas and does not claim any right to relicense its content.

## License

The original content of this repository is licensed under [MIT](./LICENSE) © 2026 FeiYun-Novel.
