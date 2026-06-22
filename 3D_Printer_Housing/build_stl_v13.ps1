$scadFile = "13_qr_scanner_housing_slide_fit.scad"
$openscad = "C:\Program Files\OpenSCAD\openscad.com"

Write-Host "Starting V13.0 Slide-Fit Handheld Scanner 3D printing STL generation..."

# 1. Left Half STL
Write-Host "Rendering 13_housing_left.stl..."
(Get-Content $scadFile) -replace 'render_part = "[a-zA-Z_]+";', 'render_part = "left_half";' | Set-Content $scadFile
& $openscad -o "13_housing_left.stl" $scadFile

# 2. Right Half STL
Write-Host "Rendering 13_housing_right.stl..."
(Get-Content $scadFile) -replace 'render_part = "[a-zA-Z_]+";', 'render_part = "right_half";' | Set-Content $scadFile
& $openscad -o "13_housing_right.stl" $scadFile

# 3. Trigger Button STL
Write-Host "Rendering 13_trigger_button.stl..."
(Get-Content $scadFile) -replace 'render_part = "[a-zA-Z_]+";', 'render_part = "trigger";' | Set-Content $scadFile
& $openscad -o "13_trigger_button.stl" $scadFile

# Restore to exploded view state at the end
(Get-Content $scadFile) -replace 'render_part = "[a-zA-Z_]+";', 'render_part = "exploded";' | Set-Content $scadFile

Write-Host "V13.0 STL exports completed successfully! Check the workspace folder."
