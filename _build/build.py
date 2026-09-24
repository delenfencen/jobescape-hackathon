#!/usr/bin/env python3
"""Собирает статический сайт-презентацию: общая оболочка + страницы разделов."""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import bugs_content
import lessons_content
import money_content
import uxui_meta

OUT = pathlib.Path(__file__).resolve().parent.parent

# ── карта разделов: правим здесь, когда приедет контент ──────────────────────
PAGES = [
    dict(slug='index',   n='',   title='Обзор', group='Презентация', state=None),
    dict(slug='ux-ui',   n='01', title='UX / UI', group='Решение по трекам', state=None),
    dict(slug='lessons', n='02', title='Уроки', group='Решение по трекам', state=None),
    dict(slug='bugs',    n='03', title='Баги',  group='Решение по трекам', state=None),
    dict(slug='money',   n='04', title='Монетизация', group='Решение по трекам', state=None),
]

SPARK = ('<svg viewBox="0 0 24 24" fill="none" aria-hidden="true">'
         '<path d="M12 2.5 14.3 9 21 11.3 14.3 13.6 12 20.1 9.7 13.6 3 11.3 9.7 9 12 2.5Z" '
         'fill="currentColor"/></svg>')


def nav(active):
    out, group = [], None
    for p in PAGES:
        if p['group'] != group:
            group = p['group']
            out.append(f'    <div class="navgroup__label">{group}</div>')
        cur = ' is-current' if p['slug'] == active else ''
        num = f'<span class="n">{p["n"]}</span>' if p['n'] else '<span class="n">·</span>'
        wip = '<span class="wip">скоро</span>' if p.get('state') == 'wip' else ''
        out.append(f'    <a class="navlink{cur}" href="{p["slug"]}.html">{num}'
                   f'<span>{p["title"]}</span>{wip}</a>')
        if cur and p.get('subnav'):
            out.append('    <div class="subnav">')
            for anchor, n, label in p['subnav']:
                out.append(f'      <a class="sublink" href="#{anchor}">'
                           f'<span class="n">{n}</span><span>{label}</span></a>')
            out.append('    </div>')
    return '\n'.join(out)


SHELL = '''<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} · Jobescape</title>
<link rel="stylesheet" href="assets/doc.css">
<link rel="stylesheet" href="assets/shell.css">
</head>
<body>

<div class="topbar">
  <button class="burger" data-nav-toggle aria-label="Меню разделов">☰</button>
  <b>{title}</b>
  <button class="tbtn" data-theme-toggle type="button">Система</button>
</div>
<button class="scrim" data-nav-toggle aria-label="Закрыть меню" tabindex="-1"></button>

<aside class="shell-side">
  <a class="shell-side__brand" href="index.html">
    <span class="mark">{spark} Jobescape</span>
    <span class="tag">Хакатон · решение</span>
  </a>
  <nav class="shell-side__nav">
{nav}
  </nav>
  <div class="shell-side__foot">
    <span>Тема</span>
    <button class="tbtn" data-theme-toggle type="button">Система</button>
  </div>
</aside>

<main class="main">
{content}
</main>

<script src="assets/shell.js"></script>
</body>
</html>
'''


def head(brow, h1, sub):
    chips = ''.join(f'<span>{c}</span>' for c in brow)
    return (f'  <header class="phead">\n'
            f'    <div class="brow"><span class="d"></span>{chips}</div>\n'
            f'    <h1>{h1}</h1>\n'
            f'    <p class="sub">{sub}</p>\n'
            f'  </header>')


FOOT = ('  <footer class="pfoot"><span>Jobescape · презентация решения</span>'
        '<span>{right}</span></footer>')

