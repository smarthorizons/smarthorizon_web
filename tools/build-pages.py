#!/usr/bin/env python3
"""
Generate the static pages for www.smarthorizon.co from data/apps.json.

    python3 tools/build-pages.py

Output is plain HTML committed to the repo. GitHub Pages serves it
directly -- this script is a convenience for keeping the app pages in
sync with the catalogue, NOT a deploy-time dependency. You can hand-edit
the generated HTML instead; just re-apply your edits here if you ever
re-run the script.
"""

import json
import os
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = json.loads((ROOT / "data" / "apps.json").read_text(encoding="utf-8"))
APPS = DATA["apps"]

SITE = "https://www.smarthorizon.co"
EMAIL = "info@smarthorizon.co"
GA_ID = "G-XXXXXXXXXX"   # <-- replace with the real GA4 measurement ID

# --------------------------------------------------------------------------
# small helpers
# --------------------------------------------------------------------------

def L(en, ar, tag="span", cls=None):
    """Emit both languages; CSS shows whichever matches <html lang>."""
    c = f' class="{cls}"' if cls else ""
    return (f'<{tag} data-lang="en"{c}>{en}</{tag}>'
            f'<{tag} lang="ar" data-lang="ar"{c}>{ar}</{tag}>')


def ios_url(app):
    return f"https://apps.apple.com/app/id{app['ios_id']}"


def play_url(app):
    return f"https://play.google.com/store/apps/details?id={app['android_id']}"


ICON_APPLE = ('<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">'
              '<path d="M17.05 12.54c-.02-2.2 1.8-3.26 1.88-3.31-1.02-1.5-2.62-1.7-3.18-1.72-1.35-.14-2.64.8-3.33.8-.69 0-1.75-.78-2.87-.76-1.48.02-2.84.86-3.6 2.18-1.53 2.66-.39 6.6 1.1 8.76.73 1.06 1.6 2.25 2.74 2.2 1.1-.04 1.51-.71 2.84-.71 1.32 0 1.7.71 2.86.69 1.18-.02 1.93-1.07 2.65-2.14.84-1.23 1.18-2.42 1.2-2.48-.03-.01-2.29-.88-2.31-3.5zM14.9 5.9c.6-.74 1.01-1.75.9-2.77-.87.04-1.93.58-2.56 1.31-.56.65-1.05 1.69-.92 2.68.97.08 1.96-.49 2.58-1.22z"/></svg>')

ICON_PLAY = ('<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">'
             '<path d="M3.6 2.3c-.3.3-.5.8-.5 1.4v16.6c0 .6.2 1.1.5 1.4l.1.1 9.3-9.3v-.2L3.7 2.2l-.1.1zm12.5 6.2L4.4 1.8l-.1-.1 9.6 9.6 2.2-2.8zM17.9 9.6l-2.4 1.4-2.4 2.4 2.4 2.4 2.4 1.4c.9-.5 1.5-1.2 1.5-1.9v-3.8c0-.7-.6-1.4-1.5-1.9zM4.3 22.3l.1-.1 11.7-6.7-2.2-2.8-9.6 9.6z"/></svg>')

ICON_STAR = ('<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">'
             '<path d="M12 2.5l2.9 5.9 6.5.95-4.7 4.6 1.1 6.5-5.8-3.05L6.2 20.4l1.1-6.5-4.7-4.6 6.5-.95z"/></svg>')

ICON_DOWNLOAD = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" '
                 'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
                 '<path d="M12 3v12m0 0l-4.5-4.5M12 15l4.5-4.5M4 19h16"/></svg>')

ICON_CHECK = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" '
              'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
              '<path d="M20 6L9 17l-5-5"/></svg>')


def img_size(rel_path, display_width):
    """Real intrinsic size, scaled to the display width, so the browser
    reserves the right box and the page does not shift as images load.
    Falls back to no attributes if Pillow is not installed."""
    try:
        from PIL import Image
    except ImportError:
        return ""
    f = ROOT / rel_path.lstrip("/")
    if not f.exists():
        return ""
    with Image.open(f) as im:
        w, h = im.size
    return f' width="{display_width}" height="{round(display_width * h / w)}"'


def total_installs():
    """Play publishes ranges ("100K+"), so summing the floors gives a
    defensible lower bound -- never an inflated figure."""
    mult = {"K": 1_000, "M": 1_000_000, "B": 1_000_000_000}
    total = 0
    for a in APPS:
        v = (a.get("play_downloads") or "").rstrip("+")
        if not v:
            continue
        total += int(float(v[:-1]) * mult[v[-1]]) if v[-1] in mult else int(v)
    return total


def downloads_badge(app):
    """Google Play publishes an install range; Apple publishes nothing
    comparable. Shown for every app, which matters most for the two whose
    iOS rating counts are too low to display."""
    n = app.get("play_downloads")
    if not n:
        return ""
    return (f'<span class="rating">{ICON_DOWNLOAD}{n}'
            f'{L("<span>installs</span>", "<span>تنزيل</span>")}</span>')


