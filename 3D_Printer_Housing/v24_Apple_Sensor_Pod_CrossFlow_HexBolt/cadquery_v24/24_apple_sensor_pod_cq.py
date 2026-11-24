"""
Cold Chain Digital Twin Platform
v24 Apple Sensor Pod Housing — SHT45 CROSS-FLOW VENTILATION & M4/M3x20mm HEX BOLT EDITION
(CadQuery 2.8+ / OpenCASCADE B-Rep + CQ-Editor Dual-Mode Master Script)

주요 설계 반영 사항 (v23 대비 전면 개선):
  1. 2510 액티브 냉각팬 홀더 완전 제거 -> 내부 여유 공간 확보 및 구조 단순화.
  2. SHT45 온습도 센서 기준 좌(-X)·우(+X) 양측 맞통풍구(Cross-Flow Wind Tunnel) 신설:
     - PCB 권장 장착 방향(Top -> 전면 돔 +Y, Bottom -> 후면 배터리 -Y, USB -> 상단 +Z) 기준
       SHT45 위치(Z = -15.3 ~ +2.5 mm, Y = -12.6 ~ -1.6 mm) 양옆 후면 측벽에
       4단 대칭 맞통풍 슬릿(Z = -12.5, -8.5, -4.5, -0.5 mm, Y = -11.0 ~ -2.5 mm)을 뚫어
       외부 기류가 SHT45 센서 위를 직선 관통하도록 설계 (GPS 홀더 및 볼트 보스 간섭 0%).
     - 상단 배기 루버(Z = +15 ~ +50 mm) & 하단 흡기 루버(Z = -48 ~ -15 mm)가
       사과 외벽(Z = -44.56 ~ +47.31 mm)을 100% 관통하도록 수정 (v23 CQ 막힘 버그 해결).
  3. 4개소 외곽 육각 렌치 볼트 체결 (DIN 912 M4x20mm 기본 / M3x20mm 옵션 전환 지원):
     - 후면 외벽에서 삽입 -> Y = -10.0 mm 평면 좌면(Dome-Up 무서포트) -> Y = -10..0 (10mm 통과)
       -> 전면 쉘 Y = 0..+12.5 mm 셀프태핑 체결 (볼트 끝단 Y = +10.0 mm, 전면 겉면 구멍 0개).
     - 4개 강철 볼트가 분할면(Y = 0)을 관통해 전단 정렬 핀 역할까지 동시에 수행.
  4. 실제 CarrierBoard_BeetleC6_EdgeUSB_50x50 양면 실장 부품 6종 간섭 0% 해결:
     - 전면 M3 스탠드오프 반경을 r = 4.0 -> 3.00 mm(Ø6.0 mm)로 슬림화하고 보강 리브를
       PCB 바깥쪽(±Z)으로만 연장하여 BH1750/SHT45(홀 중심에서 3.20 mm)와 간섭 0% 달성.
     - 후면 5000mAh 배터리(55x68x10mm) 바닥을 Y = -26.0 mm로 1.5 mm 심화(최소 외벽 2.30 mm)하여
       벨크로(2 mm) 포함 시에도 PCB 뒷면 센서와 +1.4 ~ +2.4 mm 여유 공간 확보.
  5. BH1750 조도 센서 전용 채광창 복원 (전면 쉘 우측 +X, Z = +8.5, +14.0 mm, 65도 무서포트).
  6. 좌측(-X) 외장 GPS 세라믹 안테나(20 x 5 x 7 mm) 슬라이드 포켓 유지 (ATGM336H 최단 배선).

실행 방법:
  - CQ-Editor: File -> Open -> F5 (상단 VIEW_MODE / BOLT_SPEC 변경 가능)
  - 터미널 일괄 빌드: python 24_apple_sensor_pod_cq.py
"""

from __future__ import annotations

import math
import shutil
from pathlib import Path
import cadquery as cq

# ============================================================================
# 0. CQ-Editor 화면 표시 모드 & 외곽 볼트 규격 설정
# VIEW_MODE 옵션: "assembly", "exploded", "cross_section", "print_layout",
#                 "front_shell", "rear_shell", "stem"
# BOLT_SPEC 옵션: "M4" (추천: M4x20mm DIN 912 육각 렌치 볼트, PLA 반복 개폐 내구성 우수)
#                 "M3" (옵션: M3x20mm DIN 912 육각 렌치 볼트, PCB 나사와 공구 통일)
# ============================================================================
VIEW_MODE = "assembly"
BOLT_SPEC = "M4"

# ============================================================================
# 1. 설계 파라미터 정의 (실측 CarrierBoard v10 + PL105568 + DIN 912 20mm 기준)
# ============================================================================
WALL_T = 3.0
CLEARANCE = 0.25

# PCB 규격 (CarrierBoard_BeetleC6_EdgeUSB_50x50: 50 x 50 x 1.6 mm, M3 홀 피치 43 x 43 mm)
PCB_W = 50.0
PCB_H = 50.0
PCB_T = 1.6
HOLE_PITCH = 43.0
PCB_Z_CENTER = 3.0
PCB_Y_MOUNT = 0.0
PCB_Y_BACK = PCB_Y_MOUNT - PCB_T  # Y = -1.6 mm

# 후면 5000mAh 배터리 베이 (JRF PL105568: 55 x 68 x 10 mm + 2mm 벨크로)
BATTERY_FLOOR_Y = -26.0           # 기존 -24.5 -> -26.0 mm (외벽 최소 2.30 mm 유지, 후면 여유 +1.5mm)
BATTERY_BAY_W = 56.4
BATTERY_BAY_H = 70.4
BATTERY_BAY_Z_CENTER = -0.5

# 4x 외곽 육각 렌치 볼트 보스 좌표 (|X| - r_boss = 35.0 - 6.5 = 28.50 > 28.20 배터리 베이!)
BOLT_PTS: list[tuple[float, float]] = [
    (-35.0, 25.0),
    (35.0, 25.0),
    (-35.0, -22.0),
    (35.0, -22.0),
]
BOLT_BOSS_R = 6.50
BOLT_SEAT_Y = -10.0               # 후면 쉘 볼트 머리 안착 좌면 (후면 통과 10mm + 전면 체결 10mm = 20mm!)
BOLT_FRONT_HOLE_DEPTH = 12.5      # 볼트 끝단(Y=+10.0) 대비 +2.5 mm 바닥 여유 (전면 외벽 관통 없음)

