# render_mockups.ps1 - Render 3D preview images and export STL files for V17
# Usage: .\render_mockups.ps1

$openscad = "C:\Program Files\OpenSCAD\openscad.com"
$scadViewFile = "$PSScriptRoot\view_mockups.scad"
$scadHousingFile = "$PSScriptRoot\17_qr_scanner_housing.scad"
$brainDir = "C:\Users\korea\.gemini\antigravity-ide\brain\f41dadd4-22d2-439b-842c-34a16516698c"

Write-Host "Starting V17.0 Hardware Mockups & Housing STL rendering..." -ForegroundColor Cyan

# 1. RENDER PREVIEW IMAGES
$imgJobs = @(
    @{
        Name = "components"
        OutFile = "hardware_mockups_assembly.png"
        Camera = "0,15,0,0,0,0,150"
        ImgSize = "1920,1080"
        ScadFile = $scadViewFile
    },
    @{
        Name = "assembly"
        OutFile = "system_assembly_3d.png"
        Camera = "20,65,-10,25,35,0,320"
        ImgSize = "1920,1080"
        ScadFile = $scadViewFile
    }
)

foreach ($job in $imgJobs) {
    $outPath = Join-Path $PSScriptRoot $job.OutFile
    Write-Host "`n>>> Rendering $($job.Name) -> $($job.OutFile) ..." -ForegroundColor Yellow
    
    $openscadArgs = @(
        "-o", $outPath,
        "-D", "view_mode=\`"$($job.Name)\`"",
        "--camera", $job.Camera,
        "--imgsize", $job.ImgSize,
        "--colorscheme", "Tomorrow Night",
        $job.ScadFile
    )
    & $openscad @openscadArgs
        
    if ($LASTEXITCODE -eq 0) {
        Write-Host "    Successfully rendered image: $($job.OutFile)" -ForegroundColor Green
        if (Test-Path $brainDir) {
            $destPath = Join-Path $brainDir $job.OutFile
            Copy-Item -Path $outPath -Destination $destPath -Force
            Write-Host "    Copied image to brain: $($job.OutFile)" -ForegroundColor DarkGreen
        }
    } else {
        Write-Host "    FAILED to render image $($job.Name) (Exit Code: $LASTEXITCODE)" -ForegroundColor Red
    }
}

# 2. EXPORT STL HOUSING HALVES FOR 3D PRINTING
$stlJobs = @(
    @{
        Part = "left_half"
        OutFile = "17_qr_scanner_housing_left_half.stl"
    },
    @{
        Part = "right_half"
        OutFile = "17_qr_scanner_housing_right_half.stl"
    },
    @{
        Part = "trigger"
        OutFile = "17_qr_scanner_housing_trigger.stl"
    }
)

foreach ($job in $stlJobs) {
    $outPath = Join-Path $PSScriptRoot $job.OutFile
    Write-Host "`n>>> Exporting STL for $($job.Part) -> $($job.OutFile) (this may take a moment) ..." -ForegroundColor Yellow
    
    $openscadArgs = @(
        "-o", $outPath,
        "-D", "render_part=\`"$($job.Part)\`"",
        $scadHousingFile
    )
    & $openscad @openscadArgs
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "    Successfully exported STL: $($job.OutFile)" -ForegroundColor Green
        if (Test-Path $brainDir) {
            $destPath = Join-Path $brainDir $job.OutFile
            Copy-Item -Path $outPath -Destination $destPath -Force
            Write-Host "    Copied STL to brain: $($job.OutFile)" -ForegroundColor DarkGreen
        }
    } else {
        Write-Host "    FAILED to export STL $($job.Part) (Exit Code: $LASTEXITCODE)" -ForegroundColor Red
    }
}

Write-Host "`n=== Rendering and Export task completed! ===" -ForegroundColor Yellow
