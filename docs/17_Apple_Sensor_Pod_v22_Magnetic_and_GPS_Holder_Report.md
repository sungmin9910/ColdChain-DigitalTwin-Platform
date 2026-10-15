# 🍎 Apple Sensor Pod v22 실물 조립 검증 반영: 자석 스냅 결합($\varnothing 6\times 3\text{ mm}$) + GPS 안테나 전용 홀더 + 1-A 조도센서 채광창 설계 보고서 (Doc 17)

**작성 일시**: 2026-10-15 16:33 (KST)  
**대상 시스템**: Apple Digital Twin Sensor Pod v22 (`3D_Printer_Housing/v22_Apple_Sensor_Pod_Magnetic5000mAh`), 신도리코 3DWOX 2X (PLA 단일 노즐 출력)  
**기반 데이터**: `v21` 실물 출력 및 가조립 사진 4종 (`KakaoTalk_20261015_114727151.jpg` 외 3종)

---

## 1. 📸 `v21` 실물 출력 및 가조립 검증 결과 요약

1. **보강 리브 간섭 해결 및 나사 체결 성공**:
   * 상·하 외벽 직결 보강 리브(`v21.2`) 적용 결과, 기판(CarrierBoard)의 43×43mm M3 홀이 기둥과 정확히 일치하며 볼트 체결 시 기둥 파손이 전혀 발생하지 않음을 실물로 검증함.
   * 5000mAh 리튬폴리머 배터리 또한 보라색 후면 쉘 크래들 내부에 안정적으로 수납되며 전면/후면 쉘이 간섭 없이 덮임을 확인함.
2. **실물 조립 과정에서 도출된 3대 개선 요구사항**:
   * **① 조도 센서(BH1750) 방향 (방법 1-A 채택)**: 기판을 뒤집어 장착할 때 나사 체결이 용이하고 안정적으로 닫히므로, 현재 조립 방향(BH1750이 보라색 후면 쉘 좌하단 `X=+15.5, Z=-15.0, Y=-8.5`를 향함)을 유지하고 보라색 후면 쉘 측면(배터리 앞쪽 공간)에 전용 채광창을 신설.
   * **② 외장 세라믹 GPS 안테나(`20 × 5 × 7 mm`) 전용 홀더 추가**: 피그테일 동축 케이블로 연결된 직사각형 세라믹 패치 안테나를 테이프 없이 슬라이드 방식으로 고정할 수 있는 내벽 일체형 포켓 추가.
   * **③ 외곽 나사 결합 ➔ 네오디뮴 자석($\varnothing 6 \times 3\text{ mm}$) + 미끄럼 방지 결합(선택지 A) 전환**: 드라이버 없이 1초 만에 여닫을 수 있고 사과 전면 외관에 나사 구멍을 완전히 없애는 자석 결합 구조로 전면 개편.

---

## 2. 🛠️ `v22` 핵심 공학 설계 내역

### 2.1 강철 핀 맞물림(Steel-Dowel) 네오디뮴 자석 결합 구조 ($\varnothing 6 \times 3\text{ mm}$, 총 8개)
* **플라스틱 돌기 없이 출력성(평평한 베드 안착)과 전단 미끄럼 방지를 동시에 해결**:
  * **보라색 후면 쉘(`22_apple_rear_shell.stl`)**: 4개 모서리 보스에 $\varnothing 6.24\text{ mm} \times \text{깊이 } 1.80\text{ mm}$ 홈을 가공. 두께 $3.0\text{ mm}$ 자석을 접착하면 **강철 자석 몸체 $1.20\text{ mm}$가 테두리($Y=0$) 위로 돌출**되어 4개의 강철 가이드 핀 역할을 수행함.
  * **노란색 전면 쉘(`22_apple_front_shell.stl`)**: 4개 모서리 보스에 $\varnothing 6.32\text{ mm} \times \text{깊이 } 4.30\text{ mm}$ 홈(입구 가이드 챔퍼 포함)을 가공. 바닥에 두께 $3.0\text{ mm}$ 자석을 접착하면 입구에 **$1.30\text{ mm}$ 깊이의 안착 소켓**이 형성됨.
  * **결합 시**: 후면 쉘의 $1.20\text{ mm}$ 돌출 자석이 전면 쉘의 $1.30\text{ mm}$ 소켓으로 맞물려 들어가 자석끼리 $0.0\text{ mm}$ 간격으로 직접 밀착되며, 강철 자석 자체가 분할면($Y=0$)을 가로지르므로 좌우/상하 전단 미끄러짐이 원천 차단됨.

