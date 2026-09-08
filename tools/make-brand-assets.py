#!/usr/bin/env python3
"""
Generate the brand images the pages reference:

    assets/img/logo.svg            header / footer / favicon mark
    assets/img/favicon.png         512x512
    assets/img/apple-touch-icon.png 180x180
    assets/img/logo-og.png         1200x630 social card

These are STAND-INS built from the brand colours and the Alexandria
typeface. The supplied logo artwork (smarthorizon.png) carries a
FREELOGODESIGN.ORG watermark and must not be published, so nothing here
is derived from it. Replace these files once the licensed logo arrives.

    python3 tools/make-brand-assets.py
"""

import pathlib
from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).resolve().parent.parent
IMG = ROOT / "assets" / "img"
FONT = ROOT / "legal" / "alarm-app" / "fonts" / "Alexandria-VariableFont.ttf"

BLUE = (70, 145, 182)
ORANGE = (215, 134, 48)
INK = (16, 23, 32)


def glyph(draw, cx, cy, r, lw):
    """Two concentric open arcs around a ring, plus an orbiting dot."""
    draw.arc([cx - r, cy - r, cx + r, cy + r], 130, 400, fill=ORANGE, width=lw)
    r2 = r * 0.66
    draw.arc([cx - r2, cy - r2, cx + r2, cy + r2], 130, 400, fill=ORANGE, width=lw)
    r3 = r * 0.28
    draw.ellipse([cx - r3, cy - r3, cx + r3, cy + r3], outline=BLUE, width=lw)
    d = r * 0.10
    dx, dy = cx - r * 0.80, cy + r * 0.80
    draw.ellipse([dx - d, dy - d, dx + d, dy + d], fill=ORANGE)


def icon(size):
    im = Image.new("RGBA", (size * 4, size * 4), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    s = size * 4
    d.rounded_rectangle([0, 0, s - 1, s - 1], radius=int(s * 0.22), fill=(255, 255, 255, 255))
    glyph(d, s / 2, s / 2, s * 0.31, max(2, int(s * 0.055)))
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

    glyph(d, 132, 205, 52, 9)

    f_big = ImageFont.truetype(str(FONT), 82)
    f_sub = ImageFont.truetype(str(FONT), 34)

    x, y = 208, 160
    d.text((x, y), "Smart", font=f_big, fill=BLUE)
    w = d.textlength("Smart ", font=f_big)
    d.text((x + w, y), "Horizon", font=f_big, fill=ORANGE)

    d.text((132, 320), "Mobile apps, websites and the systems behind them.",
           font=f_sub, fill=INK)
    d.text((132, 372), "A software studio in Oman.", font=f_sub, fill=(90, 102, 116))
    d.text((132, 470), "smarthorizon.co", font=f_sub, fill=BLUE)
    return im


LOGO_SVG = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 40 40" role="img" aria-label="Smart Horizon">
  <title>Smart Horizon</title>
  <rect width="40" height="40" rx="9" fill="#fff"/>
  <path d="M31 34a16 16 0 1 0-22-22" stroke="#D78630" stroke-width="3" stroke-linecap="round" fill="none"/>
  <path d="M27.5 29.5a10.5 10.5 0 1 0-15-15" stroke="#D78630" stroke-width="3" stroke-linecap="round" fill="none"/>
  <circle cx="20" cy="20" r="4.6" stroke="#4691B6" stroke-width="3" fill="none"/>
  <circle cx="7" cy="33" r="2.1" fill="#D78630"/>
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
