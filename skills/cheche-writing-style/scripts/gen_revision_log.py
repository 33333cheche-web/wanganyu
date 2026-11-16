# -*- coding: utf-8 -*-
"""由 changes.json 或手写改动清单生成《文字修改对照表》，并做交付前强校验。

用法:
    python gen_revision_log.py --changes v6.json [v7.json ...] --out 对照表.md
        [--title 标题] [--note "补充说明"]
        [--verify 新文件.html]
        [--global-cats "组名,图注"]
        [--labels labels.json] [--order order.txt]
        [--cat-reason reason.json] [--drop-cats 撤销,还原,skip]
        [--untouched untouched.md]
        [--drop-old "原文片段,..."] [--fix "原文||改后"]

    # 没有 changes.json 时（纯文字改稿），直接给一份改动清单：
    python gen_revision_log.py --pairs 改动清单.txt --out 对照表.md [--verify 新文件.md]

两个输入口
    --changes  JSON，由上游脚本（如 cheche-html-deck-edit 的 apply_text_edits.py）产出。
    --pairs    纯文本清单，一行一条，手写即可。**没有 JSON 时用这个，不必依赖别的技能。**
               列序：页码 || 位置 || 原文 || 改后 || 说明 || 处数(可选)
               分隔符可用 `||`、制表符，或 Markdown 表格行（以 | 开头结尾）。
               以 # 开头的行、空行、表格分隔行会被跳过。
               页码写 `-` / `ALL` / `全局` 表示"全文统一修改"。
               示例：
                   p22 || 正文 || 不只是把数据搬过来，更要整理成口径 || 把数据整理成统一口径 || 句式规范化
                   ALL || 图注 || 沃橙团队出品 || —— || 删除占位

为什么要这个脚本
    对照表是每轮改稿的必备交付物（格式规范见 references/revision-log-format.md），
    规范里同时要求"解析表中每条改后文案，确认能在新文件里命中"。
    手工做这两件事既慢又容易漏，本脚本一次跑完。

输入格式（字段做宽容匹配，兼容不同上游脚本的产出）
    page / cls     页码（'p13' / '13' / 'ALL' / 'global' 均可；缺省视为全局）
    old / new      原文 / 改后（new 为空或 null 表示整段删除）
    pos            页内位置（大标题 / 副标题 / 右下角图注 …）
    cat            类别（用于匹配 --cat-reason，也用于 --drop-cats 过滤）
    why / reason   说明；缺省时按 cat 去 --cat-reason 里查
    n / hits / count  命中处数；缺省为 1

多轮合并（链式归约到净结果）
    依次读取多个 changes 文件，**键只用「原文」**，后一轮覆盖前一轮；
    再沿新值把链走到尾：A→B（第一轮）、B→C（第二轮）合并为 **A→C**，中继的 B 不出现在表里。
    回到起点（A→B→A）判为净无改动，整条不入表。
    cat 命中 --drop-cats 的条目直接丢弃（用于"本轮撤销上一轮改动"）。

分节
    页码为 ALL / global / 全局的条目，或 cat 命中 --global-cats 的条目，
    归入第一节「全文统一修改」；其余归入第二节「逐页文字修改」。

强校验（--verify，强烈建议每次都用）
    解析表中每条「改后」文案，剥离 HTML 标签并归一化空白后，确认它能在新文件里命中。
    命中不了就是表或文件有错，必须查清再交付；脚本会打印未命中清单。
    （「（整段删除）」这类条目天然命中不了，已自动跳过。）

逃生口（数据形态对不上时用）
    --drop-old "片段"    原文含该片段的条目整条丢弃（上一轮改过、本轮撤销但不产出条目）
    --fix "原文||改后"   人工修正某条的改后值（交叉引用文案这类要接上链路时）
"""
import io
import json
import os
import re
import sys


# ------------------------------------------------------------------ 小工具
def pick(d, *keys, default=None):
    """从上到下取第一个存在且非空的值——兼容不同上游脚本的字段命名。"""
    for k in keys:
        v = d.get(k)
        if v not in (None, ''):
            return v
    return default


