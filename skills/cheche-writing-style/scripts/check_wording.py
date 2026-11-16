# -*- coding: utf-8 -*-
"""文案文风体检：禁用词 / 慎用词 / 钦定术语 / 自称 / 可疑句式。

用法:
    python check_wording.py <file> [--json out.json] [--brand 主体名[,主体名...]]

    --brand  当前项目的我方主体名（如 沃橙）。用于核查自称是否统一；
             不传则只报「我们 / 咱们」并提示。

支持 .html / .htm（自动剥离 base64、<script>、<style>）与 .md / .txt 纯文本。
HTML 按 frame 标注所在页；纯文本标注行号。

检查项:
  1. 乱码 U+FFFD（文案质量）
  2. A 级禁用词（出现即改）
  3. B 级慎用词（读语境再定）
  4. C 级钦定术语的存在性提示（确认没有被误改）
  5. 自称：指代不清的「我们 / 咱们」；项目主体名出现次数
  6. 句式：不是……而是……、不只是……而……、第二人称煽动
  7. 破折号：自动区分「引出并列清单」（方案排版用法，保留）与「揭晓式」（待改）
  8. 通用规则（第三层判据）：翻案腔家族、冒号滥用（提示语 / 空转引列表）、起手式、
     段首零主语、翻译腔（只五种）、概括词盖住具体值、第二层另收（名词化 / 程度直译 / 复数硬译）
     ⚠ 第三层是**默认值**，与个人文风判据冲突时以个人文风为准，且需按方案体裁判断豁免。
       完整词面清单与实测依据见 references/ai-tells.md，适用边界见 edit-discipline.md 第七、八节。
  9. 翻案腔用量预算：把「先否定再肯定」全家族（句式两项 + GENERIC 里所有「翻案腔·」条目）
     合并计数，超出预算即报「重复使用」。**非必要不用**：默认预算 1 处，长稿（≥8000 字）2 处。
     依据见 references/banned-words.md 的「用量条款」。

本脚本只扫文案，不查结构。页数 / 图片 / 页码 / 放映脚本请用
cheche-html-deck-edit 的 check_deck.py；版式重叠请用 html-slide-overflow-qa。

注意：只对**正文**运行。若对着修改对照表运行，命中的 A/B 级词是表里
「原文」列的记录内容，不是待改问题。
"""
import io
import re
import sys
import json

# A 级：硬禁用（用户点名）
A_WORDS = ['兜底', '接得住', '这个归', '咱', '搞定', '玩意儿', '一把梭', '完事了']

# B 级：慎用，读语境再定
B_WORDS = ['接着用', '心智', '维护人', '在旁边带', '写死', '跑通', '拉通', '抓手',
           '赋能', '闭环', '其实', '非常', '比较', '一定程度上', '相对来说']

# 隐喻化口语（报告体裁）：场景化、器物化、身体化比喻 + 第一人称议论。
# 2026-10-20 用户点名（「站在 xxx 椅子上想问题」「手上有什么牌」「不能动的柱子」）。
# 逐条替换见 references/banned-words.md 的「隐喻清单」与「报告体裁的第一人称」两节。
# 说明：命中在**引用原文**里属正常（媒体评论、受访者原话），人工放行即可。
META_WORDS = [
    '椅子上', '鞋子',                        # 视角代入的隐喻
    '手上有什么牌', '手里的牌',                # 资源
    '不能动的柱子', '三根', '柱子',            # 约束
    '摊开', '账本',                          # 现状盘点
    '这条腿', '两条腿', '没长出来',            # 结构性短板
    '病根', '死因',                          # 问题成因
    '扎手', '刺人', '刺痛', '更锋利',          # 感受强度
    '逼出', '咀嚼',                          # 思考动作
    '叫来', '买单', '嫁接', '被砍掉', '在路上', # 资金与引流
    '三件套', '同款', '双刃剑', '往下挖',       # 口语碎片
    '不好卖', '不性感', '不好拍', '抢不走',      # 价值判断口语
    '我的自问', '我认为', '我看过的', '我自己的',  # 报告体裁第一人称
]

