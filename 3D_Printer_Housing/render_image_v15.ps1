# render_image_v15.ps1 - Render preview images for V15 QR Scanner Housing
# Usage: .\render_image_v15.ps1

$openscad = "C:\Program Files\OpenSCAD\openscad.com"
$scadFile = "$PSScriptRoot\15_qr_scanner_housing.scad"
$outDir   = $PSScriptRoot

$views = @(
    @{ Name = "assembly";      File = "15_assembly_view.png";      Camera = "29,65,25,55,0,25,350" },
    @{ Name = "exploded";      File = "15_exploded_view.png";      Camera = "29,65,25,55,0,25,500" },
    @{ Name = "cross_section"; File = "15_cross_section_view.png"; Camera = "29,65,25,55,0,25,400" }
)

foreach ($v in $views) {
    $outPath = Join-Path $outDir $v.File
    Write-Host "`n>>> Rendering $($v.Name) -> $($v.File) ..." -ForegroundColor Cyan
    & $openscad -o $outPath `
        -D "render_part=`"$($v.Name)`"" `
        --camera $v.Camera `
        --imgsize 1920,1080 `
        --colorscheme "Tomorrow Night" `
        $scadFile
    if ($LASTEXITCODE -eq 0) {
        Write-Host "    OK" -ForegroundColor Green
    } else {
        Write-Host "    FAILED (exit code $LASTEXITCODE)" -ForegroundColor Red
    }
}

Write-Host "`n=== Render complete ===" -ForegroundColor Yellow