# ═════════════════════════════ ОБЗОР ═════════════════════════════
tracks = []
for p in PAGES[1:]:
    ready = p.get('state') != 'wip'
    desc = {
        'ux-ui': 'Типографика, цвет, маскот, расположение и навигатор. Шесть разделов, '
                 '13 экранов в вебе и на iOS.',
        'lessons': 'Онбординг, форматы уроков, удержание и геймификация. '
                   'Восемь разделов на данных когорты в 37 691 покупку.',
        'bugs': 'Ручной проход платящим пользователем: 16 находок, '
                'три корня и порядок починки.',
        'money': 'Сертификат как канал привлечения и девять точек апселла '
                 'по пути пользователя.',
    }[p['slug']]
    meta = {'ux-ui': '6 разделов · 13 экранов · 27 макетов',
            'lessons': '8 разделов · 31 слайд презентацией',
            'bugs': '16 находок · 11 багов · 2 блокера',
            'money': 'реферальная петля · 9 точек апселла'}[p['slug']]
    tracks.append(
        f'''    <a class="track" href="{p['slug']}.html" data-state="{'ready' if ready else 'wip'}">
      <span class="track__n">{p['n']}
        <span class="state {'ready' if ready else 'wip'}">{'готово' if ready else 'в работе'}</span></span>
      <h2>{p['title']}</h2>
      <p>{desc}</p>
      <span class="track__go">{meta} →</span>
    </a>''')