def clean(x):
    """去掉 HTML 标签与全角占位空格，便于阅读。"""
    x = re.sub(r'<[^>]+>', '', str(x))
    return x.replace('\u3000', ' ').strip()


def norm(x):
    """强校验用的归一化：剥标签 + 去掉全部空白。"""
    return re.sub(r'[\s\u3000]+', '', re.sub(r'<[^>]+>', '', str(x)))


GLOBAL_PAGES = {'ALL', 'all', 'global', 'GLOBAL', '全局', '-', ''}


def is_global(page):
    return str(page).strip() in GLOBAL_PAGES


def load_pairs(path):
    """读手写的改动清单：一行一条，`页码 || 位置 || 原文 || 改后 || 说明 || 处数`。

    分隔符依次尝试 `||` → 制表符 → Markdown 表格行（首尾竖线包裹时按 `|` 拆）。
    空行、`#` 注释行、Markdown 表格分隔行（|---|---|）一律跳过。
    """
    out = []
    for ln in io.open(path, encoding='utf-8'):
        s = ln.strip()
        if not s or s.startswith('#') or re.fullmatch(r'[\s|:\-]+', s):
            continue
        if '||' in s:
            parts = s.split('||')
        elif '\t' in s:
            parts = s.split('\t')
        elif s.startswith('|') and s.endswith('|'):
            parts = s.strip('|').split('|')
        else:
            continue                       # 认不出分隔符就跳过，不猜
        parts = [p.strip() for p in parts]
        if len(parts) < 3 or not parts[2]:
            continue
        if parts[0] in ('页码', 'page', 'Page') or parts[2] in ('原文', 'old'):
            continue                       # 表头行，不是数据
        g = lambda i: parts[i] if i < len(parts) else ''
        try:
            n = int(g(5) or 1)
        except ValueError:
            n = 1
        out.append({'page': g(0) or 'ALL', 'pos': g(1), 'cat': '',
                    'old': g(2), 'new': g(3), 'why': g(4), 'n': n})
    return out


# ------------------------------------------------------------------ 参数
def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        if i + 1 < len(sys.argv):
            return sys.argv[i + 1]
    return default


