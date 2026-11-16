"""
Cold Chain Digital Twin Platform
v22 Apple Sensor Pod Housing - CadQuery (OpenCASCADE B-Rep) Edition
(Enlarged Magnetic Snap + Chimney Convection Vents + GPS Holder)

원본 OpenSCAD 설계(22_apple_sensor_pod.scad)와 100% 동일한 치수의 CadQuery 2.7 기반 B-Rep 스크립트.
실행 시 STEP(.step, 정밀 CAD 원본) 및 STL(.stl, 3D 프린터 슬라이서용) 파일을 자동 생성한다.

실행 방법:
    python 22_apple_sensor_pod_cq.py
"""

from __future__ import annotations

import math
import shutil
from pathlib import Path
import cadquery as cq

# ============================================================================
# 0. CQ-Editor 화면 표시 모드 설정 (CQ-Editor에서 F5 누를 때 적용됨!)
# 옵션: "assembly" (반투명 조립+부품), "exploded" (분해도), "print_layout" (출력배치),
#       "front_shell" (전면쉘 단품), "rear_shell" (후면쉘 단품), "stem" (꼭지 단품)
# ============================================================================
VIEW_MODE = "assembly"

# ============================================================================
# 1. 설계 파라미터 정의 (22_apple_sensor_pod.scad 와 100% 동일 치수)
# ============================================================================
WALL_T = 3.0
CLEARANCE = 0.25

# PCB 규격 (50 x 50 x 1.6 mm, M3 홀 간격 43 x 43 mm)
PCB_W = 50.0
PCB_H = 50.0
PCB_T = 1.6
HOLE_PITCH = 43.0
PCB_Z_CENTER = 3.0
PCB_Y_MOUNT = 0.0                # 전면 쉘 베드 바닥(Z=0.0)과 100% 밀착!
PCB_Y_BACK = PCB_Y_MOUNT - PCB_T  # Y = -1.6 mm

# 4x 네오디뮴 자석 보스 좌표 (X, Z) - 보스 내측 모서리(|X|=28.50mm)가 배터리 공간(|X|=28.20mm) 바깥에 위치!
SCREW_PTS: list[tuple[float, float]] = [
    (-35.0, 25.0),
    (35.0, 25.0),
    (-35.0, -22.0),
    (35.0, -22.0),
]

# 확장된 자석 포켓 규격 (넓고 긴 자석도 여유롭게 들어가도록 지름 7.60mm, 원통 깊이 5.50mm + 65도 원뿔 지붕 8.20mm 적용!)
MAG_R_FRONT = 3.80
MAG_H_FRONT = 5.50
MAG_R_REAR = 3.80
MAG_H_REAR = 5.50
MAG_BOSS_R = 6.50

# 외장형 GPS 세라믹 안테나 규격 (20 x 5 x 7 mm)
GPS_LEN_Z = 21.6
GPS_WID_X = 7.6
GPS_DEP_Y = 11.0
GPS_WALL = 2.4
GPS_X_CENTER = -36.5
GPS_Z_CENTER = 1.0

# 사과 외벽 회전 프로파일 (R, Z) - 외경 100.0mm (R_max = 50.0mm), 높이 91.87mm
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
# 2. 공통 기하학 헬퍼 함수 (CadQuery 핵심 패턴)
# ============================================================================
def make_revolved_apple(profile: list[tuple[float, float]], use_spline: bool = False) -> cq.Workplane:
    """XZ 평면에 (R, Z) 단면을 그린 뒤 글로벌 Z축 기준으로 360도 회전시킨다."""
    wp = cq.Workplane("XZ")
    if use_spline:
        wp = wp.moveTo(*profile[0]).spline(profile[1:]).close()
    else:
        wp = wp.polyline(profile).close()
    return wp.revolve(360, (0, 0, 0), (0, 1, 0))


