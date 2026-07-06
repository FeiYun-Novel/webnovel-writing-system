#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
style_gate.py — 章节正文文风机检闸门（写后第一步必跑；有红项不派审稿、不交稿）

用法: python3 story_system/scripts/style_gate.py 正文/第X章-xxx.md
退出码: 0=全绿可派审稿代理, 1=有红项须先改写

设计思想：**LLM 靠读感数数不可靠，数值规则一律脚本核验。**
（实证教训：给 AI 立了"破折号每章 ≤5"的文字规则，连续三章分别写了 18/9/6 处，
多路 AI 审稿全部放过——让语言模型"数数"本来就不靠谱。有明细词表的词汇层规则
基本零违规，没有数字门槛的句式层规则大面积复发。结论：凡是能数、能 grep 的
规则全部交给脚本；人工/AI 只查语义判断题。红项没清就派审稿代理＝白花钱。）

通用机检项（句式层，任何中文网文都适用；阈值在 CONFIG 区按自己文风校准，
校准后同步写进你项目的写作风格指南对应小节，保持脚本与文档一致）：
  0. 最低字数 ≥ MIN_CHARS（全文去空白字符数）
  1. 叙事破折号「——」总量上限（特殊频道内不计）
  2. 「不是A，是B」对照句式上限（防"先否定再点出真相"的顿悟模板抽卡）
  3. 明喻「像」密度上限（每 N 字最多一处）
  4. 单句成段占比上限（防"电影分镜短句轰炸"的抒情腔）
  5. 段内排比 = 0（同段 3 句以上同头，逐处列出）
  6. 符号配对：（）【】「」数量、闭合顺序、跨类型嵌套均校验
  7. 文件名/H1 一致（第X章编号 + 标题一字不差；〔执笔标注〕不计）

可配置机检项（按你自己的书填词表）：
  8. 禁用词黑名单 =0（"正文不许出现"的词——设定专有暗示词、决定淡出的梗类词等）
  9. 敏感词 =0（平台红线词）
