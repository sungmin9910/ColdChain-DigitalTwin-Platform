@echo off
chcp 65001 >nul
echo ================================================================
echo  [ColdChain DigitalTwin] 4-in-1 FastAPI 통합 포털 서버 시작
echo  접속 주소: http://localhost:8080
echo ================================================================
cd /d "%~dp0"
"C:\Users\yuyub\AppData\Local\Programs\Python\Python310\python.exe" -m uvicorn app:app --host 0.0.0.0 --port 8080 --reload
pause
