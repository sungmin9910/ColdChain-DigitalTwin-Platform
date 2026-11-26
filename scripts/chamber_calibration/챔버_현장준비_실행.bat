@echo off
chcp 65001 > nul
title FDT 챔버 교정 현장 준비 실행기
cd /d "%~dp0..\.."
echo ============================================================
echo   FDT 항온항습 챔버 교정 - 현장 준비 / 모니터링 / 추출 도구
echo ============================================================
python scripts\chamber_calibration\chamber_field_wizard.py
if errorlevel 1 (
    echo.
    echo [오류] Python 실행 중 문제가 발생했습니다.
    echo        pip install pyserial paho-mqtt pymysql 설치 여부를 확인하세요.
)
echo.
pause
