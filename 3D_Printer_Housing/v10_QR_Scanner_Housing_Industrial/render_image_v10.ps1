$scadFile = "$PSScriptRoot\10_qr_scanner_housing_industrial.scad"
$openscad = "C:\Program Files\OpenSCAD\openscad.com"

Write-Host "Rendering V10.0 Industrial Handheld Scanner 3D preview images..."

# 1. Render Assembly View (Completed assembly)
Write-Host "Rendering assembly view image (10_assembly_view.png)..."
(Get-Content $scadFile) -replace 'render_part = "[a-zA-Z_]+";', 'render_part = "assembly";' | Set-Content $scadFile
& $openscad -o "$PSScriptRoot\10_assembly_view.png" --render --autocenter --viewall --imgsize=1024,768 --colorscheme="Metallic" $scadFile

# 2. Render Exploded View (Internal mounting details)
Write-Host "Rendering exploded view image (10_exploded_view.png)..."
(Get-Content $scadFile) -replace 'render_part = "[a-zA-Z_]+";', 'render_part = "exploded";' | Set-Content $scadFile
& $openscad -o "$PSScriptRoot\10_exploded_view.png" --render --autocenter --viewall --imgsize=1024,768 --colorscheme="Metallic" $scadFile

# 3. Render Cross Section View (Internal cut section)
Write-Host "Rendering cross section view image (10_cross_section_view.png)..."
(Get-Content $scadFile) -replace 'render_part = "[a-zA-Z_]+";', 'render_part = "cross_section";' | Set-Content $scadFile
# Adjust camera to cut plane view to clearly see interior fitting and clearances
& $openscad -o "$PSScriptRoot\10_cross_section_view.png" --render --camera=350,-150,140,29,55,-15 --projection=o --imgsize=1024,768 --colorscheme="Metallic" $scadFile

# Restore to exploded state
(Get-Content $scadFile) -replace 'render_part = "[a-zA-Z_]+";', 'render_part = "exploded";' | Set-Content $scadFile

Write-Host "V10.0 image rendering completed successfully!"
