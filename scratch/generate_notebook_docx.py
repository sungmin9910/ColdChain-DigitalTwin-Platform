# -*- coding: utf-8 -*-
"""
연구노트 (Research Lab Notebook) Word(.docx) 생성 스크립트 (v2 — 상단 형식 표 제거 + 전 일자 실제 사진/실행 캡처 수록)
대상 과제: 수확 후 농산물 신선도 보장을 위한 양방향 콜드체인 디지털 트윈 플랫폼 개발
구성: 표지(1p) + 작성원칙 및 단계별 요약(1p) + 전체 일자별 목차(2p) + 일자별 연구노트 본문(68p, 1일 1장, 전 페이지 실제 사진/캡처 포함) = 총 72장(A4)
"""

import math
from pathlib import Path
from PIL import Image, ImageOps
from docx import Document
from docx.shared import Mm, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import qn, nsdecls

from nb_part1 import DAYS_PART1
from nb_part2 import DAYS_PART2
from nb_part3 import DAYS_PART3
from nb_part4 import DAYS_PART4
from nb_image_map import DAY_IMAGE_MAP


ROOT = Path(r"c:\Users\korea\Desktop\1hsm\hanhanhan\ColdChain-DigitalTwin-Platform")
CACHE_DIR = ROOT / "scratch" / "notebook_captures" / "embed_cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

FONT_NAME = "맑은 고딕"
NAVY = RGBColor(0x1E, 0x3A, 0x5F)
DARK_SLATE = RGBColor(0x1E, 0x29, 0x3B)
MUTED_GRAY = RGBColor(0x47, 0x55, 0x69)
FAIL_RED = RGBColor(0x99, 0x1B, 0x1B)
FIX_GREEN = RGBColor(0x16, 0x65, 0x34)


def set_east_asia_font(run, font_name=FONT_NAME, size_pt=8.8, bold=False, color=DARK_SLATE):
    run.font.name = font_name
    run.font.size = Pt(size_pt)
    run.bold = bold
    if color is not None:
        run.font.color.rgb = color
    rPr = run._element.get_or_add_rPr()
    rFonts = rPr.find(qn("w:rFonts"))
    if rFonts is None:
        rFonts = OxmlElement("w:rFonts")
        rPr.insert(0, rFonts)
    rFonts.set(qn("w:ascii"), font_name)
    rFonts.set(qn("w:hAnsi"), font_name)
    rFonts.set(qn("w:eastAsia"), font_name)
    rFonts.set(qn("w:cs"), font_name)


def set_paragraph_bottom_border(paragraph, color_hex="1E3A5F", sz="10"):
    pPr = paragraph._p.get_or_add_pPr()
    pBdr = parse_xml(
        f'<w:pBdr {nsdecls("w")}><w:bottom w:val="single" w:sz="{sz}" w:space="3" w:color="{color_hex}"/></w:pBdr>'
    )
    pPr.append(pBdr)


def set_cell_shading(cell, hex_color: str):
    shading = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    cell._tc.get_or_add_tcPr().append(shading)


def set_cell_margins(cell, top=45, bottom=45, left=90, right=90):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement("w:tcMar")
    for m, val in [("top", top), ("bottom", bottom), ("left", left), ("right", right)]:
        node = OxmlElement(f"w:{m}")
        node.set(qn("w:w"), str(val))
        node.set(qn("w:type"), "dxa")
        tcMar.append(node)
    tcPr.append(tcMar)


def set_table_borders(table, border_color="CBD5E1", header_top_color="1E3A5F"):
    tblPr = table._tbl.tblPr
    borders = parse_xml(
        f"""
        <w:tblBorders {nsdecls("w")}>
            <w:top w:val="single" w:sz="10" w:space="0" w:color="{header_top_color}"/>
            <w:bottom w:val="single" w:sz="8" w:space="0" w:color="{header_top_color}"/>
            <w:left w:val="single" w:sz="4" w:space="0" w:color="{border_color}"/>
            <w:right w:val="single" w:sz="4" w:space="0" w:color="{border_color}"/>
            <w:insideH w:val="single" w:sz="4" w:space="0" w:color="{border_color}"/>
            <w:insideV w:val="single" w:sz="4" w:space="0" w:color="{border_color}"/>
        </w:tblBorders>
        """
    )
    tblPr.append(borders)