# C 级：钦定保留，确认没被误改
C_WORDS = ['召唤', '卡点', '打通', '打法', '口径卡', '留痕', '血缘', '宽表', '语义层']

# 易误报：单独扫描并列上下文
CTX_WORDS = ['坑', '爬']

# ---------------------------------------------------------------- 第三层判据
# 通用去 AI 味规则。完整词面清单、改法、方案体裁处置与实测倍率见 references/ai-tells.md；
# 适用边界见 references/edit-discipline.md 第七、八节。
# ⚠ 这一层是**默认值**，与个人文风判据冲突时以个人文风为准；
#   且必须按方案体裁判断豁免，不能照单全改。
#
# 命名约定：
#   「翻案腔·」等 —— 通用规则（第三层）
#   「…（第二层）」 —— 通用层面测不出差异，因为本方文风偏好才收（见 ai-tells.md 第二节）
GENERIC = [
    # ---- 第 1 条 翻案腔：对立式已被 A 级/B 级词表覆盖，此处认"换皮" ----
    ('翻案腔·对立式换皮',    r'(?:并非|不在于)[^。！？\s]{1,24}?[，]?(?:而是|而在于)'),
    ('翻案腔·不是A，是B',    r'不是[^。！？\s]{1,18}?，是[^。！？\s]{1,18}?[。\n]'),
    ('翻案腔·递进换皮',      r'(?:不只是|不仅是|不仅|不只|远不止是|无非是)[^。！？\s]{1,24}?更(?:要|是|为)'),
    ('翻案腔·表面…实际',     r'表面[^。！？\s]{1,20}?实际上?'),
    ('翻案腔·看似…实则',     r'看似[^。！？\s]{1,16}?实则'),
    ('翻案腔·与其说…不如说',  r'与其说[^。！？\s]{1,20}?不如说'),
    ('翻案腔·你以为…其实',    r'你以为[^。！？\s]{1,20}?其实'),
    ('翻案腔·归结语',        r'说到底|答案恰恰相反|回头才发现'),
    # ---- 第 5 条 冒号滥用 ----
    ('冒号·提示语引出',       r'(?:一句话(?:总结|说|概括)|简单说|小结|结论|核心(?:是|在于)?'
                             r'|关键(?:是|在于)?|重点(?:是)?|原因(?:如下|有|在于)?'
                             r'|问题(?:是|在于)?|答案(?:是)?|本质(?:是|上)?'
                             r'|具体(?:来说|如下|包括)?|换句话说|也就是说|建议(?:是)?)\s*[：:]'),
    ('冒号·空转句引列表',     r'(?:^|\n)[^\n：:]{4,40}[：:][ \t]*\n[ \t]*(?:[-*+]|\d+[.、])'),
    # ---- 第 9 条 禁用起手式 ----
    ('禁用起手式',           r'(?:^|\n)\s*(?:说白了|说穿了|先说结论|先说重点|直接说结论)'),
    # ---- 第 11 条 段首零主语评论（只报段首；是否真的缺回指成分需人读）----
    ('段首零主语评论',        r'(?:^|\n)\s*(?:听起来|看起来|看上去|听上去|说到底'
                             r'|值得注意|不难看出|细看|再看|回过头看|问题在于|原因在于'
                             r'|结果是|有意思的是|更重要的是|关键在于|真正的)'),
    # ---- 第 10 条 翻译腔：只这五种，勿凭语感扩大范围 ----
    ('翻译腔·过长前置定语',    r'(?:一个|一种|一套|这种|这个)[^，。、；：！？\s]{15,}的[\u4e00-\u9fff]{2,5}'),
    ('翻译腔·当…时',         r'当[^，。\s]{2,20}(?:的时候|时)，'),
    ('翻译腔·前置话题壳',      r'(?:对于[^，。\s]{2,15}来说|对[^，。\s]{2,15}而言|就[^，。\s]{2,15}而言)'),
    ('翻译腔·句首连接词',      r'(?:^|\n)\s*(?:然而|因此|此外|与此同时|换言之|总而言之)[，、]'),
    ('翻译腔·这意味着',        r'(?:这意味着|这表明|这说明)'),
    # ---- 第 8 条 概括词盖住具体值（半自动：同段是否已有具体值要人读）----
    # 不用「效率提升 / 效率的提升」这类太泛的词面——实测在样本项目里 3 处命中
    # 全部是四组组名的固定副题（结构对仗），误报率 100%。
    ('概括词盖住具体值',       r'(?:显著提升|显著提高|大幅增长|大幅提升|大幅提高|明显改善|明显提升)'),
    # ---- 第二层另收：通用层面无区分力，因本方文风偏好才收 ----
    ('名词化/轻动词（第二层）', r'(?:完成了对|实现了|作出了|进行了|给予了|予以)[^。\n\s]{0,14}?'
                             r'(?:提升|优化|调整|改造|分析|评估|检查|讨论|支持)'),
    ('程度直译（第二层）',     r'(?:在某种程度上|一定程度上|从某种意义上说|在很大程度上|相对而言)'),
    ('复数硬译（第二层）',     r'(?:一系列的|各种各样的|诸多)'),
]

