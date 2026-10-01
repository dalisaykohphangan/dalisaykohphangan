# Dalisay Koh Phangan

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

## Notes

- The contact form opens the visitor's email app with a pre-filled enquiry to `dalisaykohphangan@gmail.com` (no server needed).
- The guest quotes on `reviews.html` are placeholders — replace them with real reviews before publishing.
