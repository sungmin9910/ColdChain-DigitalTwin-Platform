import urllib.request
import re
import html
import os

urls = {
    'SHT45': 'https://www.devicemart.co.kr/goods/view?no=15916726',
    'GY-521': 'https://www.devicemart.co.kr/goods/view?no=1247052',
    'BH1750': 'https://www.devicemart.co.kr/goods/view?no=1289977',
    'GPS_ATGM336H': 'https://www.devicemart.co.kr/goods/view?no=15870885'
}

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

for name, url in urls.items():
    print(f'==============================\nFetching {name}: {url}\n==============================')
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req) as resp:
            content = resp.read().decode('utf-8', errors='ignore')
            
            # Save raw html
            out_file = f'scratch/{name}.html'
            os.makedirs('scratch', exist_ok=True)
            with open(out_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Extract title, og:title, og:image
            title_m = re.search(r'<title>(.*?)</title>', content, re.I)
            og_img = re.search(r'<meta property="og:image" content="(.*?)"', content, re.I)
            print('Title:', title_m.group(1) if title_m else 'None')
            print('OG Image:', og_img.group(1) if og_img else 'None')
            
            # Find detail images
            detail_imgs = re.findall(r'<img[^>]+src=[\'"]([^\'"]+)[\'"]', content, re.I)
            goods_imgs = [img for img in detail_imgs if any(k in img for k in ['goods', 'upload', 'editor', 'data'])]
            print('Key Images:')
            for g in goods_imgs[:5]:
                print('  ', g)
                
            # Search for spec keywords
            # strip html tags for text
            text = re.sub(r'<[^>]+>', ' ', content)
            text = re.sub(r'\s+', ' ', text)
            
            # find snippets with mm, pin, 크기, 사이즈
            snippets = re.findall(r'(.{0,40}(?:크기|사이즈|치수|외형|규격|핀|pin|PIN|VCC|GND|SCL|SDA|TXD|RXD|\d+(?:\.\d+)?\s*(?:mm|MM)).{0,40})', text)
            print(f'Relevant snippets ({len(snippets)}):')
            seen = set()
            for s in snippets:
                clean_s = s.strip()
                if clean_s not in seen and len(clean_s) > 10:
                    seen.add(clean_s)
                    if any(k in clean_s for k in ['크기', '사이즈', '치수', 'mm', 'MM', 'x', 'X', '*']):
                        print('   *', clean_s)
                        if len(seen) > 15:
                            break
    except Exception as e:
        print(f'Error fetching {name}: {e}')
