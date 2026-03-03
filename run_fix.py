import os
import glob
import re

svg_code = '''<div class="social-icon d-flex align-items-center">
    <a href="https://www.facebook.com/mockupagency" target="_blank" rel="noopener noreferrer" aria-label="Facebook">
        <svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true" focusable="false">
            <path fill="currentColor" d="M13.5 21v-7.5H16l.5-3h-3V8.6c0-.9.3-1.6 1.7-1.6h1.4V4.3c-.2 0-1.1-.1-2.2-.1-2.2 0-3.7 1.3-3.7 3.9v2.2H8.5v3h2.2V21h2.8z"/>
        </svg>
    </a>
    <a href="https://www.instagram.com/mockup_agency/" target="_blank" rel="noopener noreferrer" aria-label="Instagram">
        <svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true" focusable="false">
            <path fill="currentColor" d="M7.8 3h8.4C19.4 3 22 5.6 22 8.8v6.4c0 3.2-2.6 5.8-5.8 5.8H7.8C4.6 21 2 18.4 2 15.2V8.8C2 5.6 4.6 3 7.8 3zm0 1.9A3.9 3.9 0 0 0 3.9 8.8v6.4A3.9 3.9 0 0 0 7.8 19h8.4a3.9 3.9 0 0 0 3.9-3.8V8.8A3.9 3.9 0 0 0 16.2 5H7.8zm8.8 1.5a1.2 1.2 0 1 1 0 2.4 1.2 1.2 0 0 1 0-2.4zM12 7.6a4.4 4.4 0 1 1 0 8.8 4.4 4.4 0 0 1 0-8.8zm0 1.9a2.5 2.5 0 1 0 0 5.1 2.5 2.5 0 0 0 0-5z"/>
        </svg>
    </a>
</div>'''

pattern = re.compile(r'<div class="social-icon d-flex align-items-center">.*?</div>', re.DOTALL)
for file in glob.glob('public/clone/**/*.html', recursive=True):
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()
    new_content = pattern.sub(svg_code, content)
    if new_content != content:
        with open(file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Updated {file}")
