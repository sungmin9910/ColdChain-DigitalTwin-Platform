import re

pcb_path = r'3D modeling/CarrierBoard_BeetleC6_EdgeUSB_50x50_NoText/CarrierBoard_BeetleC6_EdgeUSB_50x50.kicad_pcb'
with open(pcb_path, 'r', encoding='utf-8') as f:
    content = f.read()

nets = dict(re.findall(r'\(net (\d+) "([^"]*)"\)', content))
print("=== DEFINED NETS ===")
for k, v in nets.items():
    print(f"Net {k}: {v}")

print("\n=== FOOTPRINTS & PINS ===")
# split footprints
fp_blocks = content.split('(footprint ')
for b in fp_blocks[1:]:
    # get fp type
    m_name = re.match(r'"([^"]+)"', b)
    fp_type = m_name.group(1) if m_name else "Unknown"
    
    # reference
    m_ref = re.search(r'\(property "Reference" "([^"]+)"', b)
    ref = m_ref.group(1) if m_ref else "NoRef"
    
    # position
    m_at = re.search(r'\(at ([-0-9\.]+) ([-0-9\.]+)\)', b)
    pos = m_at.groups() if m_at else ("?", "?")
    
    m_layer = re.search(r'\(layer "([^"]+)"\)', b)
    layer = m_layer.group(1) if m_layer else "?"
    
    print(f"\n[{ref}] Type: {fp_type} | Position: {pos} | Layer: {layer}")
    
    # pads
    pads = re.findall(r'\(pad "([^"]+)"[^\(\)]*(?:\([^\(\)]*\)[^\(\)]*)*\(net (\d+) "([^"]*)"\)', b)
    for p in re.finditer(r'\(pad "([^"]+)"\s+(\S+)\s+(\S+)\s+\(at ([-0-9\.]+) ([-0-9\.]+)\)(.*?)\)', b):
        pad_num = p.group(1)
        pad_type = p.group(2)
        pad_shape = p.group(3)
        px = p.group(4)
        py = p.group(5)
        rest = p.group(6)
        m_net = re.search(r'\(net (\d+) "([^"]*)"\)', rest)
        net_str = f"Net {m_net.group(1)} ({m_net.group(2)})" if m_net else "NO NET (NC)"
        print(f"  Pad {pad_num:>2} @ ({px:>6}, {py:>6}): {net_str}")

print("\n=== SEGMENTS & VIAS COUNT ===")
segments = re.findall(r'\(segment.*?\)', content)
vias = re.findall(r'\(via.*?\)', content)
print(f"Total Segments: {len(segments)}")
print(f"Total Vias: {len(vias)}")