"""
import os
import re
import sys

# ============ CONFIG（示例默认值·按你自己的书校准） ============

MIN_CHARS = 2000        # 每章最低字数
MAX_DASHES = 5          # 叙事破折号 ≤N / 章
MAX_CONTRAST = 3        # 「不是A是B」 ≤N / 章
XIANG_PER_CHARS = 400   # 明喻「像」 ≤1 / N字
MAX_SINGLE_RATIO = 20   # 单句成段占比 ≤N%
SINGLE_MAX_LEN = 17     # "单句成段"的段长判定（含句号）

# 需要从句式计数中剥除的特殊频道（按你项目的格式符号约定改）：
STRIP_PATTERNS = [
    (r"【[^】]*】", 0),        # 系统语音类整段剥除
    (r"^——", re.MULTILINE),    # 行首独白格式符只剥符号本身
]

# 禁用词：正文不许出现的词。例：你的书若有"角色特征靠暗示不点破"类铁律，
# 把会点破的词填进来；若某类梗决定从第 N 章起淡出，把梗词填进来并配起始章
TABOO_RE = None            # 例: re.compile(r"词1|词2|词3")
TABOO_WHITELIST = ()       # 含禁用字但无害的常用词（成语等），例: ("狐疑",)
EXEMPT_NICKNAMES = ()      # 引号内"角色语言"豁免词（如外号），命中只警告不拦
TABOO_FROM_CHAPTER = 1     # 禁用词从第几章起生效（此前旧章只提示不拦）

# 敏感词：平台红线（按你的发布平台填）
SENSITIVE_RE = None        # 例: re.compile(r"敏感词1|敏感词2")

# ================================================================

CN_DIGITS = "零一二三四五六七八九"


def load(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def strip_channels(text):
    for pat, flags in STRIP_PATTERNS:
        text = re.sub(pat, "", text, flags=flags)
    return text


def paragraphs(text):
    return [p.strip() for p in text.split("\n") if p.strip() and not p.strip().startswith("#")]


def sentences(par):
    return [s for s in re.split(r"[。！？…]+", par) if s.strip()]


def cn_num(n):
    """阿拉伯数字 → 中文数字（1-999）"""
    if n < 10:
        return CN_DIGITS[n]
    if n < 20:
        return "十" + (CN_DIGITS[n % 10] if n % 10 else "")
    if n < 100:
        return CN_DIGITS[n // 10] + "十" + (CN_DIGITS[n % 10] if n % 10 else "")
    s = CN_DIGITS[n // 100] + "百"
    rem = n % 100
    if rem == 0:
        return s
    if rem < 10:
        return s + "零" + CN_DIGITS[rem]
    if rem < 20:
        return s + "一" + cn_num(rem)  # 110→一百一十
    return s + cn_num(rem)


def chapter_no(path):
    m = re.search(r"第(\d+)章", os.path.basename(path))
    return int(m.group(1)) if m else None


def scan_words(raw, pattern, whitelist=(), soft_nicknames=False):
    """返回命中列表 [(位置, 片段, 是否豁免为警告)]。
    soft_nicknames=True 时：豁免词出现在（）或「」引号内 → 降级为警告"""
    speech_spans = [m.span() for m in re.finditer(r"（[^）]*）|「[^」]*」", raw)]
    hits = []
    for m in re.finditer(pattern, raw):
        i = m.start()
        ctx = raw[max(0, i - 3):m.end() + 3]
        if any(w in ctx for w in whitelist):
            continue
        in_speech = any(a <= i < b for a, b in speech_spans)
        is_nick = any(n in raw[max(0, i - 3):m.end() + 3] for n in EXEMPT_NICKNAMES)
        soft = soft_nicknames and is_nick and in_speech
        snippet = raw[max(0, i - 6):m.end() + 6].replace("\n", " ")
        hits.append((i, snippet, soft))
    return hits


def check_h1(path, raw):
    """文件名 第X章-标题.md ↔ H1 # 第中文数字章　标题（〔执笔模型〕类标注不计）"""
    base = os.path.basename(path)
    m_file = re.match(r"第(\d+)章-(.+)\.md$", base)
    if not m_file:
        return False, f"文件名不合规范: {base}"
    num, title = int(m_file.group(1)), m_file.group(2)
    m_h1 = re.search(r"^#\s*第(.+?)章[　\s]+(.+)$", raw, flags=re.MULTILINE)
    if not m_h1:
        return False, "找不到 H1（# 第X章　标题）"
    h1_num, h1_title = m_h1.group(1).strip(), m_h1.group(2).strip()
    h1_title = re.sub(r"〔[^〕]*〕", "", h1_title).strip()
    if h1_num != cn_num(num):
        return False, f"章号不一致: 文件名第{num}章 vs H1第{h1_num}章（应为{cn_num(num)}）"
    if h1_title != title:
        return False, f"标题不一致: 文件名「{title}」 vs H1「{h1_title}」"
    return True, f"第{num}章「{title}」一致"


