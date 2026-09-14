import os
from bs4 import BeautifulSoup

for name in ['SHT45', 'GY-521', 'BH1750', 'GPS_ATGM336H']:
    path = f'scratch/contents/{name}.html'
    if not os.path.exists(path):
        continue
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
        
    soup = BeautifulSoup(content, 'html.parser')
    text = soup.get_text('\n', strip=True)
    out_txt = f'scratch/contents/{name}_text.txt'
    with open(out_txt, 'w', encoding='utf-8') as out_f:
        out_f.write(text)
    print(f'=== {name} ({len(text)} chars) ===')
    for line in text.split('\n'):
        if any(w in line for w in ['크기', '사이즈', '치수', '규격', 'Dimensions', 'Size', 'PIN', 'Pin', '핀', 'VCC', 'GND', 'SDA', 'SCL', 'TXD', 'RXD', 'mm', 'MM', '커넥터', '헤더', '피치']):
            print('  ', line)