def main():
    change_files = []
    if '--changes' in sys.argv:
        i = sys.argv.index('--changes')
        for a in sys.argv[i + 1:]:
            if a.startswith('--'):
                break
            change_files.append(a)
    pair_files = []
    for flag in ('--pairs', '--pairs-file'):
        if flag in sys.argv:
            i = sys.argv.index(flag)
            for a in sys.argv[i + 1:]:
                if a.startswith('--'):
                    break
                pair_files.append(a)

    if ('--out' not in sys.argv) or (not change_files and not pair_files):
        print(__doc__)
        sys.exit(1)

    out_path = arg('--out')
    verify_path = arg('--verify')
    title = arg('--title', '文字修改对照表')
    note = arg('--note', '')
    untouched_path = arg('--untouched')
    drop_cats = [s.strip() for s in (arg('--drop-cats', '撤销,还原,skip,skip_all') or '').split(',')
                 if s.strip()]
    global_cats = [s.strip() for s in (arg('--global-cats', '') or '').split(',') if s.strip()]
    # 逃生口：数据形态对不上时（上一轮改过、本轮撤销但不产出条目；原文带不同前缀）按原文字面处理
    drop_old = [s.strip() for s in (arg('--drop-old', '') or '').split(',') if s.strip()]
    fixes = {}
    for i, a in enumerate(sys.argv):
        if a == '--fix' and i + 1 < len(sys.argv) and '||' in sys.argv[i + 1]:
            o, n = sys.argv[i + 1].split('||', 1)
            fixes[o.strip()] = n.strip()
    labels = json.load(io.open(arg('--labels'), encoding='utf-8')) if arg('--labels') else {}
    cat_reason = json.load(io.open(arg('--cat-reason'), encoding='utf-8')) if arg('--cat-reason') else {}
    order = []
    if arg('--order'):
        order = [l.strip() for l in io.open(arg('--order'), encoding='utf-8') if l.strip()]

    # -------------------------------------------------------------- 读入（后轮覆盖前轮）
    # 顺序：先 --changes（多轮存档，早的在前），再 --pairs（手写清单，优先级最高）。
    records = []
    for f in change_files:
        records.extend(json.load(io.open(f, encoding='utf-8')))
    for f in pair_files:
        records.extend(load_pairs(f))

    by_old, dropped = {}, 0
    for c in records:
        old = clean(pick(c, 'old', default=''))
        if not old:
            continue
        new_raw = pick(c, 'new', default=None)
        cat = str(pick(c, 'cat', 'category', default='')).strip()
        if any(d and d in old for d in drop_old):
            by_old.pop(old, None)
            dropped += 1
            continue
        if any(d and d in cat for d in drop_cats):
            by_old.pop(old, None)          # 本轮撤销上一轮的改动 → 净结果里不留痕迹
            dropped += 1
            continue
        by_old[old] = {
            'page': str(pick(c, 'page', 'cls', default='ALL')).strip(),
            'old': old,
            'new': clean(new_raw) if new_raw is not None else '',
            'pos': clean(pick(c, 'pos', 'position', default='')),
            'cat': cat,
            'why': clean(pick(c, 'why', 'reason', default='')) or cat_reason.get(cat, ''),
            'n': int(pick(c, 'n', 'hits', 'count', default=1) or 1),
        }

    # -------------------------------------------------------------- 链式归约到净结果
    # 改稿是多轮的，同一位文案可能被连着改两次：A→B（第一轮）、B→C（第二轮）。
    # 合到表里要给出 A→C，中继的 B 不能出现，用户看不到中间态。
    # 所以键只用「原文」，再沿新值把链走到尾；回到起点说明净结果没有改动，整条不入表。
    for o, n in fixes.items():
        if o in by_old:
            by_old[o]['new'] = n          # 人工修正：把断掉的链路接上（如交叉引用文案）
    intermediates = {v['new'] for v in by_old.values() if v['new']}
    merged, cycles = {}, 0
    for old, item in by_old.items():
        if old in intermediates:
            continue                        # 中间态，跳过
        seen, cur = {old}, item
        while True:
            nxt = cur['new']
            if not nxt or nxt in seen or nxt not in by_old:
                break
            seen.add(nxt)
            cur = by_old[nxt]
        tail = cur['new']
        if tail == old or (tail and tail in seen):
            cycles += 1                     # 回到起点 / 成环：净结果不成立，不入表
            continue
        merged[(item['page'], old)] = {
            'page': item['page'], 'old': old,
            'new': tail,
            'pos': cur['pos'] or item['pos'],
            'cat': cur['cat'] or item['cat'],
            'why': cur['why'] or item['why'],
            'n': max([by_old[x]['n'] for x in seen if x in by_old] or [item['n']]),
            'del': (tail == ''),
        }

    def label(page):
        if page in labels:
            return labels[page]
        if re.fullmatch(r'[pP]\d+', page):
            return 'P' + page[1:].zfill(2)
        if page.isdigit():
            return 'P' + page.zfill(2)
        return page

    # -------------------------------------------------------------- 分组
    per_page, gsum = {}, {}
    for (page, old), c in merged.items():
        is_g = is_global(page) or any(g and g in c['cat'] for g in global_cats)
        if is_g:
            k = (c['old'], '（整段删除）' if c['del'] else c['new'], c['why'])
            g = gsum.setdefault(k, {'n': 0, 'pos': []})
            g['n'] += c['n']
            if c['pos'] and c['pos'] not in g['pos']:
                g['pos'].append(c['pos'])
        else:
            per_page.setdefault(label(page), []).append(c)

    tot_page = sum(c['n'] for lst in per_page.values() for c in lst)
    tot_glob = sum(v['n'] for v in gsum.values())

    # -------------------------------------------------------------- 输出
    L = []
    w = L.append
    w('# %s' % title)
    w('')
    w('> 全稿共修改 **%d 处文案**（逐页 %d 处 / %d 页，全文统一 %d 类 %d 处）。'
      % (tot_page + tot_glob, tot_page, len(per_page), len(gsum), tot_glob))
    if note:
        w('>')
        w('> %s' % note)
    w('')
    w('---')
    w('')

    if gsum:
        w('## 一、全文统一修改')
        w('')
        w('| # | 位置 | 原文 | 改后 | 处数 | 说明 |')
        w('|---|---|---|---|---|---|')
        for j, ((old, new, why), v) in enumerate(gsum.items(), 1):
            pos = '、'.join(v['pos']) if v['pos'] else '全稿'
            w('| %d | %s | %s | %s | %d 处 | %s |' % (j, pos, old, new, v['n'], why or '—'))
        w('')
        w('---')
        w('')

    w('## 二、逐页文字修改')
    w('')
    w('| # | 页码 | 位置 | 原文 | 改后 | 说明 |')
    w('|---|---|---|---|---|---|')
    seen, j = [], 0
    for lab in (order or sorted(per_page, key=lab_sort_key)):
        for c in per_page.get(lab, []):
            j += 1
            w('| %d | %s | %s | %s | %s | %s |'
              % (j, lab, c['pos'] or '—', c['old'], '（整段删除）' if c['del'] else c['new'],
                 c['why'] or '—'))
            seen.append(lab)
    for lab in per_page:                    # order 里漏掉的页，补在最后
        if lab in seen:
            continue
        for c in per_page[lab]:
            j += 1
            w('| %d | %s | %s | %s | %s | %s |'
              % (j, lab, c['pos'] or '—', c['old'], '（整段删除）' if c['del'] else c['new'],
                 c['why'] or '—'))
    w('')
    w('---')
    w('')

    if untouched_path:
        w('## 三、本次未改动的内容')
        w('')
        w(io.open(untouched_path, encoding='utf-8').read().strip())
        w('')

    # -------------------------------------------------------------- 强校验
    failures = []
    if verify_path:
        s = io.open(verify_path, encoding='utf-8').read()
        s = re.sub(r'data:image/[a-zA-Z0-9.+-]+;base64,[A-Za-z0-9+/=\s]+', '', s)
        hay = norm(s)
        for (page, old), c in merged.items():
            if c['del'] or not c['new']:
                continue
            if norm(c['new']) not in hay:
                failures.append((label(page), clean(c['new'])))
        w('---')
        w('')
        w('## 校验结果')
        w('')
        if failures:
            w('**未通过**：表中下列 %d 条「改后」文案在目标文件里命中不了，须查清再交付。' % len(failures))
            w('')
            for lab, t in failures:
                w('- `%s` %s' % (lab, t[:80]))
        else:
            w('**通过**：表中全部「改后」文案均能在目标文件中命中。')
        w('')

    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    io.open(out_path, 'w', encoding='utf-8').write('\n'.join(L) + '\n')

    print('对照表 -> %s' % out_path)
    print('逐页 %d 处 / %d 页 | 全文统一 %d 类 %d 处 | 合计 %d 处 | 撤销类丢弃 %d 条 | 净无改动 %d 条'
          % (tot_page, len(per_page), len(gsum), tot_glob, tot_page + tot_glob, dropped, cycles))
    if verify_path:
        print('强校验：%s（%d 条未命中）' % ('未通过' if failures else '通过', len(failures)))
        for lab, t in failures:
            print('  FAIL  %-6s %s' % (lab, t[:60]))


def lab_sort_key(lab):
    m = re.fullmatch(r'[Pp](\d+)', lab)
    return (0, int(m.group(1))) if m else (1, lab)


if __name__ == '__main__':
    main()
