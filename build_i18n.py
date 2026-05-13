import os
import time
import shutil
from deep_translator import GoogleTranslator

# Map fastlane locales to google translate locales
locale_map = {
    'ar-SA': 'ar', 'ca': 'ca', 'cs': 'cs', 'da': 'da', 'de-DE': 'de', 'el': 'el', 
    'en-US': 'en', 'es-ES': 'es', 'es-MX': 'es', 'fi': 'fi', 'fr-CA': 'fr', 
    'fr-FR': 'fr', 'he': 'iw', 'hi': 'hi', 'hr': 'hr', 'hu': 'hu', 'id': 'id', 
    'it': 'it', 'ja': 'ja', 'ko': 'ko', 'lt': 'lt', 'lv': 'lv', 'ms': 'ms', 'nl-NL': 'nl', 'no': 'no', 
    'pl': 'pl', 'pt-BR': 'pt', 'pt-PT': 'pt', 'ro': 'ro', 'ru': 'ru', 'sk': 'sk', 
    'sv': 'sv', 'th': 'th', 'tr': 'tr', 'uk': 'uk', 'vi': 'vi', 
    'zh-Hans': 'zh-CN', 'zh-Hant': 'zh-TW'
}

# The visual name mapping
lang_names = {
    'ar-SA': 'العربية', 'ca': 'Català', 'cs': 'Čeština', 'da': 'Dansk', 'de-DE': 'Deutsch', 
    'el': 'Ελληνικά', 'en-US': 'English (US)', 'es-ES': 'Español (ES)', 'es-MX': 'Español (MX)', 
    'fi': 'Suomi', 'fr-CA': 'Français (CA)', 'fr-FR': 'Français (FR)', 'he': 'עברית', 
    'hi': 'हिन्दी', 'hr': 'Hrvatski', 'hu': 'Magyar', 'id': 'Bahasa Indonesia', 
    'it': 'Italiano', 'ja': '日本語', 'ko': '한국어', 'lt': 'Lietuvių', 'lv': 'Latviešu', 'ms': 'Bahasa Melayu', 
    'nl-NL': 'Nederlands', 'no': 'Norsk', 'pl': 'Polski', 'pt-BR': 'Português (BR)', 
    'pt-PT': 'Português (PT)', 'ro': 'Română', 'ru': 'Русский', 'sk': 'Slovenčina', 
    'sv': 'Svenska', 'th': 'ไทย', 'tr': 'Türkçe', 'uk': 'Українська', 'vi': 'Tiếng Việt', 
    'zh-Hans': '简体中文', 'zh-Hant': '繁體中文'
}

texts_to_translate = [
    "WeSpend - Lightning Fast Shared Expense Tracker",
    "A real-time shared expense tracker for couples and families. Experience the lightning-fast input optimized for your daily tracking.",
    "The Fastest, Most Seamless",
    "Shared Expense Tracker",
    "Start logging your expenses the second you open the app.",
    "With our lightning-fast input and intuitive widgets, managing expenses with your partner or family has never been easier.",
    "Log Your Annoying Expenses in 1 Second",
    "Consistency is key when managing personal finance.",
    "We provide the fastest and most comfortable input experience so you never miss a receipt.",
    "Lightning-Fast Input",
    "Log your spending instantly with our custom-built numeric keypad. Features like built-in calculator functions and a dedicated safe-delete (⌫) key guarantee the fastest entry speed.",
    "Shared Household Economy",
    "Share a ledger with your loved ones using a simple 6-digit invite code. All entered records sync immediately in real-time, keeping everyone on the same page.",
    "Instant Home Screen Widgets",
    "Add expenses directly from your Home Screen or Lock Screen utilizing our powerful Numpad widget without even fully launching the app.",
    "Multi-currency & Live Rates",
    "Log in local currency while traveling abroad. We support over 50 global currencies and automatically calculate your base currency utilizing live exchange rates from the moment of purchase.",
    "Custom Folders & Smart Filters",
    "Personalize your categories with 16 preset colors. Easily analyze your spending behavior by filtering through payment methods (cash/card) or attribution (me/partner).",
    "Secure & Simple Accounts",
    "Sign up in a single tap via Apple or Google Sign-In—no typed email/password required. You can also explore all features safely using our Anonymous Tour Mode.",
    "Terms of Service",
    "Privacy Policy",
    "Download on the App Store",
    "Google Play Coming Soon"
]

