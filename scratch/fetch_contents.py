import urllib.request
import os
import re
from bs4 import BeautifulSoup

items = {
    'SHT45': 15916726,
    'GY-521': 1247052,
    'BH1750': 1289977,
    'GPS_ATGM336H': 15870885
}

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': 'https://www.devicemart.co.kr/'
}

os.makedirs('scratch/contents', exist_ok=True)
os.makedirs('scratch/images', exist_ok=True)

for name, no in items.items():
    url = f'https://www.devicemart.co.kr/goods/view_contents?no={no}&setMode=pc&zoom=1'
    print(f'Fetching {name} contents: {url}')
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req) as resp:
            content = resp.read().decode('utf-8', errors='ignore')
            with open(f'scratch/contents/{name}.html', 'w', encoding='utf-8') as f:
                f.write(content)
                
            soup = BeautifulSoup(content, 'html.parser')
            imgs = []
            for img in soup.find_all('img'):
                src = img.get('src')
                if src:
                    imgs.append(src)
            print(f'  {name} images count: {len(imgs)}')
            for i, img_url in enumerate(imgs):
                if not img_url.startswith('http'):
                    img_url = 'https://www.devicemart.co.kr' + img_url
                print(f'    [{i}] {img_url}')
                ext = os.path.splitext(img_url.split('?')[0])[1] or '.jpg'
                local_path = f'scratch/images/{name}_{i}{ext}'
                try:
                    r = urllib.request.Request(img_url, headers=headers)
                    with urllib.request.urlopen(r) as r_img, open(local_path, 'wb') as f_img:
                        f_img.write(r_img.read())
                    print(f'         Saved: {local_path} ({os.path.getsize(local_path)} bytes)')
                except Exception as e:
                    print(f'         Failed: {e}')
                    
            text = soup.get_text('\n', strip=True)
            print('  Text excerpt:')
            for line in text.split('\n')[:25]:
                if line.strip():
                    print('    ', line.strip())
    except Exception as e:
        print(f'Error fetching {name}: {e}')
