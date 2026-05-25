# -*- coding: utf-8 -*-
"""Build every localized WeSpend landing page from scripts/template.html.

Per locale it writes <dir>/index.html, localized screenshots (ss-*.webp),
and the official Apple App Store badges (appstore-black.svg / appstore-white.svg).

Usage:
    python3 scripts/build_site.py                 # all locales, full build
    python3 scripts/build_site.py ja de-DE ar-SA  # only these (html+assets)
    python3 scripts/build_site.py --html-only     # skip screenshots + badges
    python3 scripts/build_site.py --force         # rebuild screenshots/badges even if present
"""
import os
import sys
import json
import time
import urllib.request

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from i18n_data import LOCALES, STRINGS, KEYS  # noqa: E402

SS_SRC = "/Volumes/DEV_SSD/prj/wespend/darwin/fastlane/screenshots"
CACHE = os.path.join(HERE, "i18n_cache.json")
TARGET_W, QUALITY = 680, 80
BADGE_API = "https://toolbox.marketingtools.apple.com/api/v2/badges/download-on-the-app-store"

SS_MAP = {
    "iPhone 17 Pro Max-01_ScreenshotPicker.png":    "ss-scan.webp",
    "iPhone 17 Pro Max-01_ScreenshotAutoEntry.png": "ss-review.webp",
    "iPhone 17 Pro Max-02_ExpenseEntry.png":        "ss-entry.webp",
    "iPhone 17 Pro Max-03_Currency.png":            "ss-currency.webp",
    "iPhone 17 Pro Max-04_Filter.png":              "ss-filter.webp",
    "iPhone 17 Pro Max-05_Households.png":          "ss-ledgers.webp",
}


# ----------------------------- translation -----------------------------
def load_cache():
    if os.path.exists(CACHE):
        return json.load(open(CACHE, encoding="utf-8"))
    return {}


def save_cache(c):
    json.dump(c, open(CACHE, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


def translate_locale(g_code, cache):
    """Return {key: text} for a google-translate code, using/refreshing cache."""
    if g_code in cache and all(k in cache[g_code] for k in KEYS):
        return cache[g_code]
    from deep_translator import GoogleTranslator
    tr = GoogleTranslator(source="en", target=g_code)
    out = cache.get(g_code, {})
    for k in KEYS:
        if out.get(k):
            continue
        src = STRINGS["en"][k]
        try:
            res = tr.translate(src)
            out[k] = res if res else src
        except Exception as e:
            print(f"    ! {g_code}/{k} translate failed ({e}); keeping EN")
            out[k] = src
        time.sleep(0.05)
    cache[g_code] = out
    save_cache(cache)
    return out


def strings_for(loc, cache):
    if loc["fl"] == "ko":
        return STRINGS["ko"]
    if loc["fl"] == "en-US":
        return STRINGS["en"]
    return translate_locale(loc["g"], cache)


# ----------------------------- html -----------------------------
def fill(tpl, loc, s):
    p = "" if loc["dir"] == "" else "../"
    terms = "terms.html" if loc["fl"] == "ko" else "terms-en.html"
    privacy = "privacy.html" if loc["fl"] == "ko" else "privacy-en.html"
    ogurl = "https://wespend.studiotaeo.com/" + (loc["dir"] + "/" if loc["dir"] else "")
    h = tpl
    h = h.replace('content="https://wespend.studiotaeo.com/"', f'content="{ogurl}"')
    h = h.replace("%%LANGNAME%%", loc["name"])
    h = h.replace("%%LANG%%", loc["lang"])
    h = h.replace("%%DIR%%", ' dir="rtl"' if loc["rtl"] else "")
    h = h.replace("%%TERMS_FILE%%", terms)
    h = h.replace("%%PRIVACY_FILE%%", privacy)
    h = h.replace("%%SUPPORT_FILE%%", "support.html")
    h = h.replace("%%P%%", p)
    # content keys, longest marker first (avoids any prefix overlap)
    for k in sorted(KEYS, key=len, reverse=True):
        h = h.replace(f"%%{k}%%", s.get(k, STRINGS["en"][k]))
    return h


# ----------------------------- assets -----------------------------
def build_screenshots(loc, force):
    src = os.path.join(SS_SRC, loc["fl"])
    if not os.path.isdir(src):
        src = os.path.join(SS_SRC, "en-US")  # lt/lv etc.
    out = ROOT if loc["dir"] == "" else os.path.join(ROOT, loc["dir"])
    os.makedirs(out, exist_ok=True)
    n = 0
    for fn, webn in SS_MAP.items():
        dst = os.path.join(out, webn)
        if os.path.exists(dst) and not force:
            n += 1
            continue
        sp = os.path.join(src, fn)
        if not os.path.exists(sp):
            continue
        img = Image.open(sp).convert("RGB")
        w, hgt = img.size
        img = img.resize((TARGET_W, round(hgt * TARGET_W / w)), Image.LANCZOS)
        img.save(dst, format="WEBP", quality=QUALITY, method=6)
        n += 1
    return n


def fetch_badge(apple, variant):
    for code in (apple, "en-us"):
        try:
            req = urllib.request.Request(f"{BADGE_API}/{variant}/{code}",
                                         headers={"User-Agent": "Mozilla/5.0"})
            data = urllib.request.urlopen(req, timeout=20).read()
            if data[:4] == b"<svg" or b"<svg" in data[:200]:
                return data
        except Exception:
            pass
    return None


def build_badges(loc, force):
    out = ROOT if loc["dir"] == "" else os.path.join(ROOT, loc["dir"])
    os.makedirs(out, exist_ok=True)
    for variant, name in (("black", "appstore-black.svg"), ("white", "appstore-white.svg")):
        dst = os.path.join(out, name)
        if os.path.exists(dst) and not force:
            continue
        data = fetch_badge(loc["apple"], variant)
        if data:
            open(dst, "wb").write(data)
        else:
            print(f"    ! badge {variant} failed for {loc['fl']}")


# ----------------------------- main -----------------------------
def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    flags = {a for a in sys.argv[1:] if a.startswith("--")}
    html_only = "--html-only" in flags
    force = "--force" in flags
    locales = [l for l in LOCALES if (not args or l["fl"] in args)]

    tpl = open(os.path.join(HERE, "template.html"), encoding="utf-8").read()
    cache = load_cache()

    for loc in locales:
        s = strings_for(loc, cache)
        html = fill(tpl, loc, s)
        out = ROOT if loc["dir"] == "" else os.path.join(ROOT, loc["dir"])
        os.makedirs(out, exist_ok=True)
        open(os.path.join(out, "index.html"), "w", encoding="utf-8").write(html)
        extra = ""
        if not html_only:
            ns = build_screenshots(loc, force)
            build_badges(loc, force)
            extra = f" · {ns} shots · badges"
        print(f"  {loc['fl']:8s} -> /{loc['dir'] or ''}{extra}")

    print(f"Done. {len(locales)} locales.")


if __name__ == "__main__":
    main()