def set_callout_borders(table, left_color="DC2626", bg_color="FEF2F2"):
    tblPr = table._tbl.tblPr
    borders = parse_xml(
        f"""
        <w:tblBorders {nsdecls("w")}>
            <w:top w:val="single" w:sz="4" w:space="0" w:color="E2E8F0"/>
            <w:bottom w:val="single" w:sz="4" w:space="0" w:color="E2E8F0"/>
            <w:left w:val="single" w:sz="22" w:space="0" w:color="{left_color}"/>
            <w:right w:val="single" w:sz="4" w:space="0" w:color="E2E8F0"/>
        </w:tblBorders>
        """
    )
    tblPr.append(borders)
    set_cell_shading(table.cell(0, 0), bg_color)


def add_page_number_fields(paragraph):
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r1 = paragraph.add_run("- ")
    set_east_asia_font(r1, size_pt=8.2, color=MUTED_GRAY)

    for field_name in ["PAGE", "NUMPAGES"]:
        if field_name == "NUMPAGES":
            sep = paragraph.add_run(" / ")
            set_east_asia_font(sep, size_pt=8.2, color=MUTED_GRAY)
        run_begin = paragraph.add_run()
        set_east_asia_font(run_begin, size_pt=8.2, color=MUTED_GRAY)
        fldChar1 = parse_xml(r'<w:fldChar %s w:fldCharType="begin"/>' % nsdecls("w"))
        instrText = parse_xml(r'<w:instrText %s xml:space="preserve"> %s </w:instrText>' % (nsdecls("w"), field_name))
        fldChar2 = parse_xml(r'<w:fldChar %s w:fldCharType="separate"/>' % nsdecls("w"))
        fldChar3 = parse_xml(r'<w:fldChar %s w:fldCharType="end"/>' % nsdecls("w"))
        run_begin._r.append(fldChar1)
        run_begin._r.append(instrText)
        run_begin._r.append(fldChar2)
        run_begin._r.append(fldChar3)

    r2 = paragraph.add_run(" -")
    set_east_asia_font(r2, size_pt=8.2, color=MUTED_GRAY)


def add_para(doc, text="", size_pt=8.6, bold=False, color=DARK_SLATE, space_before=0.0, space_after=1.8, line_spacing=1.14, align=WD_ALIGN_PARAGRAPH.LEFT):
    p = doc.add_paragraph()
    p.alignment = align
    pf = p.paragraph_format
    pf.space_before = Pt(space_before)
    pf.space_after = Pt(space_after)
    pf.line_spacing = line_spacing
    if text:
        r = p.add_run(text)
        set_east_asia_font(r, size_pt=size_pt, bold=bold, color=color)
    return p


def fill_cell(cell, text, size_pt=8.2, bold=False, color=DARK_SLATE, align=WD_ALIGN_PARAGRAPH.LEFT, pad_v=36, pad_h=80):
    cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
    set_cell_margins(cell, top=pad_v, bottom=pad_v, left=pad_h, right=pad_h)
    p = cell.paragraphs[0]
    p.alignment = align
    pf = p.paragraph_format
    pf.space_before = Pt(0)
    pf.space_after = Pt(0)
    pf.line_spacing = 1.12
    r = p.add_run(text)
    set_east_asia_font(r, size_pt=size_pt, bold=bold, color=color)
    return p


def estimate_lines(text: str, chars_per_line: int = 58) -> int:
    """Korean full-width aware line wrap estimator for A4 content width (180mm)."""
    eff_len = 0.0
    for ch in text:
        eff_len += 1.0 if ord(ch) > 127 else 0.55
    return max(1, math.ceil(eff_len / chars_per_line))


