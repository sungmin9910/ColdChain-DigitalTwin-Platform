import os
import re
import subprocess
import json

KICAD_CLI = r"C:\Program Files\KiCad\10.0\bin\kicad-cli.exe"
SRC_PCB = r"c:\Users\korea\Desktop\1hsm\hanhanhan\ColdChain-DigitalTwin-Platform\scratch\perfect_drc.kicad_pcb"
DEST_PCB = r"c:\Users\korea\Desktop\1hsm\hanhanhan\ColdChain-DigitalTwin-Platform\scratch\optimized_drc.kicad_pcb"
REPORT_JSON = r"c:\Users\korea\Desktop\1hsm\hanhanhan\ColdChain-DigitalTwin-Platform\scratch\optimized_drc_report.json"

with open(SRC_PCB, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Hide all Reference and Value properties and set font size to 0.8mm to prevent text_height warnings
def fix_property(match):
    prop_type = match.group(1)
    val = match.group(2)
    at = match.group(3)
    layer = match.group(4)
    return f'(property "{prop_type}" "{val}" {at} (layer "{layer}") (effects (font (size 0.8 0.8) (thickness 0.12)) hide))'

content = re.sub(
    r'\(property\s+"(Reference|Value)"\s+"([^"]*)"\s+(\(at\s+[^)]+\))\s+\(layer\s+"([^"]+)"\)\s+\(effects\s+\(font\s+\(size\s+[^)]+\)\s+\(thickness\s+[^)]+\)\)[^)]*\)\)',
    fix_property,
    content
)

# 2. Remove any silkscreen lines that clip over SMD pads (specifically R3 and R4 outline boxes: 120.8 to 123.2, 126.8 to 129.2)
lines = content.splitlines()
filtered_lines = []
for line in lines:
    if any(coord in line for coord in ["120.8 141.0", "123.2 141.0", "123.2 143.0", "120.8 143.0",
                                      "126.8 141.0", "129.2 141.0", "129.2 143.0", "126.8 143.0"]):
        continue
    if any(coord in line for coord in ["112.5 144.5", "119.5 144.5", "119.5 148.5", "112.5 148.5"]):
        continue
    filtered_lines.append(line)

content = "\n".join(filtered_lines)

with open(DEST_PCB, "w", encoding="utf-8") as f:
    f.write(content)

print(f"Running KiCad DRC on {DEST_PCB}...")
res = subprocess.run([KICAD_CLI, "pcb", "drc", "--output", REPORT_JSON, "--format", "json", DEST_PCB], capture_output=True, text=True)
print("Return code:", res.returncode)

with open(REPORT_JSON, "r", encoding="utf-8") as f:
    data = json.load(f)

violations = data.get("violations", [])
unconnected = data.get("unconnected_items", [])
print(f"Violations count: {len(violations)}")
print(f"Unconnected items count: {len(unconnected)}")
types = {}
for v in violations:
    types[v["type"]] = types.get(v["type"], 0) + 1
for t, count in types.items():
    print(f"  {t}: {count}")
