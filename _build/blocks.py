#!/usr/bin/env python3
"""Блоки вёрстки, общие для треков «Уроки», «Баги» и «Монетизация».

Те же классы, что на странице UX/UI (`assets/doc.css`):
.hyp, .args, .rl3, .sc — плюс .idea и .stats из `assets/shell.css`.
"""


# ─── блоки ───────────────────────────────────────────────────────────────────
def hyp(text, effect_label, effect):
    # внутри .eff тег <b> зарезервирован под сам лейбл (он display:block,
    # uppercase), поэтому выделение в тексте — через <strong>
    effect = effect.replace('<b>', '<strong>').replace('</b>', '</strong>')
    return f'''  <div class="hyp">
    <span class="tg">Гипотеза</span>
    <p>{text}</p>
    <div class="eff"><b>{effect_label}</b>
      {effect}</div>
  </div>'''


def args(items, title='Почему так'):
    """items: [(заголовок, текст, источник|None), …]"""
    cards = []
    for i, (h4, body, src) in enumerate(items, 1):
        tag = f'\n      <span class="src">{src}</span>' if src else ''
        cards.append(f'''    <div>
      <h4><i>{i:02d}</i> {h4}</h4>
      <p>{body}</p>{tag}
    </div>''')
    head = f'  <h3>{title}</h3>\n' if title else ''
    return head + '  <div class="args">\n' + '\n'.join(cards) + '\n  </div>'


def idea(title, hypothesis, argument, example, metric, note=None):
    """Слайд вида «Гипотеза · Аргумент · Пример · Метрика»."""
    rows = [('Гипотеза', hypothesis), ('Аргумент', argument),
            ('Пример', example), ('Метрика', metric)]
    body = '\n'.join(f'    <div class="idea__r"><b>{k}</b><p>{v}</p></div>' for k, v in rows)
    tail = f'\n    <div class="idea__note">{note}</div>' if note else ''
    return f'''  <div class="idea">
    <h4>{title}</h4>
{body}{tail}
  </div>'''


def table(cols, rows, note=None, aligns=None):
    aligns = aligns or [''] * len(cols)
    num = ' class="n"'          # f-строки Python 3.9 не терпят кавычек внутри выражения
    th = ''.join(f'<th{num if a == "n" else ""}>{c}</th>' for c, a in zip(cols, aligns))
    trs = []
    for r in rows:
        tds = ''.join(f'<td{num if a == "n" else ""}>{c}</td>' for c, a in zip(r, aligns))
        trs.append(f'          <tr>{tds}</tr>')
    tail = f'\n  <p class="line">{note}</p>' if note else ''
    return f'''  <div class="sc">
    <table>
      <thead><tr>{th}</tr></thead>
      <tbody>
{chr(10).join(trs)}
      </tbody>
    </table>
  </div>{tail}'''


def rl3(head_cols, rows, title=None):
    hdr = (f'    <li class="hdr"><b>{head_cols[0]}</b><span>{head_cols[1]}</span>'
           f'<span class="why">{head_cols[2]}</span></li>')
    items = '\n'.join(
        f'    <li><b>{a}</b><span>{b}</span><span class="why">{c}</span></li>'
        for a, b, c in rows)
    h = f'  <h3>{title}</h3>\n' if title else ''
    return h + f'  <ul class="rl rl3">\n{hdr}\n{items}\n  </ul>'


def stats(items, note=None, title=None):
    """items: [(число, подпись), …]"""
    cells = '\n'.join(
        f'    <div><b>{n}</b><span>{cap}</span></div>' for n, cap in items)
    h = f'  <h3>{title}</h3>\n' if title else ''
    tail = f'\n  <p class="line">{note}</p>' if note else ''
    return h + f'  <div class="stats">\n{cells}\n  </div>{tail}'


def sec(num, anchor, title, *blocks):
    return (f'<section class="blk" id="{anchor}">\n'
            f'  <div class="hd"><span class="n">{num}</span><h2>{title}</h2></div>\n'
            + '\n\n'.join(blocks) + '\n</section>')

# ─── находка аудита: номер, метки и разделы «баг · гипотеза · влияние» ──────
PILL = {'S1': 'f', 'S2': 'w', 'S3': 'g', 'Предложение': 'm', 'Новая фича': 'v'}


def shots(items):
    """Скриншоты находки: [(имя без расширения, подпись), …].

    Кадры кладёт `build_bugs_art.py` в art-audit/*.jpg. Один кадр — во всю
    ширину, несколько — сеткой.
    """
    fig = ('      <figure>\n'
           '        <img src="art-audit/{src}.jpg" alt="{cap}" loading="lazy">\n'
           '        <figcaption>{cap}</figcaption>\n'
           '      </figure>')
    figs = '\n'.join(fig.format(src=src, cap=cap) for src, cap in items)
    one = ' shots--one' if len(items) == 1 else ''
    return f'    <div class="shots{one}">\n{figs}\n    </div>'


def finding(num, title, badges, rows, pics=None, anchor=None):
    """badges: [(текст, вид|None), …]; rows: [(лейбл, текст), …];
    pics: [(файл, подпись), …] — кадры идут сразу под заголовком."""
    tags = ''.join(
        f'<span class="pill {PILL.get(kind or b, "g")}">{b}</span>'
        for b, kind in badges)
    body = '\n'.join(
        f'    <div class="idea__r"><b>{k}</b><p>{v}</p></div>' for k, v in rows)
    aid = f' id="{anchor}"' if anchor else ''
    pic = ('\n' + shots(pics)) if pics else ''
    return f'''  <div class="idea find"{aid}>
    <h4><span class="find__n">{num}</span>{title}
      <span class="find__tags">{tags}</span></h4>{pic}
{body}
  </div>'''


def steps(items, title=None):
    """Нумерованные шаги — для петли шаринга."""
    li = '\n'.join(
        f'    <li><b>{i}</b><span>{t}</span></li>' for i, t in enumerate(items, 1))
    h = f'  <h3>{title}</h3>\n' if title else ''
    return h + f'  <ol class="steps">\n{li}\n  </ol>'
