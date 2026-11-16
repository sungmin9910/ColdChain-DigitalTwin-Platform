#!/bin/bash
set -e

echo "=========================================================="
echo " ColdChain DigitalTwin 4-in-1 FastAPI Portal EC2 Installer "
echo "=========================================================="

PORTAL_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_DIR="${PORTAL_DIR}/.venv"

echo "[1/4] 필수 시스템 패키지 확인 및 설치 (기존 coldchain-daemon 영향 없음)..."
sudo apt update -y
sudo apt install -y python3 python3-pip python3-venv curl git

echo "[2/4] 독립 파이썬 가상환경(.venv) 구성 및 패키지 설치..."
if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv "$VENV_DIR"
fi
"$VENV_DIR/bin/pip" install --upgrade pip
"$VENV_DIR/bin/pip" install -r "$PORTAL_DIR/requirements.txt"

echo "[3/4] systemd 상시 서비스(coldchain-portal.service) 등록 및 기동..."
sudo tee /etc/systemd/system/coldchain-portal.service > /dev/null <<EOF
[Unit]
Description=ColdChain DigitalTwin 4-in-1 FastAPI Unified Portal
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$PORTAL_DIR
ExecStart=$VENV_DIR/bin/python -m uvicorn app:app --host 0.0.0.0 --port 8080
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable coldchain-portal
sudo systemctl restart coldchain-portal

echo "[4/4] 서비스 구동 및 로컬 응답(8080 포트) 자동 검증 중..."
HTTP_OK=0
for i in {1..10}; do
    if curl -fsS -m 2 http://127.0.0.1:8080/ > /dev/null 2>&1; then
        HTTP_OK=1
        break
    fi
    sleep 1
done

DAEMON_STATE=$(systemctl is-active coldchain-daemon 2>/dev/null || echo "not-found")
PORTAL_STATE=$(systemctl is-active coldchain-portal 2>/dev/null || echo "failed")

IMDS_TOKEN=$(curl -fsS -m 2 -X PUT "http://169.254.169.254/latest/api/token" -H "X-aws-ec2-metadata-token-ttl-seconds: 60" 2>/dev/null || true)
if [ -n "$IMDS_TOKEN" ]; then
    PUBLIC_IP=$(curl -fsS -m 2 -H "X-aws-ec2-metadata-token: $IMDS_TOKEN" http://169.254.169.254/latest/meta-data/public-ipv4 2>/dev/null || true)
fi
if [ -z "$PUBLIC_IP" ]; then
    PUBLIC_IP=$(curl -fsS -m 3 http://checkip.amazonaws.com 2>/dev/null | tr -d '[:space:]' || echo "<EC2_PUBLIC_IP>")
fi

echo ""
echo "=========================================================="
echo " 📊 [서비스 병렬 가동 상태 확인]"
echo "  • 기존 MQTT 수신 데몬 (coldchain-daemon): ${DAEMON_STATE}"
echo "  • 신규 4-in-1 통합 포털 (coldchain-portal): ${PORTAL_STATE} (HTTP 200 검증: ${HTTP_OK})"
echo "----------------------------------------------------------"
if [ "$PORTAL_STATE" = "active" ] && [ "$HTTP_OK" = "1" ]; then
    echo " ✅ [설치 완료] 4-in-1 FastAPI 통합 포털이 24시간 상시 서비스로 가동되었습니다!"
    echo " 🌐 외부(LTE/5G 스마트폰/PC) 접속 주소: http://${PUBLIC_IP}:8080"
    echo " 🔍 소비자 이력 바로 조회 예시:          http://${PUBLIC_IP}:8080/?FmID=85"
else
    echo " ❌ 포털 시작 중 문제가 발생했습니다. 아래 명령어로 로그를 확인해 주세요:"
    echo "    sudo journalctl -u coldchain-portal -n 50 --no-pager"
    exit 1
fi
echo " ⚠️ [필수] AWS EC2 콘솔 -> 보안 그룹(Security Group) -> 인바운드 규칙에서"
echo "    '사용자 지정 TCP / 포트 8080 / 0.0.0.0/0' 허용 여부를 확인해 주세요."
echo "=========================================================="
