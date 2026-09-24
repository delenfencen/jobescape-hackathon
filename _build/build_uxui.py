#!/usr/bin/env python3
"""Готовит трек UX/UI из выгрузки артефакта «Jobescape — итоговое решение UX/UI».

Артефакт — цельная страница со своими стилями. Чтобы она жила внутри оболочки
сайта, стили скоупятся под `.doc`, а шапка и пилюли-навигация выбрасываются:
их роль играют шапка страницы и сайдбар.

Картинки артефакт ждёт в `art/*.jpg` — их кладёт `build_art.py`.
"""
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import uxui_patches

OUT = pathlib.Path(__file__).resolve().parent.parent
SRC = OUT / '_build' / 'artifact-uxui.html'   # выгрузка артефакта, как есть

if not SRC.exists():
    sys.exit(f'нет выгрузки артефакта: {SRC}\n'
             'Сохрани артефакт в HTML и положи по этому пути.')

html = SRC.read_text(encoding='utf-8')

# рантайм-обвязка claude.ai нам не нужна — берём то, что после неё
mark = '<!-- /frame-runtime -->'
if mark in html:
    html = html[html.index(mark) + len(mark):]

i = html.index('<style>', 300)
j = html.index('</style>', i)
css, rest = html[i + 7:j], html[j + 8:]
body = rest[:rest.index('</body>')]

# ── стили: всё под .doc, кроме токенов и ресета ─────────────────────────────
GLOBAL = re.compile(r'^(:root(\[[^\]]*\])?|\*|html|:focus-visible)$')


def split_rules(block):
    out, i = [], 0
    while i < len(block):
        if block[i] == '{':
            sel = block[:i].strip() if not out else block[out[-1][2]:i].strip()
            d, k = 1, i + 1
            while k < len(block) and d:
                if block[k] == '{':
                    d += 1
                elif block[k] == '}':
                    d -= 1
                k += 1
            out.append((sel, block[i + 1:k - 1], k))
            i = k
            continue
        i += 1
    return [(s, b) for s, b, _ in out]


def scope(sel):
    parts = []
    for p in (x.strip() for x in sel.split(',') if x.strip()):
        if GLOBAL.match(p):
            parts.append(p)
        elif p == 'body':
            parts.append('.doc')
        elif p.startswith('body'):
            parts.append('.doc' + p[4:])
        else:
            parts.append('.doc ' + p)
    return ', '.join(parts)


# at-правила, внутри которых лежат обычные правила — их содержимое скоупим
NESTS = re.compile(r'^@(media|supports|container|layer)\b')
# at-правила, чьё содержимое селекторами не является: 0%/50%/100% в @keyframes
# и дескрипторы в @font-face. Приписать им `.doc` — сделать правило невалидным,
# браузер выбросит его целиком, и анимации перестанут работать.
RAW = re.compile(r'^@(-\w+-)?(keyframes|font-face|page|property|counter-style)\b')


def render(rules, pad=''):
    buf = []
    for sel, inner in rules:
        if NESTS.match(sel):
            buf.append(f'{pad}{sel}{{')
            buf.append(render(split_rules(inner), pad + '  '))
            buf.append(f'{pad}}}')
        elif RAW.match(sel):
            body = ' '.join(x.strip() for x in inner.strip().split('\n'))
            buf.append(f'{pad}{sel}{{{body}}}')
        else:
            decls = ' '.join(x.strip() for x in inner.strip().split('\n'))
            buf.append(f'{pad}{scope(sel)}{{{decls}}}')
    return '\n'.join(buf)


scoped = render(split_rules(re.sub(r'/\*[\s\S]*?\*/', '', css)))
# страничную обвязку (фон, отступы) держит оболочка
scoped = re.sub(
    r'\.doc\{background:var\(--paper\); color:var\(--ink\);([^}]*)padding:0 0 5rem;\}',
    r'.doc{color:var(--ink);\1padding:0 0 4rem;}', scoped)

