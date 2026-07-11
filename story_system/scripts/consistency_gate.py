#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
consistency_gate.py — 状态账本一致性机检（每章封存/阶段5收尾后必跑）

用法: python3 story_system/scripts/consistency_gate.py            # 在项目根目录跑
      python3 story_system/scripts/consistency_gate.py -q         # 只输出红项/警告
      python3 story_system/scripts/consistency_gate.py --strict   # 警告也非零退出（接CI用）

设计思想：**手抄必漂移，账本一致性交给机器。**
（实证教训：状态文件里引用正文台词，抄错一个字能潜伏很多章；控制塔文件还在
指挥"写第X章"、而第X章正文其实已经存在；伏笔表状态列和实际回收列互相打架。
这些全是机械可查项——多轮 AI 审计轮轮翻出新漂移，根因就是没有脚本兜底。）

七项检查：
  🛑 1. 章号三处一致：正文/最新章号 vs 章节进度表 vs NEXT_ACTION——
        尤其抓"控制塔还在指挥写第X章、但第X章文件已存在"
  🛑 2. 伏笔清单状态自洽：状态列 🌱/⏳ 但"实际回收"列已填 = 打架；✅ 但空 = 打架
  ⚠️ 3. 台词引用核对：账本里引用的正文台词「…」，在 正文/ 全库 grep 不到 = 疑似抄旧
        （账本记台词要么贴原句、要么去引号写转述——改写了还挂引号是最危险漂移）
  ⚠️ 4. 角色"当前位置"新鲜度：人物状态各角色的章号落后最新章 2 章以上 = 过期快照
        （逐节匹配防串角色；缺字段报警；字段含"未再登场"标记的角色不催更新）
  🛑 5. 指针完整性：反引号/Markdown链接/"见 xxx.md"引用的文件必须真实存在
  🛑 6. 水位：累积状态文件总字符（阈值见 CONFIG），防上下文膨胀"失忆"
  🛑 7. 文件名/H1 全库抽查：正文/ 每章过命名规则

文件三层模型：
  活账本(强一致·红项)＝进度表/人物状态/已发生事件/伏笔清单 的结构性检查
  活索引(警告级)＝上述文件+修订记录+章节总结/ 的引语核对
  历史归档(排除)＝归档目录、二进制文件不入检

quote_whitelist.txt：已人工裁决为"合法压缩转述"的引语豁免清单（一行一条，#注释）。
只收裁决过的；真漂移一律修账本、不进白名单。