def build():
    root_dir = '/Users/kimhyeonmin/prj/StudioTaeo'
    with open(os.path.join(root_dir, 'index-en.html'), 'r', encoding='utf-8') as f:
        base_html = f.read()

    # Create the dropdown HTML
    dropdown_html = '<ul class="lang-dropdown" role="listbox">\n'
    # Base links
    dropdown_html += '    <li role="option"><a href="/">한국어</a></li>\n'
    dropdown_html += '    <li role="option"><a href="/en/">English</a></li>\n'
    for loc, name in lang_names.items():
        if loc not in ['ko', 'en-US']: # ko and en are base
            dropdown_html += f'    <li role="option"><a href="/{loc}/">{name}</a></li>\n'
    dropdown_html += '</ul>'

    # Prepare specific translations per language
    for fastlane_loc, g_loc in locale_map.items():
        if fastlane_loc == 'ko': continue # root handles Korean
        if fastlane_loc == 'en-US': continue # en handles English
        
        print(f"Translating for {fastlane_loc} ({g_loc})...")
        
        try:
            translator = GoogleTranslator(source='en', target=g_loc)
            translated = []
            for i, txt in enumerate(texts_to_translate):
                print(f"  [{i+1}/{len(texts_to_translate)}] Translating...")
                translated.append(translator.translate(txt))
                time.sleep(0.1)
        except Exception as e:
            print(f"Skipping {fastlane_loc} due to error: {e}")
            time.sleep(1)
            continue

        out_html = base_html
        
        # Replace the <html lang="en"> to correct lang
        out_html = out_html.replace('<html lang="en">', f'<html lang="{g_loc}">')
        
        # Replace dropdown place holder
        start_marker = '<ul class="lang-dropdown" role="listbox">'
        end_marker = '</ul>'
        s_idx = out_html.find(start_marker)
        e_idx = out_html.find(end_marker, s_idx)
        if s_idx != -1 and e_idx != -1:
            out_html = out_html[:s_idx] + dropdown_html + out_html[e_idx+len(end_marker):]

        # Update button text to language name
        out_html = out_html.replace('🌐</span> English', f'🌐</span> {lang_names[fastlane_loc]}')
        
        # Links to terms/privacy should explicitly be absolute from root so they don't 404
        out_html = out_html.replace('href="terms-en.html"', 'href="/terms-en.html"')
        out_html = out_html.replace('href="privacy-en.html"', 'href="/privacy-en.html"')
        
        # Replace texts
        for i, eng_text in enumerate(texts_to_translate):
            if translated[i]:
                out_html = out_html.replace(eng_text, translated[i])
        
        # Write to subfolder
        out_dir = os.path.join(root_dir, fastlane_loc)
        os.makedirs(out_dir, exist_ok=True)
        with open(os.path.join(out_dir, 'index.html'), 'w', encoding='utf-8') as f:
            f.write(out_html)

        # Copy screenshot
        screenshot_src = f'/Volumes/DEV_SSD/prj/wespend/darwin/fastlane/screenshots/{fastlane_loc}/iPhone 17 Pro Max-01_Home.png'
        if os.path.exists(screenshot_src):
            shutil.copy2(screenshot_src, os.path.join(out_dir, 'screenshot.png'))

    # Finally update English fallback dir /en/
    en_dir = os.path.join(root_dir, 'en')
    os.makedirs(en_dir, exist_ok=True)
    en_html = base_html.replace('href="terms-en.html"', 'href="/terms-en.html"')
    en_html = en_html.replace('href="privacy-en.html"', 'href="/privacy-en.html"')
    # replace dropdown in en html too
    s_idx = en_html.find(start_marker)
    e_idx = en_html.find(end_marker, s_idx)
    if s_idx != -1 and e_idx != -1:
        en_html = en_html[:s_idx] + dropdown_html + en_html[e_idx+len(end_marker):]
    with open(os.path.join(en_dir, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(en_html)

    screenshot_en = '/Volumes/DEV_SSD/prj/wespend/darwin/fastlane/screenshots/en-US/iPhone 17 Pro Max-01_Home.png'
    if os.path.exists(screenshot_en):
        shutil.copy2(screenshot_en, os.path.join(en_dir, 'screenshot.png'))

    # Update Korean root index.html dropdown too
    with open(os.path.join(root_dir, 'index.html'), 'r', encoding='utf-8') as f:
        ko_html = f.read()
    s_idx = ko_html.find(start_marker)
    e_idx = ko_html.find(end_marker, s_idx)
    if s_idx != -1 and e_idx != -1:
        ko_html = ko_html[:s_idx] + dropdown_html + ko_html[e_idx+len(end_marker):]
    with open(os.path.join(root_dir, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(ko_html)

    screenshot_ko = '/Volumes/DEV_SSD/prj/wespend/darwin/fastlane/screenshots/ko/iPhone 17 Pro Max-01_Home.png'
    if os.path.exists(screenshot_ko):
        shutil.copy2(screenshot_ko, os.path.join(root_dir, 'screenshot.png'))

if __name__ == "__main__":
    build()
