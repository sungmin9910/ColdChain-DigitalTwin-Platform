$scadFile = "09_qr_scanner_housing_snapfit.scad"
$openscad = "C:\Program Files\OpenSCAD\openscad.com"

Write-Host "Starting V5.0 Snap-Fit 3D printing STL generation..."

# 1. Body
Write-Host "Rendering 09_housing_body.stl..."
(Get-Content $scadFile) -replace 'render_part = "[a-zA-Z_]+";', 'render_part = "body";' | Set-Content $scadFile
& $openscad -o "09_housing_body.stl" $scadFile

# 2. Handle
Write-Host "Rendering 09_housing_handle.stl..."
(Get-Content $scadFile) -replace 'render_part = "[a-zA-Z_]+";', 'render_part = "handle";' | Set-Content $scadFile
& $openscad -o "09_housing_handle.stl" $scadFile

# 3. Lid
Write-Host "Rendering 09_housing_lid.stl..."
(Get-Content $scadFile) -replace 'render_part = "[a-zA-Z_]+";', 'render_part = "lid";' | Set-Content $scadFile
& $openscad -o "09_housing_lid.stl" $scadFile

# 4. Battery Cap
Write-Host "Rendering 09_housing_battery_cap.stl..."
(Get-Content $scadFile) -replace 'render_part = "[a-zA-Z_]+";', 'render_part = "battery_cap";' | Set-Content $scadFile
& $openscad -o "09_housing_battery_cap.stl" $scadFile

# 5. Print All Layout
Write-Host "Rendering 09_housing_print_all.stl..."
(Get-Content $scadFile) -replace 'render_part = "[a-zA-Z_]+";', 'render_part = "print_all";' | Set-Content $scadFile
& $openscad -o "09_housing_print_all.stl" $scadFile

# Restore to exploded state at the end
(Get-Content $scadFile) -replace 'render_part = "[a-zA-Z_]+";', 'render_part = "exploded";' | Set-Content $scadFile

Write-Host "V5.0 STL exports completed successfully! Check the workspace folder."
