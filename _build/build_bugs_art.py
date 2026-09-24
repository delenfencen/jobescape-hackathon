#!/usr/bin/env python3
"""Достаёт скриншоты находок из jobescape_audit.pdf в art-audit/*.jpg.

В PDF картинки лежат XObject'ами: FlateDecode — это сырые RGB-сэмплы, из них
PNG собирается руками (сигнатура, IHDR, IDAT с байтом фильтра на строку, IEND);
DCTDecode — уже JPEG. Наружу всё отдаём JPEG шириной 1400 px.

ЗАМАЗКА выключена: аккаунт тестовый, имена на кадрах — свои. REDACT = False
вернёт размытие областей из BLUR (имя ученика и почта) — на случай, если
кадры понадобится показать за пределами команды, как просит сам аудит.
"""
import binascii
import pathlib
import re
import struct
import sys
import zlib

from PIL import Image, ImageFilter

OUT = pathlib.Path(__file__).resolve().parent.parent
ART = OUT / 'art-audit'
PDF = pathlib.Path('/Users/delenfencen/Downloads/hackathon/final/все слайд/jobescape_audit.pdf')

REDACT = False

# страница в PDF → как назвать кадр на сайте (несколько картинок на странице
# перечисляются в порядке появления в /XObject)
NAMES = {
    3: ['f01-cert'], 5: ['f02-subscribe'], 7: ['f03-error'],
    9: ['f04-profile', 'f04-plan'], 11: ['f05-offer'],
    13: ['f06-form', 'f06-nvs', 'f06-simplifier', 'f06-loop'],
    15: ['f07-mentor'], 17: ['f08-award'], 19: ['f09-bronze'],
    22: ['f10-help'], 24: ['f11-typescale'], 25: ['f12-phone'],
    27: ['f13-module'], 29: ['f14-final'],
}

# доли кадра (x0, y0, x1, y1), которые размываем: имя ученика и его почта
BLUR = {
    'f01-cert':   [(.60, .42, .78, .50)],
    'f04-profile': [(.28, .205, .66, .27)],
    'f04-plan':   [(.86, .00, 1., .09), (.43, .93, .59, 1.0)],
    'f14-final':  [(.86, .00, 1., .09), (.43, .93, .59, 1.0)],
    'f08-award':  [(.38, .715, .56, .775)],
    'f09-bronze': [(.28, .57, .72, .64)],
}


def png(w, h, ncomp, raw):
    stride = w * ncomp
    rows = b''.join(b'\x00' + raw[i * stride:(i + 1) * stride] for i in range(h))

    def chunk(tag, data):
        return (struct.pack('>I', len(data)) + tag + data
                + struct.pack('>I', binascii.crc32(tag + data) & 0xffffffff))

    return (b'\x89PNG\r\n\x1a\n'
            + chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8,
                                         {1: 0, 3: 2, 4: 6}[ncomp], 0, 0, 0))
            + chunk(b'IDAT', zlib.compress(rows, 9)) + chunk(b'IEND', b''))


def redact(im, boxes):
    W, H = im.size
    for x0, y0, x1, y1 in boxes:
        box = (int(W * x0), int(H * y0), int(W * x1), int(H * y1))
        if box[2] <= box[0] or box[3] <= box[1]:
            continue
        part = im.crop(box)
        im.paste(part.filter(ImageFilter.GaussianBlur(
            max(6, min(part.size) // 3))), box)
    return im


def main():
    if not PDF.exists():
        sys.exit(f'нет PDF аудита: {PDF}')
    ART.mkdir(exist_ok=True)
    d = PDF.read_bytes()

    objs = {}
    for m in re.finditer(rb'(\d+)\s+(\d+)\s+obj\b', d):
        end = d.find(b'endobj', m.end())
        objs[int(m.group(1))] = d[m.end():end if end > 0 else len(d)]

    def stream_of(body):
        m = re.search(rb'stream\r?\n', body)
        return body[m.end():body.rfind(b'endstream')] if m else b''

    pages = sorted(n for n, b in objs.items() if re.search(rb'/Type\s*/Page\b', b))
    saved, unnamed = [], []
    for pno, num in enumerate(pages, 1):
        body = objs[num]
        rm = re.search(rb'/Resources\s+(\d+)\s+\d+\s+R', body)
        res = objs.get(int(rm.group(1)), body) if rm else body
        xm = re.search(rb'/XObject\s*<<([^>]*)>>', res)
        if not xm:
            continue
        slot = 0
        for _, onum in re.findall(rb'/(\w+)\s+(\d+)\s+0\s+R', xm.group(1)):
            img = objs.get(int(onum), b'')
            if b'/Image' not in img:
                continue
            names = NAMES.get(pno)
            if not names or slot >= len(names):
                unnamed.append(f'стр.{pno} obj {onum.decode()}')
                slot += 1
                continue
            name = names[slot]
            slot += 1

            head = img[:img.find(b'stream')]
            g = lambda k: int(re.search(rb'/' + k + rb'\s+(\d+)', head).group(1))
            w, h = g(b'Width'), g(b'Height')
            raw = stream_of(img)
            tmp = ART / f'.{name}.tmp'
            if b'DCTDecode' in head:
                tmp.write_bytes(raw)
            else:
                data = zlib.decompress(raw)
                ncomp = len(data) // (w * h)
                if ncomp not in (1, 3, 4):
                    unnamed.append(f'{name}: {ncomp} компонент')
                    continue
                tmp.write_bytes(png(w, h, ncomp, data))

            im = Image.open(tmp).convert('RGB')
            if REDACT and name in BLUR:
                im = redact(im, BLUR[name])
            im.thumbnail((1400, 1400))
            im.save(ART / f'{name}.jpg', 'JPEG', quality=82, optimize=True)
            tmp.unlink()
            saved.append((name, w, h, name in BLUR and REDACT))

    size = sum(f.stat().st_size for f in ART.glob('*.jpg')) / 1e6
    print(f'кадров {len(saved)} · замазано {sum(1 for s in saved if s[3])} '
          f'· {size:.1f} МБ в art-audit/')
    for name, w, h, r in saved:
        print(f'  {name:16} {w}×{h}{"  ← замазка" if r else ""}')
    if unnamed:
        print('без имени (добавь в NAMES):', *unnamed, sep='\n  ')


if __name__ == '__main__':
    main()
