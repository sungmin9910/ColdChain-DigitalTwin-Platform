import glob
import os

def parse_ascii_stl_bounds(filepath):
    min_x = min_y = min_z = float('inf')
    max_x = max_y = max_z = float('-inf')
    triangles = 0
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            line = line.strip()
            if line.startswith('vertex'):
                parts = line.split()
                if len(parts) >= 4:
                    x, y, z = float(parts[1]), float(parts[2]), float(parts[3])
                    min_x = min(min_x, x)
                    max_x = max(max_x, x)
                    min_y = min(min_y, y)
                    max_y = max(max_y, y)
                    min_z = min(min_z, z)
                    max_z = max(max_z, z)
            elif line.startswith('endfacet'):
                triangles += 1
    return {
        'file': os.path.basename(filepath),
        'triangles': triangles,
        'min': (round(min_x, 2), round(min_y, 2), round(min_z, 2)),
        'max': (round(max_x, 2), round(max_y, 2), round(max_z, 2)),
        'size': (round(max_x - min_x, 2), round(max_y - min_y, 2), round(max_z - min_z, 2))
    }

if __name__ == '__main__':
    stls = glob.glob(r"3D_Printer_Housing\v20_Apple_Sensor_Pod_Modular5000mAh\*.stl")
    for s in stls:
        b = parse_ascii_stl_bounds(s)
        print(f"\n[{b['file']}] ({b['triangles']} triangles)")
        print(f"  Min: {b['min']}")
        print(f"  Max: {b['max']}")
        print(f"  Size: {b['size']} mm")
