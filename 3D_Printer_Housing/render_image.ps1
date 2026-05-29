$scadFile = "06_housing_3d_design.scad"
$openscad = "C:\Program Files\OpenSCAD\openscad.com"

Write-Host "Rendering 3D preview images..."

# 1. Render Assembly View (Completed assembly)
Write-Host "Rendering assembly view image..."
(Get-Content $scadFile) -replace 'render_part = "[a-zA-Z_]+";', 'render_part = "assembly";' | Set-Content $scadFile
& $openscad -o "06_assembly_view.png" --render --autocenter --viewall --imgsize=1024,768 --colorscheme="Sunset" $scadFile

# 2. Render Exploded View (Internal mounting details)
Write-Host "Rendering exploded view image..."
(Get-Content $scadFile) -replace 'render_part = "[a-zA-Z_]+";', 'render_part = "exploded";' | Set-Content $scadFile
& $openscad -o "06_exploded_view.png" --render --autocenter --viewall --imgsize=1024,768 --colorscheme="Sunset" $scadFile

# Restore to print_all state
(Get-Content $scadFile) -replace 'render_part = "[a-zA-Z_]+";', 'render_part = "print_all";' | Set-Content $scadFile
Copy-Item -Path $scadFile -Destination "06_하우징_3D_설계_오픈스카드.scad" -Force

Write-Host "Rendering completed successfully!"
