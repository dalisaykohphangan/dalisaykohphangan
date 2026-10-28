"""Build the two island guide pages from tools/guide_data.py:

    todo.html  Things to do  (explore + stay active & unwind)  olive background
    food.html  Eat & drink   (restaurants, cafes, markets, bars)  terracotta

Edit the places in guide_data.py, then run:  python3 tools/build_guide.py
The header and footer are copied from about.html so they stay current.
"""
import os
import re
import sys
import urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from guide_data import EXPLORE, FOOD, WELL  # noqa: E402

REPO = os.path.dirname(HERE)
SITE = "https://www.dalisaykohphangan.com"
TEMPLATE = open(os.path.join(REPO, "about.html"), encoding="utf-8").read()

SHORT = {"beaches": "Beaches", "hikes": "Hikes &amp; waterfalls", "boats": "Boat trips",
         "nearby": "Near Dalisay", "thai": "Thai food", "markets": "Night markets",
         "coffee": "Coffee &amp; bakeries", "world": "Western food", "bars": "Viewpoints &amp; drinks",
         "fitness": "Gyms", "muaythai": "Muay Thai", "padel": "Padel &amp; climbing",
         "yoga": "Yoga", "spa": "Massage &amp; spa"}

EMERGENCY = '''<section class="section guide-group guide-group--emergency">
  <div class="wrap">
    <div class="emergency" id="emergency">
      <div class="emergency__head">
        <h3 class="h3">Health &amp; safety emergencies</h3>
        <p>Please call the appropriate emergency service directly for urgent health, safety or medical assistance.</p>
      </div>
      <ul class="emergency__list">
        <li><span>Government Hospital</span><a href="tel:1669">1669</a><a href="tel:+6677377034">+66 77 377 034</a></li>
        <li><span>International Hospital</span><a href="tel:+6677429559">+66 77 429 559</a></li>
        <li><span>Police</span><a href="tel:191">191</a><a href="tel:+6677377114">+66 77 377 114</a></li>
        <li><span>Tourist Police</span><a href="tel:1155">1155</a><a href="tel:+6623080333">+66 2 308 0333</a></li>
      </ul>
    </div>
  </div>
</section>

'''


def maps(q):
    return "https://www.google.com/maps/search/?api=1&amp;query=" + urllib.parse.quote_plus(q)


def place(name, where, desc, links):
    h = f'<li><h3>{name}</h3>'
    if where:
        h += f'<span class="where">{where}</span>'
    if desc:
        h += f'<p>{desc}</p>'
    h += '<p class="place-links">' + "".join(
        f'<a href="{maps(q)}" target="_blank" rel="noopener">{label or "Map"} <span aria-hidden="true">↗</span></a>'
        for label, q in links) + '</p></li>'
    return h


# Section photos (free Unsplash images, saved in assets/img/guide/<id>.jpg).
PHOTOS = {
    "beaches": "Longtail boat moored by grey rocks in clear water",
    "hikes": "Waterfall tumbling through green jungle",
    "boats": "Calm bay framed by tropical trees",
    "fitness": "A pair of dumbbells on the gym floor",
    "muaythai": "Muay Thai fighter in the ring",
    "padel": "Player with a racket on a blue court",
    "yoga": "Woman stretching her arms in a yoga pose",
    "spa": "Foot massage",
    "nearby": "Yellow chairs around tables on the sand",
    "thai": "Spread of Thai dishes",
    "markets": "Street food vendor cooking at her stall",
    "coffee": "Toast topped with avocado and vegetables",
    "world": "Close-up of a burger",
    "bars": "Two people in a boat on the sea at sunset, Koh Phangan",
}


def guide(num, gid, title, intro, items, note):
    photo = ""
    if gid in PHOTOS:
        photo = (f'        <figure class="guide__photo"><img src="assets/img/guide/{gid}.jpg" alt="{PHOTOS[gid]}" '
                 f'width="1200" height="800" loading="lazy" decoding="async"></figure>\n')
    h = (f'    <div class="guide" id="{gid}">\n      <div class="guide__head">\n        <span class="num">{num:02d}</span>\n'
         f'        <h2 class="h3">{title}</h2>\n        <p class="muted">{intro}</p>\n{photo}      </div>\n'
         f'      <div>\n        <ul class="places">' + "".join(place(*i) for i in items) + '</ul>\n')
    if note:
        h += f'        <p class="guide__note">{note}</p>\n'
    return h + '      </div>\n    </div>\n'


def group(sid, eyebrow, heading, aside, guides, start):
    out = (f'<section class="section guide-group" id="{sid}">\n  <div class="wrap">\n    <div class="section-head">\n      <div>\n'
           f'        <p class="eyebrow">{eyebrow}</p>\n        <h2 class="h2">{heading}</h2>\n      </div>\n'
           f'      <div class="section-head__aside">\n        <p class="muted">{aside}</p>\n      </div>\n    </div>\n')
    for i, g in enumerate(guides):
        out += guide(start + i, *g)
    return out + '  </div>\n</section>\n\n'