def prepare_embed_image(day_num: int, rel_path: str) -> tuple[Path, int, int]:
    """EXIF 방향 정규화 및 300+ DPI 인쇄 품질 유지 최적 해상도(최대 1600px) 준비"""
    src = ROOT / rel_path
    assert src.exists(), f"Missing image for Day {day_num}: {src}"
    with Image.open(src) as im:
        im = ImageOps.exif_transpose(im)
        w, h = im.size
        max_dim = 1550
        if max(w, h) > max_dim:
            scale = max_dim / float(max(w, h))
            w = max(1, int(round(w * scale)))
            h = max(1, int(round(h * scale)))
            im = im.resize((w, h), Image.Resampling.LANCZOS)

        # Save clean PNG or high-quality JPEG to embed cache
        if src.suffix.lower() in {".jpg", ".jpeg"} or (w * h > 900_000 and im.mode == "RGB"):
            rgb = im.convert("RGB")
            dst = CACHE_DIR / f"day_{day_num:02d}.jpg"
            rgb.save(dst, format="JPEG", quality=91, optimize=True)
        else:
            dst = CACHE_DIR / f"day_{day_num:02d}.png"
            im.save(dst, format="PNG", optimize=True)
        return dst, w, h


def build_cover_page(doc: Document, total_days: int):
    add_para(doc, "", size_pt=10, space_after=18)
    add_para(
        doc,
        "RESEARCH LAB NOTEBOOK  |  실증 하드웨어·소프트웨어 개발 기록부",
        size_pt=10.5,
        bold=True,
        color=NAVY,
        space_after=8,
        align=WD_ALIGN_PARAGRAPH.CENTER,
    )
    add_para(
        doc,
        "연  구  노  트",
        size_pt=30,
        bold=True,
        color=DARK_SLATE,
        space_before=6,
        space_after=8,
        align=WD_ALIGN_PARAGRAPH.CENTER,
    )
    add_para(
        doc,
        "수확 후 농산물의 신선도 보장을 위한 양방향 디지털 트윈 기반\n실시간 콜드체인 유통 관제 및 신뢰성 검증 플랫폼 개발",
        size_pt=13.5,
        bold=True,
        color=NAVY,
        space_before=6,
        space_after=6,
        line_spacing=1.35,
        align=WD_ALIGN_PARAGRAPH.CENTER,
    )
    add_para(
        doc,
        "Development of a Bi-directional Cold-Chain Digital Twin Platform\nfor Postharvest Freshness Assurance and Traceability",
        size_pt=9.5,
        bold=False,
        color=MUTED_GRAY,
        space_after=22,
        line_spacing=1.25,
        align=WD_ALIGN_PARAGRAPH.CENTER,
    )

    # Cover Summary Image (Real Hardware Assembly Photo!)
    cover_img_path, cw, ch = prepare_embed_image(0, "3D_Printer_Housing/v21_Apple_Sensor_Pod_2Piece5000mAh/KakaoTalk_20261015_114727151.jpg")
    p_img = doc.add_paragraph()
    p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_img.paragraph_format.space_after = Pt(4)
    p_img.add_run().add_picture(str(cover_img_path), height=Mm(56))
    add_para(
        doc,
        "▲ 독자 개발 50×50mm CarrierBoard(Beetle ESP32-C6) 및 3D 프린팅 사과 센서팟 실물 조립체",
        size_pt=8.3,
        color=MUTED_GRAY,
        space_after=14,
        align=WD_ALIGN_PARAGRAPH.CENTER,
    )

    tbl = doc.add_table(rows=7, cols=2)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl)
    meta_rows = [
        ("연구 수행 기관 / 연구실", "전북대학교 농업기계공학과  |  Agricultural Sensor and Robotics Lab"),
        ("연구 기록자", "한 성 민  (석사과정 / yuyu6243@gmail.com)"),
        ("연구 기록 기간", f"2026년 03월 22일  ~  2026년 11월 13일  (총 {total_days}일차, 1일 1페이지 구성)"),
        ("핵심 하드웨어 구성", "CarrierBoard Beetle ESP32-C6 (1~4호차), GM77/MQ160W QR 스캐너, Jetson Orin Nano, CadQuery v22 사과 센서팟"),
        ("핵심 소프트웨어 구성", "ESP32 LittleFS 링버퍼 펌웨어, AWS EC2 24/7 수집 데몬, AWS RDS MySQL, Streamlit 듀얼 대시보드"),
        ("수록 시각 증빙 자료", "전 일자(68일) 실물 하드웨어 촬영본, 실제 보드 시리얼 로그, AWS RDS/파이썬 실행 결과 및 정밀 CAD 수록 (AI 이미지 0건)"),
        ("형상관리 원격 저장소", "https://github.com/sungmin9910/ColdChain-DigitalTwin-Platform"),
    ]
    col_widths = [Mm(50), Mm(130)]
    for idx, (k, v) in enumerate(meta_rows):
        row = tbl.rows[idx]
        row.cells[0].width = col_widths[0]
        row.cells[1].width = col_widths[1]
        set_cell_shading(row.cells[0], "F1F5F9")
        fill_cell(row.cells[0], k, size_pt=9.0, bold=True, color=NAVY, align=WD_ALIGN_PARAGRAPH.CENTER, pad_v=65)
        fill_cell(row.cells[1], v, size_pt=8.8, bold=(idx == 1), color=DARK_SLATE, pad_v=65)

    add_para(
        doc,
        "※ 본 연구노트는 실제 Git 커밋 이력(200+ commits), 실물 보드·센서 촬영 사진, AWS RDS 실측 DB 및 파이썬 실행 캡처 원본에 의거하여 작성됨.",
        size_pt=8.3,
        color=MUTED_GRAY,
        space_before=14,
        align=WD_ALIGN_PARAGRAPH.CENTER,
    )
    doc.add_page_break()


