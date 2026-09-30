import re

pcb_file = r'3D modeling/CarrierBoard_BeetleC6_EdgeUSB_50x50_NoText/CarrierBoard_BeetleC6_EdgeUSB_50x50.kicad_pcb'
with open(pcb_file, 'r', encoding='utf-8') as f:
    text = f.read()

# Split by (footprint
parts = text.split('(footprint ')
for part in parts[1:]:
    lines = part.splitlines()
    fp_name = lines[0].strip().strip('"')
    ref = "?"
    val = "?"
    layer = "?"
    pos = "?"
    
    m_ref = re.search(r'\(property\s+"Reference"\s+"([^"]+)"', part)
    if m_ref: ref = m_ref.group(1)
    
    m_val = re.search(r'\(property\s+"Value"\s+"([^"]+)"', part)
    if m_val: val = m_val.group(1)
    
    m_layer = re.search(r'\(layer\s+"([^"]+)"\)', part)
    if m_layer: layer = m_layer.group(1)
    
    m_at = re.search(r'\(at\s+([-\d.]+)\s+([-\d.]+)(?:\s+([-\d.]+))?\)', part)
    if m_at: pos = m_at.groups()
    
    print(f"\n=== Ref: {ref} | Val: {val} | Layer: {layer} | Pos: {pos} ===")
    print(f"    Footprint: {fp_name}")
    
    pads = re.findall(r'\(pad\s+"([^"]+)"\s+(\S+)\s+(\S+)\s+\(at\s+([-\d.]+)\s+([-\d.]+)(?:\s+([-\d.]+))?\)(?:.*?\(size\s+([-\d.]+)\s+([-\d.]+)\))?(?:.*?\(drill\s+([-\d.]+)\))?(?:.*?\(net\s+(\d+)\s+"([^"]*)")?', part)
    for p in pads:
        p_num, p_type, p_shape, p_x, p_y, p_rot, p_sx, p_sy, p_drill, p_net_id, p_net_name = p
        print(f"    Pad {p_num:>2}: type={p_type} shape={p_shape} rel=({p_x},{p_y}) drill={p_drill} size=({p_sx},{p_sy}) net={p_net_name}")