def stores(app, small=False):
    return f'''<div class="stores">
            <a class="store-badge" href="{ios_url(app)}" rel="noopener">{ICON_APPLE}<span>{L("<small>Download on the</small>App Store", "<small>حمّل من</small>App Store")}</span></a>
            <a class="store-badge" href="{play_url(app)}" rel="noopener">{ICON_PLAY}<span>{L("<small>Get it on</small>Google Play", "<small>احصل عليه من</small>Google Play")}</span></a>
          </div>'''


def rating_badge(app):
    """Only show a rating that carries real weight."""
    if (app.get("rating_count") or 0) < 50:
        return ""
    count = f"{app['rating_count']:,}"
    return (f'<span class="rating">{ICON_STAR}{app["rating"]:.1f}'
            f'{L(f"<span>({count} ratings)</span>", f"<span>({count} تقييم)</span>")}</span>')


# --------------------------------------------------------------------------
# shared chrome
# --------------------------------------------------------------------------

def head(title_en, title_ar, desc_en, desc_ar, path,
         og_image="/assets/img/logo-og.png", og_size=(1200, 630), extra=""):
    """og_size must match the real pixel size of og_image; lying about it
    makes Twitter/LinkedIn crop or drop the card. A 1200x630 image gets a
    large card, anything else falls back to the small summary card."""
    canonical = SITE + path
    ow, oh = og_size
    card = "summary_large_image" if (ow, oh) == (1200, 630) else "summary"
    return f'''<!DOCTYPE html>
<html lang="en" dir="ltr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title data-title-en="{title_en}" data-title-ar="{title_ar}">{title_en}</title>
<meta name="description" content="{desc_en}">
<link rel="canonical" href="{canonical}">
<link rel="alternate" hreflang="en" href="{canonical}">
<link rel="alternate" hreflang="ar" href="{canonical}">
<link rel="alternate" hreflang="x-default" href="{canonical}">
<meta name="theme-color" content="#4691B6">

<meta property="og:type" content="website">
<meta property="og:site_name" content="Smart Horizon">
<meta property="og:title" content="{title_en}">
<meta property="og:description" content="{desc_en}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{SITE}{og_image}">
<meta property="og:image:width" content="{ow}">
<meta property="og:image:height" content="{oh}">
<meta property="og:locale" content="en_US">
<meta property="og:locale:alternate" content="ar_OM">
<meta name="twitter:card" content="{card}">
<meta name="twitter:title" content="{title_en}">
<meta name="twitter:description" content="{desc_en}">
<meta name="twitter:image" content="{SITE}{og_image}">

<link rel="icon" href="/assets/img/logo.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/assets/img/apple-touch-icon.png">

<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Alexandria:wght@300..800&display=swap">
<link rel="stylesheet" href="/assets/css/site.css">
<script>document.documentElement.classList.add("js");</script>
<script>window.SH_GA_ID = "{GA_ID}";</script>
{extra}</head>
<body>
<a class="skip-link" href="#main">{L("Skip to content", "تخطَّ إلى المحتوى")}</a>
'''


# Concentric-arc glyph echoing the mark in the supplied logo artwork.
# Purely a stand-in: replace .brand's contents with the real logo file
# once an un-watermarked version is available.
BRAND_GLYPH = (
    '<svg class="brand-glyph" viewBox="0 0 40 40" fill="none" aria-hidden="true">'
    '<path d="M31 34a16 16 0 1 0-22-22" stroke="#D78630" stroke-width="3" stroke-linecap="round"/>'
    '<path d="M27.5 29.5a10.5 10.5 0 1 0-15-15" stroke="#D78630" stroke-width="3" stroke-linecap="round"/>'
    '<circle cx="20" cy="20" r="4.6" stroke="#4691B6" stroke-width="3"/>'
    '<circle cx="7" cy="33" r="2.1" fill="#D78630"/>'
    '</svg>'
)


def header(active=""):
    def item(href, en, ar):
        return f'<a href="{href}">{L(en, ar)}</a>'
    return f'''<header class="site-header">
  <div class="wrap">
    <a class="brand" href="/" aria-label="Smart Horizon">
      {BRAND_GLYPH}
      <span class="wordmark"><span class="w1">Smart</span> <span class="w2">Horizon</span></span>
    </a>
    <button class="nav-toggle" type="button" data-nav-toggle aria-expanded="false" aria-controls="site-nav" aria-label="Menu">
      <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="#33404F" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M3 6h18M3 12h18M3 18h18"/></svg>
    </button>
    <nav class="nav" id="site-nav" aria-label="Main">
      {item("/#services", "Services", "خدماتنا")}
      {item("/apps/", "Our apps", "تطبيقاتنا")}
      {item("/#about", "About", "من نحن")}
      {item("/#contact", "Contact", "تواصل معنا")}
      <button class="lang-toggle" type="button" data-lang-toggle lang="ar">العربية</button>
    </nav>
  </div>
</header>
'''