index_body = f'''<div class="page">
{head(['Хакатон', 'Jobescape', 'US · CA · UK', 'ЦА 45+'],
      'Решение: что меняем в продукте и почему',
      'Четыре трека: <b>UX / UI</b>, <b>уроки</b>, <b>баги</b> и <b>монетизация</b>. '
      'Каждый устроен одинаково — сначала гипотеза, что предлагаем. Потом аргументы, '
      'почему это сработает. Потом список правок с объяснением к каждой.')}

  <div class="tracks">
{chr(10).join(tracks)}
  </div>

  <section class="sec" id="method">
    <div class="sec__hd"><span class="n">·</span><h2>Как читать каждый раздел</h2></div>
    <p>Мы не показываем «красивые экраны». В каждом разделе сначала решение, потом
      доказательство, потом правки по пунктам — чтобы на любой вопрос «почему так»
      уже был ответ на странице.</p>
    <div class="shell-tbl">
      <table>
        <thead><tr><th>Блок</th><th>Что в нём</th><th>Зачем он нужен</th></tr></thead>
        <tbody>
          <tr><td><b>Гипотеза</b></td><td>Что предлагаем изменить, одним абзацем.</td>
              <td>Чтобы решение читалось за 20 секунд, без макетов.</td></tr>
          <tr><td><b>Что должно вырасти</b></td><td>Метрика и способ проверки.</td>
              <td>Гипотеза без проверки — это мнение.</td></tr>
          <tr><td><b>Аргументы</b></td><td>Исследования, нормы и примеры рынка.</td>
              <td>Аудитория 45+ ведёт себя иначе, чем мы. Проверяем, а не угадываем.</td></tr>
          <tr><td><b>Решение по пунктам</b></td><td>Таблица «что · решение · почему».</td>
              <td>Чтобы правку можно было взять в работу как есть.</td></tr>
          <tr><td><b>Макеты</b></td><td>Экран в вебе и на iOS, с пояснениями.</td>
              <td>Одно и то же решение должно работать на обеих платформах.</td></tr>
        </tbody>
      </table>
    </div>
  </section>

  <section class="sec" id="common">
    <div class="sec__hd"><span class="n">·</span><h2>Общее решение</h2></div>
    <p>Четыре трека делались отдельно, но упираются в одно число. Половина
      купивших — <b>48,9%</b> — не открывает ни одного урока. До пятого урока
      доходят <b>16,9%</b>, а после него дальше идут около <b>90%</b>.
      Значит цель у всех треков общая: <b>довести человека до пятого урока</b>.</p>
    <p>Дальше каждый трек снимает свою часть препятствий на этом пути.</p>

    <div class="shell-tbl">
      <table>
        <thead><tr><th>Трек</th><th>Что мешает дойти</th><th>Что делаем</th></tr></thead>
        <tbody>
          <tr>
            <td><b>01 · UX / UI</b></td>
            <td>Человек не видит, где он и что делать дальше: вход ведёт сразу
              в содержание курса, синим покрашено всё подряд, мелкий шрифт.</td>
            <td>Над планом появляется главная страница с ответом «что делать
              сегодня». Одна синяя кнопка на экран, кегль 17 px, ментор знает
              весь план и подсказывает сам.</td>
          </tr>
          <tr>
            <td><b>02 · Уроки</b></td>
            <td>Обещание рекламы не совпадает с первым опытом, а уходят
              в первый же день: у не дошедших медиана — один активный день.</td>
            <td>Онбординг показывает результат именно того плана, за который
              заплатили, и даёт получить свой первый результат за пару кликов.
              Недельная цель вместо ежедневной серии.</td>
          </tr>
          <tr>
            <td><b>03 · Баги</b></td>
            <td>Часть пути просто сломана: 16 находок, два блокера, где человек
              упирается в стену и выйти не может.</td>
            <td>Сначала биллинг — мёртвая кнопка реактивации и оффер каждые
              два клика. Потом сборка сертификата. Потом три фичи, которые
              построили и спрятали.</td>
          </tr>
          <tr>
            <td><b>04 · Монетизация</b></td>
            <td>Продукт не даёт заплатить тому, кто хочет, и выпрашивает
              у того, кто не хочет.</td>
            <td>Апселл описывается моментом, а не продуктом. Сертификат —
              единственный артефакт, который видят не-клиенты, — превращается
              в канал привлечения.</td>
          </tr>
        </tbody>
      </table>
    </div>

    <h3 class="kicker">В каком порядке</h3>
    <div class="shell-tbl">
      <table>
        <thead><tr><th class="n">#</th><th>Что</th><th>Почему сначала</th></tr></thead>
        <tbody>
          <tr><td class="n">1</td><td>Биллинг: реактивация и частота оффера</td>
            <td>Это единственное место, где продукт теряет деньги от человека,
              который сам хочет заплатить. И не видно ни в одной метрике.</td></tr>
          <tr><td class="n">2</td><td>Первый день: онбординг и вход в урок 1</td>
            <td>Здесь теряется половина. Пока сюда не дошли, остальное чинит
              путь, по которому никто не идёт.</td></tr>
          <tr><td class="n">3</td><td>Сборка сертификата и выдача</td>
            <td>Чужое описание и старое имя блокируют шаринг — и заодно
              всю монетизацию выдачи, которая строится поверх документа.</td></tr>
          <tr><td class="n">4</td><td>Дорога до пятого урока: главная, сезоны,
            недельная цель</td>
            <td>После пятого урока дальше идут сами. До него — не идут.</td></tr>
          <tr><td class="n">5</td><td>Апселлы по моменту и реферальная петля</td>
            <td>Строятся поверх починенного: предлагать доплату в продукте,
              который не даёт заплатить, — умножать раздражение.</td></tr>
        </tbody>
      </table>
    </div>
    <p class="line">Порядок не по трудозатратам, а по тому, сколько стоит
      бездействие. Первые три пункта — правки полей и настроек, а не новые
      экраны.</p>

    <h3 class="kicker">Что общего у всех решений</h3>
    <div class="tracks">
      <a class="track" href="bugs.html#out" data-state="ready">
        <span class="track__n">01</span>
        <h2>Фичу построили и спрятали</h2>
        <p>Разбор ошибки, настройка шрифта, память формы. Всё это уже есть
          в продукте — и не находится. Самый дешёвый вид правок.</p>
        <span class="track__go">баги · находки 06, 10, 11 →</span>
      </a>
      <a class="track" href="lessons.html#a" data-state="ready">
        <span class="track__n">02</span>
        <h2>Обещание должно совпадать с опытом</h2>
        <p>Реклама про видео — онбординг про WhatsApp. Сертификат за Basics
          печатает программу курса по продажам. «Bronze» на документе
          для LinkedIn.</p>
        <span class="track__go">уроки · точка А →</span>
      </a>
      <a class="track" href="ux-ui.html#ia" data-state="ready">
        <span class="track__n">03</span>
        <h2>Ответ на «что дальше» — первым экраном</h2>
        <p>Не в карте курса, не в углу, не за кнопкой. Это же правило работает
          и в навигаторе, и в разборе ошибки, и на главной.</p>
        <span class="track__go">ux/ui · архитектура →</span>
      </a>
    </div>

    <p class="line">Данные: когорта <b>37 691 покупка</b> (01.07–15.08.2026, окно
      45 дней) и онбординг 3.0.11 на 1 215 пользователей. Баги — ручной проход
      платящим пользователем 22–23 сентября 2026.</p>
  </section>

{FOOT.format(right='Обзор · четыре трека')}
</div>'''

