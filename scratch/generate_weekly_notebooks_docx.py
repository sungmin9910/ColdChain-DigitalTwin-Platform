# -*- coding: utf-8 -*-
"""
주간미팅(2425/ eric·hsm) 반영 신규 연도별 연구노트 Word(.docx) 생성 및 자동 검증 스크립트
- 기존 .docx 파일들은 일절 건드리지 않고 새로운 파일명으로 생성:
  1) docs/연구노트_2025년_주간미팅반영_신규본.docx : 목차(1p) + 일자별 기록(38p) = 총 39장
  2) docs/연구노트_2026년_주간미팅반영_신규본.docx : 목차(1p) + 일자별 기록(37p) = 총 38장
- 각 일자 상단: 오직 날짜(YYYY-MM-DD)만 표기 (Day 번호·제목·부제목·메타데이터 표 없음)
- 본문 구조: [날짜 + 실험 내용(실물 사진·실행 캡처 1~2장) + 실험 결과] (AI 생성 이미지 0건)
"""

import datetime as dt
import math
import shutil
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from PIL import Image, ImageOps
from docx import Document
from docx.shared import Mm, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import qn, nsdecls

from nb2025_weekly_data import DAYS_2025_WEEKLY
from nb2026_weekly_data import DAYS_2026_WEEKLY


ROOT = Path(r"c:\Users\korea\Desktop\1hsm\hanhanhan\ColdChain-DigitalTwin-Platform")
CACHE_DIR = ROOT / "scratch" / "notebook_captures" / "embed_cache_weekly"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

FONT_NAME = "맑은 고딕"
NAVY = RGBColor(0x1E, 0x3A, 0x5F)
DARK_SLATE = RGBColor(0x1E, 0x29, 0x3B)
MUTED_GRAY = RGBColor(0x47, 0x55, 0x69)

KR_HOLIDAYS = {
    # 2025
    "2025-01-01", "2025-01-27", "2025-01-28", "2025-01-29", "2025-01-30",
    "2025-03-01", "2025-03-03", "2025-05-05", "2025-05-06", "2025-06-03",
    "2025-06-06", "2025-08-15", "2025-10-03", "2025-10-06", "2025-10-07",
    "2025-10-08", "2025-10-09", "2025-12-25",
    # 2026
    "2026-01-01", "2026-02-16", "2026-02-17", "2026-02-18", "2026-03-01",
    "2026-03-02", "2026-05-05", "2026-05-24", "2026-05-25", "2026-06-03",
    "2026-06-06", "2026-08-15", "2026-08-17", "2026-09-24", "2026-09-25",
    "2026-09-26", "2026-10-03", "2026-10-05", "2026-10-09", "2026-12-25",
}

FORBIDDEN_TERMS = [
    "Day ", "실험 목적", "발생 오류 및 시행착오 분석", "정량적 실행",
    "대상 코드/산출물", "RandomForest", "sensor_classification",
    "desktop_stand", "cable_clip", "신도리코", "3DWOX", "문서번호", "점검자",
]

FORBIDDEN_IMAGE_PATTERNS = [
    "m26_20260428_s10_1",
    "m26_20260504_s07_1",
    "m26_20260518_s04_",
    "m25_20250103_s08_2",
]


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
        f'<w:pBdr {nsdecls("w")}><w:bottom w:val="single" w:sz="{sz}" w:space="4" w:color="{color_hex}"/></w:pBdr>'
    )
    pPr.append(pBdr)


def set_cell_shading(cell, hex_color: str):
    shading = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    cell._tc.get_or_add_tcPr().append(shading)


def set_cell_margins(cell, top=40, bottom=40, left=80, right=80):
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


def set_borderless_table(table):
    tblPr = table._tbl.tblPr
    borders = parse_xml(
        f"""
        <w:tblBorders {nsdecls("w")}>
            <w:top w:val="none" w:sz="0" w:space="0" w:color="auto"/>
            <w:bottom w:val="none" w:sz="0" w:space="0" w:color="auto"/>
            <w:left w:val="none" w:sz="0" w:space="0" w:color="auto"/>
            <w:right w:val="none" w:sz="0" w:space="0" w:color="auto"/>
            <w:insideH w:val="none" w:sz="0" w:space="0" w:color="auto"/>
            <w:insideV w:val="none" w:sz="0" w:space="0" w:color="auto"/>
        </w:tblBorders>
        """
    )
    tblPr.append(borders)


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