def footer():
    app_links = "\n".join(
        f'        <li><a href="/apps/{a["slug"]}/">{L(a["name_en"], a["name_ar"])}</a></li>'
        for a in APPS)
    legal_links = "\n".join(
        f'        <li><a href="/legal/{a["legal_slug"]}/privacy-policy.html">{L(a["name_en"], a["name_ar"])}</a></li>'
        for a in APPS)
    return f'''<footer class="site-footer">
  <div class="wrap">
    <div class="footer-grid">
      <div>
        <span class="brand">
          {BRAND_GLYPH}
          <span class="wordmark"><span class="w1">Smart</span> <span class="w2">Horizon</span></span>
        </span>
        {L("We design and build mobile apps, websites and the systems behind them &mdash; and we ship our own apps to prove it.",
           "نصمم ونطوّر تطبيقات الجوال والمواقع والأنظمة التي تقف خلفها &mdash; وننشر تطبيقاتنا الخاصة كدليل على ذلك.", tag="p")}
        <p><a href="mailto:{EMAIL}">{EMAIL}</a></p>
      </div>
      <div>
        <h4>{L("Company", "الشركة")}</h4>
        <ul>
          <li><a href="/#services">{L("Services", "خدماتنا")}</a></li>
          <li><a href="/#about">{L("About", "من نحن")}</a></li>
          <li><a href="/#contact">{L("Contact", "تواصل معنا")}</a></li>
        </ul>
      </div>
      <div>
        <h4>{L("Apps", "التطبيقات")}</h4>
        <ul>
{app_links}
        </ul>
      </div>
      <div>
        <h4>{L("Privacy policies", "سياسات الخصوصية")}</h4>
        <ul>
{legal_links}
        </ul>
      </div>
    </div>
    <div class="footer-bottom">
      {L("&copy; 2026 Smart Horizon. All rights reserved.", "&copy; ٢٠٢٦ سمارت هورايزن. جميع الحقوق محفوظة.", tag="span")}
      {L("Based in Oman", "مقرنا سلطنة عُمان", tag="span")}
    </div>
  </div>
</footer>
<script src="/assets/js/site.js" defer></script>
</body>
</html>
'''


def write(path, html):
    p = ROOT / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(html, encoding="utf-8")
    print(f"  {path}  ({len(html.encode('utf-8'))//1024} KB)")


# --------------------------------------------------------------------------
# service + process content
# --------------------------------------------------------------------------

# Animated hero motif. Echoes the concentric arcs of the Smart Horizon mark:
# a rising sun over a horizon, with radar-style pulses expanding outward.
# Pure SVG + CSS -- no image file, no library, crisp at any size, and it
# costs about 4KB. Every animation is transform/opacity only, and the whole
# thing freezes under prefers-reduced-motion.
HERO_ART = '''      <svg class="hero-motif" viewBox="0 0 420 420" role="img" aria-label="Smart Horizon">
        <defs>
          <linearGradient id="hm-sun" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0" stop-color="#6FB0CE"/>
            <stop offset="1" stop-color="#2E6E8E"/>
          </linearGradient>
          <linearGradient id="hm-ray" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0" stop-color="#D78630"/>
            <stop offset="1" stop-color="#4691B6"/>
          </linearGradient>
          <clipPath id="hm-above"><rect x="0" y="0" width="420" height="252"/></clipPath>
        </defs>

        <!-- expanding pulses -->
        <g clip-path="url(#hm-above)" fill="none" stroke="url(#hm-ray)" stroke-width="2">
          <circle class="hm-pulse hm-pulse--1" cx="210" cy="252" r="62"/>
          <circle class="hm-pulse hm-pulse--2" cx="210" cy="252" r="62"/>
          <circle class="hm-pulse hm-pulse--3" cx="210" cy="252" r="62"/>
        </g>

        <!-- fixed arcs, echoing the logo mark -->
        <g clip-path="url(#hm-above)" fill="none" stroke-linecap="round">
          <path class="hm-arc" d="M96 252a114 114 0 0 1 228 0" stroke="#D78630" stroke-width="3" opacity=".55"/>
          <path class="hm-arc hm-arc--2" d="M126 252a84 84 0 0 1 168 0" stroke="#4691B6" stroke-width="3" opacity=".45"/>
        </g>

        <!-- the sun -->
        <circle class="hm-sun" cx="210" cy="252" r="52" fill="url(#hm-sun)"/>
        <circle class="hm-sun-ring" cx="210" cy="252" r="52" fill="none" stroke="#fff" stroke-width="2" opacity=".55"/>

        <!-- horizon -->
        <g class="hm-horizon">
          <line x1="34" y1="252" x2="386" y2="252" stroke="#CBD5E1" stroke-width="3" stroke-linecap="round"/>
          <line class="hm-horizon-lit" x1="120" y1="252" x2="300" y2="252" stroke="#D78630" stroke-width="3" stroke-linecap="round"/>
        </g>

        <!-- orbiting dot -->
        <g class="hm-orbit"><circle cx="210" cy="118" r="7" fill="#D78630"/></g>

        <!-- drifting motes -->
        <circle class="hm-mote hm-mote--1" cx="92"  cy="168" r="4.5" fill="#4691B6" opacity=".65"/>
        <circle class="hm-mote hm-mote--2" cx="330" cy="132" r="5.5" fill="#D78630" opacity=".55"/>
        <circle class="hm-mote hm-mote--3" cx="352" cy="206" r="3.5" fill="#4691B6" opacity=".5"/>
      </svg>'''


