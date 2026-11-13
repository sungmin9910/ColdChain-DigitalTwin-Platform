# -*- coding: utf-8 -*-
"""
공식 연구노트 (Research Lab Notebook) Word(.docx) 생성 스크립트
대상 과제: 수확 후 농산물 신선도 보장을 위한 양방향 콜드체인 디지털 트윈 플랫폼 개발
구성: 표지(1p) + 작성지침 및 단계별 요약(1p) + 전체 일자별 목차(2p) + 일자별 연구노트 본문(68p, 1일 1장) = 총 72장(A4)
"""

import math
from pathlib import Path
import docx
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


FONT_NAME = "맑은 고딕"
NAVY = RGBColor(0x1E, 0x3A, 0x5F)
DARK_SLATE = RGBColor(0x1E, 0x29, 0x3B)
MUTED_GRAY = RGBColor(0x47, 0x55, 0x69)
FAIL_RED = RGBColor(0x99, 0x1B, 0x1B)
FIX_GREEN = RGBColor(0x16, 0x65, 0x34)


def set_east_asia_font(run, font_name=FONT_NAME, size_pt=9.0, bold=False, color=DARK_SLATE):
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


def set_cell_shading(cell, hex_color: str):
    shading = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    cell._tc.get_or_add_tcPr().append(shading)


