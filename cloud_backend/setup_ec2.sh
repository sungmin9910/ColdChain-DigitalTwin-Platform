#!/bin/bash
set -e

echo "=========================================================="
echo " ColdChain DigitalTwin EC2 Daemon Installer "
echo "=========================================================="

# 1. 패키지 업데이트 및 필수 패키지 설치
sudo apt update -y
sudo apt install -y python3 python3-pip python3-pymysql python3-paho-mqtt git

# 2. 파이썬 라이브러리 설치 (Ubuntu 24.04 PEP 668 대응)
pip3 install --break-system-packages -r requirements.txt || true

# 3. systemd 서비스 등록 및 활성화
sudo cp coldchain-daemon.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable coldchain-daemon
sudo systemctl restart coldchain-daemon

echo ""
echo "✅ [설치 완료] ColdChain 24/7 수신 데몬이 성공적으로 가동되었습니다!"
echo "• 상태 확인: sudo systemctl status coldchain-daemon"
echo "• 실시간 로그: sudo journalctl -u coldchain-daemon -f"
echo "=========================================================="
