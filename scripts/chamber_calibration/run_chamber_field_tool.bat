@echo off
chcp 65001 > nul
set PYTHONIOENCODING=utf-8
title FDT Chamber Field Tool
cd /d "%~dp0..\.."
python scripts\chamber_calibration\chamber_field_wizard.py %*
if errorlevel 1 (
    echo.
    echo [ERROR] Python execution failed. Check: pip install pyserial paho-mqtt pymysql
)
echo.
pause
