# Dalisay Koh Phangan

**Live site:** https://www.dalisaykohphangan.com/

Static website for Dalisay — adults-only, family-run, eco-conscious elevated bungalows on Koh Phangan, Thailand.

## Pages

| Page | File |
| --- | --- |
| Home | `index.html` |
| Bungalows (Mangosteen, Pomelo, Tamarind) | `bungalows.html` |
| Gallery | `gallery.html` |
| Reviews | `reviews.html` |
| About Us | `about.html` |
| Discover Phangan | `discover.html` |
| Contact / booking enquiry | `contact.html` |

Shared styles live in `assets/css/style.css`, behaviour (mobile menu, gallery filters, lightbox, enquiry form) in `assets/js/main.js`, and photos in `assets/img/`.

## Running locally

No build step. Open `index.html` in a browser, or serve the folder:

```sh
python3 -m http.server 8000
```

## Hosting

The site is published with GitHub Pages from the `main` branch (repository root). Every push to `main` redeploys it automatically, usually within a minute.

- `.nojekyll` tells Pages to serve the files as-is.
- `404.html` is the not-found page.
- `sitemap.xml` lists every page — submit it in Google Search Console once the site is live.
- `CNAME` holds the custom domain (`www.dalisaykohphangan.com`) — don't delete it.
- DNS for the domain must point at GitHub Pages: `www` → CNAME `dalisaykohphangan.github.io`; apex `dalisaykohphangan.com` → A `185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153`.

## Notes

- The contact form opens the visitor's email app with a pre-filled enquiry to `dalisaykohphangan@gmail.com` (no server needed).
- The guest quotes on `reviews.html` are placeholders — replace them with real reviews before publishing.
