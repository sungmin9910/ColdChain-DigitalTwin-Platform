#!/bin/bash
set -e

echo "=========================================================="
echo " ColdChain DigitalTwin 4-in-1 FastAPI Portal EC2 Installer "
echo "=========================================================="

sudo apt update -y
sudo apt install -y python3 python3-pip git

pip3 install --break-system-packages fastapi "uvicorn[standard]" pymysql paho-mqtt qrcode pillow || true

PORTAL_DIR="$(cd "$(dirname "$0")" && pwd)"

sudo tee /etc/systemd/system/coldchain-portal.service > /dev/null <<EOF
[Unit]
Description=ColdChain DigitalTwin 4-in-1 FastAPI Unified Portal
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$PORTAL_DIR
ExecStart=/usr/bin/python3 -m uvicorn app:app --host 0.0.0.0 --port 8080
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable coldchain-portal
sudo systemctl restart coldchain-portal

PUBLIC_IP=$(curl -s http://checkip.amazonaws.com || echo "<EC2_PUBLIC_IP>")
echo ""
echo "✅ [설치 완료] 4-in-1 FastAPI 통합 포털이 24시간 상시 서비스로 가동되었습니다!"
echo "🌐 외부(LTE/5G 스마트폰) 접속 주소: http://${PUBLIC_IP}:8080"
echo "⚠️ AWS EC2 콘솔 -> 보안 그룹(Security Group) -> 인바운드 규칙에서 TCP 8080 포트를 허용(0.0.0.0/0)해 주세요."
echo "=========================================================="
