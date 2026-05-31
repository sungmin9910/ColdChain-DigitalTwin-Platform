$scadFile = "07_coldchain_sensor_pod.scad"
$openscad = "C:\Program Files\OpenSCAD\openscad.com"

Write-Host "Rendering Cold Chain Sensor Pod 3D preview images..."

# 1. Render Assembly View (Completed assembly)
Write-Host "Rendering assembly view image..."
(Get-Content $scadFile) -replace 'render_part = "[a-zA-Z_]+";', 'render_part = "assembly";' | Set-Content $scadFile
& $openscad -o "07_assembly_view.png" --render --autocenter --viewall --imgsize=1024,768 --colorscheme="Metallic" $scadFile

# 2. Render Exploded View (Internal details)
Write-Host "Rendering exploded view image..."
(Get-Content $scadFile) -replace 'render_part = "[a-zA-Z_]+";', 'render_part = "exploded";' | Set-Content $scadFile
& $openscad -o "07_exploded_view.png" --render --autocenter --viewall --imgsize=1024,768 --colorscheme="Metallic" $scadFile

# 3. Render Cross Section View (Angled split cut)
Write-Host "Rendering cross section view image..."
(Get-Content $scadFile) -replace 'render_part = "[a-zA-Z_]+";', 'render_part = "cross_section";' | Set-Content $scadFile
& $openscad -o "07_cross_section_view.png" --render --camera=200,-30,50,0,0,10 --projection=o --imgsize=1024,768 --colorscheme="Metallic" $scadFile

# Restore to print_all state
(Get-Content $scadFile) -replace 'render_part = "[a-zA-Z_]+";', 'render_part = "assembly";' | Set-Content $scadFile

Write-Host "Sensor pod rendering completed successfully!"
