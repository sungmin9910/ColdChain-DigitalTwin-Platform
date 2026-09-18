import os
import subprocess
import json

KICAD_CLI = r"C:\Program Files\KiCad\10.0\bin\kicad-cli.exe"
TARGET_DIR = r"c:\Users\korea\Desktop\1hsm\hanhanhan\ColdChain-DigitalTwin-Platform\3D modeling\CarrierBoard_BeetleC6_EdgeUSB_50x50_NoText"
TEST_PCB = os.path.join(TARGET_DIR, "CarrierBoard_BeetleC6_EdgeUSB_50x50.kicad_pcb")

print("Checking current status...")
res = subprocess.run([KICAD_CLI, "pcb", "drc", "--output", "drc_test.json", TEST_PCB], capture_output=True, text=True)
print(res.stdout)