def check(path):
    raw = load(path)
    body = strip_channels(raw)
    chars = len(re.sub(r"\s", "", body))
    results = []  # (name, ok, detail)

    # 0. 最低字数
    raw_chars = len(re.sub(r"\s", "", raw))
    results.append((f"最低字数 ≥{MIN_CHARS}", raw_chars >= MIN_CHARS, f"{raw_chars} 字"))

    # 1. 叙事破折号
    dashes = len(re.findall(r"——", body))
    results.append((f"叙事破折号 ≤{MAX_DASHES}", dashes <= MAX_DASHES, f"{dashes} 处"))

    # 2. 「不是A，是B」对照句式
    contrast, hits2 = 0, []
    for par in paragraphs(body):
        for m in re.finditer(r"不是[^。！？\n]{0,25}?[，。、]\s*(?:不是[^。！？\n]{0,25}?[，。、]\s*)?(?:—*\s*)?是", par):
            contrast += 1
            hits2.append(m.group(0)[:30])
    results.append((f"「不是A是B」 ≤{MAX_CONTRAST}", contrast <= MAX_CONTRAST,
                    f"{contrast} 处" + ("：" + "；".join(hits2[:6]) if contrast > MAX_CONTRAST else "")))

    # 3. 明喻密度（粗筛：排除明确非明喻的名词组合；超标后人工复核）
    body3 = re.sub(r"影像|画像|神像|塑像|偶像|镜像|头像|人像|录像|想像", "", body)
    xiang = len(re.findall(r"像", body3))
    limit3 = max(1, chars // XIANG_PER_CHARS)
    results.append((f"明喻「像」 ≤{limit3}（1/{XIANG_PER_CHARS}字）", xiang <= limit3, f"{xiang} 处 / {chars} 字"))

    # 4. 单句成段占比
    pars = paragraphs(body)
    single = [p for p in pars if len(p) <= SINGLE_MAX_LEN and p.endswith("。") and len(sentences(p)) == 1]
    ratio = len(single) / len(pars) * 100 if pars else 0
    results.append((f"单句成段 ≤{MAX_SINGLE_RATIO}%", ratio <= MAX_SINGLE_RATIO,
                    f"{len(single)}/{len(pars)} 段 = {ratio:.0f}%"))

    # 5. 段内排比
    parallel_hits = []
    for par in pars:
        heads = {}
        for s in [s.strip() for s in sentences(par) if len(s.strip()) >= 2]:
            heads.setdefault(s[:2], []).append(s)
        for head, group in heads.items():
            if len(group) >= 3:
                parallel_hits.append(f"「{head}…」×{len(group)}: {par[:40]}…")
    results.append(("段内排比 =0", not parallel_hits,
                    f"{len(parallel_hits)} 处" + ("\n      " + "\n      ".join(parallel_hits) if parallel_hits else "")))

    # 6. 符号配对（全局单栈：数量+闭合顺序+跨类型嵌套）
    OPENS = {"（": "）", "【": "】", "「": "」"}
    CLOSES = {v: k for k, v in OPENS.items()}
    stack, pair_bad = [], []
    for idx, ch2 in enumerate(raw):
        if ch2 in OPENS:
            stack.append((ch2, idx))
        elif ch2 in CLOSES:
            if not stack:
                pair_bad.append(f"{ch2} 无配对起始（第{idx}字符附近：{raw[max(0, idx - 10):idx + 5]}）")
                break
            o, oi = stack.pop()
            if OPENS[o] != ch2:
                pair_bad.append(f"嵌套错序：{o}…{ch2}（第{idx}字符附近：{raw[max(0, idx - 10):idx + 5]}）")
                break
    if not pair_bad and stack:
        pair_bad.append("未闭合：" + "".join(o for o, _ in stack[:5]))
    results.append(("符号配对", not pair_bad, "；".join(pair_bad) if pair_bad else "（）【】「」均成对且嵌套正确"))

    # 7. 文件名/H1 一致
    ok7, detail7 = check_h1(path, raw)
    results.append(("文件名/H1 一致", ok7, detail7))

    # 8. 禁用词（可配置；未配置则跳过）
    if TABOO_RE is not None:
        ch = chapter_no(path)
        hits = scan_words(raw, TABOO_RE, TABOO_WHITELIST, soft_nicknames=True)
        hard = [s for _, s, soft in hits if not soft]
        soft = [s for _, s, soft in hits if soft]
        if ch is not None and ch < TABOO_FROM_CHAPTER:
            results.append((f"禁用词（第{TABOO_FROM_CHAPTER}章前豁免）", True, f"{len(hard)} 处（旧章不拦）"))
        else:
            detail = f"{len(hard)} 处" + ("：" + "；".join(hard[:5]) if hard else "")
            if soft:
                detail += f"（另⚠️引号内豁免词 {len(soft)} 处，允许）"
            results.append(("禁用词 =0", not hard, detail))

    # 9. 敏感词（可配置；未配置则跳过）
    if SENSITIVE_RE is not None:
        sv = [s for _, s, _ in scan_words(raw, SENSITIVE_RE)]
        results.append(("敏感词 =0", not sv, f"{len(sv)} 处" + ("：" + "；".join(sv[:5]) if sv else "")))

    # 输出
    print(f"== style_gate: {path} ==")
    failed = False
    for name, ok, detail in results:
        mark = "✅" if ok else "🛑"
        if not ok:
            failed = True
        print(f"  {mark} {name}: {detail}")
    print("  ==> " + ("全绿，可派审稿代理" if not failed else "有红项：先改写再重跑，不过闸门不派审稿"))
    return failed


if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print(__doc__)
        sys.exit(2)
    any_fail = False
    for p in sys.argv[1:]:
        if check(p):
            any_fail = True
        print()
    sys.exit(1 if any_fail else 0)
