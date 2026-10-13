from PIL import Image

img_path = r'C:\Users\korea\.gemini\antigravity-ide\brain\2c7bae59-1a22-405a-826e-5cc59d1783ae\.user_uploaded\media_1790770307774.jpg'
img = Image.open(img_path)
w, h = img.size

# GPS module is around middle-left
# In the image, hand is on the left, board is centered
# Let's crop x: 0.25 to 0.45, y: 0.45 to 0.65
crop_box = (int(w * 0.25), int(h * 0.45), int(w * 0.45), int(h * 0.62))
cropped = img.crop(crop_box)
cropped.save(r'C:\Users\korea\.gemini\antigravity-ide\brain\2c7bae59-1a22-405a-826e-5cc59d1783ae\gps_crop.png')
print("Cropped successfully, size:", cropped.size)
