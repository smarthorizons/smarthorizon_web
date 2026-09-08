# Brand assets

## Drop the real Smart Horizon logo here

Replace `logo.svg` with the real mark. The site references it at exactly
one path — `/assets/img/logo.svg` — so replacing this file updates the
header, the footer, and every app page at once.

| File | What it is | Size |
| --- | --- | --- |
| `logo.svg` | Primary mark, used in the header and footer | Square-ish, any viewBox; renders at 34×34 |
| `logo-og.png` | Social preview image for link cards | **1200 × 630** |
| `favicon.png` | Browser tab icon | **512 × 512** |
| `apple-touch-icon.png` | iOS home-screen icon | **180 × 180** |

If you only have a PDF or a raster logo, hand it over and it can be
traced to SVG and exported at the sizes above.

## App icons and screenshots

`../apps/<slug>/` holds icons and screenshots pulled directly from the
App Store listings on 2026-09-08:

- `icon.png` — 512 × 512
- `screenshot-1.webp` … `screenshot-N.webp` — 750 px wide

Refresh them any time with:

    python3 tools/fetch-store-data.py

These are your own store assets, re-downloaded from Apple's CDN rather
than hotlinked, so the site does not depend on Apple's servers staying up.
