<a id="中文"></a>
**🌐 Language：中文 ｜ [English](#english)**

# 网文写作系统 · Webnovel Writing System

> 一套**跨会话的「AI 写小说」工程系统**——把「写作」当成一个可持续迭代的工程流程来做：跨会话状态、每章 SOP、分阶段检查表、上下文水位管理，以及写完初稿后的跨提供方独立审稿。
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
- **风险分级审稿**：完整初稿和机检通过后，固定运行“读者体验＋写法与 AI 痕迹”，其他路线按本章触碰风险追加；每 3 章用一次轻量一致性巡检兜底。
- **单源+指针制**：每条规则/事实的全文只存一个权威源，其他文件一律一行指针——从机制上消灭"改一处忘三处"。
- **文件三层模型**：活账本（强一致·机检红项）/ 活索引（警告级）/ 历史归档（排除）——覆盖面和维护成本的平衡点。

## 核心理念

| 理念 | 说明 |
|---|---|
| **状态即文件（Cross-session state as files）** | 章节进度、伏笔、人物状态、已发生事件、未解决问题全部存 Markdown。冷启动只读文件，不靠对话记忆。 |
| **两段式封章** | 适用检查通过只算候选定稿；用户认可并完成状态同步后才正式封存，之后 forward-only，不回头改。 |
| **写前查技法，不是写完补** | 动笔前先把本章拆成几个场景，对照技法库给每场点名具体招式，产出「本章技法清单」——专治 AI 味。 |
| **上下文水位管理** | 三大累积文件定期量字数、报绿/黄/红灯，超阈值就归档，防止上下文膨胀拖垮质量与成本。 |
| **跨提供方独立审稿（v2.3）** | 完整初稿和机检通过后，由不同于主笔提供方的模型审稿；固定两路、风险追加、认领去重、两轮封顶。 |
| **机检闸门（v1.1 新增）** | 数值可判定的风格规则（破折号/对照句/明喻密度/单句段/排比）一律脚本核验——LLM 靠读感数数不可靠，多路审稿代理都可能读不出超标。写后第一步跑 `story_system/scripts/style_gate.py`，全绿才派审稿。 |
| **文风样本卡（v1.1 新增）** | 规则告诉模型"别写什么"，样本告诉模型"写成什么样"。把作者点头认可的正文选段按场景类型归档，写场景前先对同类样本——**换模型/换工具时靠它对齐文风**（抽象规则跨模型损耗大，具体范文几乎无损）。 |

## ⭐ 头牌特性：跨提供方独立审稿

同一模型既写又审，容易重复自己的盲区。v2.3 把写后检查改为**主笔提供方与审稿提供方隔离**，并把成本控制写进流程（详见 `story_system/检查表/跨模型写后审稿SOP.md`）：

- **固定两路**：读者体验、写法与 AI 痕迹每章必跑。
- **风险追加**：人物、设定伏笔、剧情因果、战斗等级等只在本章实际触碰时启动。
- **覆盖认领**：脚本先领机械项，审稿路线领专项，主笔只补空缺，避免重复通读。
- **硬伤三问**：有据、必修、非故意同时成立才算硬伤；证据不足进入待确认。
- **输出限额与两轮封顶**：按根因去重，限制低收益意见；第二轮后仍有争议就交用户裁决。

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
│   │   └── 跨模型写后审稿SOP.md # ★ v2.3 跨提供方审稿、认领、限额与复核阈值
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
4. **每章照 SOP 走**：写前读状态 + 查技法库 → 出本章计划 → 写正文 → 阶段4 跨提供方审稿 → 更新活文档。逐阶段对照 `检查表/`。

> **关于写作技法库：** 本仓库提供的是技法库的**框架**——一张"什么场景翻哪份"的路由表 + 每类技法的**占位指引**（讲清这份该放什么方向、什么内容），但**不含具体招式正文**（那是各人自己积累的手艺，需自行填充）。怎么建见 `story_system/写作技法/如何建立你自己的技法库.md`。角色、设定、题材相关的东西也都做成了**空白槽位**，填成你自己的即可。

## 关于「示例项目」

系统里偶尔用抽象举例来演示某些机制怎么落地（比如「主角专属信息机制」可以是预知/读心/面板/信息外泄等，「角色专属反应特征」可以是小动作/口头禅/瞳色变化等）。这些都是**可选示例**，不是使用本系统的前提，也不指向任何具体作品——你完全可以换成任何你自己的设定。详见 `EXAMPLE.md`。

## 更新日志

### v2.3（2026-07）——跨提供方写后审稿

- 审稿必须等完整初稿与机检通过后启动，且审稿模型提供方不同于主笔提供方。
- 固定“读者体验＋写法与 AI 痕迹”两路，人物、设定、因果、战斗等路线按风险追加。
- 引入覆盖认领制、硬伤三问、按根因计数的 findings 上限、三分之一重审阈值和两轮封顶。
- 每三章运行一次只看新增变化的轻量一致性巡检。
- 新增 `PUBLICATION_BOUNDARY.md`，明确本仓库是唯一 Public 架构发布仓库，不接收任何作品内容。

### v2.2（2026-07）——机制升级：分流器 + 两段式封存 + 状态账本硬化（经两轮双 AI 交叉审计验证）

- **新增 `写作技法/技法分流器.md`（⭐本版核心）**：技法库超过十份后"凭感觉挑卡"会退化成"永远只翻最熟的两份"。分流器把选卡变成机械判定：每章固定二问（谁被蒙在鼓里／读者推进了什么）＋逐场过判定问题清单，命中即入清单、路由精确到节。阶段2 技法清单步骤同步改为"跑分流器四小步"。
- **封存点改两段式**：原"过自检即封存"与"交用户过目"两条规则打架（用户要求改时 AI 同时收到"必须改"和"禁止改"）。现统一为：自检全过＝**候选定稿**（AI 停止自我找茬），**用户认可＋阶段5状态同步完成＝正式封存**（此后 forward-only）。全部入口文件同步（实证：终审时被外部 AI 审计发现三处入口残留旧表述——改规则要 grep 全库，别只改权威源）。
- **状态账本硬化（consistency_gate.py）**："当前位置"检查改逐节匹配（原正则会跨节把别的角色的位置错归到缺字段的角色头上）；缺字段报警；新增"未再登场"标记让没戏份的角色不被误催。人物状态模板补充位置字段维护要点（实证：位置字段最容易停在角色上次大事件那章，伤势/装备等相邻活字段要一起刷新）。
- **水位口径统一**：文档命令与机检脚本原本一个含空白一个去空白，差 3-5%，卡在灯色边界会给相反指令；统一为去空白口径。基线记录改"当前基线单列真值＋历史时间序"写法。
- **阶段2 新增"本章例外与豁免"栏**：本章获批的特殊写法集中列在计划里，写中只认这张卡；**阶段4 新增对应验收条**核对逐场兑现（没有验收回路的例外栏只是摆设）。
- **文风样本卡模板新增 S0 总基调层与优先级判定**：样本 ＞ S0——样本是作者亲口认证的原话，AI 概括的总基调只作空白场景兜底，不构成改写样本的理由。
- **过场章审稿第三路扩容**：改为"本章主角色一致性组"，纯反派章/纯配角过场不再无组可用。

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

> A **cross-session engineering system for "AI-assisted novel writing"** — treating "writing" as a sustainable, iterative engineering process: cross-session state, per-chapter SOP, staged checklists, context-budget management, and post-draft independent review by a different model provider.
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
- **Risk-tiered review**: after the full draft and machine checks pass, reader experience and AI-flavor review always run; character, continuity, causality, and combat routes are added only when the chapter actually touches those risks. A lightweight consistency sweep runs every 3 chapters.
- **Single source + pointer discipline**: every rule/fact has exactly one authoritative full-text source; every other file holds only a one-line pointer to it — structurally eliminating the "fixed it in one place, forgot the other three" failure mode.
- **Three-tier file model**: living ledger (strict consistency, machine-check red-flag level) / living index (warning level) / historical archive (excluded from active reads) — a deliberate balance between coverage and maintenance cost.

## Core Principles

| Principle | Description |
|---|---|
| **Cross-session state as files** | Chapter progress, foreshadowing, character states, event log, and open questions all live in Markdown. A cold start only reads files — it never relies on conversation memory. |
| **Two-stage sealing** | Passing all applicable checks makes a chapter a candidate final; it is officially sealed only after user approval and state synchronization, then becomes forward-only. |
| **Look up technique before writing, not patch it in after** | Before drafting, break the chapter into scenes and match each one to a specific move from the technique library, producing a "this chapter's technique checklist" — the direct antidote to AI-flavored prose. |
| **Context-budget management** | Three cumulative files are periodically measured by character count and flagged green/yellow/red; once a threshold is crossed, older content gets archived — preventing context bloat from degrading quality and inflating cost. |
| **Cross-provider independent review (v2.3)** | After a complete draft passes machine checks, a model from a different provider reviews it; two fixed routes, risk-triggered additions, claimed coverage, and a two-round cap. |
| **Machine-check gate (added in v1.1)** | Any style rule that can be judged numerically (em-dashes, contrast sentences, simile density, single-sentence paragraphs, parallelism) is verified by script — LLMs are unreliable at counting by feel, and even multi-pass review agents can miss an overage. Run `story_system/scripts/style_gate.py` as the first step after writing; only dispatch review agents once every check is green. |
| **Style sample cards (added in v1.1)** | Rules tell the model "what not to write"; samples show it "what good looks like." File author-approved prose excerpts by scene type, and reference the matching samples before writing a similar scene — **this is what keeps style consistent when you switch models or tools** (abstract rules degrade a lot across models; concrete reference prose barely degrades at all). |

## ⭐ Headline Feature: Cross-Provider Independent Review

A model reviewing its own draft can repeat the same blind spots. v2.3 separates the lead writer's provider from the review provider and builds cost control into the process (full details in `story_system/检查表/跨模型写后审稿SOP.md`):

- **Two fixed routes**: reader experience, and craft/AI-flavor.
- **Risk-triggered routes**: character, continuity, causality, and combat checks run only when touched.
- **Claimed coverage**: scripts own mechanical checks, review routes own their specialties, and the lead fills only uncovered gaps.
- **Evidence-gated severity**: a critical defect must be evidenced, mandatory to fix, and not an intentional narrative choice.
- **Capped findings and two rounds**: deduplicate by root cause, suppress low-value repetition, and hand unresolved disputes to the user after round two.

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
│   │   └── 跨模型写后审稿SOP.md # ★ v2.3 cross-provider review, coverage claims, limits, and re-review thresholds
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
4. **Follow the SOP for every chapter**: read state + look up technique references → produce this chapter's plan → write the prose → run the Stage-4 cross-provider review → update the living documents. Cross-check each stage against `检查表/`.

> **On the technique library:** what this repo provides is the **framework** of the technique library — a routing table ("which scene type maps to which file") plus **placeholder guidance** per category (what direction and content each file should hold), but **not the actual move write-ups themselves** (that's craft you accumulate yourself and fill in). See `story_system/写作技法/如何建立你自己的技法库.md` for how to build it. Characters, worldbuilding, and genre-specific content are all **blank slots** — fill them in with your own.

## About the "Example Project"

The system occasionally uses abstract examples to illustrate how a mechanism plays out in practice (e.g., a "protagonist-exclusive information mechanic" could be precognition / mind-reading / a status panel / involuntary information leakage; a "character-exclusive reaction trait" could be a tic, a catchphrase, a change in eye color, etc.). These are all **optional illustrations**, not a prerequisite for using this system, and they don't point to any specific published work — you're free to swap in whatever fits your own worldbuilding. See `EXAMPLE.md` for details.

## Changelog

### v2.3 (2026-07) — Cross-provider post-draft review

- Review starts only after a complete draft passes machine checks, and the reviewer must come from a different provider than the lead writer.
- Reader experience and craft/AI-flavor always run; other routes are risk-triggered.
- Adds claimed coverage, evidence-gated critical defects, root-cause findings caps, the one-third re-review threshold, and a two-round cap.
- Adds a lightweight consistency sweep every 3 chapters.
- Adds `PUBLICATION_BOUNDARY.md`, declaring this repository the sole public architecture release and excluding all story content.

### v2.2 (2026-07) — Mechanism upgrade: technique router + two-stage sealing + state-ledger hardening (validated by two rounds of dual-AI cross-audit)

- **New `写作技法/技法分流器.md` (technique router — the headline of this release)**: once a technique library grows past ~10 cards, "picking by feel" degenerates into "always opening the two most familiar cards." The router turns card selection into mechanical judgment: two fixed per-chapter questions (who is being kept in the dark / what does the reader advance) + a per-scene checklist of routing questions — hits go on the chapter's technique list, routed down to the specific section of a card. Stage 2's technique-list step now runs the router.
- **Sealing is now two-stage**: the old "passing self-review = sealed" rule contradicted "show the draft to the user first" (if the user requested edits, the AI received both "must change" and "must not change"). Now: all checks passed = **candidate final** (the AI stops self-nitpicking); **user approval + Stage 5 state sync = officially sealed** (forward-only from then on). All entry-point files updated in sync (lesson learned: an external AI audit caught three entry points still carrying the old wording — when changing a rule, grep the whole repo, don't just edit the authoritative source).
- **State-ledger hardening (`consistency_gate.py`)**: the "current location" freshness check now matches section-by-section (the old greedy regex could cross into the next character's section and misattribute locations when a field was missing); missing fields now warn; a "not recently on stage" marker stops the gate from nagging about characters with no recent scenes. The character-state template documents the maintenance pitfall (location fields tend to freeze at the character's last big event; adjacent live fields like injuries/equipment must be refreshed together).
- **Watermark counting unified**: the doc command and the machine gate previously counted with/without whitespace respectively — a 3-5% gap that gives contradictory light colors right at a threshold; both now use the whitespace-stripped count. Baseline records switched to "single current-baseline line as the only truth + history in strict chronological order."
- **Stage 2 gains a per-chapter "exceptions & exemptions" panel** (approved special treatments listed in the plan; during writing only this card counts) — **and Stage 4 gains the matching verification item** (an exceptions panel without a verification loop is decoration).
- **Style-sample template gains an S0 "overall register" layer with an explicit priority ruling**: samples > S0 — samples are the author's own certified words; an AI-summarized register only backfills scenes with no matching sample and never justifies rewriting one.
- **Transitional-chapter review lane widened**: the third lane is now "this chapter's main-character consistency group," so villain-POV or side-character chapters are no longer left without an applicable lane.

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
