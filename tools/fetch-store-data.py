#!/usr/bin/env python3
"""
Refresh App Store metadata and imagery for the apps in data/apps.json.

    python3 tools/fetch-store-data.py            # icons + screenshots + ratings
    python3 tools/fetch-store-data.py --no-images  # ratings and counts only

Reads the public iTunes lookup API for Smart Horizon's developer account,
matches results to data/apps.json by ios_id, and updates the volatile
fields in place (rating, rating_count, screenshots). Editorial copy --
names, taglines, summaries, features -- is never touched.

Screenshots and icons are downloaded into assets/apps/<slug>/ rather than
hotlinked, so the site does not depend on Apple's CDN.
"""

import argparse
import json
import pathlib
import re
import sys
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
CATALOG = ROOT / "data" / "apps.json"
ARTIST_ID = "1527611187"          # Smart Horizon on the App Store
COUNTRY = "OM"
SHOT_WIDTH = 750                  # px, the width screenshots are stored at
UA = {"User-Agent": "Mozilla/5.0 (smarthorizon.co site build)"}


def fetch_json(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))


def fetch_text(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read().decode("utf-8", "replace")


def download(url, dest):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=90) as r:
        data = r.read()
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(data)
    return len(data)


def resized(url, spec):
    """Apple's image CDN takes the target size as the last path segment."""
    return re.sub(r"/[0-9]+x[0-9]+[a-z]{0,3}\.(png|jpg|jpeg|webp)$", "/" + spec, url)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-images", action="store_true",
                    help="update ratings only, skip downloading imagery")
    args = ap.parse_args()

    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    by_id = {a["ios_id"]: a for a in catalog["apps"]}

    url = (f"https://itunes.apple.com/lookup?id={ARTIST_ID}"
           f"&entity=software&limit=200&country={COUNTRY}")
    results = [r for r in fetch_json(url)["results"] if r.get("wrapperType") != "artist"]
    if not results:
        sys.exit("No apps returned -- check the artist id or your connection.")

    seen = set()
    for r in results:
        app = by_id.get(str(r["trackId"]))
        if not app:
            print(f"! {r['trackName']} (id {r['trackId']}) is on the App Store "
                  f"but not in data/apps.json -- add it manually.")
            continue
        seen.add(app["slug"])

        shots = r.get("screenshotUrls") or []
        app["rating"] = round(r.get("averageUserRating") or 0, 2)
        app["rating_count"] = r.get("userRatingCount") or 0
        app["screenshots"] = len(shots)
        app["last_updated"] = (r.get("currentVersionReleaseDate") or "")[:10]
        app["version"] = r.get("version")
        print(f"{app['slug']}: {app['rating']} ({app['rating_count']} ratings), "
              f"{len(shots)} screenshots")

        if args.no_images:
            continue

        out = ROOT / "assets" / "apps" / app["slug"]
        # Drop screenshots that no longer exist on the listing.
        for stale in out.glob("screenshot-*.webp"):
            n = int(re.search(r"screenshot-(\d+)", stale.name).group(1))
            if n > len(shots):
                stale.unlink()
                print(f"    removed stale {stale.name}")

        download(resized(r["artworkUrl512"], "512x512bb.png"), out / "icon.png")
        for i, u in enumerate(shots, 1):
            download(resized(u, f"{SHOT_WIDTH}x0w.webp"), out / f"screenshot-{i}.webp")
        print(f"    icon + {len(shots)} screenshots saved")

    # Google Play publishes an install range; Apple publishes nothing
    # comparable, so downloads always come from Play.
    print("\nGoogle Play install ranges:")
    for app in catalog["apps"]:
        try:
            html = fetch_text("https://play.google.com/store/apps/details"
                              f"?id={app['android_id']}&hl=en&gl=US")
            m = re.search(r"([\d.,]+[KMB]?\+)\s+Downloads", re.sub(r"<[^>]+>", " ", html))
            if m:
                app["play_downloads"] = m.group(1)
                print(f"  {app['slug']}: {m.group(1)}")
            else:
                print(f"  {app['slug']}: not found (keeping {app.get('play_downloads', '—')})")
        except Exception as exc:
            print(f"  {app['slug']}: lookup failed ({exc}) -- keeping existing value")

    missing = [a["slug"] for a in catalog["apps"] if a["slug"] not in seen]
    if missing:
        print(f"! Not found on the App Store: {', '.join(missing)}")

    CATALOG.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n",
                       encoding="utf-8")
    print("\ndata/apps.json updated. Now run: python3 tools/build-pages.py")


if __name__ == "__main__":
    main()