def set_cell_margins(cell, top=55, bottom=55, left=100, right=100):
    """dxa units (1 pt = 20 dxa)"""
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
            <w:left w:val="single" w:sz="24" w:space="0" w:color="{left_color}"/>
            <w:right w:val="single" w:sz="4" w:space="0" w:color="E2E8F0"/>
        </w:tblBorders>
        """
    )
    tblPr.append(borders)
    set_cell_shading(table.cell(0, 0), bg_color)


def add_page_number_fields(paragraph):
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r1 = paragraph.add_run("- ")
    set_east_asia_font(r1, size_pt=8.5, color=MUTED_GRAY)

    for field_name in ["PAGE", "NUMPAGES"]:
        if field_name == "NUMPAGES":
            sep = paragraph.add_run(" / ")
            set_east_asia_font(sep, size_pt=8.5, color=MUTED_GRAY)
        run_begin = paragraph.add_run()
        set_east_asia_font(run_begin, size_pt=8.5, color=MUTED_GRAY)
        fldChar1 = parse_xml(r'<w:fldChar %s w:fldCharType="begin"/>' % nsdecls("w"))
        instrText = parse_xml(r'<w:instrText %s xml:space="preserve"> %s </w:instrText>' % (nsdecls("w"), field_name))
        fldChar2 = parse_xml(r'<w:fldChar %s w:fldCharType="separate"/>' % nsdecls("w"))
        fldChar3 = parse_xml(r'<w:fldChar %s w:fldCharType="end"/>' % nsdecls("w"))
        run_begin._r.append(fldChar1)
        run_begin._r.append(instrText)
        run_begin._r.append(fldChar2)
        run_begin._r.append(fldChar3)

    r2 = paragraph.add_run(" -")
    set_east_asia_font(r2, size_pt=8.5, color=MUTED_GRAY)


def add_para(doc, text="", size_pt=9.0, bold=False, color=DARK_SLATE, space_before=0.0, space_after=2.0, line_spacing=1.18, align=WD_ALIGN_PARAGRAPH.LEFT):
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


def fill_cell(cell, text, size_pt=8.5, bold=False, color=DARK_SLATE, align=WD_ALIGN_PARAGRAPH.LEFT, pad_v=45, pad_h=90):
    cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
    set_cell_margins(cell, top=pad_v, bottom=pad_v, left=pad_h, right=pad_h)
    p = cell.paragraphs[0]
    p.alignment = align
    pf = p.paragraph_format
    pf.space_before = Pt(0)
    pf.space_after = Pt(0)
    pf.line_spacing = 1.15
    r = p.add_run(text)
    set_east_asia_font(r, size_pt=size_pt, bold=bold, color=color)
    return p


def estimate_lines(text: str, chars_per_line: int = 56) -> int:
    """Korean full-width aware line wrap estimator for A4 width (178mm)."""
    eff_len = 0.0
    for ch in text:
        eff_len += 1.0 if ord(ch) > 127 else 0.56
    return max(1, math.ceil(eff_len / chars_per_line))


def build_cover_page(doc: Document, total_days: int):
    add_para(doc, "", size_pt=10, space_after=18)
    p_badge = add_para(
        doc,
        "국가연구개발사업 표준 서식 준용  |  RESEARCH LAB NOTEBOOK",
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
        space_after=24,
        line_spacing=1.25,
        align=WD_ALIGN_PARAGRAPH.CENTER,
    )

    # Meta Information Table
    tbl = doc.add_table(rows=8, cols=2)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl)
    meta_rows = [
        ("연구노트 관리번호", "JBNU-ASRL-CCDT-2026-001"),
        ("연구 수행 기관 / 연구실", "전북대학교 농업기계공학과  |  Agricultural Sensor and Robotics Lab"),
        ("연구 기록자 (작성자)", "한 성 민  (석사과정 / yuyu6243@gmail.com)"),
        ("연구 기록 기간", f"2026년 03월 22일  ~  2026년 11월 13일  (총 {total_days}일차 일별 기록)"),
        ("핵심 하드웨어 구성", "CarrierBoard Beetle ESP32-C6 (1~4호차), GM77/MQ160W QR 스캐너, Jetson Orin Nano, CadQuery v22 사과 센서팟"),
        ("핵심 소프트웨어 구성", "ESP32 LittleFS 링버퍼 펌웨어, AWS EC2 24/7 수집 데몬, AWS RDS MySQL, Streamlit 듀얼 대시보드"),
        ("형상관리 원격 저장소", "https://github.com/sungmin9910/ColdChain-DigitalTwin-Platform"),
        ("보안 등급 및 보존 기한", "일반 연구자료 (학위논문 및 학술지 게재 근거자료)  /  영구 보존"),
    ]
    col_widths = [Mm(52), Mm(126)]
    for idx, (k, v) in enumerate(meta_rows):
        row = tbl.rows[idx]
        row.cells[0].width = col_widths[0]
        row.cells[1].width = col_widths[1]
        set_cell_shading(row.cells[0], "F1F5F9")
        fill_cell(row.cells[0], k, size_pt=9.5, bold=True, color=NAVY, align=WD_ALIGN_PARAGRAPH.CENTER, pad_v=85)
        fill_cell(row.cells[1], v, size_pt=9.5, bold=(idx in (0, 2)), color=DARK_SLATE, pad_v=85)

    add_para(doc, "", size_pt=10, space_after=22)

    # Signature Verification Box
    sig_tbl = doc.add_table(rows=3, cols=4)
    sig_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(sig_tbl)
    sig_headers = ["구  분", "성  명 / 직  책", "최초 개시 확인", "최종 마감 검인"]
    sig_widths = [Mm(35), Mm(53), Mm(45), Mm(45)]
    for c_idx, h_text in enumerate(sig_headers):
        cell = sig_tbl.rows[0].cells[c_idx]
        cell.width = sig_widths[c_idx]
        set_cell_shading(cell, "1E3A5F")
        fill_cell(cell, h_text, size_pt=9.0, bold=True, color=RGBColor(255, 255, 255), align=WD_ALIGN_PARAGRAPH.CENTER, pad_v=70)

    sig_data = [
        ("기 록 자", "한 성 민 (석사과정)", "2026. 03. 22.  (인)", "2026. 11. 13.  (인)"),
        ("점 검 자", "지도교수 / 연구책임자", "2026. 03. 22.  (인)", "2026. 11. 13.  (인)"),
    ]
    for r_idx, row_vals in enumerate(sig_data, start=1):
        for c_idx, val in enumerate(row_vals):
            cell = sig_tbl.rows[r_idx].cells[c_idx]
            cell.width = sig_widths[c_idx]
            if c_idx == 0:
                set_cell_shading(cell, "F8FAFC")
            fill_cell(cell, val, size_pt=9.0, bold=(c_idx == 0), align=WD_ALIGN_PARAGRAPH.CENTER, pad_v=95)

    add_para(
        doc,
        "※ 본 연구노트는 실제 Git 커밋 이력(200+ commits), 하드웨어 실측 로그, 3D 프린팅 시행착오(v06~v22) 및 실차 주행 실험 원본에 의거하여 작성됨.",
        size_pt=8.5,
        color=MUTED_GRAY,
        space_before=16,
        align=WD_ALIGN_PARAGRAPH.CENTER,
    )
    doc.add_page_break()


def build_guideline_and_phase_page(doc: Document):
    add_para(doc, "Ⅰ. 연구노트 작성 원칙 및 단계별 연구개발 총괄표", size_pt=13.5, bold=True, color=NAVY, space_after=6)
    add_para(
        doc,
        "본 연구노트는 국가연구개발사업 연구노트 지침에 따라 성공한 최종 결과뿐만 아니라, 연구 과정에서 겪은 하드웨어 역삽입·패드 박리·부트로더 벽돌·통신 두절·기구 간섭 등 모든 실패(Trial & Error)와 그 원인 규명, 설계 변경 내역을 가감 없이 기록하였다.",
        size_pt=9.0,
        space_after=8,
    )

    rules = [
        "1. 객관성 및 추적성 원칙: 모든 일자별 기록은 Git 커밋 해시(Hash), 실제 소스코드 파일명, 시리얼 계측 수치 및 DB 세션 ID와 1:1 대응된다.",
        "2. 실패 및 변경 이력 보존: 작동하지 않았던 초기 시도(DHT11, Bowl-Up 평바닥, 기둥 날개 간섭, get_columns 누락 등)를 삭제하지 않고 실패 원인과 해결 전·후 수치 변화를 명시한다.",
        "3. 1일 1면 완결 원칙: 각 연구일지(Day 01 ~ Day 68)는 독립된 A4 1페이지 단위로 완결 작성되며 상단에 기록자·점검자 서명란을 구비한다.",
    ]
    for r_txt in rules:
        add_para(doc, r_txt, size_pt=8.8, space_after=3.5)

    add_para(doc, "■ 전 주기 연구개발 단계(Phase 1 ~ Phase 15) 요약", size_pt=10.5, bold=True, color=NAVY, space_before=8, space_after=4)

    phases = [
        ("Phase 1", "03.22 ~ 04.27", "Day 01~07", "연구 기획, Jetson Orin Nano JP6.2 3D/TensorRT 구축(OOM 해결), DHT11 한계 검증 및 KSHS 포스터"),
        ("Phase 2", "05.03 ~ 05.20", "Day 08~15", "AWS RDS MySQL 구축, Flask➔Streamlit 전면 개편, KST 타임존/다크모드/CARTO 빈 지도 버그 해결"),
        ("Phase 3", "05.27 ~ 06.28", "Day 16~22", "GM77+ESP32 스마트 스캐너 UART Wake-up 해결, OpenSCAD 좌/우 반할 하우징(v06➔v17) 완성"),
        ("Phase 4", "07.07 ~ 08.24", "Day 23~27", "GY-521 고속 Peak-Hold 충격 계측, MQ160W 무선 스캐너 Method 2 자동 단계 판별, Beetle C6 선정"),
        ("Phase 5", "08.30 ~ 09.29", "Day 28~31", "50×50mm 양면 CarrierBoard PCB 설계·발주(Gerber/STEP) 및 석사논문·SCIE 5대 수학 모델 정립"),
        ("Phase 6", "09.30 ~ 10.03", "Day 32~36", "실물 PCB 조립, 센서 180° 역삽입 I2C 복구, 전주↔대전 174km 주행 복원, SW1 패드박리 복구, 링버퍼"),
        ("Phase 7", "10.06 ~ 10.09", "Day 37~39", "냉장 급랭 열시상수(τ=16.4분) 규명, Jetson 2분할 Split HUD 키오스크, Wi-Fi 블로킹 5대 최적화"),
        ("Phase 8~9", "10.10 ~ 10.12", "Day 40~46", "5000mAh 100mm 사과팟(v19~v21), GM77 부트루프 및 get_columns() 버그 해결, A00~A15 실증 완료"),
        ("Phase 10~11", "10.13 ~ 10.17", "Day 47~52", "1.5cm 단차 기둥(GPS 간섭 해결), v22 자석+GPS 홀더, 1~4호차 플릿 구축 및 02호차 주야간 실차 주행"),
        ("Phase 12~13", "10.17 ~ 10.29", "Day 53~60", "AWS EC2 24/7 무인 데몬 배포, 유령 충격 스택 버그 박멸, 04호차 RF 자가복구, 배터리 코너 베이 가공"),
        ("Phase 14~15", "11.02 ~ 11.13", "Day 61~68", "CadQuery 2.7 B-Rep 표준 전환, 원피스 서포트 분리, 4점 베요넷 잠금 & 굴뚝 통풍, 국내 유통 적용성 감사"),
    ]

    tbl = doc.add_table(rows=len(phases) + 1, cols=4)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl)
    widths = [Mm(24), Mm(28), Mm(22), Mm(104)]
    headers = ["단계", "수행 기간", "연구일차", "핵심 연구 내용 및 주요 시행착오 해결 성과"]
    for c_i, h in enumerate(headers):
        c = tbl.rows[0].cells[c_i]
        c.width = widths[c_i]
        set_cell_shading(c, "1E3A5F")
        fill_cell(c, h, size_pt=8.5, bold=True, color=RGBColor(255, 255, 255), align=WD_ALIGN_PARAGRAPH.CENTER, pad_v=55)

    for r_i, row_data in enumerate(phases, start=1):
        for c_i, val in enumerate(row_data):
            c = tbl.rows[r_i].cells[c_i]
            c.width = widths[c_i]
            if r_i % 2 == 0:
                set_cell_shading(c, "F8FAFC")
            fill_cell(
                c,
                val,
                size_pt=8.2,
                bold=(c_i == 0),
                color=NAVY if c_i == 0 else DARK_SLATE,
                align=WD_ALIGN_PARAGRAPH.CENTER if c_i < 3 else WD_ALIGN_PARAGRAPH.LEFT,
                pad_v=52,
            )

    add_para(
        doc,
        "■ 핵심 정량적 달성 지표: ① 왕복 174.6km 고속도로 및 다중 도심 주행 데이터 유실률 0.0%  ② 패키징 열응답 시상수 τ = 16.4분 규명  ③ 실물 스캐너 A00~A15 자동 전이 응답 1.84초  ④ 1~4호차 멀티 플릿 + AWS EC2 24/7 무인 자동 적재 완성.",
        size_pt=8.6,
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
            size_pt=12.5,
            bold=True,
            color=NAVY,
            space_after=5,
        )
        tbl = doc.add_table(rows=len(chunk) + 1, cols=4)
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        set_table_borders(tbl)
        widths = [Mm(16), Mm(24), Mm(110), Mm(28)]
        headers = ["일차", "작성일자", "연구노트 주제 (실패 분석 및 핵심 변경 사항 포함)", "기준 커밋/문서"]
        for c_i, h in enumerate(headers):
            c = tbl.rows[0].cells[c_i]
            c.width = widths[c_i]
            set_cell_shading(c, "1E3A5F")
            fill_cell(c, h, size_pt=8.0, bold=True, color=RGBColor(255, 255, 255), align=WD_ALIGN_PARAGRAPH.CENTER, pad_v=36)

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
                    size_pt=7.7,
                    bold=(c_i == 0),
                    color=NAVY if c_i == 0 else DARK_SLATE,
                    align=WD_ALIGN_PARAGRAPH.CENTER if c_i in (0, 1, 3) else WD_ALIGN_PARAGRAPH.LEFT,
                    pad_v=24,
                    pad_h=60,
                )
        doc.add_page_break()


def build_day_page(doc: Document, entry: dict, is_last: bool = False) -> float:
    """Renders exactly 1 full A4 page for a single day's research note and returns estimated pt height."""
    day_num = entry["day"]
    est_pt = 0.0

    # 1. Top Official Research Note Header Table (4 rows)
    hdr_tbl = doc.add_table(rows=4, cols=4)
    hdr_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(hdr_tbl)
    w_cols = [Mm(28), Mm(61), Mm(28), Mm(61)]

    r0 = hdr_tbl.rows[0]
    for i, w in enumerate(w_cols):
        r0.cells[i].width = w
    set_cell_shading(r0.cells[0], "1E3A5F")
    set_cell_shading(r0.cells[2], "1E3A5F")
    fill_cell(r0.cells[0], "문서번호", size_pt=8.5, bold=True, color=RGBColor(255, 255, 255), align=WD_ALIGN_PARAGRAPH.CENTER, pad_v=38)
    fill_cell(r0.cells[1], f"RN-2026-{day_num:03d}  ({entry['phase']})", size_pt=8.3, bold=True, color=NAVY, pad_v=38)
    fill_cell(r0.cells[2], "작성일자", size_pt=8.5, bold=True, color=RGBColor(255, 255, 255), align=WD_ALIGN_PARAGRAPH.CENTER, pad_v=38)
    fill_cell(r0.cells[3], f"{entry['date']}  (Day {day_num:02d} / 68)", size_pt=8.5, bold=True, color=DARK_SLATE, align=WD_ALIGN_PARAGRAPH.CENTER, pad_v=38)

    r1 = hdr_tbl.rows[1]
    for i, w in enumerate(w_cols):
        r1.cells[i].width = w
    set_cell_shading(r1.cells[0], "F1F5F9")
    set_cell_shading(r1.cells[2], "F1F5F9")
    fill_cell(r1.cells[0], "기 록 자", size_pt=8.3, bold=True, color=NAVY, align=WD_ALIGN_PARAGRAPH.CENTER, pad_v=35)
    fill_cell(r1.cells[1], "한 성 민  (서명: 한성민)", size_pt=8.3, color=DARK_SLATE, pad_v=35)
    fill_cell(r1.cells[2], "점 검 자", size_pt=8.3, bold=True, color=NAVY, align=WD_ALIGN_PARAGRAPH.CENTER, pad_v=35)
    fill_cell(r1.cells[3], "지도교수 / 연구책임자  (인)", size_pt=8.3, color=MUTED_GRAY, align=WD_ALIGN_PARAGRAPH.CENTER, pad_v=35)

    r2 = hdr_tbl.rows[2]
    r2.cells[0].width = Mm(28)
    merged_title = r2.cells[1].merge(r2.cells[3])
    merged_title.width = Mm(150)
    set_cell_shading(r2.cells[0], "F1F5F9")
    set_cell_shading(merged_title, "F8FAFC")
    fill_cell(r2.cells[0], "연구제목", size_pt=8.3, bold=True, color=NAVY, align=WD_ALIGN_PARAGRAPH.CENTER, pad_v=38)
    fill_cell(merged_title, entry["title"], size_pt=9.0, bold=True, color=DARK_SLATE, pad_v=38)

    r3 = hdr_tbl.rows[3]
    r3.cells[0].width = Mm(28)
    merged_files = r3.cells[1].merge(r3.cells[3])
    merged_files.width = Mm(150)
    set_cell_shading(r3.cells[0], "F1F5F9")
    fill_cell(r3.cells[0], "관련파일/커밋", size_pt=8.0, bold=True, color=NAVY, align=WD_ALIGN_PARAGRAPH.CENTER, pad_v=35)
    fill_cell(merged_files, f"{entry['files']}  |  Commit: {entry['commit']}", size_pt=8.0, color=MUTED_GRAY, pad_v=35)
    est_pt += 86.0

    # 2. Section 1: Objective
    add_para(doc, "1. 연구 목적 및 배경 (Objective)", size_pt=10.0, bold=True, color=NAVY, space_before=7.5, space_after=2.5)
    add_para(doc, entry["objective"], size_pt=9.2, space_after=4.0, line_spacing=1.24)
    est_pt += 20.0 + estimate_lines(entry["objective"], 52) * 12.2

    # 3. Section 2: Experimental Setup & Work Performed
    add_para(doc, "2. 실험 설계 및 수행 내용 (Experimental Procedure & Implementation)", size_pt=10.0, bold=True, color=NAVY, space_before=6.0, space_after=2.5)
    est_pt += 19.0
    for idx, w_item in enumerate(entry["work"], start=1):
        txt = f"• [{idx}] {w_item}"
        add_para(doc, txt, size_pt=9.1, space_after=2.8, line_spacing=1.22)
        est_pt += estimate_lines(txt, 52) * 12.0 + 2.8

    # 4. Section 3: Failures, Bugs & Root Cause Analysis (Highlighted Callout Box)
    add_para(doc, "3. 발생 문제 및 시행착오 기록 (Failures, Bugs & Root Cause Analysis)", size_pt=10.0, bold=True, color=FAIL_RED, space_before=6.5, space_after=3.0)
    fail_box = doc.add_table(rows=1, cols=1)
    fail_box.alignment = WD_TABLE_ALIGNMENT.CENTER
    fail_box.rows[0].cells[0].width = Mm(178)
    set_callout_borders(fail_box, left_color="DC2626", bg_color="FEF2F2")
    fail_txt = f"[시행착오 및 원인 진단] {entry['failure']}"
    fill_cell(fail_box.rows[0].cells[0], fail_txt, size_pt=9.0, color=DARK_SLATE, pad_v=75, pad_h=120)
    est_pt += 21.0 + estimate_lines(fail_txt, 49) * 12.0 + 15.0

    # 5. Section 4: Design Modifications & Engineering Resolution
    add_para(doc, "4. 설계 변경 및 해결 조치 (Design Changes & Resolution)", size_pt=10.0, bold=True, color=FIX_GREEN, space_before=6.5, space_after=2.5)
    est_pt += 19.0
    for c_item in entry["change"]:
        txt = f"✔ [변경/해결] {c_item}"
        add_para(doc, txt, size_pt=9.1, space_after=2.8, line_spacing=1.22)
        est_pt += estimate_lines(txt, 52) * 12.0 + 2.8

    # 6. Section 5: Quantitative Metrics & Before/After Comparison Table
    add_para(doc, "5. 정량적 검증 결과 및 변경 전·후 비교 (Verification Metrics)", size_pt=10.0, bold=True, color=NAVY, space_before=6.5, space_after=3.0)
    m_tbl = doc.add_table(rows=len(entry["metrics"]) + 1, cols=3)
    m_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(m_tbl)
    m_widths = [Mm(42), Mm(66), Mm(70)]
    m_headers = ["검증 항목 / 지표", "개선 전 (실패·한계 상태)", "개선 후 (변경·해결 결과)"]
    for c_i, mh in enumerate(m_headers):
        cell = m_tbl.rows[0].cells[c_i]
        cell.width = m_widths[c_i]
        set_cell_shading(cell, "334155")
        fill_cell(cell, mh, size_pt=8.6, bold=True, color=RGBColor(255, 255, 255), align=WD_ALIGN_PARAGRAPH.CENTER, pad_v=48)

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
                size_pt=8.5,
                bold=(c_i in (0, 2)),
                color=FIX_GREEN if c_i == 2 else (NAVY if c_i == 0 else MUTED_GRAY),
                align=WD_ALIGN_PARAGRAPH.CENTER if c_i == 0 else WD_ALIGN_PARAGRAPH.LEFT,
                pad_v=48,
                pad_h=85,
            )
    est_pt += 24.0 + (len(entry["metrics"]) + 1) * 23.0

    # 7. Section 6: Discussion & Next Action + Bottom Official Sign-off Bar
    add_para(doc, "6. 고찰 및 차기 연구 계획 (Next Plan)", size_pt=9.8, bold=True, color=NAVY, space_before=6.5, space_after=3.5)
    next_txt = f"➔ 차기 과제: {entry['next']}"
    add_para(doc, next_txt, size_pt=9.0, bold=False, color=DARK_SLATE, space_after=6.0, line_spacing=1.20)
    est_pt += 22.0 + estimate_lines(next_txt, 52) * 11.8

    sign_tbl = doc.add_table(rows=1, cols=4)
    sign_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(sign_tbl)
    s_widths = [Mm(32), Mm(57), Mm(32), Mm(57)]
    s_vals = [
        ("증빙 구분", "Git 형상관리 / 실측 데이터 검증 완료"),
        ("기록자 확인", f"한성민  ({entry['date']})"),
    ]
    sign_tbl.rows[0].cells[0].width = s_widths[0]
    sign_tbl.rows[0].cells[1].width = s_widths[1]
    sign_tbl.rows[0].cells[2].width = s_widths[2]
    sign_tbl.rows[0].cells[3].width = s_widths[3]
    set_cell_shading(sign_tbl.rows[0].cells[0], "F1F5F9")
    set_cell_shading(sign_tbl.rows[0].cells[2], "F1F5F9")
    fill_cell(sign_tbl.rows[0].cells[0], s_vals[0][0], size_pt=8.2, bold=True, color=NAVY, align=WD_ALIGN_PARAGRAPH.CENTER, pad_v=38)
    fill_cell(sign_tbl.rows[0].cells[1], s_vals[0][1], size_pt=8.2, color=DARK_SLATE, align=WD_ALIGN_PARAGRAPH.CENTER, pad_v=38)
    fill_cell(sign_tbl.rows[0].cells[2], s_vals[1][0], size_pt=8.2, bold=True, color=NAVY, align=WD_ALIGN_PARAGRAPH.CENTER, pad_v=38)
    fill_cell(sign_tbl.rows[0].cells[3], s_vals[1][1], size_pt=8.2, color=DARK_SLATE, align=WD_ALIGN_PARAGRAPH.CENTER, pad_v=38)
    est_pt += 26.0

    if not is_last:
        doc.add_page_break()
    return est_pt


