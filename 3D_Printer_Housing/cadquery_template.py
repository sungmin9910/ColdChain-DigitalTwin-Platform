"""
Cold Chain Digital Twin Platform - CadQuery + CQ-Editor 표준 스타터 템플릿

사용법:
  1) CQ-Editor에서 열기 (File -> Open) 후 F5(Render) 클릭 -> 3D 화면 및 Objects 트리에 즉시 표시
  2) 터미널에서 실행: python cadquery_template.py -> 동일 폴더에 .step 및 .stl 자동 생성
"""

from __future__ import annotations

from pathlib import Path
import cadquery as cq

# ============================================================================
# 0. CQ-Editor 화면 표시 모드 ("assembly" | "exploded" | "print_layout" | "body")
# ============================================================================
VIEW_MODE = "assembly"

# ============================================================================
# 1. 파라메트릭 치수 변수 (단위: mm)
# ============================================================================
OUTER_W = 60.0
OUTER_D = 60.0
OUTER_H = 25.0
WALL_T = 2.8
CORNER_R = 4.0
CLEARANCE = 0.25


# ============================================================================
# 2. 부품 모델링 함수
# ============================================================================
def build_lower_body() -> cq.Workplane:
    """하부 케이스 예시 (외곽 필렛 + 내부 포켓 가공)"""
    cavity_w = OUTER_W - 2.0 * WALL_T
    cavity_d = OUTER_D - 2.0 * WALL_T
    cavity_h = OUTER_H - WALL_T

    body = (
        cq.Workplane("XY")
        .box(OUTER_W, OUTER_D, OUTER_H, centered=(True, True, False))
        .edges("|Z")
        .fillet(CORNER_R)
        .faces(">Z")
        .workplane()
        .rect(cavity_w, cavity_d)
        .cutBlind(-cavity_h)
    )
    return body


def build_upper_lid() -> cq.Workplane:
    """상부 뚜껑 예시 (결합 립 포함)"""
    lip_w = OUTER_W - 2.0 * (WALL_T + CLEARANCE)
    lip_d = OUTER_D - 2.0 * (WALL_T + CLEARANCE)

    lid_top = (
        cq.Workplane("XY")
        .workplane(offset=OUTER_H)
        .box(OUTER_W, OUTER_D, WALL_T, centered=(True, True, False))
        .edges("|Z")
        .fillet(CORNER_R)
    )
    lid_lip = (
        cq.Workplane("XY")
        .workplane(offset=OUTER_H - 3.0)
        .box(lip_w, lip_d, 3.0, centered=(True, True, False))
        .edges("|Z")
        .fillet(max(0.8, CORNER_R - WALL_T))
        .faces("<Z")
        .workplane()
        .rect(lip_w - 2.4, lip_d - 2.4)
        .cutBlind(-3.0)
    )
    return lid_top.union(lid_lip)


def align_to_bed(part: cq.Workplane) -> cq.Workplane:
    """3D 프린터 베드 바닥(Z_min = 0.00 mm)에 자동 밀착 정렬"""
    verts, _ = part.val().tessellate(0.05)
    zmin = min(v.z for v in verts)
    return part.translate((0.0, 0.0, -zmin))


# ============================================================================
# 3. CQ-Editor 연동부 (F5 렌더링 시 자동 실행)
# ============================================================================
def render_for_cq_editor(show_fn) -> None:
    lower = build_lower_body()
    upper = build_upper_lid()

    if VIEW_MODE == "body":
        show_fn(lower, name="Lower_Body", options={"color": "#4b7bec"})
    elif VIEW_MODE == "exploded":
        show_fn(lower, name="Lower_Body", options={"color": "#4b7bec"})
        show_fn(upper.translate((0.0, 0.0, 20.0)), name="Upper_Lid", options={"color": "#fed330"})
    elif VIEW_MODE == "print_layout":
        # 뚜껑은 뒤집어서 상판이 바닥(Z=0)에 닿도록 무서포트 정렬
        lid_flipped = align_to_bed(upper.rotate((0.0, 0.0, 0.0), (1.0, 0.0, 0.0), 180.0))
        show_fn(align_to_bed(lower).translate((-40.0, 0.0, 0.0)), name="Lower_Print", options={"color": "#4b7bec"})
        show_fn(lid_flipped.translate((40.0, 0.0, 0.0)), name="Upper_Print", options={"color": "#fed330"})
    else:
        show_fn(lower, name="Lower_Body", options={"color": "#4b7bec", "alpha": 0.65})
        show_fn(upper, name="Upper_Lid", options={"color": "#fed330", "alpha": 0.55})


# ============================================================================
# 4. 터미널 실행 시 STEP / STL 일괄 저장부
# ============================================================================
def export_all(out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    lower_print = align_to_bed(build_lower_body())
    upper_print = align_to_bed(build_upper_lid().rotate((0.0, 0.0, 0.0), (1.0, 0.0, 0.0), 180.0))

    for name, part in [("template_lower_body", lower_print), ("template_upper_lid", upper_print)]:
        cq.exporters.export(part, str(out_dir / f"{name}.step"))
        cq.exporters.export(part, str(out_dir / f"{name}.stl"), tolerance=0.04, angularTolerance=0.08)
        print(f"Saved: {name}.step / {name}.stl")


if "show_object" in globals():
    render_for_cq_editor(globals()["show_object"])  # type: ignore[name-defined]
elif __name__ == "__main__":
    export_all(Path(__file__).resolve().parent / "scratch_out")