def add_para(
    doc,
    text="",
    size_pt=8.8,
    bold=False,
    color=DARK_SLATE,
    space_before=0.0,
    space_after=2.5,
    line_spacing=1.20,
    align=WD_ALIGN_PARAGRAPH.LEFT,
):
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


def fill_cell(
    cell,
    text,
    size_pt=8.0,
    bold=False,
    color=DARK_SLATE,
    align=WD_ALIGN_PARAGRAPH.LEFT,
    pad_v=24,
    pad_h=60,
    line_spacing=1.08,
):
    cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
    set_cell_margins(cell, top=pad_v, bottom=pad_v, left=pad_h, right=pad_h)
    p = cell.paragraphs[0]
    p.alignment = align
    pf = p.paragraph_format
    pf.space_before = Pt(0)
    pf.space_after = Pt(0)
    pf.line_spacing = line_spacing
    r = p.add_run(text)
    set_east_asia_font(r, size_pt=size_pt, bold=bold, color=color)
    return p


def estimate_lines(text: str, chars_per_line: int = 56) -> int:
    eff_len = 0.0
    for ch in text:
        eff_len += 1.0 if ord(ch) > 127 else 0.56
    return max(1, math.ceil(eff_len / chars_per_line))


def prevalidate_dataset(year: int, expected_days: int, days: list[dict]) -> None:
    assert len(days) == expected_days, f"Expected {expected_days} days for {year}, got {len(days)}"
    prev_d = None
    for idx, d in enumerate(days, start=1):
        d_str = d["date"]
        parsed = dt.date.fromisoformat(d_str)
        assert parsed.year == year, f"Wrong year at {d_str}"
        assert parsed.weekday() < 5, f"Weekend date at {d_str} (weekday={parsed.weekday()})"
        assert d_str not in KR_HOLIDAYS, f"Korean public holiday used: {d_str}"
        if prev_d is not None:
            assert parsed > prev_d, f"Non-increasing date order: {prev_d} -> {parsed}"
        prev_d = parsed

        # Ensure every TOC line fits on 1 single line inside 153mm cell at 7.1pt
        assert estimate_lines(d["toc"], 58) == 1, f"TOC line wraps to 2 lines at {d_str}: {d['toc']}"

        all_texts = [d["date"], d["toc"]] + d["content"] + d["result"] + [im[1] for im in d["images"]]
        joined = "\n".join(all_texts)
        for bad in FORBIDDEN_TERMS:
            assert bad not in joined, f"Forbidden term '{bad}' found in {year} {d_str}"

        assert 1 <= len(d["images"]) <= 2, f"Invalid image count at {d_str}"
        for rel_p, _cap in d["images"]:
            for bad_img in FORBIDDEN_IMAGE_PATTERNS:
                assert bad_img not in rel_p, f"Forbidden/AI image referenced at {d_str}: {rel_p}"
            full_p = ROOT / rel_p
            assert full_p.exists(), f"Missing image file at {d_str}: {full_p}"


def prepare_embed_image(year: int, page_idx: int, img_idx: int, rel_path: str) -> tuple[Path, int, int]:
    """EXIF 방향 정규화 및 인쇄 선명도 유지 해상도(최대 1600px) 변환"""
    src = ROOT / rel_path
    with Image.open(src) as im:
        im = ImageOps.exif_transpose(im)
        w, h = im.size
        max_dim = 1600
        if max(w, h) > max_dim:
            scale = max_dim / float(max(w, h))
            w = max(1, int(round(w * scale)))
            h = max(1, int(round(h * scale)))
            im = im.resize((w, h), Image.Resampling.LANCZOS)

        if src.suffix.lower() in {".jpg", ".jpeg"} or (w * h > 950_000 and im.mode == "RGB"):
            rgb = im.convert("RGB")
            dst = CACHE_DIR / f"y{year}_p{page_idx:02d}_{img_idx}.jpg"
            rgb.save(dst, format="JPEG", quality=92, optimize=True)
        else:
            dst = CACHE_DIR / f"y{year}_p{page_idx:02d}_{img_idx}.png"
            im.save(dst, format="PNG", optimize=True)
        return dst, w, h


