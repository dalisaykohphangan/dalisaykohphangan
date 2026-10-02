#!/usr/bin/env python3
"""Build the Thai site in th/ from the English pages.

Text is swapped using tools/th.json (English -> Thai). Blocks of text are keyed
with their inline markup (<br>, <em>, <strong>) so Thai word order can differ.

    python3 tools/build_th.py            # build th/*.html
    python3 tools/build_th.py --extract  # list English strings missing from th.json
"""
import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGES = ["index.html", "bungalows.html", "gallery.html", "reviews.html",
         "about.html", "contact.html", "404.html"]
SITE = "https://www.dalisaykohphangan.com"
INLINE = {"br", "em", "strong", "b", "i"}
ATTRS = ("alt", "aria-label", "title", "placeholder", "data-caption")
META = ("description", "og:title", "og:description")

TOKEN = re.compile(r"(<!--.*?-->|<script\b.*?</script>|<style\b.*?</style>|<[^>]+>)", re.S)
TAGNAME = re.compile(r"^</?\s*([a-zA-Z0-9]+)")


def norm(s):
    return re.sub(r"\s+", " ", s).strip()


def runs(html):
    """Yield (start, end, text) for each run of text plus inline tags."""
    parts = TOKEN.split(html)
    pos, run_start, buf = 0, None, []
    for part in parts:
        is_tag = bool(TOKEN.fullmatch(part)) if part else False
        name = TAGNAME.match(part).group(1).lower() if is_tag and TAGNAME.match(part) else None
        inline = is_tag and name in INLINE
        if (not is_tag) or inline:
            if run_start is None:
                run_start = pos
            buf.append(part)
        else:
            if run_start is not None:
                yield run_start, pos, "".join(buf)
            run_start, buf = None, []
        pos += len(part)
    if run_start is not None:
        yield run_start, pos, "".join(buf)


def translatable(text):
    t = norm(re.sub(r"<[^>]+>", "", text))
    return bool(re.search(r"[A-Za-z]", t))


def attr_values(html):
    for m in re.finditer(r'<[^>]+>', html):
        tag = m.group(0)
        if tag.startswith(("<!--", "<script", "<style")):
            continue
        for a in ATTRS:
            for am in re.finditer(r'\s%s="([^"]*)"' % re.escape(a), tag):
                yield am.group(1)
        if tag.startswith("<meta"):
            key = re.search(r'(?:name|property)="([^"]+)"', tag)
            if key and key.group(1) in META:
                yield re.search(r'content="([^"]*)"', tag).group(1)
        if tag.startswith("<title"):
            pass


def extract(dic):
    missing = {}
    for page in PAGES:
        html = open(os.path.join(ROOT, page), encoding="utf-8").read()
        for _, _, text in runs(html):
            k = norm(text)
            if translatable(k) and k not in dic:
                missing.setdefault(k, page)
        for v in attr_values(html):
            k = norm(v)
            if translatable(k) and k not in dic:
                missing.setdefault(k, page)
    return missing


def tr(dic, s):
    k = norm(s)
    if not translatable(k):
        return s
    if k in dic:
        lead = s[:len(s) - len(s.lstrip())]
        trail = s[len(s.rstrip()):]
        return lead + dic[k] + trail
    return None


def build_page(page, dic, missing):
    html = open(os.path.join(ROOT, page), encoding="utf-8").read()
    # Leave comments (e.g. hidden sections) untouched but out of the way.
    keep = []
    def stash(m):
        keep.append(m.group(0)); return "\x00%d\x00" % (len(keep) - 1)
    html = re.sub(r"<!--.*?-->", stash, html, flags=re.S)

    out, last = [], 0
    for a, b, text in runs(html):
        out.append(html[last:a])
        t = tr(dic, text)
        if t is None:
            missing.add(norm(text)); t = text
        out.append(t); last = b
    out.append(html[last:])
    html = "".join(out)

    def fix_tag(m):
        tag = m.group(0)
        if tag.startswith(("<script", "<style")):
            return re.sub(r'(src=")(assets/)', r"\1../\2", tag)
        for a in ATTRS:
            def rep(am):
                t = tr(dic, am.group(2))
                if t is None:
                    missing.add(norm(am.group(2))); t = am.group(2)
                return am.group(1) + t + '"'
            tag = re.sub(r'(\s%s=")([^"]*)"' % re.escape(a), rep, tag)
        if tag.startswith("<meta"):
            key = re.search(r'(?:name|property)="([^"]+)"', tag)
            if key and key.group(1) in META:
                def repc(cm):
                    t = tr(dic, cm.group(1))
                    if t is None:
                        missing.add(norm(cm.group(1))); t = cm.group(1)
                    return 'content="%s"' % t
                tag = re.sub(r'content="([^"]*)"', repc, tag)
        # Asset and page paths: th/ sits one folder down.
        tag = re.sub(r'((?:src|href|srcset|data-full)=")(assets/)', r"\1../\2", tag)
        tag = re.sub(r'(href=")(discover\.html)', r"\1../\2", tag)
        return tag
    html = re.sub(r"<[^>]+>", fix_tag, html)

    # Language, canonical/og:url, switcher and Thai font.
    html = html.replace('<html lang="en"', '<html lang="th"', 1)
    en_url = SITE + "/" + ("" if page == "index.html" else page)
    th_url = SITE + "/th/" + ("" if page == "index.html" else page)
    html = html.replace('rel="canonical" href="%s"' % en_url, 'rel="canonical" href="%s"' % th_url)
    html = html.replace('property="og:url" content="%s"' % en_url, 'property="og:url" content="%s"' % th_url)
    html = re.sub(r'<a class="lang-switch" href="th/[^"]*" hreflang="th" lang="th"[^>]*>[^<]*</a>',
                  '<a class="lang-switch" href="../%s" hreflang="en" lang="en" aria-label="Read in English">EN</a>' % page, html)
    html = html.replace(
        'family=Archivo:wght@200;300;400;500&display=swap',
        'family=Archivo:wght@200;300;400;500&family=Anuphan:wght@200;300;400;500&display=swap')
    html = re.sub(r"\x00(\d+)\x00", lambda m: keep[int(m.group(1))], html)
    return html


def main():
    dic = json.load(open(os.path.join(ROOT, "tools", "th.json"), encoding="utf-8")) \
        if os.path.exists(os.path.join(ROOT, "tools", "th.json")) else {}
    if "--extract" in sys.argv:
        miss = extract(dic)
        json.dump(miss, sys.stdout, ensure_ascii=False, indent=1)
        print("\n%d missing" % len(miss), file=sys.stderr)
        return
    os.makedirs(os.path.join(ROOT, "th"), exist_ok=True)
    missing = set()
    for page in PAGES:
        html = build_page(page, dic, missing)
        open(os.path.join(ROOT, "th", page), "w", encoding="utf-8").write(html)
    if missing:
        print("Untranslated (left in English):", file=sys.stderr)
        for m in sorted(missing):
            print("  -", m, file=sys.stderr)
        sys.exit(1)
    print("Built %d Thai pages in th/" % len(PAGES))


if __name__ == "__main__":
    main()
