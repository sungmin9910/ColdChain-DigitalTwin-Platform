import json

data = json.load(open('scratch/test_new_pinout_report.json', encoding='utf-8'))
errors = [v for v in data.get('violations', []) if v.get('severity') == 'error']
print(f"Total Critical Errors: {len(errors)}")
for i, v in enumerate(errors):
    print(f"{i+1}. [{v.get('type')}]: {v.get('description')}")
    for item in v.get('items', []):
        desc = item.get('description', '')
        pos = item.get('pos', {})
        print(f"    - {desc} at ({pos.get('x')}, {pos.get('y')})")
