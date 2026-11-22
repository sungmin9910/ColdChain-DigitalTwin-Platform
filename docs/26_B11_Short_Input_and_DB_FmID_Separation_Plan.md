# 26. 모바일 B11 유색 QR 단축 입력(`FmID + 품목번호`) 및 DB `FmID` / `lot_id` 분리 개선 계획서

**문서 번호**: CC-DOC-2026-26  
**작성 일자**: 2026-11-23  
**상태**: 📋 **사전 검토·보관 문서 (미적용 — 연구실에서 진행 결정 시 즉시 실행용)**  
**적용 예정 대상**: FastAPI 통합 포털 (`http://54.180.112.191:8080/`), AWS RDS (`lab225_v2`, `lab225`), `bridge_sync.py`, Streamlit 소비자 대시보드

---

## 1. 배경 및 해결 과제

공급망 v3(`16자리 LotID` + `A00~D10` 분기 공정) 적용 이후, 모바일 현장 테스트 과정에서 아래 2가지 개선 요구가 확인되었습니다.

1. **모바일 B11 유색 QR 생성 시 수동 입력 불편**:
   - 현재 통합 포털 Tab 3 (`B11 APC Sorting & Grade Colored QR Issuance`)의 `Scan Farm QR or Enter 16-Digit LotID:` 입력창은 QR 스캔 시에는 편리하지만, 번호를 직접 입력할 때는 16자리 전체(`예: 5563467411261109`)를 입력해야 하므로 모바일 환경에서 오타 및 피로도가 큼.
   - 기존처럼 **`FmID(2자리)` + `품목번호(CropCode 3자리)`**만 짧게 입력(또는 선택)해도 해당 로트를 바로 불러와 유색 QR을 생성할 수 있어야 함.
2. **DB 테이블 내 `FmID`와 `lot_id` 분리 가독성 및 일관성 확보**:
   - `lab225_v2.harvest_lots`의 첫 번째 컬럼 `lot_id`(PK)에 기존 v2 행(`01`, `07`, ...)과 신규 v3 행(`5563467411261109`)이 혼재되어 보이고, 농가 2자리 번호 컬럼명이 `farmer_code`로 되어 있어 `FmID` 칸이 직관적으로 구분되지 않음.
   - **`lot_id` (16자리 고유 PK)와 `fmid` (2자리 농가번호 전용 칸)을 명확히 분리**하여 저장·조회하도록 정리 필요.

---

## 2. [작업 1] 모바일 B11 단축 입력(`FmID + 품목번호`) 구현 계획

### 2.1 프론트엔드 UI 개선 ([templates/index.html](../Final_Experiment/5_Unified_FastAPI_Portal/templates/index.html))
- **기존 QR 스캔 입력창 유지 + 단축 패턴 허용**:
  - `apc-qr-scanner-input` (`#apc-qr-scanner-input`)에서 기존 QR URL 및 16자리 `LotID` 입력은 100% 유지.
  - 추가로 `67-411`, `67 411`, `67411`(5자리), `67`(2자리 `FmID`) 형식 입력 시에도 자동 인식하도록 연동.
- **모바일 전용 빠른 입력 바 추가** (`#apc-qr-scanner-input` 바로 아래):
  - `[FmID (2자리, inputmode="numeric", maxlength="2")]` + `[품목 선택 드롭다운: 411 사과 / 412 배 / 413 복숭아 / 415 감귤 / 222 참외 / 223 멜론]` + `[🔍 빠른 조회]` 버튼.
- **대기 로트 드롭다운(`#apc-fmid-select`) 가독성 개선**:
  - 표시 포맷을 `[FmID 67 · 사과(411)] 11/09 · 50kg (B10)` 형태로 핵심 정보를 앞배치해 모바일에서 1탭 선택 가능하게 개선.