def main():
    all_days = DAYS_PART1 + DAYS_PART2 + DAYS_PART3 + DAYS_PART4
    assert len(all_days) == 68, f"Expected 68 days, got {len(all_days)}"
    for idx, d in enumerate(all_days, start=1):
        assert d["day"] == idx, f"Day sequence mismatch at {idx}: {d['day']}"

    doc = Document()

    # Configure A4 Page Setup (210 x 297 mm)
    section = doc.sections[0]
    section.page_width = Mm(210)
    section.page_height = Mm(297)
    section.top_margin = Mm(14)
    section.bottom_margin = Mm(14)
    section.left_margin = Mm(16)
    section.right_margin = Mm(16)
    section.header_distance = Mm(7)
    section.footer_distance = Mm(7)
    section.different_first_page_header_footer = True

    # Running Header & Footer (Pages 2+)
    hdr_p = section.header.paragraphs[0]
    hdr_p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    hr = hdr_p.add_run("전북대학교 농업기계공학과 (ASRL)  |  콜드체인 디지털 트윈 플랫폼 연구노트 (2026)")
    set_east_asia_font(hr, size_pt=8.0, color=MUTED_GRAY)

    ftr_p = section.footer.paragraphs[0]
    add_page_number_fields(ftr_p)

    # Build Sections
    build_cover_page(doc, len(all_days))          # Page 1
    build_guideline_and_phase_page(doc)           # Page 2
    build_toc_pages(doc, all_days)                # Pages 3 ~ 4

    heights = []
    for i, entry in enumerate(all_days):
        h = build_day_page(doc, entry, is_last=(i == len(all_days) - 1))
        heights.append((entry["day"], h))

    out_path = Path(r"c:\Users\korea\Desktop\1hsm\hanhanhan\ColdChain-DigitalTwin-Platform\docs\연구노트_콜드체인_디지털트윈_플랫폼_2026.docx")
    doc.save(str(out_path))

    min_h = min(heights, key=lambda x: x[1])
    max_h = max(heights, key=lambda x: x[1])
    overflow = [x for x in heights if x[1] > 735.0]
    print(f"[SUCCESS] Saved: {out_path} ({out_path.stat().st_size:,} bytes)")
    print(f"[PAGE AUDIT] Cover(1) + Guide(1) + TOC(2) + Daily({len(all_days)}) = {4 + len(all_days)} A4 Pages!")
    print(f"[HEIGHT AUDIT] Min Day Height: Day {min_h[0]} ({min_h[1]:.1f} pt) | Max Day Height: Day {max_h[0]} ({max_h[1]:.1f} pt) / Usable A4: 762.5 pt")
    print(f"[OVERFLOW CHECK] Pages > 735 pt: {len(overflow)} -> {overflow}")


if __name__ == "__main__":
    main()
