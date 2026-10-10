# render_v19.ps1 - Render 3D preview images and export STL files for v19 Apple Sensor Pod (5000mAh)

$openscad = "C:\Program Files\OpenSCAD\openscad.com"
$scadFile = "$PSScriptRoot\19_apple_sensor_pod.scad"
$artifactDir = "C:\Users\korea\.gemini\antigravity-ide\brain\0b1358ca-580d-4db5-8ea5-d228b1bcc520"

Write-Host "=========================================================" -ForegroundColor Cyan
Write-Host "  v19 Apple Sensor Pod Housing (5000mAh) Generator & Exporter  " -ForegroundColor Cyan
Write-Host "=========================================================" -ForegroundColor Cyan

# 1. RENDER PREVIEW IMAGES
$imgJobs = @(
    @{
        Name = "exploded"
        OutFile = "19_exploded_view.png"
        Camera = "0,10,15,65,0,25,360"
        ImgSize = "1024,1024"
        ColorScheme = "Tomorrow Night"
    },
    @{
        Name = "cross_section"
        OutFile = "19_cross_section_view.png"
        Camera = "0,0,5,65,0,45,260"
        ImgSize = "1024,1024"
        ColorScheme = "Tomorrow Night"
    },
    @{
        Name = "assembly"
        OutFile = "19_assembly_view.png"
        Camera = "0,0,5,65,0,35,270"
        ImgSize = "1024,1024"
        ColorScheme = "Tomorrow Night"
    },
    @{
        Name = "print_all"
        OutFile = "19_print_layout_view.png"
        Camera = "0,0,15,55,0,30,290"
        ImgSize = "1024,1024"
        ColorScheme = "Tomorrow Night"
    }
)

Write-Host "`n[Step 1/2] Rendering 3D Preview Images..." -ForegroundColor Yellow
foreach ($job in $imgJobs) {
    $outPath = Join-Path $PSScriptRoot $job.OutFile
    Write-Host "  -> Rendering $($job.Name) -> $($job.OutFile) ..." -NoNewline
    
    $partDef = "render_part=\`"$($job.Name)\`""
    $openscadArgs = @(
        "-o", $outPath,
        "-D", $partDef,
        "--camera", $job.Camera,
        "--imgsize", $job.ImgSize,
        "--colorscheme", $job.ColorScheme,
        $scadFile
    )
    & $openscad @openscadArgs
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host " [OK]" -ForegroundColor Green
        if (Test-Path $artifactDir) {
            Copy-Item -Path $outPath -Destination (Join-Path $artifactDir $job.OutFile) -Force
        }
    } else {
        Write-Host " [FAILED (Exit Code: $LASTEXITCODE)]" -ForegroundColor Red
    }
}

# 2. EXPORT 3D PRINTABLE STL FILES
$stlJobs = @(
    @{
        Part = "rear_shell"
        OutFile = "19_apple_rear_shell.stl"
        Desc = "Apple Rear Housing (Base with PCB standoffs & 5000mAh battery bay)"
    },
    @{
        Part = "front_shell"
        OutFile = "19_apple_front_shell.stl"
        Desc = "Apple Front Housing (Dome cover with mating lip & light window)"
    },
    @{
        Part = "stem"
        OutFile = "19_apple_stem.stl"
        Desc = "Apple Stem & Leaf Accessory (Cosmetic plug)"
    }
)

Write-Host "`n[Step 2/2] Exporting 3D Printable STL Files..." -ForegroundColor Yellow
foreach ($job in $stlJobs) {
    $outPath = Join-Path $PSScriptRoot $job.OutFile
    Write-Host "  -> Exporting $($job.Desc) -> $($job.OutFile) ..." -NoNewline
    
    $partDef = "render_part=\`"$($job.Part)\`""
    $openscadArgs = @(
        "-o", $outPath,
        "-D", $partDef,
        $scadFile
    )
    & $openscad @openscadArgs
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host " [OK]" -ForegroundColor Green
    } else {
        Write-Host " [FAILED (Exit Code: $LASTEXITCODE)]" -ForegroundColor Red
    }
}

Write-Host "`nAll rendering and STL export tasks completed successfully!" -ForegroundColor Cyan