# ═════════════════════════ УРОКИ И БАГИ ═════════════════════════
def placeholder(p, h1, sub, bullets, right):
    items = '\n'.join(f'        <li>{b}</li>' for b in bullets)
    return f'''<div class="page">
{head(['Хакатон', 'Jobescape', f'трек {p["n"]}'], h1, sub)}

  <section class="sec">
    <div class="sec__hd"><span class="n">{p['n']}</span><h2>{p['title']}</h2></div>
    <div class="slot">
      <span class="slot__tag">Ждём контент</span>
      <h3>Раздел готов принять решение</h3>
      <p>Вёрстка, навигация и стили уже на месте — те же, что в разделе UX / UI.
        Как только пришлёшь текст, он встанет в тот же формат: гипотеза → аргументы →
        решение по пунктам → макеты.</p>
      <ul>
{items}
      </ul>
    </div>
  </section>

{FOOT.format(right=right)}
</div>'''


# ═════════════════════════════ УРОКИ ═════════════════════════════
# Страница — в той же вёрстке, что UX/UI: читается сверху вниз, без фрейма.
# Дек остаётся отдельной страницей для показа с проектора.
DECK = 'lessons-deck.html'


def build_lessons():
    PAGES[2]['subnav'] = [(a, n, t) for n, a, t in lessons_content.SECTIONS]
    return f"""<article class="doc">
<div class="wrap">
{head(['Jobescape · трек 02', 'Уроки и персональный план', 'ЦА 45+', 'US · CA · UK'],
      'Онбординг, уроки, удержание, геймификация',
      'Половина купивших не проходит ни одного урока. Каждый раздел устроен одинаково: '
      'сначала <b>гипотеза</b> — что предлагаем. Потом <b>данные и аргументы</b> — '
      'почему это сработает. Потом <b>идеи по пунктам</b> с метрикой к каждой.')}

  <p class="deckbox__go"><a href="{DECK}" target="_blank" rel="noopener">
    Открыть то же самое презентацией — 31 слайд →</a></p>

{lessons_content.build()}

<footer>
  <span>Jobescape · трек «Уроки» · итоговое решение</span>
  <span>8 разделов · когорта 37 691 покупка</span>
</footer>
</div>
</article>"""


lessons_body = build_lessons()

def track_page(mod, brow, h1, sub, right, extra=''):
    """Страница трека в вёрстке UX/UI: шапка, разделы из модуля, подвал."""
    return f"""<article class="doc">
<div class="wrap">
{head(brow, h1, sub)}
{extra}
{mod.build()}

<footer>
  <span>Jobescape · презентация решения</span>
  <span>{right}</span>
</footer>
</div>
</article>"""


PAGES[3]['subnav'] = [(a, n, t) for n, a, t in bugs_content.SECTIONS]
bugs_body = track_page(
    bugs_content,
    ['Jobescape · трек 03', 'Аудит продукта', 'ручной проход', '22–23.09.2026'],
    'Что сломано, что задумывалось и что мы предлагаем',
    'Мы прошли продукт руками как платящий пользователь. <b>16 находок</b>: '
    '11 багов, 5 предложений, 2 блокера. Каждая — что сломано, почему так вышло, '
    'что из этого получает пользователь и что делать.',
    'Трек 03 · баги · 16 находок')

