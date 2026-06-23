$scadFile = "$PSScriptRoot\11_qr_scanner_housing_flush_oled.scad"
$openscad = "C:\Program Files\OpenSCAD\openscad.com"

Write-Host "Starting V11.0 Flush OLED Handheld Scanner 3D printing STL generation..."

# 1. Left Half STL
Write-Host "Rendering 11_housing_left.stl..."
(Get-Content $scadFile) -replace 'render_part = "[a-zA-Z_]+";', 'render_part = "left_half";' | Set-Content $scadFile
& $openscad -o "$PSScriptRoot\11_housing_left.stl" $scadFile

# 2. Right Half STL
Write-Host "Rendering 11_housing_right.stl..."
(Get-Content $scadFile) -replace 'render_part = "[a-zA-Z_]+";', 'render_part = "right_half";' | Set-Content $scadFile
& $openscad -o "$PSScriptRoot\11_housing_right.stl" $scadFile

# 3. Trigger Button STL
Write-Host "Rendering 11_trigger_button.stl..."
(Get-Content $scadFile) -replace 'render_part = "[a-zA-Z_]+";', 'render_part = "trigger";' | Set-Content $scadFile
& $openscad -o "$PSScriptRoot\11_trigger_button.stl" $scadFile

# Restore to exploded view state at the end
(Get-Content $scadFile) -replace 'render_part = "[a-zA-Z_]+";', 'render_part = "exploded";' | Set-Content $scadFile

Write-Host "V11.0 STL exports completed successfully! Check the workspace folder."