(OUT / 'assets' / 'doc.css').write_text(
    '/* Стили трека UX/UI — из артефакта, заскоуплены под .doc.\n'
    '   Файл генерируется: _build/build_uxui.py. Руками не править. */\n'
    + scoped + '\n', encoding='utf-8')

# ── тело: шапку и пилюли-навигацию заменяет оболочка ────────────────────────
frag = re.sub(r'<header class="top">[\s\S]*?</header>', '', body, count=1)
frag = re.sub(r'<nav class="snav">[\s\S]*?</nav>', '', frag, count=1)
frag = re.sub(r'^\s*<div class="wrap">', '', frag, count=1).rstrip()
assert frag.endswith('</div>'), 'не нашла закрывающий .wrap'
frag = frag[:-len('</div>')].rstrip()

# ── наши замены разделов поверх артефакта ───────────────────────────────────
for sid, replacement in uxui_patches.PATCHES.items():
    m = re.search(rf'<section class="blk" id="{sid}">[\s\S]*?</section>', frag)
    if not m:
        print(f'! раздела #{sid} в артефакте нет — патч не применён', file=sys.stderr)
        continue
    frag = frag[:m.start()] + replacement + frag[m.end():]
    print(f'патч: раздел #{sid} заменён')

(OUT / '_ux-ui.fragment.html').write_text(frag, encoding='utf-8')

# ── что оболочке нужно знать про разделы и шапку ────────────────────────────
nav = re.findall(r'<a href="#(\w+)"><span class="n">(\d+)</span>\s*([^<]+?)\s*</a>', body)
tiles = re.findall(r'<dt>([^<]+)</dt><dd>([^<]+)</dd>', body)
tiles = [list(t) for t in tiles]
missing = sorted({s for s in re.findall(r'<img[^>]+src="(art/[^"]+)"', frag)
                  if not (OUT / s).exists()})

# Плашки в шапке артефакта проставлены руками и отстают от содержания
# (например, аргументы добавили, а число не поправили). Те, что можно
# пересчитать по разметке, — пересчитываем и говорим, где не сошлось.
COUNTABLE = {
    'Экранов': lambda f: f.count('class="screen"'),          # по блоку на экран
    'Макетов': lambda f: len(re.findall(r'<img[^>]+src="art/v2-', f)),
    'Аргументов': lambda f: len(re.findall(r'<h4><i>\d+</i>', f)),
    'Состояний маскота': lambda f: f.count('class="stage"'),  # по сцене на состояние
    'Токенов цвета': lambda f: len(re.findall(r'<div class="h">#', f)),
}
fixed = []
for idx, (label, value) in enumerate(tiles):
    fn = COUNTABLE.get(label)
    if not fn:
        continue
    real = fn(frag)
    if real and str(real) != value:
        tiles[idx][1] = str(real)
        fixed.append(f'{label}: в артефакте {value}, по факту {real}')

# шапку и сайдбар собирает build.py — отдаём ему разделы, плашки и лид,
# чтобы после обновления артефакта они не разъехались
m = re.search(r'<p class="sub">([\s\S]*?)</p>', body)
sub = ' '.join(m.group(1).split()) if m else ''
(OUT / '_build' / 'uxui_meta.py').write_text(
    '# Генерируется build_uxui.py из артефакта. Руками не править.\n'
    f'SECTIONS = {[(n, a, t) for a, n, t in nav]!r}\n'
    f'TILES = {[tuple(t) for t in tiles]!r}\n'
    f'SUB = {sub!r}\n', encoding='utf-8')

screens = frag.count('class="screen"')
print(f'doc.css {(OUT / "assets" / "doc.css").stat().st_size} б · '
      f'фрагмент {len(frag)} симв · разделов {len(nav)} · экранов {screens}')
print('разделы:', ', '.join(f'{n} {t}' for _, n, t in nav))
print('плашки:', ', '.join(f'{k} {v}' for k, v in tiles))
if fixed:
    print('пересчитано:', *fixed, sep='\n  ')
if missing:
    print('НЕТ КАРТИНОК:', *missing, sep='\n  ')
