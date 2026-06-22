# build_stl_v15.ps1 - Build STL files for V15 QR Scanner Housing
# Usage: .\build_stl_v15.ps1

$scadFile = "$PSScriptRoot\15_qr_scanner_housing.scad"
$openscad = "C:\Program Files\OpenSCAD\openscad.com"

Write-Host "Starting V15.0 Scanner Housing STL generation..."

# 1. Left Half STL
Write-Host "Rendering 15_housing_left.stl..."
(Get-Content $scadFile) -replace 'render_part = "[a-zA-Z_]+";', 'render_part = "left_half";' | Set-Content $scadFile
& $openscad -o "$PSScriptRoot\15_housing_left.stl" $scadFile

# 2. Right Half STL
Write-Host "Rendering 15_housing_right.stl..."
(Get-Content $scadFile) -replace 'render_part = "[a-zA-Z_]+";', 'render_part = "right_half";' | Set-Content $scadFile
& $openscad -o "$PSScriptRoot\15_housing_right.stl" $scadFile

# 3. Trigger Button STL
Write-Host "Rendering 15_trigger.stl..."
(Get-Content $scadFile) -replace 'render_part = "[a-zA-Z_]+";', 'render_part = "trigger";' | Set-Content $scadFile
& $openscad -o "$PSScriptRoot\15_trigger.stl" $scadFile

# Restore to exploded view
(Get-Content $scadFile) -replace 'render_part = "[a-zA-Z_]+";', 'render_part = "exploded";' | Set-Content $scadFile

Write-Host "V15.0 STL exports completed!" -ForegroundColor Green
