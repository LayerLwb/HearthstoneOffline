import re

with open(r'C:\HearthstoneWeb\assets\index-CTplPp4x.css', 'r', encoding='utf-8') as f:
    css = f.read()

for cls in ['battle-stage', 'battle-page', 'hand-area', 'hand-card']:
    matches = re.findall(rf'(\.[^{{}}]*?{cls}[^{{}}]*?\{{[^}}]*?\}})', css)
    print(f'=== Class: {cls} ({len(matches)} matches) ===')
    for m in matches[:5]:
        print(m)