def svg(paths, extra=""):
    return (f'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" '
            f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"{extra}>{paths}</svg>')


SERVICES = [
    {
        "icon": svg('<rect x="6" y="2" width="12" height="20" rx="2.5"/><path d="M11 18.5h2"/>'),
        "en_t": "Mobile development",
        "ar_t": "تطوير تطبيقات الجوال",
        "en_d": "Cross-platform iOS and Android apps with native integrations, background processing and offline-first architecture &mdash; so the app still works on a weak connection. Four of our own apps have been through this whole process, from first sketch to a live store listing.",
        "ar_d": "تطبيقات iOS و Android متعددة المنصات مع تكاملات أصلية، ومعالجة في الخلفية، وبنية تعمل دون اتصال أولاً &mdash; ليواصل التطبيق عمله على شبكة ضعيفة. مررنا بأربعة من تطبيقاتنا عبر هذه الرحلة كاملة، من الفكرة الأولى حتى النشر في المتاجر.",
    },
    {
        "icon": svg('<ellipse cx="12" cy="5.5" rx="8" ry="3"/><path d="M4 5.5v13c0 1.7 3.6 3 8 3s8-1.3 8-3v-13M4 12c0 1.7 3.6 3 8 3s8-1.3 8-3"/>'),
        "en_t": "Web & SaaS engineering",
        "ar_t": "هندسة الويب والبرمجيات كخدمة",
        "en_d": "Full-stack web applications and SaaS platforms: REST and GraphQL APIs, backend architecture, databases, and cloud deployment. Built to be handed over and maintained, not to be rewritten in a year.",
        "ar_d": "تطبيقات ويب متكاملة ومنصات برمجيات كخدمة: واجهات REST و GraphQL، وبنية خلفية، وقواعد بيانات، ونشر سحابي. مبنية لتُسلَّم وتُصان، لا لتُعاد كتابتها بعد عام.",
    },
    {
        "icon": svg('<path d="M12 2.5l2.6 6.2 6.7.6-5.1 4.4 1.5 6.6L12 16.9 6.3 20.3l1.5-6.6L2.7 9.3l6.7-.6z"/>'),
        "en_t": "UI/UX, design systems & RTL",
        "ar_t": "الواجهات وأنظمة التصميم ودعم العربية",
        "en_d": "Product design, design systems, app icons and brand identity &mdash; plus the part most teams get wrong: proper bidirectional Arabic and RTL, state management design, and multi-platform monorepo architecture.",
        "ar_d": "تصميم المنتجات وأنظمة التصميم وأيقونات التطبيقات والهوية البصرية &mdash; إضافة إلى ما تخطئ فيه معظم الفرق: دعم صحيح للعربية والاتجاه من اليمين إلى اليسار، وتصميم إدارة الحالة، وبنية أحادية المستودع متعددة المنصات.",
    },
]


STEPS = [
    ("Discover", "الاستكشاف",
     "We start with the problem, not the feature list. What are you trying to change, for whom, and how will you know it worked?",
     "نبدأ بالمشكلة، لا بقائمة المزايا. ما الذي تحاول تغييره، ولمن، وكيف ستعرف أنه نجح؟"),
    ("Design", "التصميم",
     "Wireframes and then a full interface design you can react to before a line of production code exists.",
     "مخططات أولية ثم تصميم كامل للواجهة يمكنك الحكم عليه قبل كتابة أي سطر برمجي."),
    ("Build", "التطوير",
     "Development in short, visible increments. You see working software regularly, not a status report.",
     "تطوير على دفعات قصيرة وواضحة. ترى برنامجاً يعمل بانتظام، لا تقريراً عن الحالة."),
    ("Launch & support", "الإطلاق والدعم",
     "Store submission, release, and the unglamorous work afterwards: monitoring, fixes, and the next version.",
     "النشر في المتاجر والإطلاق، ثم العمل غير اللامع الذي يليه: المتابعة والإصلاحات والإصدار التالي."),
]


# --------------------------------------------------------------------------
# reusable blocks
# --------------------------------------------------------------------------

def app_card(app):
    return f'''      <article class="app-card">
        <div class="app-card__body">
          <div class="app-card__top">
            <img class="app-icon" src="/assets/apps/{app['slug']}/icon.png" alt="" width="62" height="62" loading="lazy">
            <div>
              <h3 class="app-card__name">{L(app['name_en'], app['name_ar'])}</h3>
              <span class="app-card__cat">{L(app['category_en'], app['category_ar'])}</span>
            </div>
          </div>
          {L(app['tagline_en'], app['tagline_ar'], tag="p")}
          <div class="app-card__foot">
            <div class="app-card__metrics">{rating_badge(app)}{downloads_badge(app)}</div>
            <a class="btn btn--ghost" style="padding:9px 18px;font-size:.92rem" href="/apps/{app['slug']}/">{L("Details", "التفاصيل")}</a>
          </div>
        </div>
      </article>'''


def cta_block():
    return f'''    <div class="cta" data-reveal>
      {L("Have something you want built?", "لديك مشروع تريد بناءه؟", tag="h2")}
      {L("Tell us what you are trying to make. We will tell you honestly whether we are the right people to build it, roughly what it takes, and how long it would run.",
         "أخبرنا بما تريد بناءه. سنخبرك بصراحة ما إذا كنا الجهة المناسبة لتنفيذه، وما الذي يتطلبه تقريباً، وكم سيستغرق.", tag="p")}
      <div class="btn-row" style="justify-content:center;margin-block-start:26px">
        <a class="btn btn--primary" href="mailto:{EMAIL}">{L("Email us", "راسلنا")}</a>
        <a class="btn btn--ghost" href="/apps/">{L("See our work", "شاهد أعمالنا")}</a>
      </div>
      <p style="margin-block-start:20px;margin-block-end:0;font-size:.96rem">
        <a class="cta__email" href="mailto:{EMAIL}">{EMAIL}</a>
      </p>
    </div>'''


# --------------------------------------------------------------------------
# home page
# --------------------------------------------------------------------------

def build_index():
    total_ratings = sum(a.get("rating_count") or 0 for a in APPS)
    installs = total_installs()
    installs_label = f"{installs // 1000:,}K+" if installs < 1_000_000 else f"{installs / 1_000_000:.1f}M+"
    best = max(APPS, key=lambda a: (a.get("rating_count") or 0))

    org_ld = json.dumps({
        "@context": "https://schema.org",
        "@type": "Organization",
        "name": "Smart Horizon",
        "url": SITE + "/",
        "email": EMAIL,
        "address": {"@type": "PostalAddress", "addressCountry": "OM"},
        "description": "Software studio in Oman building mobile apps, websites and the systems behind them.",
        "sameAs": ["https://apps.apple.com/developer/smart-horizon/id1527611187"],
    }, ensure_ascii=False, indent=2)

    services = "\n".join(f'''      <article class="card card--link">
        <div class="card__icon">{s['icon']}</div>
        {L(s['en_t'], s['ar_t'], tag="h3")}
        {L(s['en_d'], s['ar_d'], tag="p")}
      </article>''' for s in SERVICES)

    steps = "\n".join(f'''      <div class="step">
        {L(en_t, ar_t, tag="h3")}
        {L(en_d, ar_d, tag="p")}
      </div>''' for en_t, ar_t, en_d, ar_d in STEPS)

    cards = "\n".join(app_card(a) for a in APPS)

    hero_shots = HERO_ART

    html = head(
        "Smart Horizon — App, web and software development in Oman",
        "سمارت هورايزن — تطوير التطبيقات والمواقع والبرمجيات في عُمان",
        "Smart Horizon is a software studio in Oman. We design and build mobile apps, websites, and the backends behind them — and publish our own apps on the App Store and Google Play.",
        "سمارت هورايزن استوديو برمجيات في عُمان. نصمم ونطوّر تطبيقات الجوال والمواقع والأنظمة الخلفية — وننشر تطبيقاتنا الخاصة على App Store و Google Play.",
        "/",
        extra=f'<script type="application/ld+json">\n{org_ld}\n</script>\n')

    html += header()
    html += f'''<main id="main">

<section class="hero">
  <div class="wrap hero__grid">
    <div data-reveal>
      <span class="eyebrow">{L("Software studio &middot; Oman", "استوديو برمجيات &middot; عُمان")}</span>
      {L("We build software people keep using.",
         "نبني برمجيات يستمر الناس في استخدامها.", tag="h1")}
      {L("We build cross-platform mobile apps, web platforms and SaaS, and the backends behind them. We also publish our own apps &mdash; four of them, downloaded more than " + installs_label.replace("+", "") + " times. That is the same team, and the same standard, that your project gets.",
         "نبني تطبيقات جوال متعددة المنصات ومنصات ويب وبرمجيات كخدمة، والأنظمة الخلفية التي تقف خلفها. كما ننشر تطبيقاتنا الخاصة &mdash; أربعة تطبيقات جرى تنزيلها أكثر من " + installs_label.replace("+", "") + " مرة. وهو الفريق نفسه والمعيار نفسه الذي سيحصل عليه مشروعك.",
         tag="p", cls="lede")}
      <div class="btn-row">
        <a class="btn btn--primary" href="#apps">{L("Explore our apps", "استعرض تطبيقاتنا")}</a>
        <a class="btn btn--ghost" href="#contact">{L("Request a quote", "اطلب عرض سعر")}</a>
      </div>
    </div>
    <div class="hero__art" aria-hidden="true">
{hero_shots}
    </div>
  </div>
</section>

<section class="section" style="padding-block:44px">
  <div class="wrap">
    <div class="stats" data-reveal-group>
      <div class="stat"><span class="stat__num">{installs_label}</span><span class="stat__label">{L("downloads on Google Play", "تنزيل على Google Play")}</span></div>
      <div class="stat"><span class="stat__num">{total_ratings:,}</span><span class="stat__label">{L("App Store ratings", "تقييم على App Store")}</span></div>
      <div class="stat"><span class="stat__num">{best['rating']:.1f}{ICON_STAR}</span><span class="stat__label">{L("top-rated app", "أعلى تطبيق تقييماً")}</span></div>
      <div class="stat"><span class="stat__num">2020</span><span class="stat__label">{L("shipping since", "ننشر منذ")}</span></div>
    </div>
  </div>
</section>

<section class="section section--alt" id="services">
  <div class="wrap">
    <div class="section-head" data-reveal>
      <span class="eyebrow">{L("What we do", "ما نقوم به")}</span>
      {L("Services", "خدماتنا", tag="h2")}
      {L("We take on the whole thing &mdash; design, apps, web and the backend &mdash; or slot into the part you are missing.",
         "ننفّذ المشروع كاملاً &mdash; التصميم والتطبيقات والويب والأنظمة الخلفية &mdash; أو نكمل الجزء الناقص لديك فقط.", tag="p")}
    </div>
    <div class="grid grid--3" data-reveal-group>
{services}
    </div>
  </div>
</section>

<section class="section" id="apps">
  <div class="wrap">
    <div class="section-head" data-reveal>
      <span class="eyebrow">{L("Our own products", "منتجاتنا الخاصة")}</span>
      {L("Apps we built and publish ourselves", "تطبيقات بنيناها وننشرها بأنفسنا", tag="h2")}
      {L("Not a portfolio of screenshots &mdash; these are live products we maintain, support and answer for.",
         "ليست مجرد لقطات في معرض أعمال &mdash; بل منتجات حية نصونها وندعمها ونتحمّل مسؤوليتها.", tag="p")}
    </div>
    <div class="grid grid--4" data-reveal-group>
{cards}
    </div>
  </div>
</section>

<section class="section section--alt" id="process">
  <div class="wrap">
    <div class="section-head" data-reveal>
      <span class="eyebrow">{L("How we work", "كيف نعمل")}</span>
      {L("From first conversation to a live release", "من أول محادثة إلى إطلاق حقيقي", tag="h2")}
    </div>
    <div class="grid grid--4 steps" data-reveal-group>
{steps}
    </div>
  </div>
</section>

<section class="section" id="about">
  <div class="wrap grid grid--2" style="gap:44px;align-items:start" data-reveal-group>
    <div>
      <span class="eyebrow">{L("About", "من نحن")}</span>
      {L("A small studio that ships", "استوديو صغير ينجز ويُطلق", tag="h2")}
      {L("Smart Horizon is a software studio based in Oman. We started by building our own apps &mdash; the first went live in 2020 &mdash; and we have kept them running, updated and supported ever since.",
         "سمارت هورايزن استوديو برمجيات مقره سلطنة عُمان. بدأنا ببناء تطبيقاتنا الخاصة &mdash; صدر أولها عام ٢٠٢٠ &mdash; وواصلنا تشغيلها وتحديثها ودعمها منذ ذلك الحين.", tag="p")}
      {L("That shaped how we work for clients. We know what it costs to keep software alive after launch, so we build for the version that comes after the first one: readable code, sensible architecture, and interfaces that still make sense when the feature list doubles.",
         "وقد شكّل ذلك طريقة عملنا مع العملاء. نعرف كلفة إبقاء البرمجيات حية بعد الإطلاق، لذلك نبني للإصدار الذي يلي الأول: شيفرة مقروءة، وبنية منطقية، وواجهات تبقى مفهومة حتى لو تضاعفت قائمة المزايا.", tag="p")}
      {L("We work in Arabic and English, and we build for both properly &mdash; right-to-left layouts, Arabic typography and localisation treated as part of the design, not a translation pass at the end.",
         "نعمل بالعربية والإنجليزية، ونبني للغتين كما ينبغي &mdash; تخطيطات من اليمين إلى اليسار، وطباعة عربية، وتعريب يُعامل كجزء من التصميم لا كترجمة تُضاف في النهاية.", tag="p")}
    </div>
    <div>
      <div class="card">
        {L("At a glance", "لمحة سريعة", tag="h3")}
        <ul class="feature-list" style="grid-template-columns:1fr">
          <li>{ICON_CHECK}{L("Based in Oman", "مقرنا سلطنة عُمان")}</li>
          <li>{ICON_CHECK}{L("Publishing our own apps since 2020", "ننشر تطبيقاتنا الخاصة منذ عام ٢٠٢٠")}</li>
          <li>{ICON_CHECK}{L("Design, mobile, web and backend under one roof", "التصميم والتطبيقات والويب والأنظمة الخلفية تحت سقف واحد")}</li>
          <li>{ICON_CHECK}{L("Apps supported and updated long after launch", "تطبيقات مدعومة ومحدّثة بعد الإطلاق بوقت طويل")}</li>
          <li>{ICON_CHECK}{L("Arabic and English, RTL done properly", "العربية والإنجليزية، مع دعم صحيح للاتجاه من اليمين لليسار")}</li>
        </ul>
      </div>
    </div>
  </div>
</section>

<section class="section" id="contact" style="padding-block-start:0">
  <div class="wrap">
{cta_block()}
  </div>
</section>

</main>
'''
    html += footer()
    write("index.html", html)


# --------------------------------------------------------------------------
# apps index
# --------------------------------------------------------------------------

def build_apps_index():
    cards = "\n".join(app_card(a) for a in APPS)
    html = head(
        "Our apps — Smart Horizon",
        "تطبيقاتنا — سمارت هورايزن",
        "The apps Smart Horizon builds, publishes and maintains on the App Store and Google Play.",
        "التطبيقات التي تبنيها سمارت هورايزن وتنشرها وتصونها على App Store و Google Play.",
        "/apps/")
    html += header()
    html += f'''<main id="main">
<section class="section">
  <div class="wrap">
    <p class="breadcrumb"><a href="/">{L("Home", "الرئيسية")}</a> / {L("Apps", "التطبيقات")}</p>
    <div class="section-head" data-reveal>
      <span class="eyebrow">{L("Our own products", "منتجاتنا الخاصة")}</span>
      {L("Apps we build and publish", "تطبيقات نبنيها وننشرها", tag="h2")}
      {L("Every one of these is live on the App Store and Google Play, maintained by the same team that takes on client work.",
         "كل تطبيق من هذه التطبيقات منشور على App Store و Google Play، ويصونه الفريق نفسه الذي ينفّذ مشاريع العملاء.", tag="p")}
    </div>
    <div class="grid grid--4" data-reveal-group>
{cards}
    </div>
  </div>
</section>

<section class="section" style="padding-block-start:0">
  <div class="wrap">
{cta_block()}
  </div>
</section>
</main>
'''
    html += footer()
    write("apps/index.html", html)


# --------------------------------------------------------------------------
# app detail pages
# --------------------------------------------------------------------------

def build_app_page(app):
    slug = app["slug"]
    shots = "\n".join(
        f'      <img src="/assets/apps/{slug}/screenshot-{i}.webp" '
        f'alt="{app["name_en"]} screenshot {i}"'
        f'{img_size(f"/assets/apps/{slug}/screenshot-{i}.webp", 250)} loading="lazy">'
        for i in range(1, app["screenshots"] + 1))

    feats = "\n".join(
        f'        <li>{ICON_CHECK}{L(en, ar)}</li>'
        for en, ar in zip(app["features_en"], app["features_ar"]))

    ld = {
        "@context": "https://schema.org",
        "@type": "SoftwareApplication",
        "name": app["name_en"],
        "alternateName": app["name_ar"],
        "operatingSystem": "iOS, Android",
        "applicationCategory": "MobileApplication",
        "url": f"{SITE}/apps/{slug}/",
        "image": f"{SITE}/assets/apps/{slug}/icon.png",
        "description": app["summary_en"],
        "author": {"@type": "Organization", "name": "Smart Horizon"},
        "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"},
    }
    if (app.get("rating_count") or 0) >= 50:
        ld["aggregateRating"] = {
            "@type": "AggregateRating",
            "ratingValue": app["rating"],
            "ratingCount": app["rating_count"],
        }

    legal = f'/legal/{app["legal_slug"]}/privacy-policy.html'
    legal_links = f'<a href="{legal}">{L("Privacy policy", "سياسة الخصوصية")}</a>'
    if app.get("has_terms"):
        legal_links += f' &nbsp;&middot;&nbsp; <a href="/legal/{app["legal_slug"]}/terms-of-service.html">{L("Terms of service", "شروط الاستخدام")}</a>'
    legal_links += f' &nbsp;&middot;&nbsp; <a href="/legal/{app["legal_slug"]}/changelog.html">{L("Version history", "سجل الإصدارات")}</a>'

    html = head(
        f'{app["name_en"]} — Smart Horizon',
        f'{app["name_ar"]} — سمارت هورايزن',
        app["summary_en"][:180],
        app["summary_ar"][:180],
        f"/apps/{slug}/",
        og_image=f"/assets/apps/{slug}/icon.png", og_size=(512, 512),
        extra=f'<script type="application/ld+json">\n{json.dumps(ld, ensure_ascii=False, indent=2)}\n</script>\n')

    html += header()
    html += f'''<main id="main">

<section class="app-hero">
  <div class="wrap">
    <p class="breadcrumb"><a href="/">{L("Home", "الرئيسية")}</a> / <a href="/apps/">{L("Apps", "التطبيقات")}</a> / {L(app['name_en'], app['name_ar'])}</p>
    <div class="app-hero__grid" data-reveal>
      <img class="app-icon" src="/assets/apps/{slug}/icon.png" alt="" width="104" height="104">
      <div>
        <span class="app-card__cat">{L(app['category_en'], app['category_ar'])}</span>
        {L(app['name_en'], app['name_ar'], tag="h1")}
        {L(app['tagline_en'], app['tagline_ar'], tag="p", cls="lede")}
        <div class="app-card__foot" style="margin-block-start:20px">
          {rating_badge(app)}
        </div>
        <div style="margin-block-start:18px">
{stores(app)}
        </div>
      </div>
    </div>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <div class="grid grid--2" style="gap:44px;align-items:start" data-reveal-group>
      <div>
        {L("About the app", "عن التطبيق", tag="h2")}
        {L(app['summary_en'], app['summary_ar'], tag="p")}
      </div>
      <div>
        {L("Features", "المزايا", tag="h2")}
        <ul class="feature-list">
{feats}
        </ul>
      </div>
    </div>
  </div>
</section>

<section class="section section--alt" style="padding-block:56px">
  <div class="wrap">
    {L("Screenshots", "لقطات الشاشة", tag="h2")}
    {L("Scroll sideways to see more.", "مرّر جانبياً لرؤية المزيد.", tag="p")}
    <div class="shots" data-reveal>
{shots}
    </div>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <div class="card center" data-reveal>
      {L("Get the app", "احصل على التطبيق", tag="h3")}
      <div style="display:flex;justify-content:center;margin-block:18px">
{stores(app)}
      </div>
      <p class="legal-links">{legal_links}</p>
    </div>
  </div>
</section>

<section class="section" style="padding-block-start:0">
  <div class="wrap">
{cta_block()}
  </div>
</section>

</main>
'''
    html += footer()
    write(f"apps/{slug}/index.html", html)


