# 🛡️ AWS RDS `lab225` 원상복구(Rollback) 가이드

**백업 생성 시각**: `2026-11-16 17:10:33 (KST)`  
**백업 대상 호스트**: `labdb.cn26yq6q0mu6.ap-northeast-2.rds.amazonaws.com:3306`

본 디렉터리에는 정규화 DB(`lab225_v2`) 전환 작업 직전의 `lab225` 전체 테이블 구조와 데이터(총 5개 테이블, **12,250행**)가 **서버 내부 복제본**과 **로컬 파일(`.sql` / `.json`)** 이중으로 보존되어 있습니다.

---

## 1. 보관된 백업 자산 목록

| 구분 | 경로 / DB명 | 설명 |
| :--- | :--- | :--- |
| **RDS 내부 스냅샷 DB** | `lab225_backup_20261116` | AWS RDS 서버 내부에 복제된 읽기 전용 원본 DB (`qr` 63행, `sensor_data` 7,256행 외 3개 테이블) |
| **로컬 전체 SQL 덤프** | `full_dump_lab225_20261116.sql` | `CREATE TABLE` 스키마 원문 + 12,250행 전체 `INSERT` 구문 (1.64 MB) |
| **테이블별 JSON 원본** | `tables_json/*.json` | 테이블별 데이터 JSON 백업 및 SHA-256 무결성 해시 검증용 |
| **매니페스트** | `manifest.json` | 백업 시각, 테이블별 기대 행 개수 및 SHA-256 해시 기록 |
| **원클릭 복구 도구** | `restore_rds_v1.py` | 명령어 한 줄로 `lab225`를 백업 시점으로 되돌리는 스크립트 |

---

## 2. 상황별 되돌리기(복구) 방법

### 방법 A. 가장 빠른 전환 복귀 (코드 설정만 변경 — 1초 소요)
신규 정규화 테이블들은 기존 `lab225`를 건드리지 않고 별도의 **`lab225_v2`** 데이터베이스에 생성되어 있습니다.  
따라서 대시보드나 데몬의 DB 이름을 다시 `"lab225"`로 지정하기만 하면 즉시 기존 환경으로 돌아갑니다.

### 방법 B. 백업 상태 사전 점검 (덮어쓰기 없이 무결성만 확인)
```powershell
python Final_Experiment\_backup_before_db_v2_20261116\restore_rds_v1.py --dry-run
```

### 방법 C. RDS 서버 내부 복제본(`lab225_backup_20261116`)으로부터 초고속 복원 (약 2초 소요)
만약 `lab225` 내부 데이터가 수정·오염되어 2026-11-16 백업 시점으로 완전히 되돌리고 싶을 때 실행합니다:
```powershell
python Final_Experiment\_backup_before_db_v2_20261116\restore_rds_v1.py --source rds_clone --yes
```

### 방법 D. 내 PC 로컬 `.sql` 덤프 파일로부터 완전 복원 (클라우드 백업마저 지워졌을 때)
```powershell
python Final_Experiment\_backup_before_db_v2_20261116\restore_rds_v1.py --source local_sql --yes
```