def build_guideline_and_phase_page(doc: Document):
    add_para(doc, "Ⅰ. 연구노트 작성 원칙 및 단계별 연구개발 총괄표", size_pt=13.0, bold=True, color=NAVY, space_after=6)
    add_para(
        doc,
        "본 연구노트는 성공한 최종 결과뿐만 아니라 연구 과정에서 직면한 센서 180° 역삽입, 전원 스위치 패드 박리, 부트로더 진입 실패, 주행 중 통신 두절, 3D 프린팅 기구 간섭 등 모든 실패(Trial & Error)와 해결 과정을 실제 촬영 사진 및 파이썬·보드 실행 결과 캡처와 함께 기록하였다.",
        size_pt=8.9,
        space_after=8,
    )

    rules = [
        "1. 실증 데이터 및 실제 캡처 원칙: 모든 페이지의 시각 자료는 실제 촬영한 하드웨어·실험 사진, 보드 시리얼 모니터 출력, AWS RDS 실데이터 기반 파이썬 플롯, 실제 동작 대시보드 캡처 및 정밀 CAD 산출물만 사용한다(AI 생성 이미지 배제).",
        "2. 실패 및 설계 변경 보존 원칙: 작동하지 않았던 초기 시도(DHT11 양자화 한계, 기둥 날개 간섭, get_columns 누락, 유령 충격 등)를 삭제하지 않고 원인 진단과 변경 전·후 정량 수치를 함께 기록한다.",
        "3. 1일 1페이지 완결 원칙: 각 일자별 기록(Day 01 ~ Day 68)은 불필요한 상단 형식 표를 배제하고 핵심 목적·실험·실제 사진/결과 캡처·시행착오·정량 검증을 A4 1페이지 내에 완결 배치한다.",
    ]
    for r_txt in rules:
        add_para(doc, r_txt, size_pt=8.6, space_after=3.5)

    add_para(doc, "■ 전 주기 연구개발 단계(Phase 1 ~ Phase 15) 요약", size_pt=10.2, bold=True, color=NAVY, space_before=7, space_after=4)

    phases = [
        ("Phase 1", "03.22 ~ 04.27", "Day 01~07", "연구 기획, Jetson Orin Nano JP6.2 3D/TensorRT 구축(OOM 해결), DHT11 한계 검증 및 초기 웹 프로토타입"),
        ("Phase 2", "05.03 ~ 05.20", "Day 08~15", "AWS RDS MySQL 구축, Flask→Streamlit 전면 개편, KST 타임존/다크모드/GPS 0좌표 필터링 해결"),
        ("Phase 3", "05.27 ~ 06.28", "Day 16~22", "GM77+ESP32 스마트 스캐너 UART Wake-up 해결, OpenSCAD 좌/우 반할 하우징(v06→v17) 완성"),
        ("Phase 4", "07.07 ~ 08.24", "Day 23~27", "GY-521 고속 Peak-Hold 충격 계측, Sorting GUI 및 무선 스캐너 자동 단계 판별, Beetle C6 선정"),
        ("Phase 5", "08.30 ~ 09.29", "Day 28~31", "50×50mm 양면 CarrierBoard PCB 설계·발주(Gerber/STEP) 및 과일 디지털 트윈(FDT) 5대 수학 모델 정립"),
        ("Phase 6", "09.30 ~ 10.03", "Day 32~36", "실물 PCB 조립, 센서 180° 역삽입 I2C 복구, 전주↔대전 174km 주행 복원, SW1 보강 및 LittleFS 링버퍼"),
        ("Phase 7", "10.06 ~ 10.09", "Day 37~39", "냉장 급랭 열시상수(τ) 규명, Jetson 2분할 Split HUD 대시보드, 주행 세션 병합 및 Wi-Fi 블로킹 제거"),
        ("Phase 8~9", "10.10 ~ 10.12", "Day 40~46", "5000mAh 100mm 사과팟(v19~v21), GM77 부트루프 및 get_columns() 버그 해결, 상자 #77 A00~A15 실증"),
        ("Phase 10~11", "10.13 ~ 10.17", "Day 47~52", "1.5cm 단차 기둥(GPS 간섭 해결), 실물 출력 가조립(v21→v22), 1~4호차 구축 및 02호차 주야간 실차 주행"),
        ("Phase 12~13", "10.17 ~ 10.29", "Day 53~60", "AWS EC2 24/7 무인 데몬 배포, 유령 충격 스택 버그 박멸, 04호차 장거리 실증, G-code 및 공차 보정"),
        ("Phase 14~15", "11.02 ~ 11.13", "Day 61~68", "CadQuery 2.7 B-Rep 전환, Z=0 무서포트 직결 기둥, 4점 베요넷 잠금 & 굴뚝 통풍, 국내 유통 적용성 감사"),
    ]

    tbl = doc.add_table(rows=len(phases) + 1, cols=4)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl)
    widths = [Mm(24), Mm(28), Mm(22), Mm(106)]
    headers = ["단계", "수행 기간", "연구일차", "핵심 연구 내용 및 주요 시행착오 해결 성과"]
    for c_i, h in enumerate(headers):
        c = tbl.rows[0].cells[c_i]
        c.width = widths[c_i]
        set_cell_shading(c, "1E3A5F")
        fill_cell(c, h, size_pt=8.4, bold=True, color=RGBColor(255, 255, 255), align=WD_ALIGN_PARAGRAPH.CENTER, pad_v=50)

    for r_i, row_data in enumerate(phases, start=1):
        for c_i, val in enumerate(row_data):
            c = tbl.rows[r_i].cells[c_i]
            c.width = widths[c_i]
            if r_i % 2 == 0:
                set_cell_shading(c, "F8FAFC")
            fill_cell(
                c,
                val,
                size_pt=8.1,
                bold=(c_i == 0),
                color=NAVY if c_i == 0 else DARK_SLATE,
                align=WD_ALIGN_PARAGRAPH.CENTER if c_i < 3 else WD_ALIGN_PARAGRAPH.LEFT,
                pad_v=48,
            )

    add_para(
        doc,
        "■ 핵심 정량적 달성 지표: ① 왕복 174km 고속도로 및 다중 도심 주행 데이터 유실률 0.0%  ② 급랭 실험 기반 열응답 시상수 도출  ③ 실물 스캐너 A00~A15 자동 전이 완주  ④ 1~4호차 멀티 플릿 + AWS EC2 24/7 무인 적재(총 31개 세션, 6,500+ 레코드) 완성.",
        size_pt=8.5,
        bold=True,
        color=FIX_GREEN,
        space_before=8,
    )
    doc.add_page_break()


