import re

pcb_file = r'3D modeling/CarrierBoard_BeetleC6_EdgeUSB_50x50_NoText/CarrierBoard_BeetleC6_EdgeUSB_50x50.kicad_pcb'
content = open(pcb_file, encoding='utf-8').read()

# KiCad 8/9/10 format: (footprint "..." ... (at X Y [rot]) ... (fp_text reference "..." ...)
# Let's extract all (footprint blocks
fp_blocks = content.split('(footprint ')
print(f"Total footprint blocks: {len(fp_blocks)-1}")

for block in fp_blocks[1:]:
    name = block.split('\n')[0].strip('" ')
    ref_match = re.search(r'\(property\s+"Reference"\s+"([^"]+)"', block)
    if not ref_match:
        ref_match = re.search(r'\(fp_text\s+reference\s+"([^"]+)"', block)
    ref = ref_match.group(1) if ref_match else "UNKNOWN"
    
    layer_match = re.search(r'\(layer\s+"([^"]+)"\)', block)
    layer = layer_match.group(1) if layer_match else "UNKNOWN"
    
    at_match = re.search(r'\(at\s+([-\d.]+)\s+([-\d.]+)(?:\s+([-\d.]+))?\)', block)
    pos_str = f"({at_match.group(1)}, {at_match.group(2)}, rot={at_match.group(3)})" if at_match else "UNKNOWN"
    
    pads = re.findall(r'\(pad\s+"([^"]+)"', block)
    print(f"Ref: {ref:12s} | Layer: {layer:10s} | Pos: {pos_str:30s} | Pads: {len(pads):2d} ({pads[:3]}...) | Footprint: {name}")