# DIN 912 (ISO 4762) 20mm 육각 렌치 볼트 규격표
BOLT_SPECS: dict[str, dict[str, float]] = {
    "M4": {
        "cbore_r": 4.10,          # 카운터보어 Ø8.20 mm (DIN 912 M4 머리 Ø7.0 x 4.0 mm + 3mm 육각렌치)
        "clear_r": 2.20,          # 후면 통과홀 Ø4.40 mm
        "pilot_r": 1.775,         # 전면 PLA 셀프태핑 파일럿 홀 Ø3.55 mm
        "head_r": 3.50,           # 가상 목업용 머리 반경 (Ø7.0 mm)
        "head_h": 4.00,           # 가상 목업용 머리 높이 (4.0 mm)
        "shaft_r": 2.00,          # 가상 목업용 나사 반경 (Ø4.0 mm)
        "shaft_len": 20.0,        # 볼트 나사 길이 20.0 mm
    },
    "M3": {
        "cbore_r": 3.30,          # 카운터보어 Ø6.60 mm (DIN 912 M3 머리 Ø5.5 x 3.0 mm + 2.5mm 육각렌치)
        "clear_r": 1.70,          # 후면 통과홀 Ø3.40 mm
        "pilot_r": 1.375,         # 전면 PLA 셀프태핑 파일럿 홀 Ø2.75 mm
        "head_r": 2.75,           # 가상 목업용 머리 반경 (Ø5.5 mm)
        "head_h": 3.00,           # 가상 목업용 머리 높이 (3.0 mm)
        "shaft_r": 1.50,          # 가상 목업용 나사 반경 (Ø3.0 mm)
        "shaft_len": 20.0,        # 볼트 나사 길이 20.0 mm
    },
}

# 좌측(-X) 외장형 GPS 세라믹 안테나 규격 (20 x 5 x 7 mm) — 전면 쉘(Y > 0) 내장
GPS_LEN_Z = 21.6
GPS_WID_X = 7.6
GPS_DEP_Y = 11.0
GPS_WALL = 2.4
GPS_X_CENTER = -36.5
GPS_Z_CENTER = 1.5                # Z = -9.3 ~ +12.3 (외벽 포함 -11.7 ~ +14.7, 볼트 보스 간섭 0%)

# 사과 외벽 회전 프로파일 (R, Z) - 외경 100.0mm (R_max = 50.0mm), 높이 91.87mm (Z = -44.56 ~ +47.31)
APPLE_OUTER_PROFILE: list[tuple[float, float]] = [
    (0.00, -37.32), (1.15, -38.01), (2.41, -38.70), (3.79, -39.39),
    (5.17, -40.08), (6.66, -40.65), (8.27, -41.34), (9.88, -42.03),
    (11.60, -42.60), (13.44, -43.18), (15.39, -43.75), (17.46, -44.10),
    (19.52, -44.44), (21.70, -44.56), (24.00, -44.44), (26.18, -44.21),
    (28.36, -43.64), (30.55, -42.83), (32.61, -41.80), (34.68, -40.54),
    (36.63, -38.93), (38.47, -37.09), (40.31, -34.91), (41.92, -32.61),
    (43.52, -29.97), (44.90, -27.10), (46.16, -24.00), (47.20, -20.67),
    (48.12, -17.23), (48.81, -13.67), (49.38, -9.99), (49.84, -6.20),
    (49.95, -2.41), (50.00, 1.38), (49.84, 5.05), (49.49, 8.73),
    (49.04, 12.29), (48.35, 15.73), (47.43, 18.95), (46.39, 22.16),
    (45.25, 25.15), (43.87, 28.02), (42.37, 30.78), (40.77, 33.42),
    (39.04, 35.83), (37.09, 38.13), (35.14, 40.31), (32.96, 42.26),
    (30.66, 43.98), (28.25, 45.48), (25.72, 46.51), (23.20, 47.20),
    (20.67, 47.31), (18.14, 46.85), (15.73, 46.05), (13.44, 44.79),
    (11.25, 43.41), (9.19, 41.80), (7.35, 40.31), (5.63, 38.93),
    (4.13, 37.90), (2.76, 37.09), (1.49, 36.52), (0.00, 36.17),
]

# 사과 내벽 회전 프로파일 (R, Z) - 내경 93.24mm, 높이 82.91mm
APPLE_INNER_PROFILE: list[tuple[float, float]] = [
    (0.00, -33.30), (1.15, -33.99), (2.41, -34.68), (3.79, -35.25),
    (5.28, -35.94), (6.89, -36.63), (8.61, -37.32), (10.45, -38.01),
    (12.29, -38.59), (14.24, -39.16), (16.31, -39.62), (18.49, -39.96),
    (20.79, -40.19), (23.08, -40.31), (25.38, -40.08), (27.56, -39.62),
    (29.74, -38.93), (31.69, -38.01), (33.65, -36.86), (35.37, -35.48),
    (37.09, -33.76), (38.59, -31.92), (39.96, -29.86), (41.23, -27.56),
    (42.37, -25.03), (43.41, -22.39), (44.21, -19.52), (44.90, -16.54),
    (45.48, -13.44), (45.93, -10.22), (46.28, -7.01), (46.51, -3.67),
    (46.62, -0.34), (46.58, 2.99), (46.28, 6.20), (45.93, 9.42),
    (45.36, 12.52), (44.56, 15.50), (43.64, 18.49), (42.60, 21.24),
    (41.34, 23.89), (39.96, 26.41), (38.36, 28.82), (36.63, 31.01),
    (34.91, 33.07), (32.96, 35.03), (30.89, 36.75), (28.71, 38.36),
    (26.53, 39.73), (24.23, 40.88), (21.82, 41.80), (19.41, 42.37),
    (17.00, 42.60), (15.85, 42.49), (12.52, 41.92), (10.34, 41.00),
    (8.38, 39.85), (6.55, 38.59), (4.94, 37.32), (3.56, 36.29),
    (2.30, 35.48), (1.15, 34.80), (0.00, 34.22),
]


