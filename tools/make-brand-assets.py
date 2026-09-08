#!/usr/bin/env python3
"""
Generate the brand images the pages reference:

    assets/img/logo.svg            header / footer / favicon mark
    assets/img/favicon.png         512x512
    assets/img/apple-touch-icon.png 180x180
    assets/img/logo-og.png         1200x630 social card

All of it is drawn from the "Aperture" mark: a ring opening to the upper
right with a dot breaking the orbit. Original artwork in the brand
colours, so there is no licence attached to any of it. The previously
supplied smarthorizon.png is NOT used anywhere -- it carries a
FREELOGODESIGN.ORG watermark.

    python3 tools/make-brand-assets.py
"""

import pathlib
from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).resolve().parent.parent
IMG = ROOT / "assets" / "img"
FONT = ROOT / "legal" / "alarm-app" / "fonts" / "Alexandria-VariableFont.ttf"

BLUE = (70, 145, 182)     # #4691B6 logo blue
DEEP = (46, 110, 142)     # #2E6E8E outer ring, AA on white
ORANGE = (215, 134, 48)   # #D78630 logo orange
INK = (16, 23, 32)


def glyph(draw, cx, cy, r, lw):
    """The Aperture mark: two rings sharing a gap at 12 o'clock, with the
    orange dot sitting in that gap between the two ends of the outer ring.
    PIL measures arcs clockwise from 3 o'clock, so the top is 270 degrees
    and a +/-38 degree gap runs from 308 back round to 232."""
    draw.arc([cx - r, cy - r, cx + r, cy + r], 308, 232, fill=DEEP, width=lw)
    r2 = r * 0.40
    draw.arc([cx - r2, cy - r2, cx + r2, cy + r2], 312, 228,
             fill=BLUE, width=max(2, int(lw * 0.85)))
    d = r * 0.275
    draw.ellipse([cx - d, cy - r - d, cx + d, cy - r + d], fill=ORANGE)


def icon(size):
    im = Image.new("RGBA", (size * 4, size * 4), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    s = size * 4
    d.rounded_rectangle([0, 0, s - 1, s - 1], radius=int(s * 0.22), fill=(255, 255, 255, 255))
    glyph(d, s / 2, s / 2, s * 0.30, max(3, int(s * 0.075)))
    return im.resize((size, size), Image.LANCZOS)


def og():
    W, H = 1200, 630
    im = Image.new("RGB", (W, H), (255, 255, 255))
    d = ImageDraw.Draw(im)

    # soft brand wash along the top edge
    for y in range(H):
        t = max(0.0, 1 - y / (H * 0.85))
        d.line([(0, y), (W, y)],
               fill=(int(255 - 21 * t), int(255 - 8 * t), int(255 - 3 * t)))
    d.rectangle([0, H - 12, W, H], fill=BLUE)
    d.rectangle([0, H - 12, W * 0.34, H], fill=ORANGE)

    glyph(d, 132, 205, 50, 13)

    f_big = ImageFont.truetype(str(FONT), 82)
    f_sub = ImageFont.truetype(str(FONT), 34)

    x, y = 208, 160
    d.text((x, y), "Smart", font=f_big, fill=BLUE)
    w = d.textlength("Smart ", font=f_big)
    d.text((x + w, y), "Horizon", font=f_big, fill=ORANGE)

    d.text((132, 320), "Mobile apps, websites and the systems behind them.",
           font=f_sub, fill=INK)
    d.text((132, 372), "Mobile, web and SaaS engineering.", font=f_sub, fill=(90, 102, 116))
    d.text((132, 470), "smarthorizon.co", font=f_sub, fill=BLUE)
    return im


LOGO_SVG = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" role="img" aria-label="Smart Horizon">
  <title>Smart Horizon</title>
  <g transform="translate(32,32) scale(1.24) translate(-32,-30.75)">
    <path d="M44.31 16.24A20 20 0 1 1 19.69 16.24" fill="none" stroke="#2E6E8E" stroke-width="6" stroke-linecap="round"/>
    <path d="M37.35 26.05A8 8 0 1 1 26.65 26.05" fill="none" stroke="#4691B6" stroke-width="5" stroke-linecap="round"/>
    <circle cx="32" cy="12" r="5.5" fill="#D78630"/>
  </g>
</svg>
'''


def main():
    assert FONT.exists(), f"font not found: {FONT}"
    (IMG / "logo.svg").write_text(LOGO_SVG, encoding="utf-8")
    icon(512).save(IMG / "favicon.png")
    icon(180).save(IMG / "apple-touch-icon.png")
    og().save(IMG / "logo-og.png")
    for n in ("logo.svg", "favicon.png", "apple-touch-icon.png", "logo-og.png"):
        print(f"  assets/img/{n}  ({(IMG / n).stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