- **동일 농가·품목 다중 로트 선택 UI**:
  - 같은 `FmID + CropCode`로 수확일이 다른 `B10/B12` 대기 로트가 2건 이상 조회될 경우, 결과 목록(수확일·수량·현재 단계·16자리 LotID 표시)을 버튼 리스트로 띄워 1탭으로 확정하도록 처리.

### 2.2 백엔드 API 확장 ([app.py](../Final_Experiment/5_Unified_FastAPI_Portal/app.py))
- **대상 엔드포인트**: `POST /api/apc/scan-qr` (현재 718행 부근)
- **조회 우선순위 로직**:
  1. 입력값이 QR URL이거나 16자리 숫자(`^\d{16}$`)인 경우 → 기존대로 `WHERE hl.lot_id = %s` 정확 일치 조회.
  2. 입력값이 `FmID(2자리) + CropCode(3자리)` 패턴 (`67-411`, `67 411`, `67411`) 또는 별도 파라미터(`fmid`, `crop_code`)로 전달된 경우:
     - `harvest_lots`에서 `fmid = %s AND crop_code = %s` 조건 + `stage_events`의 `stage_code IN ('B10', 'B12', 'A11')` 조건으로 최신순 조회.
     - 1건 매칭 시: 즉시 해당 `lot_id` 데이터와 자동 등급 배분 결과를 반환.
     - 2건 이상 매칭 시: `{"ok": True, "multiple": True, "candidates": [...]}` 형태로 반환해 프론트에서 1탭 선택 유도.
  3. 입력값이 2자리 숫자(`^\d{1,2}$`)만 들어온 경우:
     - 레거시 v2 `lot_id = %s` 또는 v3 `fmid = %s` 중 `B10/B12/A11` 대기 로트를 최신순으로 조회(1건 즉시 로드 / 다중 건 선택 리스트 반환).

---

## 3. [작업 2] DB `FmID` 및 `lot_id` 분리 구조 정리 계획

### 3.1 핵심 원칙
- **PK는 반드시 16자리 `lot_id` 유지**: 한 농가(`fmid = '67'`)가 여러 품목(`411`, `412`) 또는 여러 수확일(`261109`, `261122`)에 걸쳐 출하하므로, `sorted_lots`, `stage_events`, `shipments`와의 외래키(`FK`) 기준 키는 16자리 `lot_id`를 유지해야 데이터 무결성이 보장됨.
- **`fmid` 컬럼을 `lot_id` 바로 옆(2번째 컬럼)에 독립 배치**: DB 뷰어(HeidiSQL/Workbench 등)에서도 `lot_id`와 `fmid`를 나란히 직관적으로 확인 가능하게 구성.

### 3.2 `lab225_v2.harvest_lots` 목표 구조
| 순서 | 컬럼명 | v3 신규 예시 | v2 레거시 예시 | 비고 |
| :---: | :--- | :--- | :--- | :--- |
| 1 (PK) | `lot_id` | `5563467411261109` | `07` *(기존 QR 호환 유지)* | 전체 로트 고유 PK |
| 2 | **`fmid`** | **`67`** | **`07`** | **농가 2자리 번호 전용 칸** |
| 3 | `crop_code` | `411` | `411` | aT KAMIS 3자리 품목번호 |
| 4 | `origin_zip` | `55634` | `55630` | 산지 5자리 우편번호 |

### 3.3 AWS RDS 마이그레이션 SQL 초안 (실행 전 백업 필수)
> 아래 SQL은 `farmer_code` → `fmid` 통일안 기준입니다. (실행 전 연구실에서 옵션 확정 후 적용)