# ⚠ 所有第三层正则在字符类里都排除 `\s`。
# 原因：HTML 路径剥标签时用**等长空格**替换（保偏移守恒），不同元素的内容会黏成一段，
# 正则若不排除空白就会跨元素匹配，产出垃圾命中（实测 p63 曾把"一套方法"+隔了半个页面的"的点"配成一对）。
# 排除空白后，标签留下的空格天然阻断了跨元素匹配，纯文本侧无副作用（中文长定语本来不含空格）。

# 已按方案体裁确认豁免、脚本不再报的通用规则（留档说明，见 ai-tells.md 第一、三节）：
#   顿号罗列过密 / 序数词当小标题       → 方案里是目录索引与交付物清单，按体裁豁免
#   相邻句结构同款 / 拟人化喻体          → 方案体裁不适用（结构对仗是刻意设计）
#   破折号                          → 另设独立检查，自动区分排版用法与揭晓式
#   不收录清单（被动句 / 正文问句 / 句内排比 / 比喻等 17 项）
#                                    → 实测无区分力，禁止自动扫，扫了就是误伤



def load(path):
    raw = io.open(path, encoding='utf-8').read()
    is_html = path.lower().endswith(('.html', '.htm'))
    if is_html:
        s = re.sub(r'data:image/[a-zA-Z0-9.+-]+;base64,[A-Za-z0-9+/=\s]+', '', raw)
        s = re.sub(r'<script[\s\S]*?</script>', '', s)
        s = re.sub(r'<style[\s\S]*?</style>', '', s)
    else:
        s = raw
    return s, is_html


def make_pager(s, is_html):
    if is_html:
        spans = [(m.start(), m.group(1)) for m in re.finditer(r'<div class="frame (p\d+)"', s)]
    else:
        spans, pos = [], 0
        for n, line in enumerate(s.split('\n'), 1):
            spans.append((pos, 'L%d' % n))
            pos += len(line) + 1

    def which(i):
        r = '-'
        for st, pid in spans:
            if st <= i:
                r = pid
            else:
                break
        return r
    return which


