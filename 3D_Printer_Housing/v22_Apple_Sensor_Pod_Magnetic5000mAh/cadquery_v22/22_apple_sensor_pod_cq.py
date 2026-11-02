"""
Cold Chain Digital Twin Platform
v22 Apple Sensor Pod Housing - CadQuery (OpenCASCADE B-Rep) Edition

원본 OpenSCAD 설계(22_apple_sensor_pod.scad)를 CadQuery 2.7 기반으로 1:1 변환한 스크립트.
실행 시 STEP(.step, 정밀 CAD 원본) 및 STL(.stl, 3D 프린터 슬라이서용) 파일을 자동 생성한다.

실행 방법:
    python 22_apple_sensor_pod_cq.py
"""

from __future__ import annotations

import math
from pathlib import Path
import cadquery as cq

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
PCB_Y_MOUNT = 3.5
PCB_Y_BACK = PCB_Y_MOUNT - PCB_T  # Y = +1.9 mm

# 4x 네오디뮴 자석 보스 좌표 (X, Z)
SCREW_PTS: list[tuple[float, float]] = [
    (-35.0, 26.0),
    (35.0, 26.0),
    (-34.0, -23.0),
    (34.0, -23.0),
]

# 자석 포켓 규격 (D6x3mm 자석용 여유 공차 적용: 지름 6.70mm, 깊이 3.60mm)
MAG_R_FRONT = 3.35
MAG_H_FRONT = 3.60
MAG_R_REAR = 3.35
MAG_H_REAR = 3.60

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
def make_revolved_apple(profile: list[tuple[float, float]], use_spline: bool = True) -> cq.Workplane:
    """
    [CadQuery 핵심 1: Workplane("XZ") + revolve]
    XZ 평면(로컬 X=+X, 로컬 Y=+Z, 법선=-Y)에 (R, Z) 단면을 그린 뒤,
    글로벌 Z축(로컬 (0,0,0)->(0,1,0))을 기준으로 360도 회전시킨다.
    use_spline=True 이면 OpenSCAD의 각진 다각형 대신 매끄러운 NURBS 곡면을 생성한다.
    """
    wp = cq.Workplane("XZ")
    if use_spline:
        wp = wp.moveTo(*profile[0]).spline(profile[1:]).close()
    else:
        wp = wp.polyline(profile).close()
    return wp.revolve(360, (0, 0, 0), (0, 1, 0))


def make_functional_cutouts() -> cq.Workplane:
    """상단 사과 꼭지 소켓 홈 + 우측(+X) SHT45 온습도 센서 통기구"""
    # 1) 상단 꼭지 홈: 중심 (0, 1.5, 36.0), r=2.5, h=14 (Z = 29 ~ 43)
    stem_socket = (
        cq.Workplane("XY")
        .workplane(offset=36.0 - 7.0)
        .center(0.0, 1.5)
        .circle(2.5)
        .extrude(14.0)
    )
    # 2) 측면 통기구: 중심 (48.0, -2.0, 16.0), X축 방향 원기둥 r=2.2, h=25
    vent_hole = (
        cq.Workplane("YZ")
        .workplane(offset=48.0 - 12.5)
        .center(-2.0, 16.0)
        .circle(2.2)
        .extrude(25.0)
    )
    return stem_socket.union(vent_hole)


def make_sphere_hull(
    p1: tuple[float, float, float],
    r1: float,
    p2: tuple[float, float, float],
    r2: float,
) -> cq.Workplane:
    """
    [OpenSCAD의 두 구(sphere) hull() 대체]
    두 구와 외접 원뿔대(Tangent Cone)를 결합해 매끄러운 채광 터널을 생성한다.
    """
    v1 = cq.Vector(*p1)
    v2 = cq.Vector(*p2)
    diff = v2 - v1
    dist = diff.Length
    u = diff.normalized()

    dr = r2 - r1
    sin_a = dr / dist
    cos_a = math.sqrt(max(0.0, 1.0 - sin_a * sin_a))

    s1 = -r1 * sin_a
    s2 = dist - r2 * sin_a
    c_r1 = r1 * cos_a
    c_r2 = r2 * cos_a

    sp1 = cq.Solid.makeSphere(r1, v1)
    sp2 = cq.Solid.makeSphere(r2, v2)
    cone = cq.Solid.makeCone(c_r1, c_r2, s2 - s1, v1 + u * s1, u)
    return cq.Workplane(obj=sp1).union(cq.Workplane(obj=sp2)).union(cq.Workplane(obj=cone))


