# render_mockups.ps1 - Render 3D preview images for Hardware Component Mockups & Wiring Diagram
# Usage: .\render_mockups.ps1

$openscad = "C:\Program Files\OpenSCAD\openscad.com"
$scadFile = "$PSScriptRoot\view_mockups.scad"
$brainDir = "C:\Users\yuyub\.gemini\antigravity-ide\brain\eb525943-44a2-4955-aafc-8ff4643c2e2e"

Write-Host "Starting V16.0 Hardware Mockups & 3D Wiring rendering..." -ForegroundColor Cyan

$renderJobs = @(
    @{
        Name = "components"
        OutFile = "hardware_mockups_assembly.png"
        Camera = "0,15,0,0,0,0,150"
        ImgSize = "1920,1080"
    },
    @{
        Name = "wiring"
        OutFile = "system_wiring_3d.png"
        Camera = "20,65,-10,25,35,0,320"
        ImgSize = "1920,1080"
    }
)

foreach ($job in $renderJobs) {
    $outPath = Join-Path $PSScriptRoot $job.OutFile
    Write-Host "`n>>> Rendering $($job.Name) -> $($job.OutFile) ..." -ForegroundColor Yellow
    
    $openscadArgs = @(
        "-o", $outPath,
        "-D", "view_mode=\`"$($job.Name)\`"",
        "--camera", $job.Camera,
        "--imgsize", $job.ImgSize,
        "--colorscheme", "Tomorrow Night",
        $scadFile
    )
    & $openscad @openscadArgs
        
    if ($LASTEXITCODE -eq 0) {
        Write-Host "    Successfully rendered: $($job.OutFile)" -ForegroundColor Green
        
        # Copy to brain directory for artifact embedding if path exists
        if (Test-Path $brainDir) {
            $destPath = Join-Path $brainDir $job.OutFile
            Copy-Item -Path $outPath -Destination $destPath -Force
            Write-Host "    Copied to brain: $($job.OutFile)" -ForegroundColor DarkGreen
        }
    } else {
        Write-Host "    FAILED to render $($job.Name) (Exit Code: $LASTEXITCODE)" -ForegroundColor Red
    }
}

Write-Host "`n=== Rendering task completed! ===" -ForegroundColor Yellow
