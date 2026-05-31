$scadFile = "06_housing_3d_design.scad"
$openscad = "C:\Program Files\OpenSCAD\openscad.com"

Write-Host "Starting FDM 3D printing STL generation..."

# 1. Body
Write-Host "Rendering 06_housing_body.stl..."
(Get-Content $scadFile) -replace 'render_part = "[a-zA-Z_]+";', 'render_part = "body";' | Set-Content $scadFile
& $openscad -o "06_housing_body.stl" $scadFile

# 2. Handle
Write-Host "Rendering 06_housing_handle.stl..."
(Get-Content $scadFile) -replace 'render_part = "[a-zA-Z_]+";', 'render_part = "handle";' | Set-Content $scadFile
& $openscad -o "06_housing_handle.stl" $scadFile

# 3. Lid
Write-Host "Rendering 06_housing_lid.stl..."
(Get-Content $scadFile) -replace 'render_part = "[a-zA-Z_]+";', 'render_part = "lid";' | Set-Content $scadFile
& $openscad -o "06_housing_lid.stl" $scadFile

# 4. Print All Layout
Write-Host "Rendering 06_housing_print_all.stl..."
(Get-Content $scadFile) -replace 'render_part = "[a-zA-Z_]+";', 'render_part = "print_all";' | Set-Content $scadFile
& $openscad -o "06_housing_print_all.stl" $scadFile

# Restore to print_all state at the end
(Get-Content $scadFile) -replace 'render_part = "[a-zA-Z_]+";', 'render_part = "print_all";' | Set-Content $scadFile

# Safe copy of the file via cmd shell to handle Korean encoding issues
cmd /c "copy /y 06_housing_3d_design.scad 06_하우징_3D_설계_오픈스카드.scad"

Write-Host "All STL exports completed successfully! Check the workspace folder."
