import re

with open('scratch/SHT45.html', 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

print('Length of SHT45.html:', len(text))
for m in re.finditer(r'.{0,60}SZH-MIN069.{0,60}', text):
    print('Match SZH:', m.group(0).strip())

for m in re.finditer(r'<iframe[^>]+src=[\'"]([^\'"]+)[\'"]', text):
    print('Iframe:', m.group(1))

# search for images containing goods, editor, upload
imgs = re.findall(r'<img[^>]+src=[\'"]([^\'"]+)[\'"]', text)
for img in imgs:
    if any(k in img for k in ['goods', 'editor', 'upload', 'data/collect', 'tmp']):
        print('Image:', img)

# search for ajax call or common goods content container
for m in re.finditer(r'load\([\'"]([^\'"]+)[\'"]', text):
    print('Ajax load:', m.group(1))

for m in re.finditer(r'url\s*:\s*[\'"]([^\'"]+)[\'"]', text):
    if 'goods' in m.group(1):
        print('Ajax url:', m.group(1))
