import os
import re
from bs4 import BeautifulSoup
import urllib.request

os.makedirs('scratch/images', exist_ok=True)

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': 'https://www.devicemart.co.kr/'
}

for name in ['SHT45', 'GY-521', 'BH1750', 'GPS_ATGM336H']:
    path = f'scratch/{name}.html'
    if not os.path.exists(path):
        continue
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        html_doc = f.read()

    soup = BeautifulSoup(html_doc, 'html.parser')
    
    print(f'====================================')
    print(f'PRODUCT: {name}')
    print(f'====================================')
    
    # Try finding goods description container
    target = None
    for cand in ['goods_contents', 'detail_contents', 'goods_description', 'contents']:
        t = soup.find('div', id=cand) or soup.find('div', class_=cand)
        if t:
            target = t
            break
            
    if not target:
        target = soup
        
    imgs = []
    for img in target.find_all('img'):
        src = img.get('src') or img.get('data-src') or ''
        if src and any(x in src for x in ['editor', 'goods', 'upload', 'data']):
            imgs.append(src)
            
    print(f'Found {len(imgs)} product images:')
    for i, img_url in enumerate(imgs):
        if not img_url.startswith('http'):
            img_url = 'https://www.devicemart.co.kr' + img_url
        print(f'  [{i}] {img_url}')
        # download image
        img_ext = os.path.splitext(img_url.split('?')[0])[1] or '.jpg'
        local_img = f'scratch/images/{name}_{i}{img_ext}'
        try:
            req = urllib.request.Request(img_url, headers=headers)
            with urllib.request.urlopen(req) as resp, open(local_img, 'wb') as out_f:
                out_f.write(resp.read())
            print(f'       Saved to: {local_img} ({os.path.getsize(local_img)} bytes)')
        except Exception as e:
            print(f'       Download failed: {e}')

    text = target.get_text('\n', strip=True)
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    
    # Look for specifications
    print('\nKey Spec Lines:')
    for l in lines:
        if any(k in l.lower() for k in ['크기', '사이즈', '치수', '규격', 'dimension', 'size', 'pin', '핀', 'vcc', 'gnd', 'scl', 'sda', 'txd', 'rxd', 'mm', '전압', '인터페이스']):
            if len(l) < 150 and not any(skip in l for l in ['javascript', 'cookie', 'jquery', 'cart']):
                print('  -', l)