def build_toc_pages(doc: Document, all_days: list[dict]):
    chunks = [all_days[:34], all_days[34:]]
    for page_idx, chunk in enumerate(chunks, start=1):
        add_para(
            doc,
            f"Ⅱ. 일자별 연구노트 전체 목차 ({page_idx}/2)  —  Day {chunk[0]['day']:02d} ~ Day {chunk[-1]['day']:02d}",
            size_pt=12.2,
            bold=True,
            color=NAVY,
            space_after=5,
        )
        tbl = doc.add_table(rows=len(chunk) + 1, cols=4)
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        set_table_borders(tbl)
        widths = [Mm(16), Mm(24), Mm(112), Mm(28)]
        headers = ["일차", "작성일자", "연구노트 주제 (실제 사진·실행 캡처 및 시행착오 포함)", "기준 커밋/문서"]
        for c_i, h in enumerate(headers):
            c = tbl.rows[0].cells[c_i]
            c.width = widths[c_i]
            set_cell_shading(c, "1E3A5F")
            fill_cell(c, h, size_pt=8.0, bold=True, color=RGBColor(255, 255, 255), align=WD_ALIGN_PARAGRAPH.CENTER, pad_v=34)

        for r_i, item in enumerate(chunk, start=1):
            short_commit = item["commit"].split(",")[0].strip()[:14]
            vals = [f"Day {item['day']:02d}", item["date"], item["title"], short_commit]
            for c_i, val in enumerate(vals):
                c = tbl.rows[r_i].cells[c_i]
                c.width = widths[c_i]
                if r_i % 2 == 0:
                    set_cell_shading(c, "F8FAFC")
                fill_cell(
                    c,
                    val,
                    size_pt=7.6,
                    bold=(c_i == 0),
                    color=NAVY if c_i == 0 else DARK_SLATE,
                    align=WD_ALIGN_PARAGRAPH.CENTER if c_i in (0, 1, 3) else WD_ALIGN_PARAGRAPH.LEFT,
                    pad_v=23,
                    pad_h=55,
                )
        doc.add_page_break()