PAGES[4]['subnav'] = [(a, n, t) for n, a, t in money_content.SECTIONS]
money_body = track_page(
    money_content,
    ['Jobescape · трек 04', 'Монетизация', 'ЦА 45+'],
    'Сертификат как канал и апселлы по моменту',
    'Апселл описывается <b>моментом, а не продуктом</b>. Плюс единственный '
    'артефакт, который видят не-клиенты, — сертификат — превращаем '
    'в канал привлечения.',
    'Трек 04 · монетизация')

# ═════════════════════════════ UX / UI ═════════════════════════════
# Страница целиком приходит из артефакта: _build/build_uxui.py кладёт тело
# в _ux-ui.fragment.html, стили в assets/doc.css, а разделы и плашки — сюда.
PAGES[1]['subnav'] = [(a, n, t) for n, a, t in uxui_meta.SECTIONS]

tiles = '\n'.join(
    f'      <div><dt>{k}</dt><dd>{v}</dd></div>' for k, v in uxui_meta.TILES)
frag = (OUT / '_ux-ui.fragment.html').read_text(encoding='utf-8')
nargs = frag.count('<span class="src">')

uxui_body = f"""<article class="doc">
<div class="wrap">
{head(['Jobescape · итоговое решение', 'UX / UI', 'US · CA · UK', 'ЦА 45+'],
      'Типографика, цвет, маскот, расположение', uxui_meta.SUB)}

  <dl class="tiles">
{tiles}
  </dl>

  <h3>На чём стоят решения</h3>
  <p class="line">Ни одно решение здесь не «потому что красивее». За каждым стоит
    аргумент — их {nargs}, и у каждого помечен источник. Опор четыре.</p>
  <div class="args">
    <div><h4><i>01</i>Как видит глаз после сорока</h4>
      <p>Возрастная дальнозоркость начинается примерно в сорок, к пятидесяти есть
        почти у всех; вместе с ней слабеет способность различать близкие оттенки.
        Отсюда кегль 17 px, заголовки размером, а не жирностью, и запрет различать
        состояния парой «синий / зелёный».</p>
      <span class="src">физиология зрения</span></div>
    <div><h4><i>02</i>Когнитивная психология и законы интерфейса</h4>
      <p>Закон Хика, закон Фиттса, закон Якоба, эффект фон Ресторфф, эффект близкой
        цели, нежелание терять накопленное, постепенное раскрытие. Ими объясняются
        и один акцент на экран, и то, почему навигатор ведёт по одному шагу.</p>
      <span class="src">законы UX</span></div>
    <div><h4><i>03</i>Нормы, а не вкус</h4>
      <p>WCAG 1.4.3 требует минимум 4.5 : 1 на текст — в США, Канаде и Англии за это
        судятся по ADA, AODA и Equality Act. Плюс рекомендации Apple HIG, Material
        и исследования NN/g по чтению и движениям глаз.</p>
      <span class="src">WCAG · ADA · AODA</span></div>
    <div><h4><i>04</i>Рынок и ручной проход</h4>
      <p>Что уже работает на этой аудитории: Duolingo, Headspace, Amazon. И то, что
        мы увидели сами, пройдя продукт руками как платящий пользователь.</p>
      <span class="src">примеры и наблюдения</span></div>
  </div>
  <p class="line">У каждого аргумента снизу плашка с источником — закон,
    исследование, норма или наше наблюдение. Где мы не уверены, так и написано:
    формулировку про ИИ-ментора для США и Англии стоит показать юристу.</p>

<nav class="snav">
{chr(10).join(f'  <a href="#{a}"><span class="n">{n}</span> {t}</a>'
              for n, a, t in uxui_meta.SECTIONS)}
</nav>
{frag}
</div>
</article>"""

BODIES = {'index': index_body, 'ux-ui': uxui_body, 'lessons': lessons_body,
          'bugs': bugs_body, 'money': money_body}

for p in PAGES:
    html = SHELL.format(title=p['title'], spark=SPARK,
                        nav=nav(p['slug']), content=BODIES[p['slug']])
    (OUT / f'{p["slug"]}.html').write_text(html, encoding='utf-8')
    print(f'{p["slug"]}.html', (OUT / f'{p["slug"]}.html').stat().st_size)
