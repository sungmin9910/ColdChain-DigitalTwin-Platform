$scadFile = "06_housing_3d_design.scad"
$openscad = "C:\Program Files\OpenSCAD\openscad.com"

Write-Host "Rendering 3D preview images..."

# 1. Render Assembly View (Completed assembly)
Write-Host "Rendering assembly view image..."
(Get-Content $scadFile) -replace 'render_part = "[a-zA-Z_]+";', 'render_part = "assembly";' | Set-Content $scadFile
& $openscad -o "06_assembly_view.png" --render --autocenter --viewall --imgsize=1024,768 --colorscheme="Metallic" $scadFile

# 2. Render Exploded View (Internal mounting details)
Write-Host "Rendering exploded view image..."
(Get-Content $scadFile) -replace 'render_part = "[a-zA-Z_]+";', 'render_part = "exploded";' | Set-Content $scadFile
& $openscad -o "06_exploded_view.png" --render --autocenter --viewall --imgsize=1024,768 --colorscheme="Metallic" $scadFile

# 3. Render Cross Section View (Internal cut section)
Write-Host "Rendering cross section view image..."
(Get-Content $scadFile) -replace 'render_part = "[a-zA-Z_]+";', 'render_part = "cross_section";' | Set-Content $scadFile
& $openscad -o "06_cross_section_view.png" --render --camera=367,-133,156,24,56,-20 --projection=o --imgsize=1024,768 --colorscheme="Metallic" $scadFile

# Restore to print_all state
(Get-Content $scadFile) -replace 'render_part = "[a-zA-Z_]+";', 'render_part = "print_all";' | Set-Content $scadFile

# Safe copy of the file via cmd shell to handle Korean encoding issues
cmd /c "copy /y 06_housing_3d_design.scad 06_하우징_3D_설계_오픈스카드.scad"

Write-Host "Rendering completed successfully!"
