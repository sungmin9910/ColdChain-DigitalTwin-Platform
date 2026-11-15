@echo off
cd /d "%~dp0"
echo ======================================================================
echo  [ColdChain DigitalTwin] 4-in-1 FastAPI Unified Portal Launcher
echo  - Starting background FastAPI server (port 8080) & Cloudflare Tunnel
echo  - Even if you close this window, the server stays ON in background!
echo ======================================================================

powershell -NoProfile -Command ^
  "$dir = '%~dp0'.TrimEnd('\'); " ^
  "$proc = Get-NetTCPConnection -LocalPort 8080 -State Listen -ErrorAction SilentlyContinue; " ^
  "if (-not $proc) { Start-Process -FilePath 'C:\Users\yuyub\AppData\Local\Programs\Python\Python310\python.exe' -ArgumentList '-m uvicorn app:app --host 0.0.0.0 --port 8080 --reload' -WorkingDirectory $dir -WindowStyle Hidden }; " ^
  "$cfExe = Join-Path $dir 'cloudflared.exe'; " ^
  "$cfLog = Join-Path $dir 'cloudflared_live.log'; " ^
  "$pubTxt = Join-Path $dir 'PUBLIC_URL.txt'; " ^
  "if ((Test-Path $cfExe) -and -not (Get-Process cloudflared -ErrorAction SilentlyContinue)) { " ^
  "  if (Test-Path $cfLog) { Remove-Item $cfLog -Force -ErrorAction SilentlyContinue }; " ^
  "  Start-Process -FilePath $cfExe -ArgumentList ('tunnel --url http://localhost:8080 --no-autoupdate --logfile \"' + $cfLog + '\"') -WorkingDirectory $dir -WindowStyle Hidden; " ^
  "  Start-Sleep -Seconds 6 " ^
  "}; " ^
  "if (Test-Path $cfLog) { " ^
  "  $m = Select-String -Path $cfLog -Pattern 'https://[a-z0-9-]+\.trycloudflare\.com' | Select-Object -Last 1; " ^
  "  if ($m) { $url = $m.Matches[0].Value; Set-Content -Path $pubTxt -Value $url; Write-Host ('`n [External LTE/5G URL] ' + $url + ' (Saved to PUBLIC_URL.txt)`n') -ForegroundColor Cyan } " ^
  "}"

start "" "http://localhost:8080"
echo.
echo  [Local PC URL]   http://localhost:8080
echo  [Same WiFi URL]  http://192.168.0.40:8080
echo  (External LTE/5G URL is also saved in PUBLIC_URL.txt in this folder)
echo.
pause