退出码: 0=全绿(警告不拦) 1=有红项 2=--strict 下有警告
"""
import glob
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SS = os.path.join(ROOT, 'story_system')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from style_gate import check_h1  # noqa: E402

# ============ CONFIG（按你自己的项目配置） ============
WATER_YELLOW = 55000   # 水位黄灯阈值（字符）
WATER_RED = 80000      # 水位红灯阈值
LEDGER_CORE = ('已发生事件.md', '人物状态.md', '章节进度表.md')   # 水位盯防的累积大户
LEDGER_QUOTE = ('章节进度表.md', '人物状态.md', '已发生事件.md', '伏笔清单.md', '修订记录.md')  # 引语核对面
FORESHADOW_ID = r'[A-Z]\d+$'   # 伏笔编号形态（如 F01/G02/M01）
# ======================================================


def load(p):
    with open(p, encoding='utf-8') as f:
        return f.read()


def exists(p):
    return os.path.exists(p)


def latest_chapter():
    nums = [(int(re.search(r'第(\d+)章', os.path.basename(p)).group(1)), p)
            for p in glob.glob(os.path.join(ROOT, '正文', '第*章-*.md'))
            if re.search(r'第(\d+)章', os.path.basename(p))]
    return max(nums) if nums else (0, None)


def main(quiet=False):
    reds, warns, oks = [], [], []
    latest, _ = latest_chapter()
    if latest == 0:
        print('== consistency_gate ==\n  （正文/ 下还没有章节文件，跳过全部检查）')
        return 0

    # ---- 1. 章号三处一致 ----
    prog_p = os.path.join(SS, '章节进度表.md')
    prog = load(prog_p) if exists(prog_p) else ''
    na_p = os.path.join(ROOT, '00_AI_WIKI', 'NEXT_ACTION.md')
    na = load(na_p) if exists(na_p) else ''
    m_last = re.search(r'最后更新：[^\n]*?第\s*(\d+)\s*章', prog)
    m_next = re.search(r'下一步[^\n]{0,10}?第\s*(\d+)\s*章', prog)
    if m_last and int(m_last.group(1)) != latest:
        reds.append(f'章号: 进度表"最后更新"=第{m_last.group(1)}章, 但正文最新=第{latest}章')
    if m_next and int(m_next.group(1)) <= latest:
        reds.append(f'章号: 进度表"下一步"=第{m_next.group(1)}章, 但该章正文已存在')
    for m in re.finditer(r'写第\s*(\d+)\s*章', na):
        if int(m.group(1)) <= latest:
            reds.append(f'章号: NEXT_ACTION 还在指挥"写第{m.group(1)}章", 但该章正文已存在')
    m_line = re.search(r'当前进度[^\n]*', prog)
    if m_line:
        ends = [int(x) for x in re.findall(r'第\s*\d+\s*[-–—]\s*(\d+)\s*章', m_line.group(0))]
        if ends and max(ends) != latest:
            reds.append(f'章号: 进度表"当前进度"完成范围到第{max(ends)}章, 但正文最新=第{latest}章')
    if not any(s.startswith('章号') for s in reds):
        oks.append(f'章号三处一致（正文最新=第{latest}章）')

    # ---- 2. 伏笔清单状态自洽（按表头定位"状态/实际回收"列） ----
    fb_p = os.path.join(SS, '伏笔清单.md')
    if exists(fb_p):
        fb = load(fb_p)
        bad2, col_status, col_actual = [], None, None
        for ln in fb.split('\n'):
            cells = [c.strip() for c in ln.split('|')]
            if col_status is None and '状态' in cells:
                col_status = cells.index('状态')
                col_actual = cells.index('实际回收') if '实际回收' in cells else len(cells) - 2
                continue
            if col_status is None or len(cells) <= max(col_status, col_actual):
                continue
            if not re.match(FORESHADOW_ID, cells[1].replace('~', '').strip() if len(cells) > 1 else ''):
                continue
            fid, status, actual = cells[1], cells[col_status], cells[col_actual]
            filled = bool(actual) and not actual.startswith(('—', '-'))
            if ('🌱' in status or '⏳' in status) and filled:
                bad2.append(f'{fid}: 状态{status[:6]} 但"实际回收"已填「{actual[:20]}」')
            if '✅' in status and not filled and '💥' not in ln:
                bad2.append(f'{fid}: 状态✅ 但"实际回收"列为空')
        if bad2:
            reds += ['伏笔自洽: ' + b for b in bad2]
        else:
            oks.append('伏笔清单状态列与实际回收列自洽')

    # ---- 3. 台词引用核对（警告级） ----
    corpus = ''.join(load(p) for p in glob.glob(os.path.join(ROOT, '正文', '第*章-*.md')))
    PUNCT = r'[\s。，！？…·、—～：；""''「」]'
    corpus_flat = re.sub(PUNCT, '', corpus)
    wl_path = os.path.join(SS, 'scripts', 'quote_whitelist.txt')
    whitelist = set()
    if exists(wl_path):
        for ln in load(wl_path).split('\n'):
            ln = ln.split('#')[0].strip()
            if ln:
                whitelist.add(re.sub(PUNCT, '', ln))
    miss3 = []
    ledger_paths = [os.path.join(SS, f) for f in LEDGER_QUOTE if exists(os.path.join(SS, f))]
    ledger_paths += sorted(glob.glob(os.path.join(SS, '章节总结', '第*章-总结.md')))
    for lp in ledger_paths:
        for m in re.finditer(r'「([^「」\n]{6,40})」|"([^"\n]{6,40})"', load(lp)):
            q = m.group(1) or m.group(2)
            if re.match(r'[，、。—…；：？！]', q):
                continue  # 两段引号之间的叙述被误捕
            if not re.search(r'[。！？…，]', q) or re.search(r'[（）【】→=＝/]|[A-Z]\d', q):
                continue
            if re.sub(PUNCT, '', q) in whitelist:
                continue
            frags = [re.sub(PUNCT, '', f) for f in re.split(r'[。，！？…、—～：；]', q)]
            frags = [f for f in frags if len(f) >= 5]
            if not frags:
                continue
            missing = [f for f in frags if f not in corpus_flat]
            if missing:
                miss3.append(f'{os.path.relpath(lp, SS)}: 「{q}」 片段「{missing[0]}」正文里 grep 不到（疑似抄旧改词，人工确认）')
    if miss3:
        warns += miss3[:10] + ([f'……共{len(miss3)}条引语核不上'] if len(miss3) > 10 else [])
    else:
        oks.append('账本引用的台词均能在正文中找到')

    # ---- 4. 角色"当前位置"新鲜度（警告级） ----
    # 逐节匹配（切到下一个 ### 为止）——跨节的贪婪匹配会在某节缺字段时把下一个角色的位置错归到它头上
    NO_LOC_OK = ('系统',)  # 无实体位置的角色（金手指/系统类），按你的书配置
    ps_p = os.path.join(SS, '人物状态.md')
    if exists(ps_p):
        stale4, noloc4 = [], []
        for sec in re.split(r'\n(?=### )', load(ps_p)):
            hm = re.match(r'### (\S+?)（', sec)
            if not hm:
                continue
            name = hm.group(1)
            lm = re.search(r'- \*\*当前位置：\*\* ([^\n]*)', sec)
            if not lm:
                if name not in NO_LOC_OK:
                    noloc4.append(name)
                continue
            loc = lm.group(1)
            if '未再登场' in loc or '未登场' in loc:  # 近期没戏份的角色不催更新（字段里标注末次章号+该标记即可）
                continue
            cm = re.search(r'第(\d+)章', loc)
            if cm and latest - int(cm.group(1)) > 2:
                stale4.append(f'{name} 当前位置停在第{cm.group(1)}章（最新第{latest}章）')
        if stale4 or noloc4:
            warns += ['位置过期: ' + s for s in stale4]
            warns += [f'缺"当前位置"字段: {n}' for n in noloc4]
        else:
            oks.append('各角色"当前位置"新鲜（落后≤2章或标记未再登场）且字段齐全')

    # ---- 5. 指针完整性 ----
    dangling = []
    scan = glob.glob(os.path.join(SS, '**', '*.md'), recursive=True)
    scan += [p for p in (os.path.join(ROOT, 'CLAUDE.md'), os.path.join(ROOT, 'AGENTS.md')) if exists(p)]
    for p in scan:
        for m in re.finditer(r'`([^`\s]+\.(?:md|py))`|\]\(([^)\s]+\.md)\)|见\s+([^\s`，。;；)（]+\.md)', load(p)):
            ref = m.group(1) or m.group(2) or m.group(3)
            if '](' in ref:
                ref = ref.split('](')[-1]
            ref = ref.strip('[]()`')
            base = os.path.basename(ref)
            if (ref.startswith('~') or '<' in ref or 'X章' in ref or '第X' in ref or '*' in ref
                    or base.startswith('_') or 'xxx' in base):
                continue
            search_dirs = [os.path.dirname(p), ROOT, SS] + \
                [os.path.join(SS, d) for d in os.listdir(SS) if os.path.isdir(os.path.join(SS, d))] + \
                [os.path.join(ROOT, d) for d in ('设定', '剧情', '角色', 'docs') if os.path.isdir(os.path.join(ROOT, d))]
            if not any(exists(os.path.join(d, ref)) for d in search_dirs):
                dangling.append(f'{os.path.relpath(p, ROOT)} → `{ref}` 不存在')
    dangling = sorted(set(dangling))
    if dangling:
        reds += ['悬空指针: ' + d for d in dangling]
    else:
        oks.append('全部文件指针可达')

    # ---- 6. 水位 ----
    total = sum(len(re.sub(r'\s', '', load(os.path.join(SS, f)))) for f in LEDGER_CORE if exists(os.path.join(SS, f)))
    if total > WATER_RED:
        reds.append(f'水位红灯: 累积状态文件 {total} 字符 > {WATER_RED}, 先归档再写（见 上下文管理.md）')
    elif total > WATER_YELLOW:
        warns.append(f'水位黄灯: {total} 字符, 本章写完就归档')
    else:
        oks.append(f'水位绿灯: {total} 字符')

    # ---- 7. 正文全库 文件名/H1 ----
    bad7 = [f'{os.path.basename(p)}: {d}' for p in sorted(glob.glob(os.path.join(ROOT, '正文', '第*章-*.md')))
            for ok, d in [check_h1(p, load(p))] if not ok]
    if bad7:
        reds += ['命名: ' + b for b in bad7]
    else:
        oks.append('正文全库文件名/H1一致')

    # ---- 输出 ----
    print('== consistency_gate ==')
    for r in reds:
        print('  🛑', r)
    for w in warns:
        print('  ⚠️ ', w)
    if not quiet:
        for o in oks:
            print('  ✅', o)
    print('  ==> ' + ('有红项：先把账本修一致再封存' if reds else ('全绿' + (f'（{len(warns)}条警告，人工过目）' if warns else '') + '，账本一致')))
    return 1 if reds else (2 if warns and '--strict' in sys.argv else 0)


if __name__ == '__main__':
    sys.exit(main(quiet='-q' in sys.argv))