def build_single_page_toc(doc: Document, year: int, period_str: str, days: list[dict]) -> float:
    """표지 없이 첫 페이지(1p)에 37~38행 전체가 단 1장으로 넉넉히 들어오는 2열 목차 배치"""
    add_para(
        doc,
        f"{year}년도 연구노트 목차  ({period_str})",
        size_pt=11.4,
        bold=True,
        color=NAVY,
        space_before=0.0,
        space_after=4.0,
        line_spacing=1.06,
    )

    tbl = doc.add_table(rows=len(days) + 1, cols=2)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl)
    widths = [Mm(27), Mm(153)]
    headers = ["날짜", "실험 내용 요약"]
    for c_i, h in enumerate(headers):
        c = tbl.rows[0].cells[c_i]
        c.width = widths[c_i]
        set_cell_shading(c, "1E3A5F")
        fill_cell(
            c,
            h,
            size_pt=7.8,
            bold=True,
            color=RGBColor(255, 255, 255),
            align=WD_ALIGN_PARAGRAPH.CENTER,
            pad_v=20,
            pad_h=50,
            line_spacing=1.02,
        )

    est_pt = 20.0 + 14.5
    for r_i, item in enumerate(days, start=1):
        vals = [item["date"], item["toc"]]
        row_lines = estimate_lines(item["toc"], 62)
        est_pt += row_lines * 8.4 + 2.4
        for c_i, val in enumerate(vals):
            c = tbl.rows[r_i].cells[c_i]
            c.width = widths[c_i]
            if r_i % 2 == 0:
                set_cell_shading(c, "F8FAFC")
            fill_cell(
                c,
                val,
                size_pt=7.1,
                bold=(c_i == 0),
                color=NAVY if c_i == 0 else DARK_SLATE,
                align=WD_ALIGN_PARAGRAPH.CENTER if c_i == 0 else WD_ALIGN_PARAGRAPH.LEFT,
                pad_v=11,
                pad_h=50,
                line_spacing=1.02,
            )

    doc.add_page_break()
    return est_pt


def estimate_day_text_pt(entry: dict) -> float:
    pt = 0.0
    pt += 28.0
    pt += 23.0
    for c_line in entry["content"]:
        pt += estimate_lines(f"• {c_line}", 50) * 12.3 + 3.8
    if len(entry["images"]) == 1:
        pt += estimate_lines(entry["images"][0][1], 56) * 10.4 + 14.0
    else:
        pt += (
            estimate_lines(entry["images"][0][1], 52) * 10.2
            + estimate_lines(entry["images"][1][1], 52) * 10.2
            + 20.0
        )
    pt += 24.0
    for r_line in entry["result"]:
        pt += estimate_lines(f"• {r_line}", 50) * 12.3 + 3.8
    return pt


