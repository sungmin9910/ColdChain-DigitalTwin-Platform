# A16 단계 및 소비자 주행 경로 연동 백업 안내서 (2026-11-15)

* **기준 Git 커밋 (변경 전 원본)**: `c173e75`
* **백업 일시**: 2026-11-15 15:56 KST

## 백업 파일 목록
* `main.cpp.bak` / `platformio.ini.bak`: ESP32 GM77 스마트 스캐너 원본 소스 및 설정 (`A00~A15`)
* `firmware_before_A16.bin` / `bootloader_before_A16.bin` / `partitions_before_A16.bin`: 변경 직전 빌드된 스캐너 바이너리
* `pc_qr_scanner.py.bak`: PC/젯슨 USB 스캐너 스크립트 원본
* `Step5_Run_Dashboard.py.bak`: 소비자용 대시보드 원본 (`st.map` 버전)
* `qr_table_backup_20261115.json`: AWS RDS `lab225.qr` 테이블 변경 전 전체 45건 데이터 및 DDL 덤프

## 이전 상태로 되돌리는 방법 (1초 원클릭 복구)

프로젝트 루트 폴더에서 아래 명령어를 실행하면 언제든 즉시 복구됩니다:

```powershell
# 1. 코드 파일만 이전으로 되돌리기
python Final_Experiment/_backup_before_A16_20261115/restore_backup.py --files

# 2. 코드 복원 + USB 연결된 스캐너(예: COM16)까지 이전 펌웨어로 재업로드
python Final_Experiment/_backup_before_A16_20261115/restore_backup.py --files --flash COM16

# 3. DB에 추가한 컬럼(Retail_AD, truck_device)까지 이전으로 제거
python Final_Experiment/_backup_before_A16_20261115/restore_backup.py --db
```