def page(filename, body_class, eyebrow, title_html, intro, other, groups, cta, meta_title, meta_desc):
    guides = [g for _, _, _, _, gs in groups for g in gs]
    index = "".join(f'<a href="#{g[0]}">{SHORT[g[0]]}</a>' for g in guides)
    other_href, other_label = other
    main = f'''<main id="main">

<section class="page-hero">
  <div class="wrap">
    <p class="eyebrow">{eyebrow}</p>
    <div class="page-hero__row">
      <h1 class="display page-hero__title">{title_html}</h1>
      <p>{intro}</p>
    </div>
    <div class="guide-hero__actions"><a class="btn btn--ghost" href="{other_href}">{other_label}</a></div>
    <nav class="guide-index" aria-label="On this page">{index}</nav>
  </div>
</section>

'''
    n = 1
    for sid, eb, heading, aside, gs in groups:
        main += group(sid, eb, heading, aside, gs, n)
        n += len(gs)
    main += f'''<section class="section guide-cta">
  <div class="wrap cta">
    <p class="eyebrow eyebrow--plain">Need a hand?</p>
    <h2 class="display">{cta[0]}</h2>
    <p>{cta[1]}</p>
    <div class="cta__actions"><a class="btn" href="https://wa.me/66616970716" target="_blank" rel="noopener">Message us on WhatsApp</a></div>
  </div>
</section>

</main>'''

    write(filename, body_class, main, meta_title, meta_desc)
    print(f"{filename}: {sum(len(g[3]) for g in guides)} places")


def write(filename, body_class, main, meta_title, meta_desc, editorial=False):
    html = re.sub(r'<main id="main">.*?</main>', lambda m: main, TEMPLATE, flags=re.S)
    if editorial:
        # Editorial guide pages add a heavy condensed display face and a handwriting face.
        html = html.replace("&display=swap",
                            "&family=Barlow+Condensed:wght@600;800&family=Caveat:wght@500;700&display=swap", 1)
    html = re.sub(r"<title>.*?</title>", f"<title>{meta_title}</title>", html)
    for attr in ('name="description"', 'property="og:description"'):
        html = re.sub(r'(<meta %s content=")[^"]*' % attr, lambda m: m.group(1) + meta_desc, html)
    html = re.sub(r'(<meta property="og:title" content=")[^"]*', lambda m: m.group(1) + meta_title, html)
    html = html.replace(f"{SITE}/about.html", f"{SITE}/{filename}")
    # Not published yet: no Thai version, so drop the language links and hreflang alternates.
    html = re.sub(r'\s*<link rel="alternate" hreflang="[^"]*" href="[^"]*">', "", html)
    html = re.sub(r'\s*<a class="lang-switch"[^>]*>[^<]*</a>', "", html)
    html = html.replace(' aria-current="page"', "")
    extra = " page-ed" if editorial else ""
    html = re.sub(r"<body[^>]*>", f'<body class="page-guide{extra} {body_class}">', html, count=1)
    open(os.path.join(REPO, filename), "w", encoding="utf-8").write(html)


# ---------------------------------------------------------------------------
# Editorial layout for the two guide pages: huge condensed titles, numbered
# sections, scrapbook "sticker" illustrations (assets/img/guide/ill/*.svg).
ILL = {"beaches": "sun-waves", "hikes": "waterfall", "boats": "longtail", "fitness": "dumbbell",
       "muaythai": "glove", "padel": "padel", "yoga": "lotus", "spa": "stones",
       "nearby": "coconut", "thai": "noodles", "markets": "cart", "coffee": "icedcoffee",
       "world": "burger", "bars": "cocktail"}
TILT = [-6, 4, -3, 7, -5, 3, -7, 5]


def sticker(name, cls, tilt):
    return (f'<img class="sticker {cls}" src="assets/img/guide/ill/{name}.svg" alt="" '
            f'width="200" height="200" style="--tilt:{tilt}deg" loading="lazy" decoding="async">')


def ed_place(i, name, where, desc, links):
    h = f'<li class="ed-place"><span class="ed-place__n">{i:02d}</span><h3 class="ed-place__name">{name}</h3>'
    if where:
        h += f'<span class="ed-place__where">{where}</span>'
    if desc:
        h += f'<p>{desc}</p>'
    h += '<p class="ed-links">' + "".join(
        f'<a href="{maps(q)}" target="_blank" rel="noopener">{label or "Map"} <span aria-hidden="true">↗</span></a>'
        for label, q in links) + '</p></li>'
    return h


def ed_section(num, gid, title, intro, items, note):
    h = (f'<section class="ed-sec" id="{gid}">\n  <div class="wrap">\n    <header class="ed-sec__head">\n'
         f'      <span class="ed-num">{num:02d}</span>\n      <h2 class="ed-sec__title">{title}</h2>\n'
         f'      {sticker(ILL[gid], "ed-sec__sticker", TILT[num % len(TILT)])}\n'
         f'      <p class="ed-sec__intro">{intro}</p>\n    </header>\n'
         f'    <ol class="ed-list">' + "".join(ed_place(i + 1, *it) for i, it in enumerate(items)) + '</ol>\n')
    if note:
        h += f'    <p class="ed-scribble">{note}</p>\n'
    return h + '  </div>\n</section>\n\n'