# ============================================================================
# 2. 공통 기하학 헬퍼 함수 (CadQuery B-Rep)
# ============================================================================
def make_revolved_apple(profile: list[tuple[float, float]], use_spline: bool = False) -> cq.Workplane:
    """XZ 평면에 (R, Z) 단면을 그린 뒤 글로벌 Z축 기준으로 360도 회전시킨다."""
    wp = cq.Workplane("XZ")
    if use_spline:
        wp = wp.moveTo(*profile[0]).spline(profile[1:]).close()
    else:
        wp = wp.polyline(profile).close()
    return wp.revolve(360, (0, 0, 0), (0, 1, 0))


def make_shared_cutouts() -> cq.Workplane:
    """
    전·후면 공통 기능성 절삭부:
      1) 상단 사과 꼭지 플러그 소켓 홈 (Ø5.0 mm)
      2) 하단 냉기 유입 루버 (Z = -48 ~ -15 mm, 사과 바닥 -44.56 mm 100% 관통)
      3) 상단 열기 배출 루버 (Z = +15 ~ +50 mm, 사과 상단 +47.31 mm 100% 관통!)
    """
    # 1) 상단 꼭지 소켓 (Y = +1.5 mm, Z = +29 ~ +43 mm)
    cutouts = (
        cq.Workplane("XY")
        .workplane(offset=29.0)
        .center(0.0, 1.5)
        .circle(2.5)
        .extrude(14.0)
    )

    # 2) & 3) 상·하단 굴뚝 효과(Stack Effect) 자연대류 루버 (65도 물방울 지붕 -> 서포트 0%)
    for x_v in (-12.0, 0.0, 12.0):
        for y_sign in (-1.0, 1.0):
            sk_louver = (
                cq.Sketch()
                .arc((x_v, y_sign * 14.0), 1.8, 0.0, 360.0)
                .arc((x_v, y_sign * 19.0), 0.35, 0.0, 360.0)
                .hull()
            )
            # 하단 외벽 Z_min = -44.56 -> -48.0 ~ -15.0 (33.0mm 돌출, 100% 관통)
            intake = cq.Workplane("XY").workplane(offset=-48.0).placeSketch(sk_louver).extrude(33.0)
            # 상단 외벽 Z_max = +47.31 -> +15.0 ~ +50.0 (35.0mm 돌출, 100% 관통!)
            exhaust = cq.Workplane("XY").workplane(offset=15.0).placeSketch(sk_louver).extrude(35.0)
            cutouts = cutouts.union(intake).union(exhaust)

    return cutouts


def make_sht45_crossflow_cutouts() -> cq.Workplane:
    """
    SHT45 온습도 센서 기준 좌(-X)·우(+X) 양측 맞통풍구(Cross-Flow Wind Tunnel):
      - SHT45 실제 영역: Z = -15.3 ~ +2.5 mm, Y = -12.6 ~ -1.6 mm (후면 쉘 공간, 배터리 앞쪽)
      - 좌·우 측벽 모두 Z = -12.5, -8.5, -4.5, -0.5 mm 4단 슬릿(높이 2.6mm, 깊이 Y = -11.0 ~ -2.5 mm)
      - -Y 방향으로 65도 물방울 꼭짓점(Y = -13.6 mm) 적용 -> 후면 쉘 Dome-Up 출력 시 서포트 0%!
      - 볼트 보스(Z >= +18.5, Z <= -15.5) 및 전면 GPS 홀더(Y > 0)와 간섭 0%!
    """
    crossflow: cq.Workplane | None = None
    for z_s in (-12.5, -8.5, -4.5, -0.5):
        # Workplane("YZ")의 로컬 (x, y)는 글로벌 (+Y, +Z), 기본 돌출 법선은 글로벌 +X
        sk_slot = (
            cq.Sketch()
            .arc((-3.0, z_s), 1.3, 0.0, 360.0)
            .arc((-10.5, z_s), 1.3, 0.0, 360.0)
            .arc((-13.4, z_s), 0.35, 0.0, 360.0)
            .hull()
        )
        # 우측(+X) 측벽 관통 (X = +34.0 ~ +56.0 mm)
        right_slot = cq.Workplane("YZ").workplane(offset=34.0).placeSketch(sk_slot).extrude(22.0)
        # 좌측(-X) 측벽 관통 (X = -56.0 ~ -34.0 mm)
        left_slot = cq.Workplane("YZ").workplane(offset=-56.0).placeSketch(sk_slot).extrude(22.0)
        pair = right_slot.union(left_slot)
        crossflow = pair if crossflow is None else crossflow.union(pair)

    assert crossflow is not None
    return crossflow


def make_bh1750_window_cutouts() -> cq.Workplane:
    """
    BH1750 조도 센서 전용 채광창 (전면 쉘 우측 +X 측벽):
      - 방향 C 기준 BH1750 위치: X = +10.8 ~ +24.7 mm, Z = +2.8 ~ +21.3 mm, Y = 0 ~ +12.0 mm
      - Z = +8.5, +14.0 mm 2단 광폭 슬릿 (Y = +4.0 ~ +13.5 mm + 65도 물방울 지붕 Y = +17.8 mm)
      - 전면 쉘 Dome-Up 출력 시 서포트 0% & 우상단 볼트 보스(Z >= +18.5 mm)와 간섭 0%!
    """
    window: cq.Workplane | None = None
    for z_w in (8.5, 14.0):
        sk_win = (
            cq.Sketch()
            .arc((4.2, z_w), 2.1, 0.0, 360.0)
            .arc((13.0, z_w), 2.1, 0.0, 360.0)
            .arc((17.6, z_w), 0.35, 0.0, 360.0)
            .hull()
        )
        slot = cq.Workplane("YZ").workplane(offset=32.0).placeSketch(sk_win).extrude(24.0)
        window = slot if window is None else window.union(slot)

    assert window is not None
    return window


