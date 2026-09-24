#!/usr/bin/env python3
"""Собирает папку для развёртывания: только то, что отдаётся браузеру.

Список файлов не зашит — берётся из самих страниц: что они грузят, то и кладём.
Сборочные скрипты, промежуточный фрагмент и serve.sh наружу не едут.

    python3 _build/build_dist.py [куда]     # по умолчанию ../jobescape-site
"""
import pathlib
import re
import shutil
import sys

SRC = pathlib.Path(__file__).resolve().parent.parent
DST = pathlib.Path(sys.argv[1]).expanduser().resolve() if len(sys.argv) > 1 \
    else SRC.parent / 'jobescape-site'

# кладём сверх того, что нашлось по ссылкам
EXTRA = ['vercel.json']


def wanted():
    """Страницы плюс всё, на что они ссылаются."""
    out = set()
    for page in SRC.glob('*.html'):
        if page.name.startswith('_'):
            continue                      # промежуточные фрагменты не страницы
        out.add(page.name)
        for ref in re.findall(r'(?:src|href)="([^"#:]+)"',
                              page.read_text(encoding='utf-8')):
            if not ref.startswith(('http', '//', 'mailto')):
                out.add(ref.split('#')[0])
    return {r for r in out if r}


def main():
    files = sorted(wanted())
    missing = [f for f in files if not (SRC / f).exists()]
    if missing:
        sys.exit('в исходниках нет: ' + ', '.join(missing))

    if DST.exists():
        shutil.rmtree(DST)
    for rel in files + [e for e in EXTRA if (SRC / e).exists()]:
        dst = DST / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(SRC / rel, dst)

    total = sum(f.stat().st_size for f in DST.rglob('*') if f.is_file())
    pages = sum(1 for f in DST.glob('*.html'))
    print(f'{DST}')
    print(f'  файлов {sum(1 for f in DST.rglob("*") if f.is_file())} · '
          f'страниц {pages} · {total / 1e6:.1f} МБ')
    for d in sorted(p for p in DST.iterdir() if p.is_dir()):
        print(f'  {d.name}/: {sum(1 for _ in d.rglob("*"))}')


if __name__ == '__main__':
    main()
