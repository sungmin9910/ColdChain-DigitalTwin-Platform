@echo off
cd /d "%~dp0"
echo ================================================================
echo  [ColdChain DigitalTwin] 4-in-1 FastAPI Unified Portal Server
echo  URL: http://localhost:8080
echo ================================================================
start "" "http://localhost:8080"
"C:\Users\yuyub\AppData\Local\Programs\Python\Python310\python.exe" -m uvicorn app:app --host 0.0.0.0 --port 8080 --reload
pause