def estimate_day_text_pt(entry: dict, caption_txt: str) -> float:
    """Estimates total non-image vertical height in points (pt) for dynamic image scaling."""
    pt = 0.0
    # Clean 2-line title header
    pt += estimate_lines(f"[Day {entry['day']:02d} | {entry['date']}] {entry['title']}", 48) * 14.5 + 16.0
    # Section 1
    pt += 15.0 + estimate_lines(entry["objective"], 58) * 10.6 + 2.0
    # Section 2
    pt += 15.0
    for idx, w_item in enumerate(entry["work"], start=1):
        pt += estimate_lines(f"• [{idx}] {w_item}", 58) * 10.4 + 1.8
    # Caption below image
    pt += estimate_lines(caption_txt, 62) * 9.6 + 6.0
    # Section 3 (Failure Callout)
    fail_txt = f"[시행착오 및 원인 진단] {entry['failure']}"
    pt += 15.0 + estimate_lines(fail_txt, 54) * 10.3 + 11.0
    # Section 4 (Design Changes)
    pt += 15.0
    for c_item in entry["change"]:
        pt += estimate_lines(f"✔ [해결] {c_item}", 58) * 10.4 + 1.8
    # Section 5 (Metrics Table)
    pt += 16.0 + 18.0
    for m_name, m_before, m_after in entry["metrics"]:
        row_lines = max(
            estimate_lines(m_name, 13),
            estimate_lines(m_before, 22),
            estimate_lines(m_after, 23),
        )
        pt += row_lines * 9.8 + 6.5
    # Section 6 (Next Plan)
    pt += 14.5 + estimate_lines(f"→ 차기 계획: {entry['next']}", 58) * 10.2 + 3.0
    return pt


