$openscad = "C:\Program Files\OpenSCAD\openscad.com"
$scadFile = "09_qr_scanner_housing_snapfit_v2.scad"

Write-Host "Exporting STL files using file substitution..."

# 1. Left Half
Write-Host "1. Exporting Left Half STL..."
(Get-Content $scadFile) -replace 'render_part = "[a-zA-Z_]+";', 'render_part = "left_half";' | Set-Content $scadFile
& $openscad -o "09_left_half_v2.stl" $scadFile

# 2. Right Half
Write-Host "2. Exporting Right Half STL..."
(Get-Content $scadFile) -replace 'render_part = "[a-zA-Z_]+";', 'render_part = "right_half";' | Set-Content $scadFile
& $openscad -o "09_right_half_v2.stl" $scadFile

# 3. Trigger
Write-Host "3. Exporting Trigger STL..."
(Get-Content $scadFile) -replace 'render_part = "[a-zA-Z_]+";', 'render_part = "trigger";' | Set-Content $scadFile
& $openscad -o "09_trigger_v2.stl" $scadFile

# 4. Plug
Write-Host "4. Exporting Plug STL..."
(Get-Content $scadFile) -replace 'render_part = "[a-zA-Z_]+";', 'render_part = "plug";' | Set-Content $scadFile
& $openscad -o "09_plug_v2.stl" $scadFile

# 5. Print All
Write-Host "5. Exporting Print All STL (Integrated)..."
(Get-Content $scadFile) -replace 'render_part = "[a-zA-Z_]+";', 'render_part = "print_all";' | Set-Content $scadFile
& $openscad -o "09_print_all_v2.stl" $scadFile

# Restore to exploded state
(Get-Content $scadFile) -replace 'render_part = "[a-zA-Z_]+";', 'render_part = "exploded";' | Set-Content $scadFile

Write-Host "STL Export completed successfully!"