# ============================================================================
# 3. 후면 쉘 (REAR SHELL - 심화 배터리 바닥 + 4x 볼트 카운터보어 + SHT45 좌우 맞통풍구)
# ============================================================================
def build_rear_shell(
    outer: cq.Workplane,
    hollow_apple: cq.Workplane,
    bolt_spec: str = BOLT_SPEC,
) -> cq.Workplane:
    spec = BOLT_SPECS[bolt_spec]

    rear_half_box = cq.Workplane("XY").transformed(offset=(0.0, -70.0, 0.0)).box(140.0, 140.0, 140.0)
    shell_body = hollow_apple.intersect(rear_half_box)

    # 평면 벨크로 배터리 바닥 플랫폼 (Y = -52.0 ~ BATTERY_FLOOR_Y = -26.0 mm)
    platform_h = 26.0
    platform_cy = BATTERY_FLOOR_Y - platform_h / 2.0
    velcro_platform = cq.Workplane("XY").transformed(offset=(0.0, platform_cy, 0.0)).box(140.0, platform_h, 140.0)
    internal_union = shell_body.union(velcro_platform)

    # 4x 외곽 볼트 보스 (Y = 0.0에서 후면 사과 외벽까지 통째로 융합 -> 카운터보어 벽 두께 2.4mm+ 보장)
    # Workplane("XZ")의 기본 법선은 글로벌 -Y 방향이므로 extrude(+36.0)는 Y = 0 -> -36.0 mm
    for px, pz in BOLT_PTS:
        norm_len = math.hypot(px, pz)
        dir_x, dir_z = px / norm_len, pz / norm_len
        sk_boss = (
            cq.Sketch()
            .arc((px, pz), BOLT_BOSS_R, 0.0, 360.0)
            .arc((px + dir_x * 11.0, pz + dir_z * 11.0), BOLT_BOSS_R, 0.0, 360.0)
            .hull()
        )
        boss_col = cq.Workplane("XZ").placeSketch(sk_boss).extrude(36.0)
        internal_union = internal_union.union(boss_col)

    # 사과 외벽 안쪽으로 정밀 트리밍
    rear = outer.intersect(internal_union)

    # 5000mAh 배터리 수납 사각 베이 절삭 (Y = +0.5 -> BATTERY_FLOOR_Y + 0.02 = -25.98 mm)
    bay_depth = abs(BATTERY_FLOOR_Y) + 0.48  # 26.48 mm
    battery_bay_cut = (
        cq.Workplane("XZ")
        .workplane(offset=-0.5)  # offset=-0.5 on XZ(-Y normal) -> Y = +0.5 mm
        .center(0.0, BATTERY_BAY_Z_CENTER)
        .rect(BATTERY_BAY_W, BATTERY_BAY_H)
        .extrude(bay_depth)      # Y = +0.5 -> -25.98 mm
        .edges("|Y")
        .fillet(2.2)
    )
    rear = rear.cut(battery_bay_cut)

    # 4x 육각 렌치 볼트 통과홀(Y = 0..-10) + 카운터보어 터널(Y = -10..-38)
    # Dome-Up 출력 시 Z_print=0..10이 좁은 통과홀, Z_print=10..30이 넓은 카운터보어 -> 오버행 0%, 서포트 0%!
    seat_depth = abs(BOLT_SEAT_Y)  # 10.0 mm
    for px, pz in BOLT_PTS:
        # 1) 통과홀 (Y = +0.5 ~ -10.5 mm)
        clear_hole = (
            cq.Workplane("XZ")
            .workplane(offset=-0.5)
            .center(px, pz)
            .circle(spec["clear_r"])
            .extrude(seat_depth + 1.0)
        )
        # 2) 카운터보어 터널 (Y = -10.0 ~ -38.0 mm, 볼트 머리 + 육각렌치 진입)
        cbore_hole = (
            cq.Workplane("XZ")
            .workplane(offset=seat_depth)  # Y = -10.0 mm
            .center(px, pz)
            .circle(spec["cbore_r"])
            .extrude(28.0)                 # Y = -10.0 -> -38.0 mm
        )
        rear = rear.cut(clear_hole).cut(cbore_hole)

    # 공통 절삭부(꼭지, 상·하단 루버) + SHT45 좌·우 맞통풍구 적용
    rear = rear.cut(make_shared_cutouts()).cut(make_sht45_crossflow_cutouts())
    return rear


