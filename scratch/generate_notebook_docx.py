# -*- coding: utf-8 -*-
"""
연도별 분리 연구노트 (2025년 / 2026년) Word(.docx) 생성 스크립트
- 표지·작성원칙·기획·향후계획 전면 배제 -> 1페이지 목차 + 일자별 수행 결과 본문(1일 1페이지) 구성
  1) docs/연구노트_2025년_콜드체인_디지털트윈_플랫폼.docx : 목차(1p) + 본문(33p, 2025.03~2025.12) = 총 34장
  2) docs/연구노트_2026년_콜드체인_디지털트윈_플랫폼.docx : 목차(1p) + 본문(36p, 2026.01~2026.11, 하반기 9월 PCB 발주 포함) = 총 37장
- 상단 형식 메타데이터 표 제거, 전 일자(총 69일) 고유 실물 사진 및 실제 파이썬·보드·대시보드·CAD 실행 결과 삽입 (AI 이미지 0건)
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

from nb2025_data import DAYS_2025
from nb2026_data import DAYS_2026


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


def fill_cell(cell, text, size_pt=8.2, bold=False, color=DARK_SLATE, align=WD_ALIGN_PARAGRAPH.LEFT, pad_v=36, pad_h=80, line_spacing=1.12):
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


def estimate_lines(text: str, chars_per_line: int = 58) -> int:
    eff_len = 0.0
    for ch in text:
        eff_len += 1.0 if ord(ch) > 127 else 0.55
    return max(1, math.ceil(eff_len / chars_per_line))


def prepare_embed_image(year: int, day_num: int, rel_path: str) -> tuple[Path, int, int]:
    """EXIF 방향 정규화 및 인쇄 품질 유지 최적 해상도(최대 1550px) 변환"""
    src = ROOT / rel_path
    assert src.exists(), f"Missing image for {year} Day {day_num}: {src}"
    with Image.open(src) as im:
        im = ImageOps.exif_transpose(im)
        w, h = im.size
        max_dim = 1550
        if max(w, h) > max_dim:
            scale = max_dim / float(max(w, h))
            w = max(1, int(round(w * scale)))
            h = max(1, int(round(h * scale)))
            im = im.resize((w, h), Image.Resampling.LANCZOS)

        if src.suffix.lower() in {".jpg", ".jpeg"} or (w * h > 900_000 and im.mode == "RGB"):
            rgb = im.convert("RGB")
            dst = CACHE_DIR / f"y{year}_day_{day_num:02d}.jpg"
            rgb.save(dst, format="JPEG", quality=91, optimize=True)
        else:
            dst = CACHE_DIR / f"y{year}_day_{day_num:02d}.png"
            im.save(dst, format="PNG", optimize=True)
        return dst, w, h


def build_single_page_toc(doc: Document, year: int, period_str: str, days: list[dict]) -> float:
    """표지 없이 첫 페이지(1p)에 전체 일자별 수행 목차만 깔끔하게 배치"""
    p_hdr = add_para(
        doc,
        f"{year}년도 연구노트 목차  ({period_str}  |  총 {len(days)}일차)",
        size_pt=12.0,
        bold=True,
        color=NAVY,
        space_before=0.0,
        space_after=4.5,
        line_spacing=1.10,
    )

    tbl = doc.add_table(rows=len(days) + 1, cols=3)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl)
    widths = [Mm(15), Mm(23), Mm(142)]
    headers = ["일차", "수행일자", "수행 실험 · 하드웨어/소프트웨어 구현 결과 요약"]
    for c_i, h in enumerate(headers):
        c = tbl.rows[0].cells[c_i]
        c.width = widths[c_i]
        set_cell_shading(c, "1E3A5F")
        fill_cell(c, h, size_pt=7.8, bold=True, color=RGBColor(255, 255, 255), align=WD_ALIGN_PARAGRAPH.CENTER, pad_v=26, pad_h=50, line_spacing=1.05)

    est_pt = 22.0 + 16.0
    for r_i, item in enumerate(days, start=1):
        vals = [f"Day {item['day']:02d}", item["date"], item["title"]]
        row_lines = estimate_lines(item["title"], 55)
        est_pt += row_lines * 8.8 + 3.2
        for c_i, val in enumerate(vals):
            c = tbl.rows[r_i].cells[c_i]
            c.width = widths[c_i]
            if r_i % 2 == 0:
                set_cell_shading(c, "F8FAFC")
            fill_cell(
                c,
                val,
                size_pt=7.35,
                bold=(c_i == 0),
                color=NAVY if c_i == 0 else DARK_SLATE,
                align=WD_ALIGN_PARAGRAPH.CENTER if c_i in (0, 1) else WD_ALIGN_PARAGRAPH.LEFT,
                pad_v=16,
                pad_h=50,
                line_spacing=1.05,
            )

    doc.add_page_break()
    return est_pt


def estimate_day_text_pt(entry: dict) -> float:
    pt = 0.0
    # Top 2-line title bar
    pt += estimate_lines(f"Day {entry['day']:02d} | {entry['date']} — {entry['title']}", 48) * 14.2 + 15.0
    # Section 1
    pt += 15.0 + estimate_lines(entry["objective"], 58) * 10.5 + 2.5
    # Section 2
    pt += 15.0
    for idx, w_item in enumerate(entry["work"], start=1):
        pt += estimate_lines(f"• [{idx}] {w_item}", 58) * 10.3 + 1.8
    # Caption below image
    pt += estimate_lines(entry["caption"], 62) * 9.5 + 6.0
    # Section 3 (Failure Callout)
    fail_txt = f"[시행착오 및 원인 진단] {entry['failure']}"
    pt += 15.0 + estimate_lines(fail_txt, 54) * 10.2 + 11.0
    # Section 4 (Fixes)
    pt += 15.0
    for c_item in entry["change"]:
        pt += estimate_lines(f"✔ [해결] {c_item}", 58) * 10.3 + 1.8
    # Section 5 (Metrics Table)
    pt += 16.0 + 18.0
    for m_name, m_before, m_after in entry["metrics"]:
        row_lines = max(
            estimate_lines(m_name, 13),
            estimate_lines(m_before, 22),
            estimate_lines(m_after, 23),
        )
        pt += row_lines * 9.7 + 6.5
    return pt


def build_day_page(doc: Document, year: int, entry: dict, is_last: bool = False) -> tuple[float, float]:
    day_num = entry["day"]
    embed_path, px_w, px_h = prepare_embed_image(year, day_num, entry["image"])

    # Dynamically size image height so full page stays ~665-720 pt (< 773.9 pt usable A4)
    text_pt = estimate_day_text_pt(entry)
    avail_img_pt = max(126.0, min(180.0, 718.0 - text_pt))
    img_h_mm = avail_img_pt / 2.83465
    aspect = px_w / float(px_h)
    img_w_mm = img_h_mm * aspect
    if img_w_mm > 160.0:
        img_w_mm = 160.0
        img_h_mm = img_w_mm / aspect

    # 1. Clean Top Heading (NO formal metadata table!)
    add_para(
        doc,
        f"Day {day_num:02d}  |  {entry['date']}  —  {entry['title']}",
        size_pt=10.6,
        bold=True,
        color=NAVY,
        space_before=0.0,
        space_after=1.5,
        line_spacing=1.14,
    )
    p_sub = add_para(
        doc,
        f"{entry['phase']}   ·   대상 코드/산출물: {entry['files']}",
        size_pt=7.7,
        bold=False,
        color=MUTED_GRAY,
        space_before=0.0,
        space_after=4.5,
        line_spacing=1.10,
    )
    set_paragraph_bottom_border(p_sub, color_hex="1E3A5F", sz="8")

    # 2. Section 1: Objective
    add_para(doc, "1. 실험 목적", size_pt=9.1, bold=True, color=NAVY, space_before=3.5, space_after=1.5)
    add_para(doc, entry["objective"], size_pt=8.4, space_after=2.5, line_spacing=1.14)

    # 3. Section 2: Executed Work
    add_para(doc, "2. 실험 및 구현 수행 내용", size_pt=9.1, bold=True, color=NAVY, space_before=3.0, space_after=1.5)
    for idx, w_item in enumerate(entry["work"], start=1):
        add_para(doc, f"• [{idx}] {w_item}", size_pt=8.3, space_after=1.5, line_spacing=1.13)

    # 4. Embedded Authentic Photo / Real Execution Result Capture
    p_pic = doc.add_paragraph()
    p_pic.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_pic.paragraph_format.space_before = Pt(3.5)
    p_pic.paragraph_format.space_after = Pt(1.5)
    p_pic.add_run().add_picture(str(embed_path), width=Mm(img_w_mm), height=Mm(img_h_mm))

    add_para(
        doc,
        entry["caption"],
        size_pt=7.8,
        bold=True,
        color=MUTED_GRAY,
        space_before=0.0,
        space_after=3.0,
        line_spacing=1.10,
        align=WD_ALIGN_PARAGRAPH.CENTER,
    )

    # 5. Section 3: Failures & Root Cause
    add_para(doc, "3. 발생 오류 및 시행착오 분석", size_pt=9.1, bold=True, color=FAIL_RED, space_before=2.5, space_after=1.8)
    fail_box = doc.add_table(rows=1, cols=1)
    fail_box.alignment = WD_TABLE_ALIGNMENT.CENTER
    fail_box.rows[0].cells[0].width = Mm(180)
    set_callout_borders(fail_box, left_color="DC2626", bg_color="FEF2F2")
    fail_txt = f"[시행착오 및 원인 진단] {entry['failure']}"
    fill_cell(fail_box.rows[0].cells[0], fail_txt, size_pt=8.2, color=DARK_SLATE, pad_v=42, pad_h=95)

    # 6. Section 4: Resolution & Modification
    add_para(doc, "4. 설계 수정 및 해결 결과", size_pt=9.1, bold=True, color=FIX_GREEN, space_before=3.5, space_after=1.5)
    for c_item in entry["change"]:
        add_para(doc, f"✔ [해결] {c_item}", size_pt=8.3, space_after=1.5, line_spacing=1.13)

    # 7. Section 5: Quantitative Metrics Table (NO future plan line!)
    add_para(doc, "5. 정량적 실행·검증 결과", size_pt=9.1, bold=True, color=NAVY, space_before=3.0, space_after=2.0)
    m_tbl = doc.add_table(rows=len(entry["metrics"]) + 1, cols=3)
    m_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(m_tbl)
    m_widths = [Mm(42), Mm(67), Mm(71)]
    m_headers = ["검증 항목 / 지표", "개선 전 (오류·한계 상태)", "개선 후 (수행·해결 결과)"]
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

    total_est_pt = text_pt + (img_h_mm * 2.83465)
    if not is_last:
        doc.add_page_break()
    return total_est_pt, img_h_mm


def build_year_notebook(year: int, period_str: str, days: list[dict], out_filename: str):
    for idx, d in enumerate(days, start=1):
        assert d["day"] == idx, f"{year} Day sequence mismatch at {idx}: {d['day']}"

    doc = Document()
    section = doc.sections[0]
    section.page_width = Mm(210)
    section.page_height = Mm(297)
    section.top_margin = Mm(12)
    section.bottom_margin = Mm(12)
    section.left_margin = Mm(15)
    section.right_margin = Mm(15)
    section.header_distance = Mm(6)
    section.footer_distance = Mm(6)
    section.different_first_page_header_footer = False

    hdr_p = section.header.paragraphs[0]
    hdr_p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    hr = hdr_p.add_run(f"{year}년도 콜드체인 디지털 트윈 플랫폼 연구노트 ({period_str})")
    set_east_asia_font(hr, size_pt=7.8, color=MUTED_GRAY)

    ftr_p = section.footer.paragraphs[0]
    add_page_number_fields(ftr_p)

    # Page 1: Single-Page TOC ONLY (No Cover, No Guidelines)
    toc_pt = build_single_page_toc(doc, year, period_str, days)

    # Pages 2 .. N+1: Daily Executed R&D Pages
    stats = []
    for i, entry in enumerate(days):
        tot_pt, im_h = build_day_page(doc, year, entry, is_last=(i == len(days) - 1))
        stats.append((entry["day"], tot_pt, im_h))

    out_path = ROOT / "docs" / out_filename
    doc.save(str(out_path))

    min_s = min(stats, key=lambda x: x[1])
    max_s = max(stats, key=lambda x: x[1])
    overflow = [x for x in stats if x[1] > 745.0]
    print(f"=== [{year}년도 연구노트 빌드 완료] ===")
    print(f"  파일 경로 : {out_path} ({out_path.stat().st_size / (1024*1024):.2f} MB)")
    print(f"  총 페이지 : 목차(1p, {toc_pt:.1f}pt) + 본문({len(days)}p) = 총 {1 + len(days)}장 (A4)")
    print(f"  높이 검증 : 최소 Day {min_s[0]} ({min_s[1]:.1f}pt) ~ 최대 Day {max_s[0]} ({max_s[1]:.1f}pt) / 가용 773.9pt")
    print(f"  넘침 페이지(>745pt) : {len(overflow)}건")
    assert toc_pt < 720.0, f"TOC overflow risk ({toc_pt:.1f}pt)"
    assert len(overflow) == 0, f"Day page overflow risk: {overflow}"


def main():
    # Global uniqueness & anti-AI verification across BOTH years
    all_imgs = [d["image"] for d in DAYS_2025] + [d["image"] for d in DAYS_2026]
    assert len(all_imgs) == len(set(all_imgs)), (
        f"Duplicate image detected! Total={len(all_imgs)}, Unique={len(set(all_imgs))}"
    )
    banned_keywords = ["extracted_pdf_images", "four_layer", "conceptual_vision", "consumer_guide", "farm_process", "apc_storage_process"]
    for img_p in all_imgs:
        assert not any(bk in img_p for bk in banned_keywords), f"Banned AI illustration detected: {img_p}"
        assert (ROOT / img_p).exists(), f"Image missing on disk: {img_p}"

    build_year_notebook(
        year=2025,
        period_str="2025.03 ~ 2025.12",
        days=DAYS_2025,
        out_filename="연구노트_2025년_콜드체인_디지털트윈_플랫폼.docx",
    )
    build_year_notebook(
        year=2026,
        period_str="2026.01 ~ 2026.11",
        days=DAYS_2026,
        out_filename="연구노트_2026년_콜드체인_디지털트윈_플랫폼.docx",
    )


if __name__ == "__main__":
    main()
