# render_apple_pod.ps1 - Render 3D preview images and export STL files for v18 Apple Sensor Pod
# Usage: .\render_apple_pod.ps1

$openscad = "C:\Program Files\OpenSCAD\openscad.com"
$scadFile = "$PSScriptRoot\18_apple_sensor_pod.scad"
$brainDir = "C:\Users\yuyu6\.gemini\antigravity-ide\brain\3dd8f0ac-baaa-4698-8646-5148815648d5"

Write-Host "=========================================================" -ForegroundColor Cyan
Write-Host "  v18 Apple Sensor Pod Housing - 3D Generator & Exporter  " -ForegroundColor Cyan
Write-Host "=========================================================" -ForegroundColor Cyan

# 1. RENDER PREVIEW IMAGES
$imgJobs = @(
    @{
        Name = "cross_section"
        OutFile = "18_cross_section_view.png"
        Camera = "0,0,3,75,0,180,240"
        ImgSize = "1024,1024"
        ColorScheme = "Tomorrow Night"
    },
    @{
        Name = "assembly"
        OutFile = "18_assembly_view.png"
        Camera = "0,0,5,65,0,35,260"
        ImgSize = "1024,1024"
        ColorScheme = "Tomorrow Night"
    },
    @{
        Name = "exploded"
        OutFile = "18_exploded_view.png"
        Camera = "0,0,5,65,0,25,320"
        ImgSize = "1024,1024"
        ColorScheme = "Tomorrow Night"
    },
    @{
        Name = "print_all"
        OutFile = "18_print_layout_view.png"
        Camera = "0,0,15,55,0,30,280"
        ImgSize = "1024,1024"
        ColorScheme = "Tomorrow Night"
    }
)

Write-Host "`n[Step 1/2] Rendering 3D Preview Images..." -ForegroundColor Yellow
foreach ($job in $imgJobs) {
    $outPath = Join-Path $PSScriptRoot $job.OutFile
    Write-Host "  -> Rendering $($job.Name) -> $($job.OutFile) ..." -NoNewline
    
    $openscadArgs = @(
        "-o", $outPath,
        "-D", "render_part=\`"$($job.Name)\`"",
        "--camera", $job.Camera,
        "--imgsize", $job.ImgSize,
        "--colorscheme", $job.ColorScheme,
        $scadFile
    )
    & $openscad @openscadArgs
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host " [OK]" -ForegroundColor Green
        if (Test-Path $brainDir) {
            Copy-Item -Path $outPath -Destination (Join-Path $brainDir $job.OutFile) -Force
        }
    } else {
        Write-Host " [FAILED (Exit Code: $LASTEXITCODE)]" -ForegroundColor Red
    }
}

# 2. EXPORT 3D PRINTABLE STL FILES
$stlJobs = @(
    @{
        Part = "rear_shell"
        OutFile = "18_apple_rear_shell.stl"
        Desc = "Apple Rear Housing (Base with PCB standoffs & battery cradle)"
    },
    @{
        Part = "front_shell"
        OutFile = "18_apple_front_shell.stl"
        Desc = "Apple Front Housing (Front cover with mating tongue & light window)"
    },
    @{
        Part = "stem"
        OutFile = "18_apple_stem.stl"
        Desc = "Apple Stem & Leaf Accessory (Optional cosmetic handle / plug)"
    }
)

Write-Host "`n[Step 2/2] Exporting 3D Printable STL Files..." -ForegroundColor Yellow
foreach ($job in $stlJobs) {
    $outPath = Join-Path $PSScriptRoot $job.OutFile
    Write-Host "  -> Exporting $($job.Desc) -> $($job.OutFile) ..." -NoNewline
    
    $openscadArgs = @(
        "-o", $outPath,
        "-D", "render_part=\`"$($job.Part)\`"",
        $scadFile
    )
    & $openscad @openscadArgs
    
    if ($LASTEXITCODE -eq 0) {
        $fileInfo = Get-Item $outPath
        $sizeKb = [math]::Round($fileInfo.Length / 1KB, 1)
        Write-Host " [OK ($sizeKb KB)]" -ForegroundColor Green
    } else {
        Write-Host " [FAILED (Exit Code: $LASTEXITCODE)]" -ForegroundColor Red
    }
}

Write-Host "`nAll rendering and STL export tasks completed successfully!" -ForegroundColor Cyan