# ============================================================================
# 4. 전면 쉘 (FRONT SHELL - 4x 볼트 체결 보스 + 슬림 PCB 스탠드오프 + GPS 홀더 + BH1750 채광창)
# ============================================================================
def build_front_shell(
    outer: cq.Workplane,
    hollow_apple: cq.Workplane,
    bolt_spec: str = BOLT_SPEC,
) -> cq.Workplane:
    spec = BOLT_SPECS[bolt_spec]

    front_half_box = cq.Workplane("XY").transformed(offset=(0.0, 70.0, 0.0)).box(140.0, 140.0, 140.0)
    internal_union = hollow_apple.intersect(front_half_box)

    # A. 4x 전면 볼트 체결 보스 (r = 6.50 mm, Y = 0.0 베드 바닥 밀착 -> Y = +18mm + 테이퍼 +25mm)
    # Workplane("XZ")의 법선은 -Y이므로 음수 돌출 extrude(-L)가 글로벌 +Y 방향!
    for px, pz in BOLT_PTS:
        norm_len = math.hypot(px, pz)
        dir_x, dir_z = px / norm_len, pz / norm_len
        sk_top = (
            cq.Sketch()
            .arc((px, pz), BOLT_BOSS_R, 0.0, 360.0)
            .arc((px + dir_x * 11.0, pz + dir_z * 11.0), BOLT_BOSS_R, 0.0, 360.0)
            .hull()
        )
        sk_bot = cq.Sketch().push([(px + dir_x * 3.0, pz + dir_z * 3.0)]).circle(5.5)

        boss_lower = cq.Workplane("XZ").placeSketch(sk_top).extrude(-18.0)  # Y = 0 -> +18.0 mm
        boss_taper = (
            cq.Workplane("XZ")
            .workplane(offset=-18.0)  # Y = +18.0 mm
            .placeSketch(sk_top, sk_bot.moved(cq.Location(cq.Vector(0.0, 0.0, -7.0))))  # -> Y = +25.0 mm
            .loft(ruled=True)
        )
        internal_union = internal_union.union(boss_lower).union(boss_taper)

    # B. 4x 슬림 PCB 고정 스탠드오프 (r = 3.00 mm) + PCB 바깥쪽(±Z) 외벽 직결 보강 리브
    # BH1750 / SHT45는 M3 홀 중심에서 3.20 mm 거리 -> r = 3.00 mm로 모든 방향에서 간섭 0%!
    for dx in (-1, 1):
        for dz in (-1, 1):
            x_pos = dx * (HOLE_PITCH / 2.0)
            z_pos = PCB_Z_CENTER + dz * (HOLE_PITCH / 2.0)
            rib_len_z = 16.5 if dz > 0 else 20.0
            rib_target_x = x_pos + dx * 3.5
            rib_target_z = z_pos + dz * rib_len_z

            sk_rib = (
                cq.Sketch()
                .arc((x_pos, z_pos), 3.00, 0.0, 360.0)
                .arc((rib_target_x, rib_target_z), 3.60, 0.0, 360.0)
                .hull()
            )
            standoff_monolith = (
                cq.Workplane("XZ")
                .workplane(offset=-PCB_Y_MOUNT)  # Y = 0.0 mm
                .placeSketch(sk_rib)
                .extrude(-46.0)                  # Y = 0.0 -> +46.0 mm (외벽과 완전 융합)
            )
            internal_union = internal_union.union(standoff_monolith)

    # C. 좌측(-X) 내장형 GPS 세라믹 안테나 홀더 (20 x 5 x 7 mm, 전면 쉘 Y = 0 ~ +11 mm)
    gps_outer_h = GPS_LEN_Z + 2.0 * GPS_WALL
    sk_gps_base = cq.Sketch().push([(-40.5, GPS_Z_CENTER)]).rect(19.0, gps_outer_h)
    sk_gps_tip = cq.Sketch().push([(-45.5, GPS_Z_CENTER)]).rect(9.0, gps_outer_h - 4.0)

    gps_base = cq.Workplane("XZ").placeSketch(sk_gps_base).extrude(-13.0)
    gps_ramp = (
        cq.Workplane("XZ")
        .workplane(offset=-13.0)
        .placeSketch(sk_gps_base, sk_gps_tip.moved(cq.Location(cq.Vector(0.0, 0.0, -13.0))))
        .loft(ruled=True)
    )
    gps_holder = gps_base.union(gps_ramp)

    pocket_main = cq.Workplane("XY").transformed(offset=(GPS_X_CENTER, 4.65, GPS_Z_CENTER)).box(5.8, 9.6, GPS_LEN_Z)
    pocket_roof = (
        cq.Workplane("XZ")
        .workplane(offset=-9.4)
        .center(GPS_X_CENTER, GPS_Z_CENTER)
        .rect(5.8, GPS_LEN_Z)
        .workplane(offset=-6.3)
        .rect(0.4, GPS_LEN_Z - 2.0)
        .loft(ruled=True)
    )
    pocket_relief = cq.Workplane("XY").transformed(offset=(GPS_X_CENTER, 4.65, GPS_Z_CENTER)).box(7.8, 9.6, GPS_LEN_Z - 5.0)
    relief_roof = (
        cq.Workplane("XZ")
        .workplane(offset=-9.4)
        .center(GPS_X_CENTER, GPS_Z_CENTER)
        .rect(7.8, GPS_LEN_Z - 5.0)
        .workplane(offset=-8.1)
        .rect(0.4, GPS_LEN_Z - 7.0)
        .loft(ruled=True)
    )
    pocket_entry = cq.Workplane("XY").transformed(offset=(GPS_X_CENTER, 0.7, GPS_Z_CENTER)).box(8.2, 1.6, GPS_LEN_Z + 0.8)
    cable_slot = cq.Workplane("XY").transformed(offset=(GPS_X_CENTER, 4.5, GPS_Z_CENTER + GPS_LEN_Z / 2.0)).box(4.4, 9.2, 8.0)
    cable_roof = (
        cq.Workplane("XZ")
        .workplane(offset=-9.0)
        .center(GPS_X_CENTER, GPS_Z_CENTER + GPS_LEN_Z / 2.0)
        .rect(4.4, 8.0)
        .workplane(offset=-4.8)
        .rect(0.4, 6.0)
        .loft(ruled=True)
    )

    gps_holder = (
        gps_holder
        .cut(pocket_main)
        .cut(pocket_roof)
        .cut(pocket_relief)
        .cut(relief_roof)
        .cut(pocket_entry)
        .cut(cable_slot)
        .cut(cable_roof)
    )
    internal_union = internal_union.union(gps_holder)

    # 사과 외형 안쪽으로 깔끔하게 교집합 트리밍
    front = outer.intersect(internal_union)

    # D. 4x 전면 외곽 볼트 셀프태핑 체결 홀 (Y = 0 ~ +12.5 mm + 65도 원뿔 지붕 -> 서포트 0%, 전면 관통 0%)
    pilot_r = spec["pilot_r"]
    spire_h = pilot_r * math.tan(math.radians(65.0))  # 65도 자립형 고깔 높이 (~3.81 mm for M4, ~2.95 mm for M3)
    for px, pz in BOLT_PTS:
        lead_in = cq.Solid.makeCone(
            pilot_r + 0.45,
            pilot_r,
            0.8,
            cq.Vector(px, -0.1, pz),
            cq.Vector(0.0, 1.0, 0.0),
        )
        pilot_cyl = (
            cq.Workplane("XZ")
            .workplane(offset=0.1)  # Y = -0.1 mm
            .center(px, pz)
            .circle(pilot_r)
            .extrude(-(BOLT_FRONT_HOLE_DEPTH + 0.1))  # Y = -0.1 -> +12.5 mm
        )
        spire_cone = cq.Solid.makeCone(
            pilot_r,
            0.05,
            spire_h,
            cq.Vector(px, BOLT_FRONT_HOLE_DEPTH - 0.02, pz),
            cq.Vector(0.0, 1.0, 0.0),
        )
        front = (
            front
            .cut(cq.Workplane(obj=lead_in))
            .cut(pilot_cyl)
            .cut(cq.Workplane(obj=spire_cone))
        )

    # E. 4x PCB M3 블라인드 파일럿 홀 (Ø2.80 mm, 깊이 18.0 mm, 전면 겉면 관통 0%)
    for dx in (-1, 1):
        for dz in (-1, 1):
            x_pos = dx * (HOLE_PITCH / 2.0)
            z_pos = PCB_Z_CENTER + dz * (HOLE_PITCH / 2.0)
            pcb_pilot = (
                cq.Workplane("XZ")
                .workplane(offset=-(PCB_Y_MOUNT - 0.5))  # Y = -0.5 mm
                .center(x_pos, z_pos)
                .circle(1.40)
                .extrude(-18.5)  # Y = -0.5 -> +18.0 mm
            )
            front = front.cut(pcb_pilot)

    # F. 공통 절삭부(꼭지, 상·하단 루버) + BH1750 채광창 적용
    front = front.cut(make_shared_cutouts()).cut(make_bh1750_window_cutouts())
    return front


