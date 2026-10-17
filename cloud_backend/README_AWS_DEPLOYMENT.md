# ☁️ AWS EC2 24/7 상시 백엔드 수신 데몬 배포 가이드

본 문서는 차량 센서노드(1호차~4호차)에서 송출하는 MQTT 패킷을 중앙에서 24시간 365일 실시간으로 수신하여 AWS RDS MySQL에 자동 적재하는 **상시 백엔드 수신 데몬(`mqtt_to_mysql_daemon.py`)**의 AWS EC2 배포 가이드입니다.

---

## 📌 1. 비용 분석 및 요약
* **소프트웨어 비용:** **0원 (완전 무료)**
* **AWS 인스턴스 비용:** **0원 (AWS Free Tier 매월 750시간 무료 또는 계정 잔여 크레딧 $70.08 전액 차감)**
* **데이터 전송 비용:** 단말기 패킷이 5초당 200Byte이므로 한 달 내내 가동해도 수십 MB 수준으로 비용 0원.

---

## 🚀 2. AWS EC2 인스턴스 생성 (콘솔 3분 세팅)

1. [AWS 관리 콘솔](https://aws.amazon.com/console/) 로그인 후 상단 리전을 **`아시아 태평양 (서울) ap-northeast-2`**로 선택합니다.
2. 검색창에 **EC2** 검색 ➔ **[인스턴스 시작 (Launch Instance)]** 클릭
3. 인스턴스 옵션 설정:
   * **이름:** `ColdChain-Telemetry-Daemon`
   * **애플리케이션 및 OS 이미지:** **Ubuntu 24.04 LTS (Free Tier eligible)**
   * **인스턴스 유형:** **`t3.micro`** (또는 `t4g.nano` / `t2.micro` - 프리티어 사용 가능)
   * **키 페어(로그인):** 기존 키 페어 선택 또는 신규 생성하여 `.pem` 파일 다운로드
   * **네트워크 설정:** 
     * [SSH 트래픽 허용] 체크
     * 보안 그룹: 아웃바운드 전체 허용 (HiveMQ 1883 포트 및 RDS 3306 포트 접속용)
   * **스토리지 구성:** 기본값 8 GiB (gp3)
4. 우측 하단 **[인스턴스 시작]** 클릭 (1~2분 후 인스턴스가 `Running` 상태로 변경됨).

---

## 💻 3. EC2 서버 접속 및 1-Click 데몬 설치

### 3.1 터미널 또는 웹 콘솔(EC2 Instance Connect) 접속
AWS 콘솔에서 방금 생성한 인스턴스를 선택하고 **[연결 (Connect)] ➔ [EC2 Instance Connect] ➔ [연결]**을 누르면 브라우저 화면에서 바로 검은색 리눅스 터미널이 열립니다.

### 3.2 원클릭 자동 설치 스크립트 실행
열린 터미널에 아래 명령어를 복사하여 붙여넣기만 하면 모든 라이브러리 설치와 24시간 백그라운드 서비스 등록이 1분 만에 완료됩니다:

```bash
# 1. 레포지토리 클론
git clone https://github.com/sungmin9910/ColdChain-DigitalTwin-Platform.git
cd ColdChain-DigitalTwin-Platform/cloud_backend

# 2. 설치 및 서비스 등록 스크립트 실행
bash setup_ec2.sh
```

---

## 🔍 4. 동작 확인 및 관리 명령어

설치가 완료되면 백그라운드 `systemd` 서비스(`coldchain-daemon`)가 24시간 상시 가동됩니다:

```bash
# 1. 서비스 가동 상태 확인
sudo systemctl status coldchain-daemon

# 2. 실시간 수신 및 DB 적재 로그 스트리밍 확인
sudo journalctl -u coldchain-daemon -f

# 3. 서비스 재시작 / 중지
sudo systemctl restart coldchain-daemon
sudo systemctl stop coldchain-daemon
```

---

## 🌟 5. 배포 후 기대 효과
1. **PC 전원 무관**: 연구실 컴퓨터를 끄거나 화면을 닫아도 24시간 주행 데이터가 1초의 누락 없이 MySQL DB에 자동 적재됩니다.
2. **다차량 동시 관제**: 1호차부터 4호차까지 어떤 차량이든 시동을 걸고 주행을 시작하면 자동으로 출발 시간 기준 세션 ID(`truckXX_주행_YYYY-MM-DD_HH시MM분`)가 생성되어 분할 저장됩니다.
3. **웹 대시보드 연동**: 관리자는 언제 어디서든 스마트폰이나 태블릿, PC로 Streamlit 웹 대시보드에 접속하기만 하면 모든 차량의 실시간 위치와 충격량, 온습도 곡선을 라이브로 확인할 수 있습니다.
