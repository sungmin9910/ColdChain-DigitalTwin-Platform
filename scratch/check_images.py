import os
from PIL import Image

image_dir = 'scratch/images'
for f in sorted(os.listdir(image_dir)):
    p = os.path.join(image_dir, f)
    if os.path.isfile(p):
        try:
            im = Image.open(p)
            print(f'{f}: format={im.format}, size={im.size}, mode={im.mode}')
        except Exception as e:
            print(f'{f}: error {e}')
