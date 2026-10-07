#!/bin/bash
# ================================================================
# ColdChain Jetson Split HUD Launcher Script
# ================================================================

# 환경변수 PATH 보강 (GNOME 바로가기 실행 시 pip 모듈 경로 누락 방지)
export PATH="$HOME/.local/bin:/usr/local/bin:$PATH"

# 프로젝트 디렉토리로 이동
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_DIR" || exit 1

# 기존 실행 중인 이전 프로세스 정리 (포트 충돌 및 중복 실행 방지)
pkill -f "Step4_Jetson_SplitHUD.py" >/dev/null 2>&1
sleep 0.5

# X11 DISPLAY 환경변수 자동 감지
if [ -z "$DISPLAY" ]; then
    ACTIVE_DISP=$(who | grep -o '(:[0-9])' | tr -d '()' | head -n 1)
    if [ -n "$ACTIVE_DISP" ]; then
        export DISPLAY="$ACTIVE_DISP"
    elif [ -S /tmp/.X11-unix/X1 ]; then
        export DISPLAY=:1
    else
        export DISPLAY=:0
    fi
fi

if [ -z "$XAUTHORITY" ]; then
    export XAUTHORITY="$HOME/.Xauthority"
fi

# Streamlit 백그라운드 구동
python3 -m streamlit run Final_Experiment/4_APC_Coldchain_Dashboard/Step4_Jetson_SplitHUD.py \
  --server.port 8501 \
  --server.headless true \
  --browser.serverAddress localhost \
  --server.fileWatcherType none >/dev/null 2>&1 &

# 웹서버 활성화 대기 (포트 8501이 응답할 때까지 최대 15초 대기)
for i in {1..15}; do
    if curl -s http://localhost:8501 >/dev/null 2>&1; then
        break
    fi
    sleep 1
done

# Epiphany 브라우저 실행 (백그라운드)
epiphany-browser http://localhost:8501 >/dev/null 2>&1 &