def ed_page(filename, body_class, title_html, intro, scribble, hero_stickers, other, parts, cta,
            meta_title, meta_desc):
    guides = [g for _, gs in parts for g in gs]
    count = sum(len(g[3]) for g in guides)
    index = "".join(f'<a href="#{g[0]}"><span>{i + 1:02d}</span>{SHORT[g[0]]}</a>' for i, g in enumerate(guides))
    stickers = "".join(sticker(n, f"ed-hero__sticker ed-hero__sticker--{k}", t)
                       for k, (n, t) in enumerate(hero_stickers, 1))
    main = f"""<main id="main">

<section class="ed-hero">
  <div class="wrap">
    <div class="ed-meta"><span>Dalisay island guide</span><span>Koh Phangan</span><span>{count} places we love</span></div>
    <div class="ed-hero__stage">
      <h1 class="ed-title">{title_html}</h1>
      {stickers}
    </div>
    <div class="ed-hero__foot">
      <p class="ed-lede">{intro}</p>
      <p class="ed-scribble ed-scribble--hero">{scribble}</p>
      <a class="ed-switch" href="{other[0]}">{other[1]} <span aria-hidden="true">→</span></a>
    </div>
    <nav class="ed-index" aria-label="On this page">{index}</nav>
  </div>
</section>

"""
    n = 1
    for part_title, gs in parts:
        if part_title:
            main += f'<div class="ed-part"><div class="wrap"><span>{part_title}</span></div></div>\n\n'
        for g in gs:
            main += ed_section(n, *g)
            n += 1
    main += f"""<section class="ed-cta">
  <div class="wrap">
    <p class="ed-scribble">need a hand?</p>
    <h2 class="ed-cta__title">{cta[0]}</h2>
    <p class="ed-lede">{cta[1]}</p>
    <a class="btn" href="https://wa.me/66616970716" target="_blank" rel="noopener">Message us on WhatsApp</a>
  </div>
</section>

</main>"""
    write(filename, body_class, main, meta_title, meta_desc, editorial=True)
    print(f"{filename}: {count} places")


ed_page("todo.html", "page-guide--todo",
        "Things<br>to do",
        "Our favourite beaches, hikes, boat trips and ways to stay active or unwind on Koh Phangan.",
        "go explore ↓",
        [("palm", -8), ("longtail", 6), ("sun-waves", -4)],
        ("food.html", "Eat &amp; drink"),
        [("Part one: explore the island", EXPLORE), ("Part two: stay active &amp; unwind", WELL)],
        ("Tell us what you enjoy",
         "We'll help you plan your days, arrange boat trips and diving, and point you to the right trail."),
        "Things to Do — Dalisay Koh Phangan",
        "Dalisay's guide to things to do on Koh Phangan: beaches, hikes, waterfalls, boat trips, gyms, yoga and spas.")

ed_page("food.html", "page-guide--food",
        "Eat &amp;<br>drink",
        "Where we eat on Koh Phangan, from a coffee a few minutes from Dalisay to night markets, Thai kitchens and sunset bars.",
        "our favourite spots ↓",
        [("dragonfruit", 7), ("chili", -10), ("noodles", 5)],
        ("todo.html", "Things to do"),
        [("", FOOD)],
        ("Hungry for more ideas?",
         "Tell us what you feel like and we'll point you to our favourite spot for it."),
        "Eat & Drink — Dalisay Koh Phangan",
        "Dalisay's favourite places to eat and drink on Koh Phangan: cafes near Hin Kong, Thai food, night markets, bakeries and sunset bars.")

write("info.html", "page-info", """<main id="main">

<section class="page-hero">
  <div class="wrap">
    <p class="eyebrow">Emergency &amp; things to know</p>
    <div class="page-hero__row">
      <h1 class="display page-hero__title">Good <em>to know</em>.</h1>
      <p>Emergency numbers, and soon our trusted contacts for ferries, taxis and getting around the island.</p>
    </div>
  </div>
</section>

<section class="section" style="padding-top:0">
  <div class="wrap">
    <div class="emergency emergency--page">
      <div class="emergency__head">
        <h2 class="h3">At Dalisay</h2>
        <p>For property emergencies, voice call us any time on WhatsApp or by phone.</p>
      </div>
      <ul class="emergency__list">
        <li><span>Dalisay</span><a href="tel:+66616970716">+66 61 697 0716</a><a href="https://wa.me/66616970716" target="_blank" rel="noopener">WhatsApp</a></li>
      </ul>
    </div>
""" + EMERGENCY.split('<div class="emergency" id="emergency">', 1)[1].split("    </div>\n  </div>\n</section>", 1)[0].join(
    ['    <div class="emergency emergency--page">', "    </div>\n"]) + """  </div>
</section>

</main>""", "Emergency & Things to Know — Dalisay Koh Phangan",
      "Emergency numbers on Koh Phangan (Dalisay, hospitals, police and tourist police) and practical tips for your stay.")
print("info.html written")
