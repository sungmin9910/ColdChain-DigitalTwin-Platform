$scadFile = "$PSScriptRoot\09_qr_scanner_housing_snapfit.scad"
$openscad = "C:\Program Files\OpenSCAD\openscad.com"

Write-Host "Starting V5.0 Split-Half 3D printing STL generation..."

# 1. Left Half
Write-Host "Rendering 09_housing_left.stl..."
(Get-Content $scadFile) -replace 'render_part = "[a-zA-Z_]+";', 'render_part = "left_half";' | Set-Content $scadFile
& $openscad -o "$PSScriptRoot\09_housing_left.stl" $scadFile

# 2. Right Half
Write-Host "Rendering 09_housing_right.stl..."
(Get-Content $scadFile) -replace 'render_part = "[a-zA-Z_]+";', 'render_part = "right_half";' | Set-Content $scadFile
& $openscad -o "$PSScriptRoot\09_housing_right.stl" $scadFile

# 3. Trigger Button
Write-Host "Rendering 09_trigger_button.stl..."
(Get-Content $scadFile) -replace 'render_part = "[a-zA-Z_]+";', 'render_part = "trigger";' | Set-Content $scadFile
& $openscad -o "$PSScriptRoot\09_trigger_button.stl" $scadFile

# 4. Print All Layout
Write-Host "Rendering 09_housing_print_all.stl..."
(Get-Content $scadFile) -replace 'render_part = "[a-zA-Z_]+";', 'render_part = "print_all";' | Set-Content $scadFile
& $openscad -o "$PSScriptRoot\09_housing_print_all.stl" $scadFile

# Restore to exploded state at the end
(Get-Content $scadFile) -replace 'render_part = "[a-zA-Z_]+";', 'render_part = "exploded";' | Set-Content $scadFile

Write-Host "V5.0 STL exports completed successfully! Check the workspace folder."