```sql
USE `lab225_v2`;

-- 1) farmer_code 컬럼을 fmid로 이름 변경 및 lot_id 바로 뒤(2번째 위치)로 이동
ALTER TABLE `harvest_lots`
  CHANGE COLUMN `farmer_code` `fmid` VARCHAR(10) NULL COMMENT '농가 2자리 번호 (FmID)' AFTER `lot_id`;

-- 2) 기존 v2 레거시 행 및 누락된 v3 행의 fmid 자동 백필
UPDATE `harvest_lots`
SET `fmid` = CASE
    WHEN CHAR_LENGTH(`lot_id`) = 16 AND `lot_id` REGEXP '^[0-9]{16}$' THEN SUBSTRING(`lot_id`, 6, 2)
    ELSE `lot_id`
END
WHERE `fmid` IS NULL OR `fmid` = '';

-- 3) FmID + 품목번호 단축 검색용 복합 인덱스 추가
ALTER TABLE `harvest_lots`
  ADD INDEX `idx_lots_fmid_crop` (`fmid`, `crop_code`, `created_at`);
```

### 3.4 `lab225.qr` (v1 테이블) 일관성 점검
- `lab225.qr`에는 이미 `FmID` 컬럼과 `LotID` 컬럼이 별도로 존재함.
- 모든 쓰기 경로(`app.py`, `Step1_Farm_QR_Creator.py`, `Step3_Sorting_QR_Creator.py`, `pc_qr_scanner.py`, ESP32 `main.cpp`, `bridge_sync.py`)에서:
  - `FmID` = 항상 2자리 농가번호 (`67`)
  - `LotID` = 항상 16자리 통합 코드 (`5563467411261109`)
  로 분리 저장되는지 일괄 검증.

### 3.5 코드 수정 대상 파일 목록
1. [cloud_backend/db_v2/schema_v2.sql](../cloud_backend/db_v2/schema_v2.sql): `harvest_lots.fmid` 컬럼 위치 및 `idx_lots_fmid_crop` 인덱스 반영
2. [cloud_backend/db_v2/bridge_sync.py](../cloud_backend/db_v2/bridge_sync.py): `farmer_code` 참조를 `fmid`로 통일 및 동기화 시 `fmid` 항상 채움
3. [Final_Experiment/5_Unified_FastAPI_Portal/app.py](../Final_Experiment/5_Unified_FastAPI_Portal/app.py): `farmer_code` → `fmid` 반영 + `/api/apc/scan-qr` 단축 검색 및 다중 후보 응답 구현
4. [Final_Experiment/5_Unified_FastAPI_Portal/templates/index.html](../Final_Experiment/5_Unified_FastAPI_Portal/templates/index.html): B11 모바일 빠른 입력 바(`FmID` + `품목`) 및 다중 후보 선택 UI 추가
5. [Final_Experiment/3_Consumer_Dashboard/Step5_Run_Dashboard.py](../Final_Experiment/3_Consumer_Dashboard/Step5_Run_Dashboard.py): `farmer_code` 참조가 있는 쿼리를 `fmid`로 일괄 반영

---

## 4. 연구실 실행 전 최종 확인 체크리스트

내일 연구실에서 진행 결정 시 아래 2가지만 확인하고 바로 착수합니다:

1. **`harvest_lots` 컬럼명 선택**:
   - [ ] **(권장)** 기존 `farmer_code`를 **`fmid`** 로 변경하고 `lot_id` 바로 옆으로 이동 + 관련 파이썬 코드 일괄 반영
   - [ ] *(대안)* `farmer_code`는 그대로 두고 `fmid` 컬럼만 추가
2. **하위 테이블(`sorted_lots`, `stage_events`) 보조 컬럼 여부**:
   - [ ] `harvest_lots`에만 `fmid` 유지 (정규화 표준)
   - [ ] `sorted_lots`, `stage_events`에도 `fmid` 보조 컬럼을 함께 저장 (DB 뷰어 조회 편의 우선)

---

## 5. 적용 후 AWS EC2 배포 명령어 (진행 완료 시)

```bash
cd ~/ColdChain-DigitalTwin-Platform
git pull origin main
sudo systemctl restart coldchain-daemon coldchain-portal
```