# --------------------------------------------------------------------------
# 404 + sitemap + robots
# --------------------------------------------------------------------------

def build_404():
    html = head("Page not found — Smart Horizon", "الصفحة غير موجودة — سمارت هورايزن",
                "That page does not exist.", "هذه الصفحة غير موجودة.", "/404.html")
    html += header()
    html += f'''<main id="main">
<section class="section center">
  <div class="wrap">
    <span class="eyebrow">404</span>
    {L("We could not find that page", "لم نتمكن من العثور على تلك الصفحة", tag="h1")}
    {L("The link may be out of date, or the page may have moved.",
       "قد يكون الرابط قديماً أو أن الصفحة قد نُقلت.", tag="p", cls="lede")}
    <div class="btn-row" style="justify-content:center;margin-block-start:24px">
      <a class="btn btn--primary" href="/">{L("Go home", "العودة للرئيسية")}</a>
      <a class="btn btn--ghost" href="/apps/">{L("Our apps", "تطبيقاتنا")}</a>
    </div>
  </div>
</section>
</main>
'''
    html += footer()
    write("404.html", html)


def build_sitemap():
    urls = ["/", "/apps/"] + [f"/apps/{a['slug']}/" for a in APPS]
    urls += [f"/legal/{a['legal_slug']}/privacy-policy.html" for a in APPS]
    body = "\n".join(
        f'  <url>\n    <loc>{SITE}{u}</loc>\n'
        f'    <changefreq>{"monthly" if u.startswith("/legal") else "weekly"}</changefreq>\n'
        f'    <priority>{"1.0" if u == "/" else "0.8" if u.startswith("/apps") else "0.4"}</priority>\n  </url>'
        for u in urls)
    write("sitemap.xml",
          '<?xml version="1.0" encoding="UTF-8"?>\n'
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
          f'{body}\n</urlset>\n')

    write("robots.txt",
          "User-agent: *\n"
          "Allow: /\n"
          "Disallow: /tools/\n"
          "Disallow: /.history/\n\n"
          f"Sitemap: {SITE}/sitemap.xml\n")


# --------------------------------------------------------------------------

def main():
    print("Building pages:")
    build_index()
    build_apps_index()
    for a in APPS:
        build_app_page(a)
    build_404()
    build_sitemap()
    # Keep GitHub Pages from running the files through Jekyll.
    (ROOT / ".nojekyll").touch()
    print("Done.")


if __name__ == "__main__":
    main()