# ============================================================================
# 3. 후면 쉘 (REAR SHELL - 배터리 벨크로 평면 바닥 + 자석 홈 4곳 + BH1750 채광창)
# ============================================================================
def build_rear_shell(outer: cq.Workplane, hollow_apple: cq.Workplane) -> cq.Workplane:
    # A. 중공 사과(outer.cut(inner))에서 Y <= 0 후면 반구 추출 (공면 아티팩트 방지!)
    rear_half_box = cq.Workplane("XY").transformed(offset=(0.0, -70.0, 0.0)).box(140.0, 140.0, 140.0)
    shell_body = hollow_apple.intersect(rear_half_box)

    # B. Y <= -24.5 mm 오픈형 평면 벨크로 배터리 바닥 채우기
    velcro_platform = cq.Workplane("XY").transformed(offset=(0.0, -38.0, 0.0)).box(140.0, 27.0, 140.0)
    internal_union = shell_body.union(velcro_platform)

    # C. 4x 벽체 일체형 자석 보스 (Sketch.hull + loft 로 45도 무서포트 테이퍼 구현)
    # 참고: Workplane("XZ")는 로컬(x, y) = 글로벌(X, +Z), 법선(zDir) = 글로벌(0, -1, 0) 즉 -Y 방향이다.
    for px, pz in SCREW_PTS:
        norm_len = math.hypot(px, pz)
        dir_x, dir_z = px / norm_len, pz / norm_len

        sk_top = (
            cq.Sketch()
            .arc((px, pz), 5.5, 0.0, 360.0)
            .arc((px + dir_x * 10.0, pz + dir_z * 10.0), 6.0, 0.0, 360.0)
            .hull()
        )
        sk_bot = cq.Sketch().push([(px + dir_x * 7.5, pz + dir_z * 7.5)]).circle(4.0)

        # 상단 기둥 (Y = 0 -> -6.5) + 하단 45도 경사 로프트 (Y = -6.5 -> -13.5)
        boss_upper = cq.Workplane("XZ").placeSketch(sk_top).extrude(6.5)
        boss_taper = (
            cq.Workplane("XZ")
            .workplane(offset=6.5)
            .placeSketch(sk_top, sk_bot.moved(cq.Location(cq.Vector(0.0, 0.0, 7.0))))
            .loft(ruled=True)
        )
        internal_union = internal_union.union(boss_upper).union(boss_taper)

    # 외벽 바깥으로 튀어나온 내부 구조물을 사과 외형으로 깔끔하게 트리밍
    rear = outer.intersect(internal_union)

    # D. 5000mAh 배터리 사각 코너 여유 공간 컷아웃 (56.4 x 70.4 mm, 코너 필렛 R2.2, Y = +1.0 -> -24.5)
    # [CadQuery 핵심 2: .rect() + .extrude() + .edges("|Y").fillet()]
    battery_bay_cut = (
        cq.Workplane("XZ")
        .workplane(offset=-1.0)  # Y = +1.0 mm 에서 시작
        .center(0.0, -0.5)
        .rect(56.4, 70.4)
        .extrude(25.5)           # -Y 방향으로 25.5 mm 돌출 -> 바닥 Y = -24.5 mm
        .edges("|Y")             # Y축과 평행한 4개 코너 모서리만 선택해 R2.2 필렛!
        .fillet(2.2)
    )
    rear = rear.cut(battery_bay_cut)

    # E. 4x 후면 자석 포켓 (입구 챔퍼 콘 + D=6.70mm, 깊이 3.60mm 평바닥 원기둥)
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
            .workplane(offset=-0.1)     # Y = +0.1 mm
            .center(px, pz)
            .circle(MAG_R_REAR)
            .extrude(MAG_H_REAR + 0.1)  # Y = -3.60 mm 까지 컷아웃
        )
        rear = rear.cut(cq.Workplane(obj=chamfer_cone)).cut(pocket_cyl)

    # F. BH1750 조도 센서용 채광 터널 (Method 1-A) 및 공통 개구부 컷아웃
    rear = rear.cut(make_sphere_hull((16.0, -8.5, -14.5), 3.8, (48.0, -11.0, -11.0), 4.8))
    rear = rear.cut(make_functional_cutouts())
    return rear