def make_functional_cutouts() -> cq.Workplane:
    """
    1) 상단 사과 꼭지 소켓 홈
    2) 우측(+X) SHT45 온습도 센서 3슬롯 통기 그릴 (Z = -4, +2, +8 mm)
    3) 상·하단 굴뚝 효과(Stack Effect) 자연대류 통풍 슬릿 (하단 냉기 유입 Z=-28mm, 상단 열기 배출 Z=+30mm)
    """
    cutouts = (
        cq.Workplane("XY")
        .workplane(offset=36.0 - 7.0)
        .center(0.0, 1.5)
        .circle(2.5)
        .extrude(14.0)
    )

    # 우측(+X) SHT45 3단 통풍 슬롯 (65도 물방울 지붕 적용 -> 슬롯 내부 서포트 0%)
    for z_s in (-4.0, 2.0, 8.0):
        sk_side = (
            cq.Sketch()
            .arc((-2.0, z_s), 1.8, 0.0, 360.0)
            .arc((2.5, z_s), 0.4, 0.0, 360.0)
            .arc((-6.5, z_s), 0.4, 0.0, 360.0)
            .hull()
        )
        slot_side = cq.Workplane("YZ").workplane(offset=35.5).placeSketch(sk_side).extrude(25.0)
        cutouts = cutouts.union(slot_side)

    # 하단 냉기 유입구(Z = -28 mm) + 상단 MCU/GPS 열기 배출구(Z = +30 mm)
    for x_v in (-12.0, 0.0, 12.0):
        for y_sign in (-1.0, 1.0):
            sk_louver = (
                cq.Sketch()
                .arc((x_v, y_sign * 14.0), 1.8, 0.0, 360.0)
                .arc((x_v, y_sign * 19.0), 0.35, 0.0, 360.0)
                .hull()
            )
            intake = cq.Workplane("XY").workplane(offset=-45.0).placeSketch(sk_louver).extrude(30.0)
            exhaust = cq.Workplane("XY").workplane(offset=15.0).placeSketch(sk_louver).extrude(30.0)
            cutouts = cutouts.union(intake).union(exhaust)

    return cutouts


# ============================================================================
# 3. 후면 쉘 (REAR SHELL - 배터리 벨크로 평면 바닥 + 확장형 자석 홈 4곳 + 굴뚝 통풍구)
# ============================================================================
def build_rear_shell(outer: cq.Workplane, hollow_apple: cq.Workplane) -> cq.Workplane:
    # A. 중공 사과에서 Y <= 0 후면 반구 추출
    rear_half_box = cq.Workplane("XY").transformed(offset=(0.0, -70.0, 0.0)).box(140.0, 140.0, 140.0)
    shell_body = hollow_apple.intersect(rear_half_box)

    # B. Y <= -24.5 mm 오픈형 평면 벨크로 배터리 바닥 채우기
    velcro_platform = cq.Workplane("XY").transformed(offset=(0.0, -38.0, 0.0)).box(140.0, 27.0, 140.0)
    internal_union = shell_body.union(velcro_platform)

    # C. 4x 확장형 벽체 일체형 자석 보스 (r = 6.50mm, 깊이 Y = -18.5mm 까지 확장하여 긴 자석 + 원뿔 지붕 완벽 수용!)
    for px, pz in SCREW_PTS:
        norm_len = math.hypot(px, pz)
        dir_x, dir_z = px / norm_len, pz / norm_len

        sk_top = (
            cq.Sketch()
            .arc((px, pz), MAG_BOSS_R, 0.0, 360.0)
            .arc((px + dir_x * 10.0, pz + dir_z * 10.0), MAG_BOSS_R, 0.0, 360.0)
            .hull()
        )
        sk_bot = cq.Sketch().push([(px + dir_x * 3.0, pz + dir_z * 3.0)]).circle(5.5)

        # 상단 기둥 (Y = 0 -> -12.0mm) + 하단 경사 로프트 (Y = -12.0 -> -20.0mm)
        boss_upper = cq.Workplane("XZ").placeSketch(sk_top).extrude(12.0)
        boss_taper = (
            cq.Workplane("XZ")
            .workplane(offset=12.0)
            .placeSketch(sk_top, sk_bot.moved(cq.Location(cq.Vector(0.0, 0.0, 8.0))))
            .loft(ruled=True)
        )
        internal_union = internal_union.union(boss_upper).union(boss_taper)

    # 사과 외형 바깥으로 나간 보스 외곽 트리밍
    rear = outer.intersect(internal_union)

    # D. 5000mAh 배터리 사각 코너 여유 공간 컷아웃 (56.4 x 70.4 mm, 코너 필렛 R2.2, Y = +0.5 -> -24.48)
    battery_bay_cut = (
        cq.Workplane("XZ")
        .workplane(offset=-0.5)
        .center(0.0, -0.5)
        .rect(56.4, 70.4)
        .extrude(24.98)
        .edges("|Y")
        .fillet(2.2)
    )
    rear = rear.cut(battery_bay_cut)

    # E. 4x 후면 확장형 자석 포켓 (입구 챔퍼 D=8.50mm + 본체 D=7.60mm x 깊이 5.50mm + 65도 원뿔 지붕 8.20mm)
    for px, pz in SCREW_PTS:
        chamfer_cone = cq.Solid.makeCone(
            MAG_R_REAR + 0.45,
            MAG_R_REAR,
            0.9,
            cq.Vector(px, 0.1, pz),
            cq.Vector(0.0, -1.0, 0.0),
        )
        pocket_cyl = (
            cq.Workplane("XZ")
            .workplane(offset=-0.1)
            .center(px, pz)
            .circle(MAG_R_REAR)
            .extrude(MAG_H_REAR + 0.1)
        )
        spire_cone = cq.Solid.makeCone(
            MAG_R_REAR,
            0.05,
            8.20,
            cq.Vector(px, -(MAG_H_REAR - 0.02), pz),
            cq.Vector(0.0, -1.0, 0.0),
        )
        rear = (
            rear
            .cut(cq.Workplane(obj=chamfer_cone))
            .cut(pocket_cyl)
            .cut(cq.Workplane(obj=spire_cone))
        )

    rear = rear.cut(make_functional_cutouts())
    return rear


