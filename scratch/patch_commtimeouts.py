path = r"C:\Users\korea\.platformio\packages\tool-esptoolpy\esptool\loader.py"
with open(path, "r", encoding="utf-8") as f:
    c = f.read()

# 1. Set fixed 30.0s port timeout at initialization
target_init = "self._set_port_baudrate(baud)"
replace_init = "self._set_port_baudrate(baud)\n        self._port.timeout = 30.0"

if target_init in c and "self._port.timeout = 30.0" not in c:
    c = c.replace(target_init, replace_init, 1)

# 2. Disable frequent SetCommTimeouts calls inside command()
target_cmd = """        saved_timeout = self._port.timeout
        new_timeout = min(timeout, MAX_TIMEOUT)
        if new_timeout != saved_timeout:
            self._port.timeout = new_timeout"""

replace_cmd = """        # Disabled repeated SetCommTimeouts for CH340 stability
        saved_timeout = 30.0
        new_timeout = 30.0"""

if target_cmd in c:
    c = c.replace(target_cmd, replace_cmd)

# 3. Disable restore in finally
target_finally = """        finally:
            if new_timeout != saved_timeout:
                self._port.timeout = saved_timeout"""

replace_finally = """        finally:
            pass"""

if target_finally in c:
    c = c.replace(target_finally, replace_finally)

with open(path, "w", encoding="utf-8") as f:
    f.write(c)

print("SUCCESS: CommTimeouts jitter patched for CH340!")
