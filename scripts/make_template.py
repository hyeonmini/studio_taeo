# -*- coding: utf-8 -*-
"""Turn the validated Korean index.html into scripts/template.html with %%MARKERS%%.

Run once whenever index.html's structure changes. build_site.py consumes the
template to generate every locale.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from i18n_data import STRINGS  # noqa: E402

KO = STRINGS["ko"]


def build_template() -> str:
    h = open(os.path.join(ROOT, "index.html"), encoding="utf-8").read()

    # ---- structural ----
    h = h.replace('<html lang="ko">', '<html lang="%%LANG%%"%%DIR%%>')
    h = h.replace('href="assets/favicon.png"', 'href="%%P%%assets/favicon.png"')
    h = h.replace('assets/icon.png', '%%P%%assets/icon.png')          # apple-touch + nav brand
    h = h.replace('assets/appstore-ko-black.svg', 'appstore-black.svg')
    h = h.replace('assets/appstore-ko-white.svg', 'appstore-white.svg')
    h = h.replace('alt="App Store에서 다운로드"', 'alt="%%BADGE_ALT%%"')
    h = h.replace('🌐 한국어 ▾', '🌐 %%LANGNAME%% ▾')
    h = h.replace('href="terms.html"', 'href="%%P%%%%TERMS_FILE%%"')
    h = h.replace('href="privacy.html"', 'href="%%P%%%%PRIVACY_FILE%%"')
    h = h.replace('href="support.html"', 'href="%%P%%%%SUPPORT_FILE%%"')

    # ---- context-sensitive text (markup around the value) ----
    ctx = [
        ('<div class="rail-hd">둘러보기</div>',   '<div class="rail-hd">%%RAIL_HD%%</div>'),
        ('alt="스크린샷으로 지출 등록 화면"',       'alt="%%ALT_SCAN%%"'),
        ('alt="자동으로 정리된 거래 검토 화면"',    'alt="%%ALT_REVIEW%%"'),
        ('alt="예산과 계산기 키패드 입력 화면"',    'alt="%%ALT_ENTRY%%"'),
        ('alt="목적별 공동 가계부 목록 화면"',      'alt="%%ALT_LEDGERS%%"'),
        ('alt="다중 통화와 실시간 환율 선택 화면"', 'alt="%%ALT_CURRENCY%%"'),
        ('alt="카테고리·결제수단·주체 필터 화면"',  'alt="%%ALT_FILTER%%"'),
        ('<span class="dot">곧</span>',          '<span class="dot">%%GP_SOON%%</span>'),
        ('<span class="stamp">✓ 7건 정리</span>', '<span class="stamp">✓ %%DEMO_STAMP%%</span>'),
        ('⌨ 타이핑 <b>0</b>',                     '⌨ %%CHIP_TYPING%%'),
        ('⏱ 약 <b>10초</b>',                      '⏱ %%CHIP_TIME%%'),
        ('🖼 한 번에 <b>5장</b>',                  '🖼 %%CHIP_BATCH%%'),
        ('🌐 <b>38개</b> 언어',                    '🌐 %%CHIP_LANG%%'),
        ('ACT I — 입력이 간단하다',                'ACT I — %%ACT1_LABEL%%'),
        ('THANK YOU — 결제하신 게 없으니 0원입니다 :)', 'THANK YOU — %%RC_TY%%'),
        (KO["TITLE"],   '%%TITLE%%'),    # <title> + og:title
        (KO["DESC"],    '%%DESC%%'),
        (KO["OG_DESC"], '%%OG_DESC%%'),
    ]
    for a, b in ctx:
        if a not in h:
            print(f"  ! context string not found: {a[:40]}…")
        h = h.replace(a, b)

    # ---- plain value -> marker, longest first to avoid nesting collisions ----
    handled = {"TITLE", "DESC", "OG_DESC", "BADGE_ALT", "GP_SOON", "DEMO_STAMP",
               "CHIP_TYPING", "CHIP_TIME", "CHIP_BATCH", "CHIP_LANG", "ACT1_LABEL", "RC_TY",
               "RAIL_HD", "ALT_SCAN", "ALT_REVIEW", "ALT_ENTRY", "ALT_LEDGERS",
               "ALT_CURRENCY", "ALT_FILTER"}
    plain = [(k, KO[k]) for k in KO if k not in handled]
    plain.sort(key=lambda kv: len(kv[1]), reverse=True)
    for k, v in plain:
        if v not in h:
            print(f"  ! value not found for {k}: {v[:40]}…")
        h = h.replace(v, f"%%{k}%%")

    return h


def main():
    out = build_template()
    path = os.path.join(HERE, "template.html")
    open(path, "w", encoding="utf-8").write(out)
    # report leftover Hangul (should be only inside the language dropdown 한국어)
    import re
    leftover = re.findall(r"[가-힣]+", out)
    print(f"template.html written ({len(out)} bytes). markers: {out.count('%%')//2}. "
          f"leftover Hangul tokens: {leftover}")


if __name__ == "__main__":
    main()
