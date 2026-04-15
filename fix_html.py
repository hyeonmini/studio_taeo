import os
import re

def fix():
    root = '/Users/kimhyeonmin/prj/StudioTaeo'
    
    css_pattern = re.compile(r'\.lang-switcher:hover \.lang-dropdown,[\s]*\.lang-switcher:focus-within \.lang-dropdown\s*\{\s*display: block;\s*\}')
    
    new_css = """.lang-dropdown.show {
            display: block;
        }"""
        
    js_inject = """
    <script>
        document.addEventListener('click', function(e) {
            const dropdown = document.querySelector('.lang-dropdown');
            const btn = e.target.closest('.lang-switch-btn');
            if (btn) {
                e.preventDefault();
                dropdown.classList.toggle('show');
            } else if (dropdown && !e.target.closest('.lang-dropdown')) {
                dropdown.classList.remove('show');
            }
        });
    </script>
</body>"""

    count = 0
    for dirpath, _, files in os.walk(root):
        for f in files:
            if f.endswith('.html'):
                p = os.path.join(dirpath, f)
                with open(p, 'r', encoding='utf-8') as file:
                    content = file.read()
                
                original = content
                
                # 1. Fix CSS typo
                if '.lang-switch {' in content:
                    content = content.replace('.lang-switch {', '.lang-switch-btn {')
                
                # 2. Fix hover to click
                content = css_pattern.sub(new_css, content)
                
                # 3. Inject JS if not present
                if "dropdown.classList.toggle('show');" not in content:
                    content = content.replace('</body>', js_inject)
                    
                if original != content:
                    with open(p, 'w', encoding='utf-8') as file:
                        file.write(content)
                    count += 1
                    
    print(f"Fixed {count} files.")

if __name__ == '__main__':
    fix()