def build_day_page(doc: Document, entry: dict, is_last: bool = False) -> tuple[float, float]:
    """Renders 1 clean A4 page without the top formal table, embedding an authentic photo/capture."""
    day_num = entry["day"]
    rel_img, caption_txt = DAY_IMAGE_MAP[day_num]
    embed_path, px_w, px_h = prepare_embed_image(day_num, rel_img)

    # Calculate exact available height for image so total page stays ~685-720 pt (< 773.8 pt usable A4)
    text_pt = estimate_day_text_pt(entry, caption_txt)
    avail_img_pt = max(118.0, min(172.0, 712.0 - text_pt))
    img_h_mm = avail_img_pt / 2.83465
    aspect = px_w / float(px_h)
    img_w_mm = img_h_mm * aspect
    if img_w_mm > 158.0:
        img_w_mm = 158.0
        img_h_mm = img_w_mm / aspect

    # 1. Clean Top Heading (NO formal 4-row metadata table!)
    p_title = add_para(
        doc,
        f"Day {day_num:02d}  |  {entry['date']}  —  {entry['title']}",
        size_pt=10.8,
        bold=True,
        color=NAVY,
        space_before=0.0,
        space_after=1.5,
        line_spacing=1.15,
    )
    p_sub = add_para(
        doc,
        f"{entry['phase']}   ·   관련 파일/커밋: {entry['files']}  ({entry['commit']})",
        size_pt=7.7,
        bold=False,
        color=MUTED_GRAY,
        space_before=0.0,
        space_after=4.5,
        line_spacing=1.10,
    )
    set_paragraph_bottom_border(p_sub, color_hex="1E3A5F", sz="8")

    # 2. Section 1: Objective
    add_para(doc, "1. 연구 목적 및 배경", size_pt=9.2, bold=True, color=NAVY, space_before=3.5, space_after=1.5)
    add_para(doc, entry["objective"], size_pt=8.4, space_after=2.5, line_spacing=1.14)

    # 3. Section 2: Experimental Procedure & Work Performed
    add_para(doc, "2. 실험 설계 및 수행 내용", size_pt=9.2, bold=True, color=NAVY, space_before=3.0, space_after=1.5)
    for idx, w_item in enumerate(entry["work"], start=1):
        add_para(doc, f"• [{idx}] {w_item}", size_pt=8.3, space_after=1.5, line_spacing=1.13)

    # 4. Embedded Authentic Photo / Real Execution Result Capture
    p_pic = doc.add_paragraph()
    p_pic.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_pic.paragraph_format.space_before = Pt(3.0)
    p_pic.paragraph_format.space_after = Pt(1.5)
    p_pic.add_run().add_picture(str(embed_path), width=Mm(img_w_mm), height=Mm(img_h_mm))

    add_para(
        doc,
        caption_txt,
        size_pt=7.8,
        bold=True,
        color=MUTED_GRAY,
        space_before=0.0,
        space_after=3.0,
        line_spacing=1.10,
        align=WD_ALIGN_PARAGRAPH.CENTER,
    )

    # 5. Section 3: Failures, Bugs & Root Cause Analysis
    add_para(doc, "3. 발생 문제 및 시행착오 분석", size_pt=9.2, bold=True, color=FAIL_RED, space_before=2.5, space_after=1.8)
    fail_box = doc.add_table(rows=1, cols=1)
    fail_box.alignment = WD_TABLE_ALIGNMENT.CENTER
    fail_box.rows[0].cells[0].width = Mm(180)
    set_callout_borders(fail_box, left_color="DC2626", bg_color="FEF2F2")
    fail_txt = f"[시행착오 및 원인 진단] {entry['failure']}"
    fill_cell(fail_box.rows[0].cells[0], fail_txt, size_pt=8.2, color=DARK_SLATE, pad_v=42, pad_h=95)

    # 6. Section 4: Design Modifications & Engineering Resolution
    add_para(doc, "4. 설계 변경 및 해결 조치", size_pt=9.2, bold=True, color=FIX_GREEN, space_before=3.5, space_after=1.5)
    for c_item in entry["change"]:
        add_para(doc, f"✔ [해결] {c_item}", size_pt=8.3, space_after=1.5, line_spacing=1.13)

    # 7. Section 5: Quantitative Metrics & Before/After Comparison Table
    add_para(doc, "5. 정량적 검증 결과 (변경 전·후 비교)", size_pt=9.2, bold=True, color=NAVY, space_before=3.0, space_after=2.0)
    m_tbl = doc.add_table(rows=len(entry["metrics"]) + 1, cols=3)
    m_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(m_tbl)
    m_widths = [Mm(42), Mm(67), Mm(71)]
    m_headers = ["검증 항목 / 지표", "개선 전 (실패·한계 상태)", "개선 후 (변경·해결 결과)"]
    for c_i, mh in enumerate(m_headers):
        cell = m_tbl.rows[0].cells[c_i]
        cell.width = m_widths[c_i]
        set_cell_shading(cell, "334155")
        fill_cell(cell, mh, size_pt=8.0, bold=True, color=RGBColor(255, 255, 255), align=WD_ALIGN_PARAGRAPH.CENTER, pad_v=30)

    for r_i, (m_name, m_before, m_after) in enumerate(entry["metrics"], start=1):
        vals = [m_name, m_before, m_after]
        for c_i, val in enumerate(vals):
            cell = m_tbl.rows[r_i].cells[c_i]
            cell.width = m_widths[c_i]
            if c_i == 0:
                set_cell_shading(cell, "F8FAFC")
            elif c_i == 2:
                set_cell_shading(cell, "F0FDF4")
            fill_cell(
                cell,
                val,
                size_pt=7.9,
                bold=(c_i in (0, 2)),
                color=FIX_GREEN if c_i == 2 else (NAVY if c_i == 0 else MUTED_GRAY),
                align=WD_ALIGN_PARAGRAPH.CENTER if c_i == 0 else WD_ALIGN_PARAGRAPH.LEFT,
                pad_v=28,
                pad_h=70,
            )

    # 8. Section 6: Next Action (clean concise line, no formal sign-off table)
    add_para(
        doc,
        f"6. 고찰 및 차기 계획: {entry['next']}",
        size_pt=8.2,
        bold=False,
        color=DARK_SLATE,
        space_before=3.5,
        space_after=0.0,
        line_spacing=1.12,
    )

    total_est_pt = text_pt + (img_h_mm * 2.83465)
    if not is_last:
        doc.add_page_break()
    return total_est_pt, img_h_mm


