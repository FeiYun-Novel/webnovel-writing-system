# Webnovel Writing System · 网文写作系统

> **中文版：[README.md](./README.md)** · This is the English version.

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
├── README.md              # Chinese version (primary)
├── README.en.md           # This file (English version)
├── EXAMPLE.md              # Abstract example: how to fill in the slots
├── CLAUDE.md / AGENTS.md   # Project-level instruction templates for the AI (cold start, formatting rules, hard constraints)
├── 00_AI_WIKI/             # Project control tower (blank templates: current state / next action / file map / boundaries)
├── story_system/           # The system core
│   ├── README.md           # Cold-start read order, explanation of the two-tier role structure
│   ├── 写作流程.md          # Per-chapter SOP (Stage 0 → 5)
│   ├── 检查表/             # One checklist per stage (Stage 0–5)
│   ├── 章节自检清单.md      # Post-writing master checklist (6 structural items / worldbuilding & foreshadowing / recurring-mistake history)
│   ├── 上下文管理.md        # Context-budget levels and archiving policy
│   ├── 写作风格指南.md      # Voice / plain-language / information-visibility conventions (template version)
│   ├── 写前速览卡.md        # One-page pre-writing cheat sheet (template version)
│   ├── 写作技法/           # ★ Technique library "framework": routing table + placeholder guidance per category (body text left blank, fill in your own)
│   ├── scripts/style_gate.py  # ★ v1.1 machine-check gate: five numeric style checks (thresholds configurable)
│   └── 模板/               # Blank templates for all living documents (character state / foreshadowing / events / outline / summary / style sample cards…)
└── templates/角色卡/         # Blank character-card templates
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
