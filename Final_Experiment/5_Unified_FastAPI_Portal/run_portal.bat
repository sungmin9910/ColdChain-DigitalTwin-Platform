@echo off
cd /d "%~dp0"
echo ================================================================
echo  [ColdChain DigitalTwin] 4-in-1 FastAPI Unified Portal Launcher
echo  - Starting background server (windowless pythonw.exe)...
echo  - Even if you close this window, http://localhost:8080 stays ON!
echo ================================================================

REM Stop any existing uvicorn process on port 8080 if needed, then start in background
powershell -NoProfile -Command "$proc = Get-NetTCPConnection -LocalPort 8080 -State Listen -ErrorAction SilentlyContinue; if (-not $proc) { Start-Process -FilePath 'C:\Users\yuyub\AppData\Local\Programs\Python\Python310\pythonw.exe' -ArgumentList '-m uvicorn app:app --host 0.0.0.0 --port 8080' -WorkingDirectory '%~dp0' -WindowStyle Hidden }"

timeout /t 2 /nobreak >nul
start "" "http://localhost:8080"
echo.
echo  [OK] Server is running in the background at:
echo       - Local PC:  http://localhost:8080
echo       - Same WiFi: http://192.168.0.40:8080
echo  You may safely close this window at any time.
timeout /t 5