def main():
    all_days = DAYS_PART1 + DAYS_PART2 + DAYS_PART3 + DAYS_PART4
    assert len(all_days) == 68, f"Expected 68 days, got {len(all_days)}"
    assert len(DAY_IMAGE_MAP) == 68, f"Expected 68 mapped images, got {len(DAY_IMAGE_MAP)}"
    for idx, d in enumerate(all_days, start=1):
        assert d["day"] == idx, f"Day sequence mismatch at {idx}: {d['day']}"
        assert idx in DAY_IMAGE_MAP, f"Missing image mapping for Day {idx}"

    doc = Document()

    # Configure A4 Page Setup (210 x 297 mm, 12mm top/bottom, 15mm left/right => usable 180 x 273 mm = 773.9 pt)
    section = doc.sections[0]
    section.page_width = Mm(210)
    section.page_height = Mm(297)
    section.top_margin = Mm(12)
    section.bottom_margin = Mm(12)
    section.left_margin = Mm(15)
    section.right_margin = Mm(15)
    section.header_distance = Mm(6)
    section.footer_distance = Mm(6)
    section.different_first_page_header_footer = True

    # Subtle Running Header & Page Number Footer (Pages 2+)
    hdr_p = section.header.paragraphs[0]
    hdr_p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    hr = hdr_p.add_run("콜드체인 디지털 트윈 플랫폼 연구노트 (2026.03 ~ 2026.11)")
    set_east_asia_font(hr, size_pt=7.8, color=MUTED_GRAY)

    ftr_p = section.footer.paragraphs[0]
    add_page_number_fields(ftr_p)

    # Build Document
    build_cover_page(doc, len(all_days))          # Page 1
    build_guideline_and_phase_page(doc)           # Page 2
    build_toc_pages(doc, all_days)                # Pages 3 ~ 4

    stats = []
    for i, entry in enumerate(all_days):
        tot_pt, im_h = build_day_page(doc, entry, is_last=(i == len(all_days) - 1))
        stats.append((entry["day"], tot_pt, im_h))

    out_path = ROOT / "docs" / "연구노트_콜드체인_디지털트윈_플랫폼_2026.docx"
    doc.save(str(out_path))

    min_s = min(stats, key=lambda x: x[1])
    max_s = max(stats, key=lambda x: x[1])
    min_im = min(stats, key=lambda x: x[2])
    max_im = max(stats, key=lambda x: x[2])
    overflow = [x for x in stats if x[1] > 745.0]
    print(f"[SUCCESS] Saved: {out_path} ({out_path.stat().st_size:,} bytes / {out_path.stat().st_size / (1024*1024):.2f} MB)")
    print(f"[PAGE AUDIT] Cover(1) + Guide(1) + TOC(2) + Daily({len(all_days)}) = {4 + len(all_days)} A4 Pages!")
    print(f"[HEIGHT AUDIT] Min Day: Day {min_s[0]} ({min_s[1]:.1f} pt) | Max Day: Day {max_s[0]} ({max_s[1]:.1f} pt) / Usable A4: 773.9 pt")
    print(f"[IMAGE HEIGHT] Min: Day {min_im[0]} ({min_im[2]:.1f} mm) | Max: Day {max_im[0]} ({max_im[2]:.1f} mm)")
    print(f"[OVERFLOW CHECK] Pages > 745 pt: {len(overflow)} -> {overflow}")


if __name__ == "__main__":
    main()
