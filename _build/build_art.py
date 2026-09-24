#!/usr/bin/env python3
"""Собирает картинки трека UX/UI в art/*.jpg.

Список берётся из самого артефакта — какие `art/*.jpg` он просит, такие
и кладём. Исходники ищутся PNG-шками по папкам хакатона и конвертируются
в JPEG шириной 1600 px: на экране разницы не видно, вес падает кратно.

Запускать до build_uxui.py (он в конце проверяет, что всё на месте).
"""
import pathlib
import re
import subprocess
import sys

OUT = pathlib.Path(__file__).resolve().parent.parent
ART = OUT / 'art'
SRC = OUT / '_build' / 'artifact-uxui.html'
H = pathlib.Path('/Users/delenfencen/Downloads/hackathon')

# где искать исходники — берётся первое совпадение
PLACES = [H, H / 'final web', H / 'final' / 'все слайд', H / 'final' / 'маскот']

WIDTH = 1600
QUALITY = 80


def main():
    if not SRC.exists():
        sys.exit(f'нет выгрузки артефакта: {SRC}')

    need = sorted({pathlib.Path(s).stem for s in
                   re.findall(r'src="art/([^"]+)"', SRC.read_text(encoding='utf-8'))})
    if not need:
        sys.exit('артефакт не ссылается ни на одну картинку — проверь выгрузку')

    ART.mkdir(exist_ok=True)
    done, skipped, missing = 0, 0, []
    for name in need:
        dst = ART / f'{name}.jpg'
        src = next((p / f'{name}.png' for p in PLACES
                    if (p / f'{name}.png').exists()), None)
        if src is None:
            if dst.exists():          # уже сконвертирована раньше, исходник унесли
                skipped += 1
                continue
            missing.append(name)
            continue
        if dst.exists() and dst.stat().st_mtime >= src.stat().st_mtime:
            skipped += 1
            continue
        r = subprocess.run(
            ['sips', '-s', 'format', 'jpeg', '-s', 'formatOptions', str(QUALITY),
             '-Z', str(WIDTH), str(src), '--out', str(dst)],
            capture_output=True)
        if r.returncode:
            missing.append(f'{name} (sips: {r.stderr.decode().strip()})')
        else:
            done += 1

    # что лежит в art/, но артефактом больше не используется
    stale = sorted(f.name for f in ART.glob('*.jpg') if f.stem not in need)

    size = sum(f.stat().st_size for f in ART.glob('*.jpg')) / 1e6
    print(f'нужно {len(need)} · сконвертировано {done} · было готово {skipped} '
          f'· {size:.1f} МБ в art/')
    if stale:
        print(f'не используется артефактом ({len(stale)}):',
              ', '.join(stale[:6]) + (' …' if len(stale) > 6 else ''))
    if missing:
        print('НЕ НАЙДЕНЫ ИСХОДНИКИ:', *missing, sep='\n  ')
        sys.exit(1)


if __name__ == '__main__':
    main()