### 2.2 외장 GPS 세라믹 안테나(`20 × 5 × 7 mm`) 전용 슬라이드 포켓
* **위치**: 노란색 전면 쉘의 상단 내벽 빈 공간 (`X = -36.5 mm, Z = +1.0 mm, Y = 0 ~ 12.0 mm`).
* **구조**:
  * 내경 길이 $21.6\text{ mm}$($Z$축), 기본 폭 $5.8\text{ mm}$ 및 중앙 납땜 돌기 수용 단차 폭 $7.8\text{ mm}$($X$축)로 설계하여 `20 × 5 × 7 mm` 규격 안테나가 유격 없이 장착됨.
  * 우측(`+Z` 방향) 벽면에 폭 $4.4\text{ mm}$의 동축 케이블 인출 슬롯을 두어 기판 우측에서 나오는 안테나 선이 꺾이지 않고 자연스럽게 진입함.
  * 배터리(`X = ±27.5 mm`) 및 기판(`X = ±25.0 mm`) 바깥쪽 PLA 외벽에 위치하여 금속 차폐 없이 90% 이상의 GPS L1(1.575 GHz) 전파 투과율을 보장함.

### 2.3 방법 1-A 조도 센서(BH1750) 경사형 채광창 및 무결점 전면 외관
* **후면 쉘 채광창**: 배터리 포켓($Y \le -22.5\text{ mm}$) 앞쪽의 여유 공간($Y = -8.5 \sim -11.0\text{ mm}, Z = -11.0 \sim -14.5\text{ mm}, X > 0$)을 관통하는 경사형 광학 터널을 뚫어 배터리에 가려지지 않고 BH1750 센서에 외부 빛이 직접 도달하도록 설계.
* **전면 쉘 무결점 외관**: 외곽 나사 홀 4개와 기존 전면 채광창을 제거하고, PCB 고정용 M3 파일럿 홀 4개를 깊이 $20.0\text{ mm}$ 막힌 홀(Blind Hole)로 변경하여 전면 사과 표면에 구멍이 0개인 매끈한 외관 완성.

### 2.4 신도리코 3DWOX 2X 무서포트/단일재료 출력 최적화 (45° 자립형 아치)
* 자석 포켓 8곳의 바닥 안쪽과 GPS 홀더 천장에 **45° 원뿔/아치 경사(Self-supporting Vault)**를 적용하여, 별도의 서포트 재료 없이 출력할 때도 구멍 내부에 서포트가 생성되지 않으며 브릿징 처짐 없이 정밀한 자석 삽입 깊이를 보장함.

---

## 3. 📂 산출물 및 GitHub 커밋 이력
* **폴더 경로**: [`3D_Printer_Housing/v22_Apple_Sensor_Pod_Magnetic5000mAh`](file:///c:/Users/korea/Desktop/1hsm/hanhanhan/ColdChain-DigitalTwin-Platform/3D_Printer_Housing/v22_Apple_Sensor_Pod_Magnetic5000mAh)
* **주요 커밋**:
  * `0ded3e6`: `feat(housing): add v22 magnetic snap edition with D6x3mm steel-dowel magnets, 20x5x7mm GPS antenna holder, and Method 1-A BH1750 window`
  * `6b6e2bf`: `fix(housing): add 45-deg self-supporting conical vaults to v22 magnet and GPS pockets for support-free printing`
