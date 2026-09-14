import sys

for name in ['SHT45', 'GY-521', 'BH1750', 'GPS_ATGM336H']:
    path = f'scratch/contents/{name}_text.txt'
    with open(path, 'r', encoding='utf-8') as f:
        print(f'************************************')
        print(f'*** {name} ***')
        print(f'************************************')
        print(f.read())