# ============================================================================
# 5. 상단 사과 꼭지 플러그 (APPLE STEM PLUG)
# ============================================================================
def build_stem() -> cq.Workplane:
    pin = (
        cq.Workplane("XY")
        .workplane(offset=29.0)
        .center(0.0, 1.5)
        .circle(2.3)
        .extrude(10.0)
    )
    trunk_cone = cq.Solid.makeCone(2.5, 1.6, 15.0, cq.Vector(0, 0, 0), cq.Vector(0, 0, 1))
    trunk = (
        cq.Workplane(obj=trunk_cone)
        .rotate((0, 0, 0), (0, 1, 0), 14.0)
        .translate((0.0, 1.5, 39.0))
    )
    scale_mat = cq.Matrix([
        [1.8, 0.0, 0.0, 0.0],
        [0.0, 0.8, 0.0, 0.0],
        [0.0, 0.0, 0.3, 0.0],
    ])
    leaf_ellipsoid = cq.Solid.makeSphere(5.0).transformGeometry(scale_mat)
    leaf = (
        cq.Workplane(obj=leaf_ellipsoid)
        .rotate((0, 0, 0), (1, 0, 0), 25.0)
        .rotate((0, 0, 0), (0, 1, 0), 45.0)
        .rotate((0, 0, 0), (0, 0, 1), 15.0)
        .translate((2.5, 1.5, 47.0))
    )
    return pin.union(trunk).union(leaf)


def measure_exact_mesh_bounds(part: cq.Workplane) -> tuple[float, float, float, float, float]:
    """실제 메쉬 표면 정밀 치수(xlen, ylen, zlen, zmin, zmax) 측정"""
    verts, _ = part.val().tessellate(0.03)
    xs = [v.x for v in verts]
    ys = [v.y for v in verts]
    zs = [v.z for v in verts]
    return max(xs) - min(xs), max(ys) - min(ys), max(zs) - min(zs), min(zs), max(zs)


# ============================================================================
# 6. 실제 CarrierBoard_BeetleC6_EdgeUSB_50x50 전체 부품 + 배터리 + 20mm 볼트 가상 목업
#    권장 실장 방향(방향 C): Top -> 전면(+Y), Bottom -> 후면(-Y), USB -> 상단(+Z)
# ============================================================================
def build_hardware_mockup(bolt_spec: str = BOLT_SPEC) -> dict[str, tuple[cq.Workplane, str]]:
    spec = BOLT_SPECS[bolt_spec]

    # 1. 5000mAh 배터리 (55 x 68 x 10 mm) + 2mm 벨크로 층 (Y = -26.0 ~ -14.0 mm)
    velcro_pad = cq.Workplane("XY").transformed(offset=(0.0, BATTERY_FLOOR_Y + 1.0, BATTERY_BAY_Z_CENTER)).box(52.0, 2.0, 64.0)
    battery = cq.Workplane("XY").transformed(offset=(0.0, BATTERY_FLOOR_Y + 2.0 + 5.0, BATTERY_BAY_Z_CENTER)).box(55.0, 10.0, 68.0)

    # 2. CarrierBoard PCB 기판 (50 x 50 x 1.6 mm, Y = -1.6 ~ 0.0, Z = -22 ~ +28)
    pcb = cq.Workplane("XY").transformed(offset=(0.0, (PCB_Y_MOUNT + PCB_Y_BACK) / 2.0, PCB_Z_CENTER)).box(PCB_W, PCB_T, PCB_H)

    # 3. Top면 부품 (전면 돔 +Y 방향: Y = 0.0 ~ +height)
    # Beetle ESP32-C6 (20.5 x 25.0 mm, 소켓 포함 13.5 mm): X=[-10.25, +10.25], Z=[+3.0, +28.0]
    esp32 = cq.Workplane("XY").transformed(offset=(0.0, 6.75, 15.5)).box(20.5, 13.5, 25.0)
    # BH1750 조도 센서 (13.9 x 18.5 mm, 소켓 포함 12.0 mm): X=[+10.8, +24.7], Z=[+2.8, +21.3]
    bh1750 = cq.Workplane("XY").transformed(offset=(17.75, 6.0, 12.05)).box(13.9, 12.0, 18.5)
    # JST-PH 2.0 & SW1 (20.0 x 4.5 mm, 높이 8.0 mm): X=[-10.0, +10.0], Z=[-21.0, -16.5]
    jst_sw1 = cq.Workplane("XY").transformed(offset=(0.0, 4.0, -18.75)).box(20.0, 8.0, 4.5)

    # 4. Bottom면 부품 (후면 배터리 -Y 방향: Y = -1.6 - height ~ -1.6)
    # ATGM336H GPS 모듈 (13.1 x 15.7 mm, 소켓 포함 10.0 mm): X=[-24.2, -11.1], Z=[+4.8, +20.5]
    gps_mod = cq.Workplane("XY").transformed(offset=(-17.65, PCB_Y_BACK - 5.0, 12.65)).box(13.1, 10.0, 15.7)
    # SHT45 온습도 센서 (25.5 x 17.8 mm, 소켓 포함 11.0 mm): X=[-24.5, +1.0], Z=[-15.3, +2.5]
    sht45 = cq.Workplane("XY").transformed(offset=(-11.75, PCB_Y_BACK - 5.5, -6.4)).box(25.5, 11.0, 17.8)
    # GY-521 MPU6050 IMU (20.7 x 15.65 mm, 소켓 포함 11.0 mm): X=[+3.5, +24.2], Z=[-13.15, +2.5]
    gy521 = cq.Workplane("XY").transformed(offset=(13.85, PCB_Y_BACK - 5.5, -5.325)).box(20.7, 11.0, 15.65)

    # 5. 좌측(-X) 외장 GPS 세라믹 패치 안테나 (5 x 7 x 20 mm)
    gps_ant = cq.Workplane("XY").transformed(offset=(GPS_X_CENTER, 4.5, GPS_Z_CENTER)).box(5.0, 7.0, 20.0)

    # 6. 4x DIN 912 20mm 육각 렌치 볼트 (머리 Y = -10..-14/-13, 나사 Y = -10..+10)
    bolts: cq.Workplane | None = None
    for px, pz in BOLT_PTS:
        head = (
            cq.Workplane("XZ")
            .workplane(offset=abs(BOLT_SEAT_Y))  # Y = -10.0 mm
            .center(px, pz)
            .circle(spec["head_r"])
            .extrude(spec["head_h"])             # Y = -10.0 -> -14.0 (M4) / -13.0 (M3)
        )
        shaft = (
            cq.Workplane("XZ")
            .workplane(offset=abs(BOLT_SEAT_Y))  # Y = -10.0 mm
            .center(px, pz)
            .circle(spec["shaft_r"])
            .extrude(-spec["shaft_len"])         # Y = -10.0 -> +10.0 mm (정확히 20.0 mm!)
        )
        bolt = head.union(shaft)
        bolts = bolt if bolts is None else bolts.union(bolt)

    assert bolts is not None
    return {
        "Velcro_Pad_2mm": (velcro_pad, "#444444"),
        "Battery_5000mAh": (battery, "#3373e6"),
        "CarrierBoard_PCB": (pcb, "#148c40"),
        "Beetle_ESP32_C6": (esp32, "#262626"),
        "BH1750_LightSensor": (bh1750, "#1f6feb"),
        "JST_PH_and_SW1": (jst_sw1, "#e6e6e6"),
        "ATGM336H_GPS": (gps_mod, "#ccbf66"),
        "SHT45_TempHumid": (sht45, "#e040fb"),
        "GY521_MPU6050": (gy521, "#00bcd4"),
        "GPS_Ceramic_Antenna": (gps_ant, "#e09e6b"),
        f"HexBolts_4x_{bolt_spec}x20mm": (bolts, "#c0c8d4"),
    }


