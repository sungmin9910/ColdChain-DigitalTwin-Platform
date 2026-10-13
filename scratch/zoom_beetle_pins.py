from PIL import Image

img_path = r'C:\Users\korea\.gemini\antigravity-ide\brain\2c7bae59-1a22-405a-826e-5cc59d1783ae\beetle_left_pins.png'
img = Image.open(img_path)
print("Image size:", img.size)

# Let's rotate or zoom to read each text label next to the pins clearly
# The image is 114x246
# Let's upscale it with LANCZOS to 4x size and increase contrast
img_large = img.resize((img.width * 4, img.height * 4), Image.Resampling.LANCZOS)
img_large.save(r'C:\Users\korea\.gemini\antigravity-ide\brain\2c7bae59-1a22-405a-826e-5cc59d1783ae\beetle_left_pins_large.png')
print("Saved large image")
