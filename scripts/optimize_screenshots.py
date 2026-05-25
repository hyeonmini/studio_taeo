#!/usr/bin/env python3
"""Resize + convert localized fastlane iPhone screenshots into web-ready WebP.

Source : /Volumes/DEV_SSD/prj/wespend/darwin/fastlane/screenshots/<fastlane_loc>/
Output : /Volumes/DEV_SSD/prj/StudioTaeo/<web_loc>/  (root for ko, 'en' for en-US)

Usage:
    python3 scripts/optimize_screenshots.py            # ko + en-US only (showcase)
    python3 scripts/optimize_screenshots.py all        # every locale that has screenshots
    python3 scripts/optimize_screenshots.py ko en-US ja
"""
import os
import sys
from PIL import Image

SRC_ROOT = "/Volumes/DEV_SSD/prj/wespend/darwin/fastlane/screenshots"
WEB_ROOT = "/Volumes/DEV_SSD/prj/StudioTaeo"
TARGET_W = 680          # display ~340px @2x
QUALITY = 80

# fastlane screenshot filename -> web webp name
NAME_MAP = {
    "iPhone 17 Pro Max-01_ScreenshotPicker.png":    "ss-scan.webp",
    "iPhone 17 Pro Max-01_ScreenshotAutoEntry.png": "ss-review.webp",
    "iPhone 17 Pro Max-02_ExpenseEntry.png":        "ss-entry.webp",
    "iPhone 17 Pro Max-03_Currency.png":            "ss-currency.webp",
    "iPhone 17 Pro Max-04_Filter.png":              "ss-filter.webp",
    "iPhone 17 Pro Max-05_Households.png":          "ss-ledgers.webp",
}


def web_dir_for(fastlane_loc: str) -> str:
    if fastlane_loc == "ko":
        return WEB_ROOT
    if fastlane_loc == "en-US":
        return os.path.join(WEB_ROOT, "en")
    return os.path.join(WEB_ROOT, fastlane_loc)


def all_locales() -> list[str]:
    return sorted(
        d for d in os.listdir(SRC_ROOT)
        if os.path.isdir(os.path.join(SRC_ROOT, d))
    )


def process(fastlane_loc: str) -> int:
    src = os.path.join(SRC_ROOT, fastlane_loc)
    if not os.path.isdir(src):
        print(f"  ! no source for {fastlane_loc}")
        return 0
    out = web_dir_for(fastlane_loc)
    os.makedirs(out, exist_ok=True)
    n = 0
    for fname, webname in NAME_MAP.items():
        sp = os.path.join(src, fname)
        if not os.path.exists(sp):
            continue
        img = Image.open(sp).convert("RGB")
        w, h = img.size
        nh = round(h * TARGET_W / w)
        img = img.resize((TARGET_W, nh), Image.LANCZOS)
        img.save(os.path.join(out, webname), format="WEBP", quality=QUALITY, method=6)
        n += 1
    print(f"  {fastlane_loc:7s} -> {os.path.relpath(out, WEB_ROOT) or '.'}  ({n} imgs)")
    return n


def main():
    args = sys.argv[1:]
    if not args:
        locales = ["ko", "en-US"]
    elif args == ["all"]:
        locales = all_locales()
    else:
        locales = args
    total = 0
    for loc in locales:
        total += process(loc)
    print(f"Done. {total} images across {len(locales)} locales.")


if __name__ == "__main__":
    main()
