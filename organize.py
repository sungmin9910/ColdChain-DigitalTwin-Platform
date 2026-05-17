import shutil
import os

base_dir = "."
dest_parent = "Hardware_Prototypes"

folders_to_move = [
    "coldchain_module",
    "coldchain_module_gy25",
    "coldchain_module_gy521",
    "qr_scanner_module",
    "code26",
    "coldchain_dashboard"
]

print("Starting file organization...")
for folder in folders_to_move:
    src_path = os.path.join(base_dir, folder)
    dest_path = os.path.join(dest_parent, folder)
    
    if os.path.exists(src_path):
        try:
            print(f"Moving {src_path} -> {dest_path}")
            shutil.move(src_path, dest_path)
            print(f"Successfully moved {folder}")
        except Exception as e:
            print(f"Error moving {folder}: {e}")
    else:
        print(f"Folder not found, skipping: {src_path}")

print("Organization complete!")
