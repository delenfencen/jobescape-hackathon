#!/usr/bin/env python3
"""Готовит дек «Уроки и персональный план 45+» для сайта: убирает слайд монетизации.

Источник — выгрузка артефакта в HTML. Дек самодостаточный (Tailwind + свой
скринридер-скейлер), поэтому на странице он живёт в iframe, а не вклеивается
в разметку: его глобальный ресет иначе сносит стили оболочки.
"""
import json
import pathlib
import re
import sys

OUT = pathlib.Path(__file__).resolve().parent.parent
SRC = pathlib.Path(
    '/Users/delenfencen/Downloads/hackathon/final/все слайд/'
    'Уроки_и_персональный_план_для_аудитории_45+.html')
DEST = OUT / 'lessons-deck.html'

# что вырезаем — id слайда в исходном деке
DROP = {'30'}          # «Монетизация · Апсел планов и семейная подписка»

if not SRC.exists():
    sys.exit(f'нет исходника: {SRC}')

html = SRC.read_text(encoding='utf-8')

# ── 1. слайды ────────────────────────────────────────────────────────────────
body_at = html.index('<body')
head, body = html[:body_at], html[body_at:]

chunks = re.split(r'(?=<section class="deck-slide")', body)
kept, dropped = [], []
for ch in chunks:
    m = re.match(r'<section class="deck-slide" id="(\d+)"', ch)
    if m and m.group(1) in DROP:
        dropped.append(m.group(1))
        continue
    kept.append(ch)
if set(dropped) != DROP:
    sys.exit(f'не нашла слайды {DROP - set(dropped)}')
body = ''.join(kept)

# ── 2. нумерация «Slide N of M» ──────────────────────────────────────────────
total = len(re.findall(r'<section class="deck-slide"', body))
counter = iter(range(1, total + 1))
body = re.sub(r'aria-label="Slide \d+ of \d+"',
              lambda _: f'aria-label="Slide {next(counter)} of {total}"', body)

# ── 3. конфиг анимаций: индексы в нём позиционные, слайд надо убрать и там ───
m = re.search(r'(<script type="application/json" id="deck-motion"[^>]*>)([\s\S]*?)(</script>)', head)
motion = json.loads(m.group(2))
motion['slides'] = [s for i, s in enumerate(motion['slides']) if str(i + 1) not in DROP]
assert len(motion['slides']) == total, (len(motion['slides']), total)
head = head[:m.start()] + m.group(1) + json.dumps(motion, ensure_ascii=False) + m.group(3) + head[m.end():]

# ── 4. титульный слайд больше не обещает раздел, которого нет ───────────────
body = body.replace(
    'Онбординг, форматы уроков, геймификация и монетизация — с опорой на JTBD стрел и исследования',
    'Онбординг, форматы уроков и геймификация — с опорой на JTBD стрел и исследования')

DEST.write_text(head + body, encoding='utf-8')
print(f'{DEST.name}: слайдов {total}, убрано {sorted(dropped)}, {DEST.stat().st_size} байт')
