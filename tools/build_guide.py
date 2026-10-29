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
from guide_data import EXPLORE, FOOD, PARTIES, WELL  # noqa: E402

REPO = os.path.dirname(HERE)
SITE = "https://www.dalisaykohphangan.com"
TEMPLATE = open(os.path.join(REPO, "about.html"), encoding="utf-8").read()

SHORT = {"beaches": "Beaches", "hikes": "Hikes &amp; waterfalls", "boats": "Boat trips",
         "nearby": "Near Dalisay", "thai": "Thai food", "markets": "Night markets",
         "coffee": "Coffee &amp; bakeries", "world": "Western food", "bars": "Viewpoints &amp; drinks",
         "fitness": "Gyms", "muaythai": "Muay Thai", "padel": "Sports &amp; games",
         "moon": "Phangan classics", "jungle": "Jungle clubs", "beach": "Beach sessions", "local": "Close to home", "ecstatic": "Ecstatic dance",
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
    # "Name|ChIJ..." pins the link to one Google place when a plain search finds the wrong one.
    q, _, place_id = q.partition("|")
    url = "https://www.google.com/maps/search/?api=1&amp;query=" + urllib.parse.quote_plus(q)
    return url + ("&amp;query_place_id=" + place_id if place_id else "")


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
        # Editorial guide pages add a handwriting face (Barlow Condensed comes with the site header).
        html = html.replace("&display=swap", "&family=Caveat:wght@500;700&display=swap", 1)
    html = re.sub(r"<title>.*?</title>", f"<title>{meta_title}</title>", html)
    for attr in ('name="description"', 'property="og:description"'):
        html = re.sub(r'(<meta %s content=")[^"]*' % attr, lambda m: m.group(1) + meta_desc, html)
    html = re.sub(r'(<meta property="og:title" content=")[^"]*', lambda m: m.group(1) + meta_title, html)
    html = html.replace(f"{SITE}/about.html", f"{SITE}/{filename}")
    # Not published yet: no Thai version, so drop the language links and hreflang alternates.
    html = re.sub(r'\s*<link rel="alternate" hreflang="[^"]*" href="[^"]*">', "", html)
    html = re.sub(r'\s*<a class="lang-switch"[^>]*>[^<]*</a>', "", html)
    html = html.replace(' aria-current="page"', "")
    # Header: highlight Island Guide; phone menu: highlight this guide page (the footer links stay plain).
    html = html.replace('<a href="todo.html">Island Guide</a>', '<a href="todo.html" aria-current="page">Island Guide</a>', 1)
    own = {"todo.html": '<a href="todo.html">Things to do</a>',
           "food.html": '<a href="food.html">Eat &amp; drink</a>'}.get(filename)
    if own:
        html = html.replace(own, own.replace("<a ", '<a aria-current="page" ', 1), 1)
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


def ed_section(num, gid, title, intro, items, note, photos=None):
    """A numbered section. With photos, the places sit in one column beside a
    messy two-photo collage that alternates left and right (parties page)."""
    art = "" if photos else f'      {sticker(ILL[gid], "ed-sec__sticker", TILT[num % len(TILT)])}\n'
    places = f'<ol class="ed-list">' + "".join(ed_place(i + 1, *it) for i, it in enumerate(items)) + '</ol>'
    if photos:
        side = "left" if num % 2 else "right"
        figs = "".join(f'<figure class="ed-collage__photo ed-collage__photo--{k}"><img src="{src}" alt="{alt}" '
                       f'loading="lazy" decoding="async"></figure>' for k, (src, alt) in enumerate(photos, 1))
        places = (f'<div class="ed-collage-row ed-collage-row--{side}"><div class="ed-collage">{figs}</div>'
                  f'{places.replace("ed-list", "ed-list ed-list--single", 1)}</div>')
    h = (f'<section class="ed-sec" id="{gid}">\n  <div class="wrap">\n    <header class="ed-sec__head">\n'
         f'      <span class="ed-num">{num:02d}</span>\n      <h2 class="ed-sec__title">{title}</h2>\n'
         f'{art}'
         f'      <p class="ed-sec__intro">{intro}</p>\n    </header>\n'
         f'    {places}\n')
    if note:
        h += f'    <p class="ed-scribble">{note}</p>\n'
    return h + '  </div>\n</section>\n\n'


def ed_page(filename, body_class, title_html, intro, scribble, hero_photo, other, parts, cta,
            meta_title, meta_desc, photos=None):
    guides = [g for _, gs in parts for g in gs]
    count = sum(len(g[3]) for g in guides)
    index = "".join(f'<a href="#{g[0]}"><span>{i + 1:02d}</span>{SHORT[g[0]]}</a>' for i, g in enumerate(guides))
    main = f"""<main id="main">

<section class="ed-hero">
  <div class="wrap">
    <div class="ed-meta"><span>Dalisay island guide</span><span>Koh Phangan</span><span>Places we love</span></div>
    <div class="ed-hero__stage">
      <h1 class="ed-title">{title_html}</h1>
      <figure class="ed-hero__photo"><img src="{hero_photo[0]}" alt="{hero_photo[1]}" width="1200" height="800" decoding="async"></figure>
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
            main += ed_section(n, *g, photos=(photos or {}).get(g[0]))
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
        ("assets/img/guide/beaches.jpg", "Clear turquoise water, granite boulders and a longtail boat in a Koh Phangan bay"),
        ("food.html", "Eat &amp; drink"),
        [("Part one: explore the island", EXPLORE), ("Part two: stay active &amp; unwind", WELL)],
        ("Need help getting around?",
         'Rent a scooter from Mena, just down the road from Dalisay: '
         '<a href="tel:+66827567582">082 756 7582</a> · '
         '<a href="https://www.google.com/maps/search/?api=1&amp;query=Mena+motorbike+for+rent+Koh+Phangan&amp;query_place_id=ChIJia5OnSr_VDARWD6SvJwPCjQ" target="_blank" rel="noopener">Map ↗</a>. '
         "We'll also help you plan your days, arrange boat trips and diving, and point you to the right trail."),
        "Things to Do — Dalisay Koh Phangan",
        "Dalisay's guide to things to do on Koh Phangan: beaches, hikes, waterfalls, boat trips, gyms, yoga and spas.")

ed_page("food.html", "page-guide--food",
        "Eat &amp;<br>drink",
        "Where we eat on Koh Phangan, from a coffee a few minutes away to night markets, Thai kitchens and sunset bars.",
        "our favourite spots ↓",
        ("assets/img/guide/markets.jpg", "A street food vendor grilling skewers at a market stall"),
        ("todo.html", "Things to do"),
        [("", FOOD)],
        ("Hungry for more ideas?",
         "Tell us what you feel like and we'll point you to our favourite spot for it."),
        "Eat & Drink — Dalisay Koh Phangan",
        "Dalisay's favourite places to eat and drink on Koh Phangan: cafes near Hin Kong, Thai food, night markets, bakeries and sunset bars.")

CALLS = [
    ("At Dalisay", "For property emergencies, voice call us any time on WhatsApp or by phone.",
     [("Dalisay", [("+66 61 697 0716", "tel:+66616970716"), ("WhatsApp", "https://wa.me/66616970716")])]),
    ("Health &amp; safety", "Please call the appropriate emergency service directly for urgent health, safety or medical assistance.",
     [("Government Hospital", [("1669", "tel:1669"), ("+66 77 377 034", "tel:+6677377034")]),
      ("International Hospital", [("+66 77 429 559", "tel:+6677429559")]),
      ("Police", [("191", "tel:191"), ("+66 77 377 114", "tel:+6677377114")]),
      ("Tourist Police", [("1155", "tel:1155"), ("+66 2 308 0333", "tel:+6623080333")])]),
]


def ed_calls(num, title, intro, rows):
    def link(label, href):
        ext = ' target="_blank" rel="noopener"' if href.startswith("http") else ""
        return f'<a href="{href}"{ext}>{label}</a>'
    items = "".join(f'<li><span class="ed-calls__name">{name}</span><span class="ed-calls__nums">'
                    + "".join(link(*n) for n in nums) + "</span></li>" for name, nums in rows)
    return f"""<section class="ed-sec">
  <div class="wrap">
    <div class="ed-sec__head">
      <span class="ed-num" aria-hidden="true">{num:02d}</span>
      <h2 class="ed-sec__title">{title}</h2>
      <p class="ed-sec__intro">{intro}</p>
    </div>
    <ul class="ed-calls">{items}</ul>
  </div>
</section>

"""


# Party nights page: set False to keep it out of a publish while it is still a draft.
BUILD_PARTIES = False

P = "assets/img/parties/"
if BUILD_PARTIES:
  ed_page("parties.html", "page-guide--party",
        "Party<br>nights",
        "Full moons, jungle clubs and barefoot beach nights. Our pick of the island's best parties.",
        "dance till sunrise ↓",
        (P + "hero.jpg", "A crowd in front of a stage lit in green and purple"),
        ("todo.html", "Things to do"),
        [("", PARTIES)],
        ("Need a ride home?",
         "Ask us which parties are on this week, and we'll share a trusted taxi number for the trip back."),
        "Party Nights — Dalisay Koh Phangan",
        "Dalisay's guide to Koh Phangan parties: Full Moon, Half Moon, jungle clubs, beach sessions and nights close to Dalisay.",
        photos={
            "moon": [(P + "sunset-crowd.jpg", "A crowd on the beach at sunset"), (P + "fire-show.jpg", "A crowd watching fire dancers on the beach at night")],
            "jungle": [(P + "light-tunnel.jpg", "A tunnel of pink and blue lights over a crowd"), (P + "decks.jpg", "A DJ mixer glowing in the dark")],
            "beach": [(P + "festival-girl.jpg", "A woman dancing with her hand in the air at a party"), (P + "fire-dancer.jpg", "A woman performing a fire show at night")],
            "local": [(P + "disco-balls.jpg", "Red disco balls"), (P + "dj.jpg", "A DJ at the controls under red light")],
            "ecstatic": [(P + "ecstatic-group.jpg", "Dancers reaching up together in blue and green light"), (P + "ecstatic-light.jpg", "A dancer's silhouette surrounded by swirls of pink and blue light")],
        })

# Emergency & things to know page: parked for now (user: "save it for future use").
# Set to True to build info.html again; the full page is also on branch info-page-draft.
BUILD_INFO = False

if BUILD_INFO:
  write("info.html", "page-info", """<main id="main">

<section class="ed-hero">
  <div class="wrap">
    <div class="ed-meta"><span>Dalisay island guide</span><span>Koh Phangan</span><span>Good to know</span></div>
    <h1 class="ed-title">Good to<br>know</h1>
    <div class="ed-hero__foot">
      <p class="ed-lede">Emergency numbers, and soon our trusted contacts for ferries, taxis and getting around the island.</p>
    </div>
  </div>
</section>

""" + "".join(ed_calls(n, *c) for n, c in enumerate(CALLS, 1)) + """</main>""",
      "Emergency & Things to Know — Dalisay Koh Phangan",
      "Emergency numbers on Koh Phangan (Dalisay, hospitals, police and tourist police) and practical tips for your stay.",
      editorial=True)
  print("info.html written")
