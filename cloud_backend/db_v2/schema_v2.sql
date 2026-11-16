-- ============================================================================
-- ColdChain DigitalTwin Platform - Normalized Relational Schema v2 (lab225_v2)
-- ----------------------------------------------------------------------------
-- 설계 핵심:
--   1. 기존 lab225 원본은 100% 보존하고 독립 스키마 `lab225_v2`에 구축
--   2. 농가 GUI 입력 항목 그대로 `harvest_lots`에 순수 보존 (defect_qty 분리)
--   3. A12 선별 분기 결과를 `sorted_lots` 단일 테이블에 A / B / C / DEFECT로 관리 (방법 A)
--   4. 농가(A00·A01·A02) ~ APC(A10~A15) ~ 판매처(A16) 전 단계 로그 및 블록체인 해시를 `stage_events`로 통합
--   5. 1구간(A02~A10) 및 2구간(A15~A16) 운송과 차량 센서 주행 세션을 `shipments`로 정밀 JOIN
-- ============================================================================

CREATE DATABASE IF NOT EXISTS `lab225_v2`
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE `lab225_v2`;

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------------------------------------------------------
-- 1. 차량 및 센서 단말기 마스터 (vehicles)
-- ----------------------------------------------------------------------------
DROP TABLE IF EXISTS `vehicles`;
CREATE TABLE `vehicles` (
    `device_id`   VARCHAR(50)  NOT NULL COMMENT '센서 보드 고유 ID (carrier-c6-01 ~ 04)',
    `truck_id`    VARCHAR(30)  NOT NULL COMMENT '차량 식별 코드 (truck01 ~ 04)',
    `truck_name`  VARCHAR(60)  NOT NULL COMMENT '대시보드 표시 차량명',
    `mqtt_topic`  VARCHAR(100) NOT NULL COMMENT '구독 MQTT 토픽',
    `is_active`   TINYINT(1)   NOT NULL DEFAULT 1 COMMENT '운용 활성 여부',
    `created_at`  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`device_id`),
    UNIQUE KEY `uq_vehicles_truck_id` (`truck_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO `vehicles` (`device_id`, `truck_id`, `truck_name`, `mqtt_topic`, `is_active`) VALUES
    ('carrier-c6-01', 'truck01', '1호차 (truck01 / carrier-c6-01)', 'coldchain/truck01/sensor', 1),
    ('carrier-c6-02', 'truck02', '2호차 (truck02 / carrier-c6-02)', 'coldchain/truck02/sensor', 1),
    ('carrier-c6-03', 'truck03', '3호차 (truck03 / carrier-c6-03)', 'coldchain/truck03/sensor', 1),
    ('carrier-c6-04', 'truck04', '4호차 (truck04 / carrier-c6-04)', 'coldchain/truck04/sensor', 1);

-- ----------------------------------------------------------------------------
-- 2. 농가 원물 수확 마스터 (harvest_lots) - 농가 GUI 입력 항목 100% 보존
-- ----------------------------------------------------------------------------
DROP TABLE IF EXISTS `harvest_lots`;
CREATE TABLE `harvest_lots` (
    `lot_id`        VARCHAR(50)  NOT NULL COMMENT '원물 고유 번호 (기존 FmID)',
    `origin_zip`    VARCHAR(20)  NOT NULL COMMENT '산지 우편번호 코드 (AC)',
    `fruit_type`    VARCHAR(50)  NOT NULL COMMENT '과실 품목 (FrT: Apples, Pears 등)',
    `variety`       VARCHAR(80)  NOT NULL COMMENT '상세 품종 (Vt: Fuji Apple 등)',
    `farmer_phone`  VARCHAR(30)  NULL     COMMENT '생산자 안심 연락처 (Ct)',
    `cultivation`   VARCHAR(50)  NULL     COMMENT '재배 방식 (Mt: Organic 등)',
    `harvest_no`    INT          NOT NULL DEFAULT 1 COMMENT '수확 회차 (HN)',
    `total_qty`     INT          NOT NULL DEFAULT 0 COMMENT '원물 총 수량 (Qt)',
    `harvest_date`  DATE         NULL     COMMENT '농가 GUI 입력 수확일 (HD 날짜)',
    `storage_date`  DATE         NULL     COMMENT '농가 GUI 입력 저온저장일 (StD)',
    `deliver_date`  DATE         NULL     COMMENT '농가 GUI 입력 출하일 (DD)',
    `ag_practice`   VARCHAR(100) NULL     COMMENT '레거시 농법 기록 보존용 (Rp, 신규 NULL)',
    `current_stage` VARCHAR(10)  NOT NULL DEFAULT 'A02' COMMENT '원물 기준 진행 단계 (A00~A12)',
    `is_test`       TINYINT(1)   NOT NULL DEFAULT 0 COMMENT '0: 정식 실증 데이터, 1: 연습/불완전 테스트',
    `created_at`    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`lot_id`),
    KEY `idx_lots_test_stage` (`is_test`, `current_stage`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------------------------------------------------------
-- 3. APC 선별 등급 및 결점과 분할 테이블 (sorted_lots) - 방법 A 적용
--    SUM(grade_qty) == harvest_lots.total_qty 수량 보존 성립
-- ----------------------------------------------------------------------------
DROP TABLE IF EXISTS `sorted_lots`;
CREATE TABLE `sorted_lots` (
    `pkg_id`         VARCHAR(60) NOT NULL COMMENT '선별 분할 ID (예: 85-A, 85-B, 85-C, 85-DEF)',
    `lot_id`         VARCHAR(50) NOT NULL COMMENT '부모 원물 번호 (harvest_lots.lot_id)',
    `grade_code`     VARCHAR(15) NOT NULL COMMENT '등급 코드: A / B / C / DEFECT',
    `grade_label_ko` VARCHAR(20) NOT NULL COMMENT '한글 등급명: 상 / 중 / 하 / 결점과',
    `grade_qty`      INT         NOT NULL DEFAULT 0 COMMENT '해당 등급 배분 수량',
    `is_shippable`   TINYINT(1)  NOT NULL DEFAULT 1 COMMENT '1: 유색QR 발행 출하 정품, 0: 결점과 제외',
    `current_stage`  VARCHAR(15) NOT NULL DEFAULT 'A12' COMMENT '정품 진행 단계(A12~A16) 또는 REJECTED',
    `sorted_at`      DATETIME    NOT NULL COMMENT 'A12 선별 확정 시각 (APC_RT)',
    PRIMARY KEY (`pkg_id`),
    UNIQUE KEY `uq_sorted_lot_grade` (`lot_id`, `grade_code`),
    KEY `idx_sorted_shippable` (`lot_id`, `is_shippable`),
    CONSTRAINT `fk_sorted_lots_lot` FOREIGN KEY (`lot_id`)
        REFERENCES `harvest_lots` (`lot_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------------------------------------------------------
-- 4. 전 주기 공정 스캔 타임라인 & 블록체인 해시 원장 (stage_events)
--    농가(A00·A01·A02) + APC 공통(A10·A11·A12) + 등급 패키지별(A13·A14·A15·A16)
-- ----------------------------------------------------------------------------
DROP TABLE IF EXISTS `stage_events`;
CREATE TABLE `stage_events` (
    `event_id`   BIGINT        NOT NULL AUTO_INCREMENT,
    `lot_id`     VARCHAR(50)  NOT NULL COMMENT '원물 번호 (전 단계 공통 참조)',
    `pkg_id`     VARCHAR(60)  NULL     COMMENT 'A13~A16일 때 정품 패키지 ID (A00~A12는 NULL)',
    `stage_code` VARCHAR(10)  NOT NULL COMMENT '공정 코드: A00, A01, A02, A10~A16',
    `event_at`   DATETIME     NOT NULL COMMENT '단계 발생 시각 (KST)',
    `lat`        DOUBLE       NULL     COMMENT '스캔/처리 지점 위도',
    `lng`        DOUBLE       NULL     COMMENT '스캔/처리 지점 경도',
    `temp`       FLOAT        NULL     COMMENT '저장고/현장 온도 (A01, A14 등)',
    `humi`       FLOAT        NULL     COMMENT '저장고/현장 습도 (A01, A14 등)',
    `tx_hash`    VARCHAR(64)  NULL     COMMENT '블록체인 무결성 SHA-256 해시',
    PRIMARY KEY (`event_id`),
    UNIQUE KEY `uq_stage_event_once` (`lot_id`, (COALESCE(`pkg_id`, _utf8mb4'LOT')), `stage_code`),
    KEY `idx_events_lot_time` (`lot_id`, `event_at`),
    KEY `idx_events_pkg_stage` (`pkg_id`, `stage_code`),
    CONSTRAINT `fk_events_lot` FOREIGN KEY (`lot_id`)
        REFERENCES `harvest_lots` (`lot_id`) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT `fk_events_pkg` FOREIGN KEY (`pkg_id`)
        REFERENCES `sorted_lots` (`pkg_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------------------------------------------------------
-- 5. 차량 주행 세션 마스터 (transport_runs)
--    실차 도로 주행(FIELD_DRIVE)과 벤치(BENCH)·모의(MOCK)·대기노이즈(NOISE) 분리
-- ----------------------------------------------------------------------------
DROP TABLE IF EXISTS `transport_runs`;
CREATE TABLE `transport_runs` (
    `run_id`        VARCHAR(100) NOT NULL COMMENT '주행 세션 고유 ID',
    `device_id`     VARCHAR(50)  NOT NULL COMMENT '차량 센서 보드 ID',
    `run_type`      VARCHAR(20)  NOT NULL DEFAULT 'FIELD_DRIVE' COMMENT 'FIELD_DRIVE / BENCH / MOCK / NOISE',
    `started_at`    DATETIME     NULL     COMMENT '세션 첫 패킷 시각 (KST)',
    `ended_at`      DATETIME     NULL     COMMENT '세션 마지막 패킷 시각 (KST)',
    `packet_cnt`    INT          NOT NULL DEFAULT 0 COMMENT '총 적재 패킷 수',
    `valid_gps_cnt` INT          NOT NULL DEFAULT 0 COMMENT '유효 GPS 좌표 패킷 수',
    `min_temp`      FLOAT        NULL     COMMENT '구간 최저 온도',
    `max_temp`      FLOAT        NULL     COMMENT '구간 최고 온도',
    `avg_temp`      FLOAT        NULL     COMMENT '구간 평균 온도',
    `max_g_force`   FLOAT        NULL     COMMENT '구간 최대 충격량 (G)',
    `max_speed`     FLOAT        NULL     COMMENT '구간 최고 속도 (km/h)',
    `shock_cnt`     INT          NOT NULL DEFAULT 0 COMMENT '1.8G 이상 강한 충격 횟수',
    PRIMARY KEY (`run_id`),
    KEY `idx_runs_dev_type_start` (`device_id`, `run_type`, `started_at`),
    CONSTRAINT `fk_runs_vehicle` FOREIGN KEY (`device_id`)
        REFERENCES `vehicles` (`device_id`) ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------------------------------------------------------
-- 6. 운송 구간 화물-차량 매핑 테이블 (shipments) - 핵심 JOIN 연결 다리
--    leg_no=1: 산지출하(A02) -> APC입고(A10)
--    leg_no=2: APC출하(A15)  -> 판매처도착(A16)
-- ----------------------------------------------------------------------------
DROP TABLE IF EXISTS `shipments`;
CREATE TABLE `shipments` (
    `shipment_id`    BIGINT       NOT NULL AUTO_INCREMENT,
    `leg_no`         TINYINT      NOT NULL COMMENT '1: 산지->APC 1구간, 2: APC->판매처 2구간',
    `lot_id`         VARCHAR(50)  NOT NULL COMMENT '원물 번호',
    `pkg_id`         VARCHAR(60)  NULL     COMMENT '2구간일 때 정품 패키지 ID (1구간은 NULL)',
    `device_id`      VARCHAR(50)  NULL     COMMENT '운송 담당 차량 보드 ID',
    `run_id`         VARCHAR(100) NULL     COMMENT '매칭된 주행 세션 ID (transport_runs.run_id)',
    `departed_at`    DATETIME     NOT NULL COMMENT '운송 구간 출발 시각 (A02 / A15)',
    `arrived_at`     DATETIME     NULL     COMMENT '운송 구간 도착 시각 (A10 / A16)',
    `status`         VARCHAR(20)  NOT NULL DEFAULT 'IN_TRANSIT' COMMENT 'IN_TRANSIT / ARRIVED',
    `gps_points_cnt` INT          NOT NULL DEFAULT 0 COMMENT '매칭된 실측 도로 궤적 포인트 수',
    `avg_temp`       FLOAT        NULL     COMMENT '해당 구간 운송 평균 온도',
    `max_g_force`    FLOAT        NULL     COMMENT '해당 구간 운송 최대 충격량',
    PRIMARY KEY (`shipment_id`),
    UNIQUE KEY `uq_shipment_leg` (`lot_id`, (COALESCE(`pkg_id`, _utf8mb4'LOT')), `leg_no`),
    KEY `idx_shipments_run_window` (`run_id`, `departed_at`, `arrived_at`),
    KEY `idx_shipments_device_status` (`device_id`, `status`),
    CONSTRAINT `fk_shipments_lot` FOREIGN KEY (`lot_id`)
        REFERENCES `harvest_lots` (`lot_id`) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT `fk_shipments_pkg` FOREIGN KEY (`pkg_id`)
        REFERENCES `sorted_lots` (`pkg_id`) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT `fk_shipments_vehicle` FOREIGN KEY (`device_id`)
        REFERENCES `vehicles` (`device_id`) ON UPDATE CASCADE,
    CONSTRAINT `fk_shipments_run` FOREIGN KEY (`run_id`)
        REFERENCES `transport_runs` (`run_id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------------------------------------------------------
-- 7. 5초 주기 순수 시계열 센서 패킷 (sensor_telemetry)
-- ----------------------------------------------------------------------------
DROP TABLE IF EXISTS `sensor_telemetry`;
CREATE TABLE `sensor_telemetry` (
    `telemetry_id` BIGINT       NOT NULL AUTO_INCREMENT,
    `run_id`       VARCHAR(100) NOT NULL COMMENT '소속 주행 세션 ID',
    `device_id`    VARCHAR(50)  NOT NULL COMMENT '차량 센서 보드 ID',
    `measured_at`  DATETIME     NOT NULL COMMENT '측정 시각 (KST 정규화)',
    `temperature`  FLOAT        NOT NULL DEFAULT 0 COMMENT '온도 (℃)',
    `humidity`     FLOAT        NOT NULL DEFAULT 0 COMMENT '습도 (%)',
    `lux`          FLOAT        NOT NULL DEFAULT 0 COMMENT '조도 (lx)',
    `g_force`      FLOAT        NOT NULL DEFAULT 1.0 COMMENT '합성 충격 가속도 (G)',
    `speed`        FLOAT        NOT NULL DEFAULT 0 COMMENT '주행 속도 (km/h)',
    `lat`          DOUBLE       NOT NULL DEFAULT 0 COMMENT '위도',
    `lng`          DOUBLE       NOT NULL DEFAULT 0 COMMENT '경도',
    `gps_state`    VARCHAR(15)  NOT NULL DEFAULT 'INDOOR' COMMENT 'FIX / TUNNEL / INDOOR',
    `event_type`   VARCHAR(20)  NOT NULL DEFAULT 'NORMAL' COMMENT 'NORMAL / SHOCK / TEMP_JUMP / LUX_JUMP / ANOMALY',
    `raw_status`   VARCHAR(60)  NULL     COMMENT '원본 상태 문자열 보존',
    PRIMARY KEY (`telemetry_id`),
    UNIQUE KEY `uq_telemetry_dev_time_run` (`device_id`, `measured_at`, `run_id`),
    KEY `idx_telemetry_run_time` (`run_id`, `measured_at`),
    KEY `idx_telemetry_dev_time` (`device_id`, `measured_at`),
    CONSTRAINT `fk_telemetry_run` FOREIGN KEY (`run_id`)
        REFERENCES `transport_runs` (`run_id`) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT `fk_telemetry_vehicle` FOREIGN KEY (`device_id`)
        REFERENCES `vehicles` (`device_id`) ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------------------------------------------------------
-- 8. 실시간 증분 브릿지 워터마크 (_sync_watermark)
--    ESP32 스캐너(lab225.qr) 및 기존 데몬(lab225.sensor_data) 신규 행을
--    0.01초 만에 lab225_v2로 증분 동기화하기 위한 커서 테이블
-- ----------------------------------------------------------------------------
DROP TABLE IF EXISTS `_sync_watermark`;
CREATE TABLE `_sync_watermark` (
    `source_table` VARCHAR(40) NOT NULL,
    `last_id`      BIGINT      NOT NULL DEFAULT 0,
    `updated_at`   DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`source_table`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

SET FOREIGN_KEY_CHECKS = 1;