def build_day_page(doc: Document, year: int, page_idx: int, entry: dict, is_last: bool = False) -> tuple[float, float]:
    # 1. 상단 날짜 단독 표기
    p_date = add_para(
        doc,
        entry["date"],
        size_pt=13.5,
        bold=True,
        color=NAVY,
        space_before=0.0,
        space_after=6.5,
        line_spacing=1.14,
    )
    set_paragraph_bottom_border(p_date, color_hex="1E3A5F", sz="10")

    # 2. 실험 내용
    add_para(doc, "실험 내용", size_pt=10.5, bold=True, color=NAVY, space_before=5.0, space_after=3.2)
    for item_txt in entry["content"]:
        add_para(doc, f"• {item_txt}", size_pt=9.3, space_after=3.5, line_spacing=1.26)

    # 3. 동적 이미지 배치 (단일 대형 / 와이드 상하 적층 / 일반 좌우 2열)
    text_pt = estimate_day_text_pt(entry)
    avail_img_pt = max(168.0, min(295.0, 696.0 - text_pt))
    target_h_mm = avail_img_pt / 2.83465

    imgs = entry["images"]
    if len(imgs) == 1:
        embed_p, px_w, px_h = prepare_embed_image(year, page_idx, 1, imgs[0][0])
        aspect = px_w / float(px_h)
        img_h_mm = target_h_mm
        img_w_mm = img_h_mm * aspect
        if img_w_mm > 172.0:
            img_w_mm = 172.0
            img_h_mm = img_w_mm / aspect

        p_pic = doc.add_paragraph()
        p_pic.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_pic.paragraph_format.space_before = Pt(6.0)
        p_pic.paragraph_format.space_after = Pt(2.5)
        p_pic.add_run().add_picture(str(embed_p), width=Mm(img_w_mm), height=Mm(img_h_mm))

        add_para(
            doc,
            imgs[0][1],
            size_pt=8.1,
            bold=False,
            color=MUTED_GRAY,
            space_before=0.0,
            space_after=5.5,
            line_spacing=1.14,
            align=WD_ALIGN_PARAGRAPH.CENTER,
        )
        used_img_h_mm = img_h_mm
    else:
        p1, w1, h1 = prepare_embed_image(year, page_idx, 1, imgs[0][0])
        p2, w2, h2 = prepare_embed_image(year, page_idx, 2, imgs[1][0])
        asp1 = w1 / float(h1)
        asp2 = w2 / float(h2)

        if (asp1 >= 1.56 and asp2 >= 1.56) or max(asp1, asp2) >= 2.15:
            # 가로로 긴 캡처/DB/지도는 상·하 2단 적층하여 글씨가 크고 선명하게 보이도록 처리
            stack_budget_mm = max(74.0, target_h_mm - 5.0)
            nat_w1 = min(162.0, 72.0 * asp1)
            nat_h1 = nat_w1 / asp1
            nat_w2 = min(162.0, 72.0 * asp2)
            nat_h2 = nat_w2 / asp2
            scale = min(1.0, stack_budget_mm / (nat_h1 + nat_h2))
            ih1_mm = nat_h1 * scale
            iw1_mm = ih1_mm * asp1
            ih2_mm = nat_h2 * scale
            iw2_mm = ih2_mm * asp2

            for idx_s, (p_img, iw, ih, cap_str) in enumerate(
                [(p1, iw1_mm, ih1_mm, imgs[0][1]), (p2, iw2_mm, ih2_mm, imgs[1][1])]
            ):
                p_pic = doc.add_paragraph()
                p_pic.alignment = WD_ALIGN_PARAGRAPH.CENTER
                p_pic.paragraph_format.space_before = Pt(4.8 if idx_s == 0 else 3.2)
                p_pic.paragraph_format.space_after = Pt(1.8)
                p_pic.add_run().add_picture(str(p_img), width=Mm(iw), height=Mm(ih))
                add_para(
                    doc,
                    cap_str,
                    size_pt=8.0,
                    bold=False,
                    color=MUTED_GRAY,
                    space_before=0.0,
                    space_after=3.2 if idx_s == 0 else 5.2,
                    line_spacing=1.12,
                    align=WD_ALIGN_PARAGRAPH.CENTER,
                )
            used_img_h_mm = ih1_mm + ih2_mm
        else:
            max_cell_w_mm = 86.5
            common_h_mm = min(target_h_mm, max_cell_w_mm / asp1, max_cell_w_mm / asp2)
            iw1_mm = common_h_mm * asp1
            iw2_mm = common_h_mm * asp2

            img_tbl = doc.add_table(rows=2, cols=2)
            img_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
            set_borderless_table(img_tbl)

            for col_i, (p_img, iw, cap_str) in enumerate([(p1, iw1_mm, imgs[0][1]), (p2, iw2_mm, imgs[1][1])]):
                c_img = img_tbl.rows[0].cells[col_i]
                c_img.width = Mm(90)
                c_img.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
                set_cell_margins(c_img, top=55, bottom=20, left=28, right=28)
                p_c = c_img.paragraphs[0]
                p_c.alignment = WD_ALIGN_PARAGRAPH.CENTER
                p_c.paragraph_format.space_before = Pt(0)
                p_c.paragraph_format.space_after = Pt(0)
                p_c.add_run().add_picture(str(p_img), width=Mm(iw), height=Mm(common_h_mm))

                c_cap = img_tbl.rows[1].cells[col_i]
                c_cap.width = Mm(90)
                fill_cell(
                    c_cap,
                    cap_str,
                    size_pt=7.9,
                    bold=False,
                    color=MUTED_GRAY,
                    align=WD_ALIGN_PARAGRAPH.CENTER,
                    pad_v=18,
                    pad_h=28,
                    line_spacing=1.12,
                )
            used_img_h_mm = common_h_mm

    # 4. 실험 결과
    add_para(doc, "실험 결과", size_pt=10.5, bold=True, color=NAVY, space_before=6.0, space_after=3.2)
    for res_txt in entry["result"]:
        add_para(doc, f"• {res_txt}", size_pt=9.3, space_after=3.5, line_spacing=1.26)

    total_est_pt = text_pt + (used_img_h_mm * 2.83465)
    if not is_last:
        doc.add_page_break()
    return total_est_pt, used_img_h_mm


