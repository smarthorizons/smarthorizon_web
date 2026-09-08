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

## Hero photograph

`hero.webp` (2000x1125, 108KB) and `hero-1200.webp` (1200x675, 36KB,
served below 700px viewport width) are crops of:

- **Clouds above ocean, drone view** — Wikimedia Commons, originally from
  Unsplash.
- **Licence: CC0 1.0 (public domain dedication).** No attribution is
  required and commercial use is permitted. Nothing needs to appear on
  the page.
- Source: <https://commons.wikimedia.org/wiki/File:Clouds_above_ocean_drone_view_(Unsplash).jpg>

It was chosen because it is a literal horizon at sunrise — the company
name — in the two brand colours. It is cropped to 16:9 rather than the
hero's own aspect ratio: the parallax layer is 136% of the hero's height,
so the image needs the extra vertical pixels to stay sharp and to travel
without exposing an edge.

The image is dark (mean luminance ~98/255), so the hero lays a white
veil over it and sets the copy in the heading colour.

The veil is deliberately a veil and not a panel: the photograph stays
visible across the full width, softened where the copy sits and clearing
progressively toward the far side. It runs .72 to .02 alpha across the
hero, flipping direction under RTL so it is always beneath the text, and
becomes a top-to-bottom wash below 760px where the copy spans the width.

Both were tuned by sampling composited pixels rather than by eye. **If
you swap this photograph, re-check the contrast** — a darker or busier
image will change it. Against the darkest 1% of the current image the
weakest point of the veil still gives about 7:1.
