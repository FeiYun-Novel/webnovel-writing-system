#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
style_gate.py — 章节正文 AI 味机检闸门（写后第一步必跑；有红项不派审稿、不交稿）

用法: python3 story_system/scripts/style_gate.py 正文/第X章-xxx.md
退出码: 0=全绿, 1=有红项

为什么要脚本：LLM 靠"读感"数数不可靠——破折号超标数倍、对照句连排，多路审稿
代理都可能读着"没问题"。凡是数值可判定的风格规则，一律脚本核验，不信读感。

五项机检（维度通用；阈值见下方 CONFIG，是**示例默认值**，按你自己书的文风校准，
校准后同步写进你项目的 写作风格指南.md 对应小节，保持脚本与文档一致）：
  1. 叙事破折号「——」总量上限（对白/系统语音等特殊频道内不计）
  2. 「不是A，是B」式对照句上限（AI 高发句式）
  3. 明喻「像」密度上限（每 N 字最多一处）
  4. 单句成段占比上限（短句独立成段的"抒情腔"）
  5. 段内排比 = 0（同段 3 句以上同头，逐处列出）
"""
import re
import sys

# ===== CONFIG（示例默认值·按自己文风校准）=====
MAX_DASHES = 5          # 叙事破折号 ≤N / 章
MAX_CONTRAST = 3        # 「不是A是B」 ≤N / 章
XIANG_PER_CHARS = 400   # 明喻「像」 ≤1 / N字
MAX_SINGLE_RATIO = 20   # 单句成段占比 ≤N%
SINGLE_MAX_LEN = 17     # "单句成段"的段长判定（含句号）
# 需要从计数中剥除的特殊频道（按你项目的格式符号约定改）：
STRIP_PATTERNS = [
    (r"【[^】]*】", 0),        # 系统语音整段剥除
    (r"^——", re.MULTILINE),    # 行首独白格式符只剥符号本身
]
# ==============================================


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


def check(path):
    body = strip_channels(load(path))
    chars = len(re.sub(r"\s", "", body))
    results = []

    dashes = len(re.findall(r"——", body))
    results.append((f"叙事破折号 ≤{MAX_DASHES}", dashes <= MAX_DASHES, f"{dashes} 处"))

    contrast, hits = 0, []
    for par in paragraphs(body):
        for m in re.finditer(r"不是[^。！？\n]{0,25}?[，。、]\s*(?:不是[^。！？\n]{0,25}?[，。、]\s*)?(?:—*\s*)?是", par):
            contrast += 1
            hits.append(m.group(0)[:30])
    results.append((f"「不是A是B」 ≤{MAX_CONTRAST}", contrast <= MAX_CONTRAST,
                    f"{contrast} 处" + ("：" + "；".join(hits[:6]) if contrast > MAX_CONTRAST else "")))

    xiang = len(re.findall(r"像", body))
    limit3 = max(1, chars // XIANG_PER_CHARS)
    results.append((f"明喻「像」 ≤{limit3}（1/{XIANG_PER_CHARS}字）", xiang <= limit3, f"{xiang} 处 / {chars} 字"))

    pars = paragraphs(body)
    single = [p for p in pars if len(p) <= SINGLE_MAX_LEN and p.endswith("。") and len(sentences(p)) == 1]
    ratio = len(single) / len(pars) * 100 if pars else 0
    results.append((f"单句成段 ≤{MAX_SINGLE_RATIO}%", ratio <= MAX_SINGLE_RATIO,
                    f"{len(single)}/{len(pars)} 段 = {ratio:.0f}%"))

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

    print(f"== style_gate: {path} ==")
    failed = False
    for name, ok, detail in results:
        if not ok:
            failed = True
        print(f"  {'✅' if ok else '🛑'} {name}: {detail}")
    print("  ==> " + ("全绿，可进审稿环节" if not failed else "有红项：先改写再重跑，不过闸门不派审稿"))
    return failed


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    sys.exit(1 if any([check(p) for p in sys.argv[1:]]) else 0)
