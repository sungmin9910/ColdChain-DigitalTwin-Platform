$scadFile = "12_qr_scanner_housing_screwless.scad"
$openscad = "C:\Program Files\OpenSCAD\openscad.com"
$brainDir = "C:\Users\korea\.gemini\antigravity-ide\brain\aa972bd4-a6cb-4651-b0b7-8cb735838b17"

Write-Host "Rendering V12.0 Screwless & Pin-Up Handheld Scanner 3D preview images..."

# 1. Render Assembly View (Completed assembly)
Write-Host "Rendering assembly view image (12_assembly_view.png)..."
(Get-Content $scadFile) -replace 'render_part = "[a-zA-Z_]+";', 'render_part = "assembly";' | Set-Content $scadFile
& $openscad -o "12_assembly_view.png" --render --autocenter --viewall --imgsize=1024,768 --colorscheme="Metallic" $scadFile

# 2. Render Exploded View (Internal mounting details)
Write-Host "Rendering exploded view image (12_exploded_view.png)..."
(Get-Content $scadFile) -replace 'render_part = "[a-zA-Z_]+";', 'render_part = "exploded";' | Set-Content $scadFile
& $openscad -o "12_exploded_view.png" --render --autocenter --viewall --imgsize=1024,768 --colorscheme="Metallic" $scadFile

# 3. Render Cross Section View (Internal cut section)
Write-Host "Rendering cross section view image (12_cross_section_view.png)..."
(Get-Content $scadFile) -replace 'render_part = "[a-zA-Z_]+";', 'render_part = "cross_section";' | Set-Content $scadFile
& $openscad -o "12_cross_section_view.png" --render --camera=350,-150,140,29,55,-15 --projection=o --imgsize=1024,768 --colorscheme="Metallic" $scadFile

# Restore to exploded state
(Get-Content $scadFile) -replace 'render_part = "[a-zA-Z_]+";', 'render_part = "exploded";' | Set-Content $scadFile

# Copy images to brain directory for walkthrough markdown
Write-Host "Copying rendered images to brain artifact directory..."
Copy-Item -Path "12_assembly_view.png" -Destination (Join-Path $brainDir "12_assembly_view.png") -Force
Copy-Item -Path "12_exploded_view.png" -Destination (Join-Path $brainDir "12_exploded_view.png") -Force
Copy-Item -Path "12_cross_section_view.png" -Destination (Join-Path $brainDir "12_cross_section_view.png") -Force

Write-Host "V12.0 image rendering and copying completed successfully!"
