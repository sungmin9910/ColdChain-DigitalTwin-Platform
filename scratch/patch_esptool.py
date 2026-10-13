path = r"C:\Users\korea\.platformio\packages\tool-esptoolpy\esptool\loader.py"
with open(path, "r", encoding="utf-8") as f:
    c = f.read()

target = 'cfg.getfloat("timeout", 3)'
replacement = 'cfg.getfloat("timeout", 30)'

if target in c:
    c = c.replace(target, replacement)
    with open(path, "w", encoding="utf-8") as f:
        f.write(c)
    print("SUCCESS: DEFAULT_TIMEOUT is now 30 seconds!")
else:
    print("Already patched or pattern not found.")
