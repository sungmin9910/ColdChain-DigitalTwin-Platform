$scadFile = "$PSScriptRoot\09_qr_scanner_housing_snapfit.scad"
$openscad = "C:\Program Files\OpenSCAD\openscad.com"

Write-Host "Rendering V5.0 Split-Half 3D preview images..."

# 1. Render Assembly View (Completed assembly)
Write-Host "Rendering assembly view image..."
(Get-Content $scadFile) -replace 'render_part = "[a-zA-Z_]+";', 'render_part = "assembly";' | Set-Content $scadFile
& $openscad -o "$PSScriptRoot\09_assembly_view.png" --render --autocenter --viewall --imgsize=1024,768 --colorscheme="Metallic" $scadFile

# 2. Render Exploded View (Internal mounting details)
Write-Host "Rendering exploded view image..."
(Get-Content $scadFile) -replace 'render_part = "[a-zA-Z_]+";', 'render_part = "exploded";' | Set-Content $scadFile
& $openscad -o "$PSScriptRoot\09_exploded_view.png" --render --autocenter --viewall --imgsize=1024,768 --colorscheme="Metallic" $scadFile

# 3. Render Cross Section View (Internal cut section)
Write-Host "Rendering cross section view image..."
(Get-Content $scadFile) -replace 'render_part = "[a-zA-Z_]+";', 'render_part = "cross_section";' | Set-Content $scadFile
& $openscad -o "$PSScriptRoot\09_cross_section_view.png" --render --camera=367,-133,156,24,56,-20 --projection=o --imgsize=1024,768 --colorscheme="Metallic" $scadFile

# Restore to exploded state
(Get-Content $scadFile) -replace 'render_part = "[a-zA-Z_]+";', 'render_part = "exploded";' | Set-Content $scadFile

Write-Host "V5.0 image rendering completed successfully!"