def verify_docx_page_breaks(docx_path: Path, expected_pages: int) -> int:
    with zipfile.ZipFile(docx_path, "r") as zf:
        xml_bytes = zf.read("word/document.xml")
    root = ET.fromstring(xml_bytes)
    ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    breaks = [
        br for br in root.findall(".//w:br", ns)
        if br.attrib.get(f"{{{ns['w']}}}type") == "page"
    ]
    actual_pages = len(breaks) + 1
    assert actual_pages == expected_pages, f"Expected {expected_pages} pages in {docx_path.name}, got {actual_pages}"
    return actual_pages


def build_year_notebook(year: int, period_str: str, days: list[dict], out_filename: str, expected_pages: int) -> Path:
    prevalidate_dataset(year=year, expected_days=expected_pages - 1, days=days)

    doc = Document()
    section = doc.sections[0]
    section.page_width = Mm(210)
    section.page_height = Mm(297)
    section.top_margin = Mm(11.0)
    section.bottom_margin = Mm(11.0)
    section.left_margin = Mm(15)
    section.right_margin = Mm(15)
    section.footer_distance = Mm(6.0)

    footer = section.footer
    add_page_number_fields(footer.paragraphs[0])

    toc_pt = build_single_page_toc(doc, year, period_str, days)
    assert toc_pt < 650.0, f"TOC height risk ({toc_pt:.1f} pt) in {year}"

    max_pt = 0.0
    min_pt = 9999.0
    min_img_mm = 999.0
    max_img_mm = 0.0

    for idx, entry in enumerate(days, start=1):
        est_pt, img_h_mm = build_day_page(doc, year, idx, entry, is_last=(idx == len(days)))
        max_pt = max(max_pt, est_pt)
        min_pt = min(min_pt, est_pt)
        min_img_mm = min(min_img_mm, img_h_mm)
        max_img_mm = max(max_img_mm, img_h_mm)
        assert est_pt < 745.0, f"Page overflow risk at {year} {entry['date']}: {est_pt:.1f} pt"

    out_dir = ROOT / "docs"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / out_filename
    doc.save(str(out_path))

    verified_pages = verify_docx_page_breaks(out_path, expected_pages=expected_pages)
    total_imgs = sum(len(d["images"]) for d in days)
    print(f"[SUCCESS] {out_path.name}")
    print(f"  - 구성 분량: 목차(1p) + 일자별 기록({len(days)}p) = 총 {verified_pages}장 (삽입 실물/실행 이미지 총 {total_imgs}장)")
    print(f"  - 목차 추정 높이: {toc_pt:.1f} pt | 본문 페이지 추정 높이: {min_pt:.1f} ~ {max_pt:.1f} pt (< 779 pt)")
    print(f"  - 삽입 이미지 높이 범위: {min_img_mm:.1f} ~ {max_img_mm:.1f} mm")
    return out_path


def main():
    if CACHE_DIR.exists():
        shutil.rmtree(CACHE_DIR)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    try:
        build_year_notebook(
            year=2025,
            period_str="2025. 01. 08. ~ 2025. 12. 18.",
            days=DAYS_2025_WEEKLY,
            out_filename="연구노트_2025년_주간미팅반영_신규본.docx",
            expected_pages=39,
        )
        build_year_notebook(
            year=2026,
            period_str="2026. 01. 12. ~ 2026. 11. 10.",
            days=DAYS_2026_WEEKLY,
            out_filename="연구노트_2026년_주간미팅반영_신규본.docx",
            expected_pages=38,
        )
    finally:
        if CACHE_DIR.exists():
            shutil.rmtree(CACHE_DIR)


if __name__ == "__main__":
    main()
