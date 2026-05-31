$scadFile = "06_scanner_desktop_stand.scad"
$openscad = "C:\Program Files\OpenSCAD\openscad.com"

Write-Host "Rendering Scanner Desktop Stand 3D preview images..."

# 1. Render Assembly View (Stand with docked scanner dummy)
Write-Host "Rendering assembly view image..."
(Get-Content $scadFile) -replace 'render_part = "[a-zA-Z_]+";', 'render_part = "assembly";' | Set-Content $scadFile
& $openscad -o "06_stand_assembly_view.png" --render --camera=220,-140,110,0,20,45 --projection=o --imgsize=1024,768 --colorscheme="Metallic" $scadFile

# 2. Render Print View (Standalone printable stand)
Write-Host "Rendering print layout view image..."
(Get-Content $scadFile) -replace 'render_part = "[a-zA-Z_]+";', 'render_part = "print";' | Set-Content $scadFile
& $openscad -o "06_stand_print_view.png" --render --camera=220,-140,110,0,20,45 --projection=o --imgsize=1024,768 --colorscheme="Metallic" $scadFile

# 3. Render Cross Section View (Sectional cut)
Write-Host "Rendering cross section view image..."
(Get-Content $scadFile) -replace 'render_part = "[a-zA-Z_]+";', 'render_part = "cross_section";' | Set-Content $scadFile
& $openscad -o "06_stand_cross_section_view.png" --render --camera=220,20,45,0,20,45 --projection=o --imgsize=1024,768 --colorscheme="Metallic" $scadFile

# Restore to assembly state at the end
(Get-Content $scadFile) -replace 'render_part = "[a-zA-Z_]+";', 'render_part = "assembly";' | Set-Content $scadFile

Write-Host "Desktop stand rendering completed successfully!"
