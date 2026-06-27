import base64
import os

dir_path = r"c:\Users\yuyub\Desktop\hsm\ColdChain-DigitalTwin-Platform\3D_Printer_Housing\v17_QR_Scanner_Housing"
left_stl = os.path.join(dir_path, "17_qr_scanner_housing_left_half.stl")
right_stl = os.path.join(dir_path, "17_qr_scanner_housing_right_half.stl")
html_file = os.path.join(dir_path, "viewer.html")

print("Reading STL files...")
with open(left_stl, "rb") as f:
    left_base64 = base64.b64encode(f.read()).decode("utf-8")

with open(right_stl, "rb") as f:
    right_base64 = base64.b64encode(f.read()).decode("utf-8")

print("Reading HTML file...")
with open(html_file, "r", encoding="utf-8") as f:
    html_content = f.read()

# Remove any existing embedded script to prevent multiple appending
if "const LEFT_HALF_STL_BASE64" in html_content:
    print("Cleaning previous embedded script...")
    parts = html_content.split("<!-- EMBEDDED STL DATA START -->")
    html_content = parts[0]
    # append </html> back if it was split
    if not html_content.strip().endswith("</html>"):
        html_content += "\n</html>"

embedded_script = f"""<!-- EMBEDDED STL DATA START -->
<script>
    const LEFT_HALF_STL_BASE64 = "{left_base64}";
    const RIGHT_HALF_STL_BASE64 = "{right_base64}";
</script>
</html>"""

html_content = html_content.replace("</html>", embedded_script)

print("Writing HTML file back...")
with open(html_file, "w", encoding="utf-8") as f:
    f.write(html_content)

print("Successfully embedded STL files inside HTML!")
