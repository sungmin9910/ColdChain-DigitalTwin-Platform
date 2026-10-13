from PIL import Image

img = Image.open(r'C:\Users\korea\.gemini\antigravity-ide\brain\2c7bae59-1a22-405a-826e-5cc59d1783ae\.user_uploaded\media_1790770311206.jpg')
w, h = img.size

# Beetle crop
beetle = img.crop((int(w*0.32), int(h*0.45), int(w*0.62), int(h*0.75)))
beetle.save(r'C:\Users\korea\.gemini\antigravity-ide\brain\2c7bae59-1a22-405a-826e-5cc59d1783ae\beetle_crop.png')

left_pins = img.crop((int(w*0.35), int(h*0.50), int(w*0.45), int(h*0.66)))
left_pins.save(r'C:\Users\korea\.gemini\antigravity-ide\brain\2c7bae59-1a22-405a-826e-5cc59d1783ae\beetle_left_pins.png')

right_pins = img.crop((int(w*0.52), int(h*0.50), int(w*0.62), int(h*0.66)))
right_pins.save(r'C:\Users\korea\.gemini\antigravity-ide\brain\2c7bae59-1a22-405a-826e-5cc59d1783ae\beetle_right_pins.png')

print("Saved crops with PIL.")