def context(s, i, n, width=26):
    return re.sub(r'\s+', ' ', s[max(0, i - width):i + n + width])


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    path = sys.argv[1]
    out_json = sys.argv[sys.argv.index('--json') + 1] if '--json' in sys.argv else None
    brands = []
    if '--brand' in sys.argv:
        i = sys.argv.index('--brand')
        if i + 1 < len(sys.argv) and not sys.argv[i + 1].startswith('--'):
            brands = [b.strip() for b in sys.argv[i + 1].split(',') if b.strip()]

    s, is_html = load(path)
    which = make_pager(s, is_html)
    # 标签用**等长空格**替换，保持字符偏移与 s 完全一致——
    # 否则 txt 的索引会前移，which() 报出的页码会系统性偏小。
    txt = re.sub(r'<[^>]+>', lambda m: ' ' * len(m.group(0)), s) if is_html else s

    report = {'file': path, 'issues': {}, 'style': {'mojibake': txt.count('\ufffd')}}

    def scan(words):
        hits = []
        for w in words:
            for m in re.finditer(re.escape(w), txt):
                hits.append({'word': w, 'page': which(m.start()),
                             'ctx': context(txt, m.start(), len(w))})
        return hits

    report['issues']['A 级 · 硬禁用'] = scan(A_WORDS)
    report['issues']['隐喻化口语（报告体裁 · 引用原文可放行）'] = scan(META_WORDS)
    report['issues']['B 级 · 慎用'] = scan(B_WORDS)
    report['issues']['C 级 · 钦定术语出现次数（确认未被误改）'] = [
        {'word': w, 'page': '-', 'ctx': '出现 %d 次' % txt.count(w)} for w in C_WORDS
    ]
    report['issues']['易误报 · 人工判断'] = scan(CTX_WORDS)

    wo = [{'word': w, 'page': which(m.start()), 'ctx': context(txt, m.start(), len(w))}
          for w in ('我们', '咱们') for m in re.finditer(w, txt)]
    report['issues']['自称 · 指代不清（我们/咱们）'] = wo
    if brands:
        report['issues']['自称 · 项目主体名出现次数（确认统一）'] = [
            {'word': b, 'page': '-', 'ctx': '%s 出现 %d 次' % (b, txt.count(b))} for b in brands]
    else:
        report['issues']['自称 · 项目主体名出现次数（确认统一）'] = [
            {'word': '-', 'page': '-', 'ctx': '未指定主体名，用 --brand 传入（如 --brand 沃橙）'}]

    # ---- 句式（个人文风判据）----
    # 前两条属于「先否定再肯定」家族（翻案腔）：除逐处报出外，还要合并计入下方的用量预算。
    # ⚠ 字符类里**排除 `\s` 但不排除逗号**：「不是技术，而是认知」这种带逗号的最常见形态要能命中；
    #   排除空白是为了不跨元素匹配（HTML 标签用等长空格替换，跨元素会产出垃圾命中）。
    pats = [
        ('翻案腔·不是…而是…', r'不是[^。；！？\s]{1,24}?而是'),
        ('翻案腔·不只是…而是…', r'不只是[^。；！？\s]{1,24}?而是'),
        ('第二人称煽动', r'[让帮](你|您)们?'),
    ]
    sent = []
    for name, pat in pats:
        for m in re.finditer(pat, txt):
            sent.append({'pattern': name, 'page': which(m.start()),
                         'ctx': context(txt, m.start(), m.end() - m.start())})
    report['issues']['句式'] = sent

    # ---- 破折号：按后文是否为并列清单自动分类 ----
    # 「标题 —— 并列清单」是方案里的排版用法，按体裁豁免保留；
    # 只有"揭晓式"破折号才需要处理。
    dash = []
    for m in re.finditer('——', txt):
        tail = txt[m.end():m.end() + 24]
        kind = ('破折号·引出并列清单（方案排版用法，保留）' if tail.count('、') >= 2
                else '破折号·揭晓式（建议改逗号或句号）')
        dash.append({'pattern': kind, 'page': which(m.start()),
                     'ctx': context(txt, m.start(), m.end() - m.start())})
    report['issues']['破折号'] = dash

    # ---- 第三层：通用规则（默认值，需按方案体裁判断豁免）----
    gen = []
    gen_count = {}
    for name, pat in GENERIC:
        for m in re.finditer(pat, txt, re.M):
            gen.append({'pattern': name, 'page': which(m.start()),
                        'ctx': context(txt, m.start(), m.end() - m.start())})
            gen_count[name] = gen_count.get(name, 0) + 1
    report['issues']['通用规则 · 第三层（冲突时以个人文风为准）'] = gen
    report['generic_count'] = gen_count

    # ---- 翻案腔用量预算（先否定再肯定 · 非必要不用）----
    # 全家族合并计数：句式里的两条 + GENERIC 里所有「翻案腔·」条目。
    # 预算：默认 1 处；长稿（≥8000 字）2 处。依据见 references/banned-words.md「用量条款」。
    budget = 2 if len(txt) >= 8000 else 1
    fanan = [h for h in (sent + gen) if h['pattern'].startswith('翻案腔')]
    if len(fanan) > budget:
        verdict = ('超支：%d 处 > 预算 %d 处 —— 重复使用，只留最关键的 1 处，其余改成直接下判断'
                   % (len(fanan), budget))
    elif fanan:
        verdict = ('预算内：%d 处 / 预算 %d 处 —— 交付说明里写明这处为什么算「必要」'
                   % (len(fanan), budget))
    else:
        verdict = '0 处 —— 符合「非必要不用」'
    report['fanan_usage'] = {
        'count': len(fanan), 'budget': budget, 'verdict': verdict,
        'hits': [{'pattern': h['pattern'], 'page': h['page'], 'ctx': h['ctx']} for h in fanan],
    }
    report['issues']['翻案腔用量（非必要不用 · 先否定再肯定）'] = (
        [{'word': '', 'pattern': '预算 %d 处 / 实际 %d 处' % (budget, len(fanan)),
          'page': '-', 'ctx': verdict}]
        + [{'word': '', 'pattern': h['pattern'], 'page': h['page'], 'ctx': h['ctx']} for h in fanan])

    kind = 'HTML（按 frame 标注页码）' if is_html else '纯文本（按行号标注）'
    print('【文件】%s  |  %s' % (path, kind))
    print('【乱码】U+FFFD 共 %d 处' % report['style']['mojibake'])
    for k, hits in report['issues'].items():
        if k.startswith('自称 · 项目主体名'):
            print('【%s】' % k)
            for h in hits:
                print('   %s' % h['ctx'])
            continue
        if k.startswith('翻案腔用量'):
            # 第一行是预算结论（超支 / 预算内 / 0 处），其后是逐处明细
            print('【%s】' % k)
            if hits:
                print('   %s' % hits[0]['ctx'])
            for h in hits[1:]:
                print('   [%s] %-18s %s' % (h['page'], h['pattern'], h['ctx']))
            continue
        if k.startswith('通用规则'):
            # 第三层按规则分组：先给各类计数，再给明细（每类最多 5 条）
            if not hits:
                print('【%s】无' % k)
                continue
            print('【%s】共 %d 处   ⚠ 第三层判据：默认值，冲突时以个人文风为准，勿照单全改'
                  % (k, len(hits)))
            by_rule = {}
            for h in hits:
                by_rule.setdefault(h['pattern'], []).append(h)
            for name, _ in GENERIC:
                if name not in by_rule:
                    continue
                items = by_rule[name]
                print('   · %s  ×%d' % (name, len(items)))
                for h in items[:5]:
                    print('       [%s] %s' % (h['page'], h['ctx']))
                if len(items) > 5:
                    print('       ...（其余 %d 处略）' % (len(items) - 5))
            continue
        note = ''
        if k.startswith('破折号'):
            note = '   （已按方案体裁自动区分保留/待改）'
        if not hits:
            print('【%s】无' % k)
            continue
        print('【%s】共 %d 处%s' % (k, len(hits), note))
        for h in hits[:40]:
            tag = h.get('word') or h.get('pattern', '')
            print('   [%s] %-10s %s' % (h.get('page', '-'), tag, h['ctx']))
        if len(hits) > 40:
            print('   ...（其余 %d 处略）' % (len(hits) - 40))

    if out_json:
        io.open(out_json, 'w', encoding='utf-8').write(
            json.dumps(report, ensure_ascii=False, indent=1))
        print('\nJSON -> %s' % out_json)


if __name__ == '__main__':
    main()
