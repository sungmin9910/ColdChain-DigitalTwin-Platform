@echo off
cd /d "%~dp0\..\.."
echo ============================================================
echo   FDT Chamber Calibration Live Graph Dashboard (Port 8505)
echo ============================================================
python scripts\chamber_calibration\live_chamber_dashboard.py
pause