# ============================================================================
# 4. 전면 쉘 (FRONT SHELL - PCB 스탠드오프 4곳 + GPS 안테나 포켓 + 자석 홈 4곳)
# ============================================================================
def build_front_shell(outer: cq.Workplane, hollow_apple: cq.Workplane) -> cq.Workplane:
    """
    참고: Workplane("XZ")는 로컬(x, y) = 글로벌(X, +Z), 법선(zDir) = -Y 이다.
    따라서 offset=-y0 는 글로벌 Y = +y0 위치를 뜻하고, extrude(-L)은 +Y 방향으로 L만큼 돌출한다!
    이렇게 통일하면 X, Z 부호 반전 없이 후면 쉘과 100% 동일한 (X, Z) 좌표를 쓸 수 있다.
    """
    # A. 중공 사과에서 Y >= 0 전면 반구 추출
    front_half_box = cq.Workplane("XY").transformed(offset=(0.0, 70.0, 0.0)).box(140.0, 140.0, 140.0)
    internal_union = hollow_apple.intersect(front_half_box)

    # B. 4x 전면 벽체 일체형 자석 보스 (r=6.8mm, 외벽 방향 앵커링, Y = 0 -> +50.0)
    for px, pz in SCREW_PTS:
        norm_len = math.hypot(px, pz)
        dir_x, dir_z = px / norm_len, pz / norm_len
        sk_boss = (
            cq.Sketch()
            .arc((px, pz), 6.8, 0.0, 360.0)
            .arc((px + dir_x * 14.0, pz + dir_z * 14.0), 6.0, 0.0, 360.0)
            .hull()
        )
        boss = cq.Workplane("XZ").placeSketch(sk_boss).extrude(-50.0)
        internal_union = internal_union.union(boss)

    # C. 4x PCB 고정용 스탠드오프 기둥 + 외벽 보강 리브 (Y = +3.5 mm 마운트 면)
    for dx in (-1, 1):
        for dz in (-1, 1):
            x_pos = dx * (HOLE_PITCH / 2.0)
            z_pos = PCB_Z_CENTER + dz * (HOLE_PITCH / 2.0)
            rib_len_z = 16.5 if dz > 0 else 20.0
            rib_target_x = x_pos + dx * 3.5
            rib_target_z = z_pos + dz * rib_len_z

            # 메인 원기둥 보스 (Y = +3.5 ~ +49.5 mm)
            standoff_cyl = (
                cq.Workplane("XZ")
                .workplane(offset=-PCB_Y_MOUNT)
                .center(x_pos, z_pos)
                .circle(4.0)
                .extrude(-46.0)
            )
            # 외벽 연결 보강 리브 (Y = +5.0 ~ +49.5 mm)
            sk_rib = (
                cq.Sketch()
                .arc((x_pos, z_pos), 4.0, 0.0, 360.0)
                .arc((rib_target_x, rib_target_z), 4.2, 0.0, 360.0)
                .hull()
            )
            standoff_rib = (
                cq.Workplane("XZ")
                .workplane(offset=-(PCB_Y_MOUNT + 1.5))
                .placeSketch(sk_rib)
                .extrude(-44.5)
            )
            internal_union = internal_union.union(standoff_cyl).union(standoff_rib)

    # D. 내장형 GPS 세라믹 안테나 홀더 (20 x 5 x 7 mm, Bowl-Up 32도 무서포트 경사대 로프트)
    gps_outer_h = GPS_LEN_Z + 2.0 * GPS_WALL  # 26.4 mm
    sk_gps_base = cq.Sketch().push([(-40.5, GPS_Z_CENTER)]).rect(19.0, gps_outer_h)
    sk_gps_tip = cq.Sketch().push([(-45.5, GPS_Z_CENTER)]).rect(9.0, gps_outer_h - 4.0)

    gps_base = cq.Workplane("XZ").placeSketch(sk_gps_base).extrude(-11.0)
    gps_ramp = (
        cq.Workplane("XZ")
        .workplane(offset=-11.0)
        .placeSketch(sk_gps_base, sk_gps_tip.moved(cq.Location(cq.Vector(0.0, 0.0, -14.5))))
        .loft(ruled=True)
    )
    gps_holder = gps_base.union(gps_ramp)

    # GPS 내부 슬라이드 포켓 / 납땜 여유 홈 / 입구 가이드 / 동축케이블 슬롯 컷아웃
    pocket_main = cq.Workplane("XY").transformed(offset=(GPS_X_CENTER, 4.65, GPS_Z_CENTER)).box(5.8, 9.6, GPS_LEN_Z)
    pocket_relief = cq.Workplane("XY").transformed(offset=(GPS_X_CENTER, 4.65, GPS_Z_CENTER)).box(7.8, 9.6, GPS_LEN_Z - 5.0)
    pocket_entry = cq.Workplane("XY").transformed(offset=(GPS_X_CENTER, 0.7, GPS_Z_CENTER)).box(8.2, 1.6, GPS_LEN_Z + 0.8)
    cable_slot = cq.Workplane("XY").transformed(offset=(GPS_X_CENTER, 4.5, GPS_Z_CENTER + GPS_LEN_Z / 2.0)).box(4.4, 9.2, 8.0)

    gps_holder = gps_holder.cut(pocket_main).cut(pocket_relief).cut(pocket_entry).cut(cable_slot)
    internal_union = internal_union.union(gps_holder)

    # 사과 외형 안쪽으로 깔끔하게 교집합 트리밍
    front = outer.intersect(internal_union)

    # E. 4x 전면 자석 포켓 컷아웃 (D=6.70mm, 깊이 3.60mm, 후면 자석 포켓과 100% 동축 정렬)
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
            .workplane(offset=0.1)  # Y = -0.1 mm
            .center(px, pz)
            .circle(MAG_R_FRONT)
            .extrude(-(MAG_H_FRONT + 0.1))  # Y = +3.60 mm 까지 컷아웃
        )
        front = front.cut(cq.Workplane(obj=chamfer_cone)).cut(pocket_cyl)

    # F. 4x PCB M3 블라인드 파일럿 홀 (전면 외피를 절대 뚫지 않는 막힌 구멍, 깊이 20.0mm)
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
    # 1) 하단 결합 핀 (중심 (0, 1.5, 34.0), r=2.3, h=10 -> Z = 29 ~ 39)
    pin = (
        cq.Workplane("XY")
        .workplane(offset=29.0)
        .center(0.0, 1.5)
        .circle(2.3)
        .extrude(10.0)
    )

    # 2) 14도 기울어진 줄기 원뿔대
    trunk_cone = cq.Solid.makeCone(2.5, 1.6, 15.0, cq.Vector(0, 0, 0), cq.Vector(0, 0, 1))
    trunk = (
        cq.Workplane(obj=trunk_cone)
        .rotate((0, 0, 0), (0, 1, 0), 14.0)
        .translate((0.0, 1.5, 39.0))
    )

    # 3) 비균일 스케일(1.8, 0.8, 0.3) 타원체 잎사귀 (Matrix + transformGeometry 활용)
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
    """B-Spline 제어점 여유값을 제외한 실제 표면 정밀 치수(xlen, ylen, zlen, zmin, zmax) 측정"""
    verts, _ = part.val().tessellate(0.03)
    xs = [v.x for v in verts]
    ys = [v.y for v in verts]
    zs = [v.z for v in verts]
    return max(xs) - min(xs), max(ys) - min(ys), max(zs) - min(zs), min(zs), max(zs)