def render_for_cq_editor(show_fn) -> None:
    """CQ-Editor에서 F5(Render) 실행 시 VIEW_MODE에 맞춰 3D 뷰포트와 Objects 트리에 출력"""
    outer = make_revolved_apple(APPLE_OUTER_PROFILE, use_spline=False)
    inner = make_revolved_apple(APPLE_INNER_PROFILE, use_spline=False)
    hollow_apple = outer.cut(inner)

    if VIEW_MODE == "rear_shell":
        show_fn(build_rear_shell(outer, hollow_apple, BOLT_SPEC), name="Rear_Shell", options={"color": "#9e2ebf"})
        return
    if VIEW_MODE == "front_shell":
        show_fn(build_front_shell(outer, hollow_apple, BOLT_SPEC), name="Front_Shell", options={"color": "#f2c71f"})
        return
    if VIEW_MODE == "stem":
        show_fn(build_stem(), name="Apple_Stem", options={"color": "#47a638"})
        return

    rear_shell = build_rear_shell(outer, hollow_apple, BOLT_SPEC)
    front_shell = build_front_shell(outer, hollow_apple, BOLT_SPEC)
    stem = build_stem()

    if VIEW_MODE == "exploded":
        show_fn(rear_shell.translate((0.0, -45.0, 0.0)), name="Rear_Shell", options={"color": "#9e2ebf"})
        show_fn(front_shell.translate((0.0, 45.0, 0.0)), name="Front_Shell", options={"color": "#f2c71f"})
        show_fn(stem.translate((0.0, 45.0, 18.0)), name="Apple_Stem", options={"color": "#47a638"})
        for hw_name, (hw_part, hw_color) in build_hardware_mockup(BOLT_SPEC).items():
            show_fn(hw_part, name=hw_name, options={"color": hw_color})
    elif VIEW_MODE == "cross_section":
        cut_box = cq.Workplane("XY").transformed(offset=(0.0, 0.0, 75.0)).box(160.0, 160.0, 140.0)
        show_fn(rear_shell.cut(cut_box), name="Rear_Section", options={"color": "#9e2ebf"})
        show_fn(front_shell.cut(cut_box), name="Front_Section", options={"color": "#f2c71f"})
        for hw_name, (hw_part, hw_color) in build_hardware_mockup(BOLT_SPEC).items():
            show_fn(hw_part, name=hw_name, options={"color": hw_color})
    elif VIEW_MODE == "print_layout":
        rear_rot = rear_shell.rotate((0, 0, 0), (1, 0, 0), -90.0)
        _, _, _, r_zmin, _ = measure_exact_mesh_bounds(rear_rot)
        front_rot = front_shell.rotate((0, 0, 0), (1, 0, 0), 90.0)
        _, _, _, f_zmin, _ = measure_exact_mesh_bounds(front_rot)
        _, _, _, s_zmin, _ = measure_exact_mesh_bounds(stem)

        show_fn(rear_rot.translate((-55.0, 0.0, -r_zmin)), name="Rear_DomeUp", options={"color": "#9e2ebf"})
        show_fn(front_rot.translate((55.0, 0.0, -f_zmin)), name="Front_DomeUp", options={"color": "#f2c71f"})
        show_fn(stem.translate((0.0, 52.0, -s_zmin)), name="Stem_Print", options={"color": "#47a638"})
    else:
        show_fn(rear_shell, name="Rear_Shell", options={"color": "#9e2ebf", "alpha": 0.45})
        show_fn(front_shell, name="Front_Shell", options={"color": "#f2c71f", "alpha": 0.40})
        show_fn(stem, name="Apple_Stem", options={"color": "#47a638"})
        for hw_name, (hw_part, hw_color) in build_hardware_mockup(BOLT_SPEC).items():
            show_fn(hw_part, name=hw_name, options={"color": hw_color})


