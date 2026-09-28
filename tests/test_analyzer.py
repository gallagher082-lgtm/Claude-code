from pathlib import Path

from specscan.analyzer import analyze_pages
from specscan.extractor import Page
from specscan.keywords import load_config

SAMPLE_PAGE_1 = """
SECTION 01 23 00 - ALTERNATES

Alternate No. 1: Provide upgraded roofing membrane in lieu of base bid
roofing system described in Section 07 50 00.

Alternate No. 2 (Deduct Alternate): Omit skylights shown on Drawing A-501.
"""

SAMPLE_PAGE_2 = """
The Basis of Design for the air handling units is Trane Model XYZ-100.
Substitutions will be considered per Section 01 25 00, or equal products
from acceptable manufacturers may be submitted for review.

Contractor shall provide attic stock of 5% of installed flooring material,
plus 2 spare parts kits for each pump, per the maintenance materials
requirements below. Base Bid price shall include all attic stock.
"""


def test_analyze_pages_finds_all_default_categories():
    config = load_config()
    pages = [Page(number=1, text=SAMPLE_PAGE_1), Page(number=2, text=SAMPLE_PAGE_2)]

    result = analyze_pages(pages, config, source_name="sample.txt")

    assert len(result.category_hits["alternates"]) >= 2
    assert any(h.page == 1 for h in result.category_hits["alternates"])

    assert len(result.category_hits["basis_of_design"]) >= 1
    assert result.category_hits["basis_of_design"][0].page == 2

    assert len(result.category_hits["base_bid"]) >= 2

    assert len(result.category_hits["attic_stock"]) >= 1

    assert result.keyword_hits["substitution"]
    assert result.keyword_hits["or equal"]


def test_extract_txt_roundtrip(tmp_path: Path):
    from specscan.extractor import extract_pages

    sample = tmp_path / "spec.txt"
    sample.write_text(SAMPLE_PAGE_1 + "\x0c" + SAMPLE_PAGE_2, encoding="utf-8")

    pages = extract_pages(sample)
    assert len(pages) == 2
    assert "Alternate No. 1" in pages[0].text
    assert "Basis of Design" in pages[1].text