# ============================================================================
# 4. 전면 쉘 (FRONT SHELL - 베드 밀착 PCB 스탠드오프 4곳 + GPS 포켓 + 확장형 자석 홈 4곳)
# ============================================================================
def build_front_shell(outer: cq.Workplane, hollow_apple: cq.Workplane) -> cq.Workplane:
    # A. 중공 사과에서 Y >= 0 전면 반구 추출
    front_half_box = cq.Workplane("XY").transformed(offset=(0.0, 70.0, 0.0)).box(140.0, 140.0, 140.0)
    internal_union = hollow_apple.intersect(front_half_box)

    # B. 4x 전면 확장형 자석 보스 (r = 6.50mm, Y = 0.0 베드 바닥에 100% 밀착 + 상단 테이퍼!)
    for px, pz in SCREW_PTS:
        norm_len = math.hypot(px, pz)
        dir_x, dir_z = px / norm_len, pz / norm_len
        sk_top = (
            cq.Sketch()
            .arc((px, pz), MAG_BOSS_R, 0.0, 360.0)
            .arc((px + dir_x * 12.0, pz + dir_z * 12.0), MAG_BOSS_R, 0.0, 360.0)
            .hull()
        )
        sk_bot = cq.Sketch().push([(px + dir_x * 3.0, pz + dir_z * 3.0)]).circle(5.5)

        boss_lower = cq.Workplane("XZ").placeSketch(sk_top).extrude(-12.0)
        boss_taper = (
            cq.Workplane("XZ")
            .workplane(offset=-12.0)
            .placeSketch(sk_top, sk_bot.moved(cq.Location(cq.Vector(0.0, 0.0, -8.0))))
            .loft(ruled=True)
        )
        internal_union = internal_union.union(boss_lower).union(boss_taper)

    # C. 4x PCB 고정용 스탠드오프 기둥 + 외벽 보강 리브 (Y = 0.0 베드 바닥에 100% 밀착 -> 잔조각 0%!)
    for dx in (-1, 1):
        for dz in (-1, 1):
            x_pos = dx * (HOLE_PITCH / 2.0)
            z_pos = PCB_Z_CENTER + dz * (HOLE_PITCH / 2.0)
            rib_len_z = 16.5 if dz > 0 else 20.0
            rib_target_x = x_pos + dx * 3.5
            rib_target_z = z_pos + dz * rib_len_z

            sk_rib = (
                cq.Sketch()
                .arc((x_pos, z_pos), 4.0, 0.0, 360.0)
                .arc((rib_target_x, rib_target_z), 4.2, 0.0, 360.0)
                .hull()
            )
            standoff_monolith = (
                cq.Workplane("XZ")
                .workplane(offset=-PCB_Y_MOUNT)
                .placeSketch(sk_rib)
                .extrude(-46.0)
            )
            internal_union = internal_union.union(standoff_monolith)

    # D. 내장형 GPS 세라믹 안테나 홀더 (20 x 5 x 7 mm, 65도 고딕 아치 지붕 적용)
    gps_outer_h = GPS_LEN_Z + 2.0 * GPS_WALL  # 26.4 mm
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

    # GPS 내부 슬라이드 포켓 + 65도 고딕 지붕 (서포트 생성 0%)
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

    # E. 4x 전면 확장형 자석 포켓 (입구 챔퍼 D=8.50mm + 본체 D=7.60mm x 깊이 5.50mm + 65도 원뿔 지붕 8.20mm)
    for px, pz in SCREW_PTS:
        chamfer_cone = cq.Solid.makeCone(
            MAG_R_FRONT + 0.45,
            MAG_R_FRONT,
            0.9,
            cq.Vector(px, -0.1, pz),
            cq.Vector(0.0, 1.0, 0.0),
        )
        pocket_cyl = (
            cq.Workplane("XZ")
            .workplane(offset=0.1)
            .center(px, pz)
            .circle(MAG_R_FRONT)
            .extrude(-(MAG_H_FRONT + 0.1))
        )
        spire_cone = cq.Solid.makeCone(
            MAG_R_FRONT,
            0.05,
            8.20,
            cq.Vector(px, MAG_H_FRONT - 0.02, pz),
            cq.Vector(0.0, 1.0, 0.0),
        )
        front = (
            front
            .cut(cq.Workplane(obj=chamfer_cone))
            .cut(pocket_cyl)
            .cut(cq.Workplane(obj=spire_cone))
        )

    # F. 4x PCB M3 블라인드 파일럿 홀 (깊이 20.0mm)
    for dx in (-1, 1):
        for dz in (-1, 1):
            x_pos = dx * (HOLE_PITCH / 2.0)
            z_pos = PCB_Z_CENTER + dz * (HOLE_PITCH / 2.0)
            pilot_hole = (
                cq.Workplane("XZ")
                .workplane(offset=-(PCB_Y_MOUNT - 0.5))
                .center(x_pos, z_pos)
                .circle(1.45)
                .extrude(-20.5)
            )
            front = front.cut(pilot_hole)

    front = front.cut(make_functional_cutouts())
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
# 6. 내부 하드웨어 가상 목업 (CQ-Editor 조립 간섭 확인용)
# ============================================================================
def build_hardware_mockup() -> dict[str, tuple[cq.Workplane, str]]:
    battery = cq.Workplane("XY").transformed(offset=(0.0, -19.5, -0.5)).box(55.0, 10.0, 68.0)
    pcb = cq.Workplane("XY").transformed(offset=(0.0, (PCB_Y_MOUNT + PCB_Y_BACK) / 2.0, PCB_Z_CENTER)).box(PCB_W, PCB_T, PCB_H)
    bh1750 = cq.Workplane("XY").transformed(offset=(15.5, PCB_Y_BACK - 5.0, -15.0)).box(18.0, 10.0, 14.0)
    esp32 = cq.Workplane("XY").transformed(offset=(16.0, PCB_Y_BACK - 5.0, -1.0)).box(20.5, 10.0, 25.0)
    gps_mod = cq.Workplane("XY").transformed(offset=(4.0, PCB_Y_MOUNT + 5.0, 18.0)).box(16.0, 10.0, 16.0)
    gps_ant = cq.Workplane("XY").transformed(offset=(GPS_X_CENTER, 4.5, GPS_Z_CENTER)).box(5.0, 7.0, 20.0)

    magnets: cq.Workplane | None = None
    for px, pz in SCREW_PTS:
        m_rear = cq.Workplane("XZ").workplane(offset=0.0).center(px, pz).circle(3.5).extrude(4.5)
        m_front = cq.Workplane("XZ").workplane(offset=0.0).center(px, pz).circle(3.5).extrude(-4.5)
        pair = m_rear.union(m_front)
        magnets = pair if magnets is None else magnets.union(pair)

    assert magnets is not None
    return {
        "Battery_5000mAh": (battery, "#3373e6"),
        "CarrierBoard_PCB": (pcb, "#148c40"),
        "BH1750_Sensor": (bh1750, "#2673f2"),
        "ESP32_C6_MCU": (esp32, "#2e2e2e"),
        "ATGM336H_GPS": (gps_mod, "#ccbf66"),
        "GPS_Ceramic_Antenna": (gps_ant, "#e09e6b"),
        "Neodymium_Magnets_8x": (magnets, "#ccd4e0"),
    }