# ============================================================================
# 7. 출력 정렬 (Dome-Up, Z_min = 0.00 mm) 및 STEP / STL 일괄 빌드 실행부
# ============================================================================
def orient_for_print(
    rear_shell: cq.Workplane,
    front_shell: cq.Workplane,
    stem: cq.Workplane,
) -> tuple[cq.Workplane, cq.Workplane, cq.Workplane]:
    rear_rot = rear_shell.rotate((0, 0, 0), (1, 0, 0), -90.0)
    _, _, _, r_zmin, _ = measure_exact_mesh_bounds(rear_rot)
    rear_print = rear_rot.translate((0.0, 0.0, -r_zmin))

    front_rot = front_shell.rotate((0, 0, 0), (1, 0, 0), 90.0)
    _, _, _, f_zmin, _ = measure_exact_mesh_bounds(front_rot)
    front_print = front_rot.translate((0.0, 0.0, -f_zmin))

    _, _, _, s_zmin, _ = measure_exact_mesh_bounds(stem)
    stem_print = stem.translate((0.0, -1.5, -s_zmin))
    return rear_print, front_print, stem_print


def export_variant(
    outer: cq.Workplane,
    hollow_apple: cq.Workplane,
    stem: cq.Workplane,
    bolt_spec: str,
    step_out_dir: Path,
    stl_root_dir: Path,
    suffix: str = "",
) -> tuple[cq.Workplane, cq.Workplane]:
    step_out_dir.mkdir(parents=True, exist_ok=True)
    stl_root_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n=== [{bolt_spec} x 20mm 육각 렌치 볼트 버전] 모델링 & 내보내기 ===")
    rear_shell = build_rear_shell(outer, hollow_apple, bolt_spec)
    front_shell = build_front_shell(outer, hollow_apple, bolt_spec)
    rear_print, front_print, stem_print = orient_for_print(rear_shell, front_shell, stem)

    assy = cq.Assembly(name=f"v24_Apple_Sensor_Pod_CrossFlow_{bolt_spec}x20")
    assy.add(rear_shell, name="rear_shell", color=cq.Color(0.62, 0.18, 0.75, 0.6))
    assy.add(front_shell, name="front_shell", color=cq.Color(0.95, 0.78, 0.12, 0.6))
    assy.add(stem, name="apple_stem", color=cq.Color(0.28, 0.65, 0.22, 1.0))

    parts = {
        f"24_apple_rear_shell{suffix}_cq": (f"24_apple_rear_shell{suffix}.stl", rear_print),
        f"24_apple_front_shell{suffix}_cq": (f"24_apple_front_shell{suffix}.stl", front_print),
        f"24_apple_stem{suffix}_cq": (f"24_apple_stem{suffix}.stl", stem_print),
    }

    for cq_name, (root_stl_name, part) in parts.items():
        step_path = step_out_dir / f"{cq_name}.step"
        stl_path = step_out_dir / f"{cq_name}.stl"
        cq.exporters.export(part, str(step_path))
        cq.exporters.export(part, str(stl_path), tolerance=0.04, angularTolerance=0.08)

        root_stl_path = stl_root_dir / root_stl_name
        shutil.copy2(stl_path, root_stl_path)

        xlen, ylen, zlen, zmin, zmax = measure_exact_mesh_bounds(part)
        print(
            f"  -> {cq_name} (& {root_stl_name}): "
            f"크기 = {xlen:.1f} x {ylen:.1f} x {zlen:.1f} mm | "
            f"Z 범위 = [{zmin:.2f}, {zmax:.2f}] mm"
        )

    assy_step_path = step_out_dir / f"24_apple_assembly{suffix}_cq.step"
    if hasattr(assy, "export"):
        assy.export(str(assy_step_path))
    else:
        assy.save(str(assy_step_path))
    print(f"  -> 조립체 STEP 저장 완료: {assy_step_path.name}")
    return rear_shell, front_shell


def export_all(out_dir: Path) -> None:
    parent_dir = out_dir.parent

    print("[1/3] 사과 외벽/내벽 B-Rep 회전체 및 중공 바디 생성 중...")
    outer = make_revolved_apple(APPLE_OUTER_PROFILE, use_spline=False)
    inner = make_revolved_apple(APPLE_INNER_PROFILE, use_spline=False)
    hollow_apple = outer.cut(inner)
    stem = build_stem()

    # 1) 메인 M4 x 20mm 버전 (추천: PLA 반복 개폐 내구성 우수)
    print("[2/3] 메인 M4 x 20mm 육각 렌치 볼트 버전 생성 중...")
    export_variant(
        outer, hollow_apple, stem,
        bolt_spec="M4",
        step_out_dir=out_dir,
        stl_root_dir=parent_dir,
        suffix="_m4",
    )

    # 2) 옵션 M3 x 20mm 버전 (PCB 나사와 2.5mm 육각렌치 통일용)
    print("[3/3] 옵션 M3 x 20mm 육각 렌치 볼트 버전 생성 중...")
    m3_dir = parent_dir / "m3_20mm_option"
    export_variant(
        outer, hollow_apple, stem,
        bolt_spec="M3",
        step_out_dir=m3_dir,
        stl_root_dir=m3_dir,
        suffix="_m3",
    )


# CQ-Editor 내부에서 실행(F5)하면 show_object가 전역에 자동 주입됨!
if "show_object" in globals():
    render_for_cq_editor(globals()["show_object"])  # type: ignore[name-defined]
elif __name__ == "__main__":
    target_dir = Path(__file__).resolve().parent
    export_all(target_dir)
