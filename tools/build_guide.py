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


def guide(num, gid, title, intro, items, note):
    h = (f'    <div class="guide" id="{gid}">\n      <div class="guide__head">\n        <span class="num">{num:02d}</span>\n'
         f'        <h2 class="h3">{title}</h2>\n        <p class="muted">{intro}</p>\n      </div>\n'
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
    <div class="guide-hero__actions"><a class="btn btn--emergency" href="#emergency">Emergency contacts</a><a class="btn btn--ghost" href="{other_href}">{other_label}</a></div>
    <nav class="guide-index" aria-label="On this page">{index}</nav>
  </div>
</section>

'''
    n = 1
    for sid, eb, heading, aside, gs in groups:
        main += group(sid, eb, heading, aside, gs, n)
        n += len(gs)
    main += EMERGENCY + f'''<section class="section guide-cta">
  <div class="wrap cta">
    <p class="eyebrow eyebrow--plain">Need a hand?</p>
    <h2 class="display">{cta[0]}</h2>
    <p>{cta[1]}</p>
    <div class="cta__actions"><a class="btn" href="https://wa.me/66616970716" target="_blank" rel="noopener">Message us on WhatsApp</a></div>
  </div>
</section>

</main>'''

    html = re.sub(r'<main id="main">.*?</main>', lambda m: main, TEMPLATE, flags=re.S)
    html = re.sub(r"<title>.*?</title>", f"<title>{meta_title}</title>", html)
    for attr in ('name="description"', 'property="og:description"'):
        html = re.sub(r'(<meta %s content=")[^"]*' % attr, lambda m: m.group(1) + meta_desc, html)
    html = re.sub(r'(<meta property="og:title" content=")[^"]*', lambda m: m.group(1) + meta_title, html)
    html = html.replace(f"{SITE}/about.html", f"{SITE}/{filename}")
    # Not published yet: no Thai version, so drop the language links and hreflang alternates.
    html = re.sub(r'\s*<link rel="alternate" hreflang="[^"]*" href="[^"]*">', "", html)
    html = re.sub(r'\s*<a class="lang-switch"[^>]*>[^<]*</a>', "", html)
    html = html.replace(' aria-current="page"', "")
    html = re.sub(r"<body[^>]*>", f'<body class="page-guide {body_class}">', html, count=1)
    open(os.path.join(REPO, filename), "w", encoding="utf-8").write(html)
    print(f"{filename}: {sum(len(g[3]) for g in guides)} places")


page("todo.html", "page-guide--todo", "Island guide",
     "Things <em>to do</em>.",
     "Our favourite beaches, hikes, boat trips and ways to stay active or unwind on Koh Phangan.",
     ("food.html", "Eat &amp; drink"),
     [("explore", "Explore", "Beaches, hikes<br>&amp; <em>day trips</em>.",
       "Our favourite corners of the island, from Hin Kong sunsets to Ang Thong's limestone islands.", EXPLORE),
      ("active", "Stay active &amp; unwind", "Move, stretch<br>&amp; <em>relax</em>.",
       "Gyms, Muay Thai, padel, yoga and spas around the island.", WELL)],
     ("Tell us what <em>you enjoy</em>.",
      "We'll help you plan your days, arrange boat trips and diving, and point you to the right trail."),
     "Things to Do — Dalisay Koh Phangan",
     "Dalisay's guide to things to do on Koh Phangan: beaches, hikes, waterfalls, boat trips, gyms, yoga, spas and emergency numbers.")

page("food.html", "page-guide--food", "Island guide",
     "Eat <em>&amp; drink</em>.",
     "Where we eat on Koh Phangan, from a coffee a few minutes from Dalisay to night markets, Thai kitchens and sunset bars.",
     ("todo.html", "Things to do"),
     [("eat", "Eat &amp; drink", "Where <em>we eat</em>.",
       "Places we love, starting with those a few minutes from Dalisay.", FOOD)],
     ("Hungry for <em>more ideas</em>?",
      "Tell us what you feel like and we'll point you to our favourite spot for it."),
     "Eat & Drink — Dalisay Koh Phangan",
     "Dalisay's favourite places to eat and drink on Koh Phangan: cafes near Hin Kong, Thai food, night markets, bakeries and sunset bars.")
