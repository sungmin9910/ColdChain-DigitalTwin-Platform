# -*- coding: utf-8 -*-
"""
생성된 2025년·2026년 연구노트 .docx XML 구조 및 금지 항목 전수 사전 검증 스크립트
"""

import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(r"c:\Users\korea\Desktop\1hsm\hanhanhan\ColdChain-DigitalTwin-Platform")

FORBIDDEN_TERMS = [
    "Day ",
    "실험 목적",
    "발생 오류 및 시행착오 분석",
    "정량적 실행",
    "대상 코드/산출물",
    "RandomForest",
    "sensor_classification",
    "desktop_stand",
    "cable_clip",
    "신도리코",
    "3DWOX",
    "문서번호",
    "점검자",
]

NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}


def verify_docx(docx_path: Path):
    assert docx_path.exists(), f"Missing file: {docx_path}"
    with zipfile.ZipFile(docx_path, "r") as zf:
        media_files = [n for n in zf.namelist() if n.startswith("word/media/")]
        xml_bytes = zf.read("word/document.xml")

    root = ET.fromstring(xml_bytes)
    all_texts = [t.text for t in root.findall(".//w:t", NS) if t.text]
    full_text = "".join(all_texts)

    # Count explicit page breaks (<w:br w:type="page"/>)
    page_breaks = [
        br for br in root.findall(".//w:br", NS)
        if br.attrib.get("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}type") == "page"
    ]
    total_pages = len(page_breaks) + 1

    print(f"=== {docx_path.name} ({docx_path.stat().st_size / (1024*1024):.2f} MB) ===")
    print(f"  - 명시적 페이지 구분(w:br page): {len(page_breaks)}개 -> 총 {total_pages}페이지 (30~40장 범위 충족: {30 <= total_pages <= 40})")
    print(f"  - 내장 실물/실행 이미지(word/media/*): {len(media_files)}개")

    violations = []
    for term in FORBIDDEN_TERMS:
        if term in full_text:
            violations.append(term)
    assert not violations, f"Forbidden terms found in {docx_path.name}: {violations}"
    print("  - 금지 문구(Day 번호·제목·부제목·목적·표·신도리코/3DWOX·RandomForest·스탠드·케이블클립) 검출: 0건 PASS!")


if __name__ == "__main__":
    p25_mod = ROOT / "docs" / "연구노트_2025년_콜드체인_디지털트윈_플랫폼_수정본.docx"
    p25 = p25_mod if p25_mod.exists() else ROOT / "docs" / "연구노트_2025년_콜드체인_디지털트윈_플랫폼.docx"
    p26_mod = ROOT / "docs" / "연구노트_2026년_콜드체인_디지털트윈_플랫폼_수정본.docx"
    p26 = p26_mod if p26_mod.exists() else ROOT / "docs" / "연구노트_2026년_콜드체인_디지털트윈_플랫폼.docx"
    verify_docx(p25)
    verify_docx(p26)