# ============================================================================
# 6. 출력 정렬 (Bowl-Up) 및 STEP / STL 일괄 빌드 실행부
# ============================================================================
def export_all(out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    print("[1/4] 사과 외벽/내벽 B-Rep 회전체 및 중공 바디 생성 중...")
    outer = make_revolved_apple(APPLE_OUTER_PROFILE, use_spline=False)
    inner = make_revolved_apple(APPLE_INNER_PROFILE, use_spline=False)
    hollow_apple = outer.cut(inner)

    print("[2/4] 후면 쉘(Rear Shell), 전면 쉘(Front Shell), 꼭지(Stem) B-Rep 모델링 중...")
    rear_shell = build_rear_shell(outer, hollow_apple)
    front_shell = build_front_shell(outer, hollow_apple)
    stem = build_stem()

    # 3DWOX 2X 무서포트 출력용 그릇 방향(Bowl-Up, Z_min = 0.00 mm 정밀 안착) 사전 정렬
    rear_rot = rear_shell.rotate((0, 0, 0), (1, 0, 0), 90.0)
    _, _, _, r_zmin, _ = measure_exact_mesh_bounds(rear_rot)
    rear_print = rear_rot.translate((0.0, 0.0, -r_zmin))

    front_rot = front_shell.rotate((0, 0, 0), (1, 0, 0), -90.0)
    _, _, _, f_zmin, _ = measure_exact_mesh_bounds(front_rot)
    front_print = front_rot.translate((0.0, 0.0, -f_zmin))

    _, _, _, s_zmin, _ = measure_exact_mesh_bounds(stem)
    stem_print = stem.translate((0.0, -1.5, -s_zmin))

    print("[3/4] 전체 조립체(Assembly) 구성 중...")
    assy = cq.Assembly(name="v22_Apple_Sensor_Pod")
    assy.add(rear_shell, name="rear_shell", color=cq.Color(0.62, 0.18, 0.75, 0.6))
    assy.add(front_shell, name="front_shell", color=cq.Color(0.95, 0.78, 0.12, 0.6))
    assy.add(stem, name="apple_stem", color=cq.Color(0.28, 0.65, 0.22, 1.0))

    print("[4/4] STEP(.step) 및 STL(.stl) 파일 내보내기 중...")
    parts_to_export = {
        "22_apple_rear_shell_cq": rear_print,
        "22_apple_front_shell_cq": front_print,
        "22_apple_stem_cq": stem_print,
    }

    for name, part in parts_to_export.items():
        step_path = out_dir / f"{name}.step"
        stl_path = out_dir / f"{name}.stl"
        cq.exporters.export(part, str(step_path))
        cq.exporters.export(part, str(stl_path), tolerance=0.04, angularTolerance=0.08)

        xlen, ylen, zlen, zmin, zmax = measure_exact_mesh_bounds(part)
        print(
            f"  -> {name}: "
            f"크기 = {xlen:.1f} x {ylen:.1f} x {zlen:.1f} mm | "
            f"Z 범위 = [{zmin:.2f}, {zmax:.2f}] mm"
        )

    assy_step_path = out_dir / "22_apple_assembly_cq.step"
    assy.export(str(assy_step_path))
    print(f"  -> 조립체 STEP 저장 완료: {assy_step_path.name}")


if __name__ == "__main__":
    target_dir = Path(__file__).resolve().parent
    export_all(target_dir)
