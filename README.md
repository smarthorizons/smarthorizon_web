# smarthorizon.co

The Smart Horizon company site, served by GitHub Pages from this repo's
root (`CNAME` → `www.smarthorizon.co`).

Plain static HTML, CSS and JavaScript. **No build step is required to
deploy** — push to `main` and GitHub Pages serves the files as they are.

## Layout

```
index.html              Landing page (services, apps, process, about, contact)
apps/index.html         App index
apps/<slug>/index.html  One page per app
404.html                Not-found page
legal/                  Privacy policies, terms and changelogs (pre-existing)
assets/css/site.css     All styles
assets/js/site.js       Language switching, mobile nav, consent-gated analytics
assets/img/             Logo, favicon, social card
assets/apps/<slug>/     App icons and screenshots, pulled from the App Store
data/apps.json          Source of truth for the app catalogue
tools/                  Optional maintenance scripts (never served)
```

## Bilingual English / Arabic

Both languages are present in the HTML at once; CSS hides the inactive
one via `html[lang]`. That means search engines see both, and the page
still shows content with JavaScript disabled.

`assets/js/site.js` picks Arabic for `ar-*` browsers and English
otherwise, remembers the choice in `localStorage`, and flips `lang`,
`dir` and the document title. Layout uses CSS **logical properties**
(`margin-inline-start`, `inset-inline-start`, …), so RTL needs no
separate stylesheet.

## Maintenance

### Refresh App Store ratings and screenshots

```bash
python3 tools/fetch-store-data.py
python3 tools/build-pages.py
```

The first command re-reads Apple's public lookup API for the Smart
Horizon developer account, updates ratings, rating counts and screenshot
counts in `data/apps.json`, and re-downloads icons and screenshots into
`assets/apps/`. Editorial copy in `data/apps.json` is never overwritten.

### Regenerate the pages

```bash
python3 tools/build-pages.py
```

Rebuilds `index.html`, `apps/`, `404.html`, `sitemap.xml` and
`robots.txt` from `data/apps.json`. You can hand-edit the generated HTML
instead — just re-apply those edits in `tools/build-pages.py` if you ever
run the script again.

### Regenerate brand images

```bash
python3 tools/make-brand-assets.py
```

## Outstanding items

These need a decision or a file from you before the site is finished:

1. **The logo is a watermarked preview.** `assets/img/smarthorizon.png`
   has `FREELOGODESIGN.ORG` tiled across it, so it is not used anywhere.
   The header and footer currently render "Smart Horizon" as styled type
   in the brand colours, next to a generated glyph. Drop the licensed
   file in as `assets/img/logo.svg` and swap `.brand`'s contents for an
   `<img>` — see `assets/img/README.md`.

2. **Google Analytics is not live.** `tools/build-pages.py` sets
   `GA_ID = "G-XXXXXXXXXX"`. Replace it with the real measurement ID and
   rebuild. Until then the analytics code and the consent banner stay
   dormant. GA4 sets cookies, so `assets/js/site.js` shows a consent
   banner and loads nothing unless the visitor accepts — **and the
   privacy policy needs a section covering site analytics before this
   goes live**, since the current policies describe app analytics only.

3. **`[N]` placeholders in the About section.** Team size and client
   project count are unverified. Fill them in or delete those lines —
   see the highlighted note on the rendered page.

4. **Contact address.** The site uses `info@smarthorizon.co`. The legal
   pages use `admin@smarthorizon.co` and `altaif.support@smarthorizon.co`.
   Confirm `info@` is monitored.

5. **Two apps are missing.** `legal/alarm-app/` and
   `legal/education-app/` (الطيف) have policies but no store listing
   found under the Smart Horizon developer account, so they are not in
   `data/apps.json`. Add them once they ship.

## Brand

| Token | Value | Use |
| --- | --- | --- |
| Blue | `#4691B6` | Logo blue; large text and decoration only |
| Blue (deep) | `#2E6E8E` | Links, buttons, small text — clears WCAG AA |
| Orange | `#D78630` | Logo orange; accents |
| Orange (deep) | `#96591C` | Accent text and badges — clears WCAG AA |

Type is [Alexandria](https://fonts.google.com/specimen/Alexandria) from
Google Fonts, which covers both Arabic and Latin.

## Local preview

```bash
python3 -m http.server 8765
```

Then open <http://localhost:8765>. A server is required — the pages use
absolute asset paths (`/assets/...`), so opening the files directly with
`file://` will not load CSS.