def render_for_cq_editor(show_fn) -> None:
    """CQ-Editor에서 F5(Render) 실행 시 VIEW_MODE에 맞춰 3D 뷰포트와 Objects 트리에 출력"""
    outer = make_revolved_apple(APPLE_OUTER_PROFILE, use_spline=False)
    inner = make_revolved_apple(APPLE_INNER_PROFILE, use_spline=False)
    hollow_apple = outer.cut(inner)

    if VIEW_MODE == "rear_shell":
        show_fn(build_rear_shell(outer, hollow_apple), name="Rear_Shell", options={"color": "#9e2ebf"})
        return
    if VIEW_MODE == "front_shell":
        show_fn(build_front_shell(outer, hollow_apple), name="Front_Shell", options={"color": "#f2c71f"})
        return
    if VIEW_MODE == "stem":
        show_fn(build_stem(), name="Apple_Stem", options={"color": "#47a638"})
        return

    rear_shell = build_rear_shell(outer, hollow_apple)
    front_shell = build_front_shell(outer, hollow_apple)
    stem = build_stem()

    if VIEW_MODE == "exploded":
        show_fn(rear_shell.translate((0.0, -45.0, 0.0)), name="Rear_Shell", options={"color": "#9e2ebf"})
        show_fn(front_shell.translate((0.0, 45.0, 0.0)), name="Front_Shell", options={"color": "#f2c71f"})
        show_fn(stem.translate((0.0, 45.0, 18.0)), name="Apple_Stem", options={"color": "#47a638"})
        for hw_name, (hw_part, hw_color) in build_hardware_mockup().items():
            show_fn(hw_part, name=hw_name, options={"color": hw_color})
    elif VIEW_MODE == "print_layout":
        # Dome-Up 출력 정렬 (둥근 사과 외면이 +Z 위쪽, Y=0.00mm 평면 테두리가 베드 바닥 Z=0.00mm에 100% 밀착!)
        rear_rot = rear_shell.rotate((0, 0, 0), (1, 0, 0), -90.0)
        _, _, _, r_zmin, _ = measure_exact_mesh_bounds(rear_rot)
        front_rot = front_shell.rotate((0, 0, 0), (1, 0, 0), 90.0)
        _, _, _, f_zmin, _ = measure_exact_mesh_bounds(front_rot)
        _, _, _, s_zmin, _ = measure_exact_mesh_bounds(stem)

        show_fn(rear_rot.translate((-55.0, 0.0, -r_zmin)), name="Rear_DomeUp", options={"color": "#9e2ebf"})
        show_fn(front_rot.translate((55.0, 0.0, -f_zmin)), name="Front_DomeUp", options={"color": "#f2c71f"})
        show_fn(stem.translate((0.0, 45.0, -s_zmin)), name="Stem_Print", options={"color": "#47a638"})
    else:
        show_fn(rear_shell, name="Rear_Shell", options={"color": "#9e2ebf", "alpha": 0.45})
        show_fn(front_shell, name="Front_Shell", options={"color": "#f2c71f", "alpha": 0.40})
        show_fn(stem, name="Apple_Stem", options={"color": "#47a638"})
        for hw_name, (hw_part, hw_color) in build_hardware_mockup().items():
            show_fn(hw_part, name=hw_name, options={"color": hw_color})


