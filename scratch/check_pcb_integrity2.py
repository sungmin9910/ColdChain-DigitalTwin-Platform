import re

pcb_path = r'3D modeling/CarrierBoard_BeetleC6_EdgeUSB_50x50_NoText/CarrierBoard_BeetleC6_EdgeUSB_50x50.kicad_pcb'
with open(pcb_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

curr_fp = None
curr_ref = None

for line in lines:
    if '(footprint ' in line:
        curr_fp = line.strip()
        curr_ref = "Unknown"
    elif 'property "Reference"' in line:
        m = re.search(r'property "Reference" "([^"]+)"', line)
        if m:
            curr_ref = m.group(1)
            print(f"\n--- {curr_ref} ---")
    elif '(pad ' in line:
        m_pad = re.search(r'pad "([^"]+)"\s+(\S+)\s+(\S+)\s+\(at ([-0-9\.]+) ([-0-9\.]+)\)', line)
        m_net = re.search(r'\(net (\d+) "([^"]*)"\)', line)
        if m_pad:
            pnum = m_pad.group(1)
            ptype = m_pad.group(2)
            pshape = m_pad.group(3)
            px = m_pad.group(4)
            py = m_pad.group(5)
            net_info = f"Net {m_net.group(1)}: {m_net.group(2)}" if m_net else "NC"
            print(f"  Pad {pnum:>2} ({ptype} {pshape}) at offset ({px:>6}, {py:>6}) -> {net_info}")
