@echo off
cd /d "%~dp0"
title QR Scanner V17 3D Presenter
echo ====================================================================
echo  QR Scanner V17 3D Interactive Presenter - 로컬 웹 서버 시작
echo ====================================================================
echo.
echo  브라우저 보안(CORS) 정책으로 인해 STL 파일을 직접 로드하려면 
echo  로컬 웹 서버가 필요합니다.
echo.
echo  서버 주소: http://localhost:8000/viewer.html
echo.
echo  [1] 기본 파이썬 간이 서버 구동을 시도합니다...
echo.

start http://localhost:8000/viewer.html
python -m http.server 8000

if %errorlevel% neq 0 (
    echo.
    echo  파이썬이 설치되어 있지 않거나 포트 8000이 이미 사용 중입니다.
    echo  [2] Node.js npx 구동을 시도합니다...
    echo.
    npx http-server -p 8000
)

if %errorlevel% neq 0 (
    echo.
    echo  웹 서버 시작에 실패했습니다. 파이썬이나 Node.js가 설치되어 있어야 합니다.
    echo  그렇지 않은 경우 VS Code의 'Live Server' 플러그인 등으로 viewer.html을 열어주세요.
)
pause