# ============================================================================
# 7. 출력 정렬 (Dome-Up, Z_min = 0.00 mm) 및 STEP / STL 일괄 빌드 실행부
# ============================================================================
def export_all(out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    parent_dir = out_dir.parent

    print("[1/4] 사과 외벽/내벽 B-Rep 회전체 및 중공 바디 생성 중...")
    outer = make_revolved_apple(APPLE_OUTER_PROFILE, use_spline=False)
    inner = make_revolved_apple(APPLE_INNER_PROFILE, use_spline=False)
    hollow_apple = outer.cut(inner)

    print("[2/4] 후면 쉘(Rear Shell), 전면 쉘(Front Shell), 꼭지(Stem) B-Rep 모델링 중...")
    rear_shell = build_rear_shell(outer, hollow_apple)
    front_shell = build_front_shell(outer, hollow_apple)
    stem = build_stem()

    # 신도리코 3DWOX 2X 출력용 Dome-Up (사과 겉면이 +Z 위쪽, Z_min = 0.00 mm 베드 밀착) 정렬
    rear_rot = rear_shell.rotate((0, 0, 0), (1, 0, 0), -90.0)
    _, _, _, r_zmin, _ = measure_exact_mesh_bounds(rear_rot)
    rear_print = rear_rot.translate((0.0, 0.0, -r_zmin))

    front_rot = front_shell.rotate((0, 0, 0), (1, 0, 0), 90.0)
    _, _, _, f_zmin, _ = measure_exact_mesh_bounds(front_rot)
    front_print = front_rot.translate((0.0, 0.0, -f_zmin))

    _, _, _, s_zmin, _ = measure_exact_mesh_bounds(stem)
    stem_print = stem.translate((0.0, -1.5, -s_zmin))

    print("[3/4] 전체 조립체(Assembly) 구성 중...")
    assy = cq.Assembly(name="v22_Apple_Sensor_Pod_Magnetic")
    assy.add(rear_shell, name="rear_shell", color=cq.Color(0.62, 0.18, 0.75, 0.6))
    assy.add(front_shell, name="front_shell", color=cq.Color(0.95, 0.78, 0.12, 0.6))
    assy.add(stem, name="apple_stem", color=cq.Color(0.28, 0.65, 0.22, 1.0))

    print("[4/4] STEP(.step) 및 STL(.stl) 파일 내보내기 중...")
    parts_to_export = {
        "22_apple_rear_shell_cq": ("22_apple_rear_shell.stl", rear_print),
        "22_apple_front_shell_cq": ("22_apple_front_shell.stl", front_print),
        "22_apple_stem_cq": ("22_apple_stem.stl", stem_print),
    }

    for cq_name, (root_stl_name, part) in parts_to_export.items():
        step_path = out_dir / f"{cq_name}.step"
        stl_path = out_dir / f"{cq_name}.stl"
        cq.exporters.export(part, str(step_path))
        cq.exporters.export(part, str(stl_path), tolerance=0.04, angularTolerance=0.08)

        root_stl_path = parent_dir / root_stl_name
        shutil.copy2(stl_path, root_stl_path)

        xlen, ylen, zlen, zmin, zmax = measure_exact_mesh_bounds(part)
        print(
            f"  -> {cq_name} (& {root_stl_name}): "
            f"크기 = {xlen:.1f} x {ylen:.1f} x {zlen:.1f} mm | "
            f"Z 범위 = [{zmin:.2f}, {zmax:.2f}] mm"
        )

    assy_step_path = out_dir / "22_apple_assembly_cq.step"
    if hasattr(assy, "export"):
        assy.export(str(assy_step_path))
    else:
        assy.save(str(assy_step_path))
    print(f"  -> 조립체 STEP 저장 완료: {assy_step_path.name}")


# CQ-Editor 내부에서 실행(F5)하면 show_object가 전역에 자동 주입됨!
if "show_object" in globals():
    render_for_cq_editor(globals()["show_object"])  # type: ignore[name-defined]
elif __name__ == "__main__":
    target_dir = Path(__file__).resolve().parent
    export_all(target_dir)
