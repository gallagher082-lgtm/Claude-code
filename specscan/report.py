"""Turns one or more AnalysisResult objects into human-readable reports."""

from __future__ import annotations

from pathlib import Path

from .analyzer import AnalysisResult
from .keywords import KeywordConfig

CATEGORY_ORDER = ["alternates", "basis_of_design", "base_bid", "attic_stock"]


def _category_label(config: KeywordConfig, key: str) -> str:
    for cat in config.categories:
        if cat.key == key:
            return cat.label
    return key


def to_markdown(results: list[AnalysisResult], config: KeywordConfig) -> str:
    lines: list[str] = []
    for result in results:
        lines.append(f"# {result.source_file}")
        lines.append("")
        lines.append(f"Pages scanned: {result.page_count}  ")
        lines.append(f"Total flagged mentions: {result.total_hits()}")
        lines.append("")

        ordered_keys = [k for k in CATEGORY_ORDER if k in result.category_hits] + [
            k for k in result.category_hits if k not in CATEGORY_ORDER
        ]
        for key in ordered_keys:
            hits = result.category_hits[key]
            label = _category_label(config, key)
            lines.append(f"## {label} ({len(hits)})")
            lines.append("")
            if not hits:
                lines.append("_No mentions found._")
            else:
                for h in sorted(hits, key=lambda x: x.page):
                    lines.append(f"- **p.{h.page}** — {h.snippet}")
            lines.append("")

        keyword_hits = {k: v for k, v in result.keyword_hits.items() if v}
        lines.append(f"## Keywords ({sum(len(v) for v in keyword_hits.values())} mentions)")
        lines.append("")
        if not keyword_hits:
            lines.append("_No configured keywords found._")
        else:
            for label in sorted(keyword_hits):
                hits = keyword_hits[label]
                lines.append(f"### {label} ({len(hits)})")
                for h in sorted(hits, key=lambda x: x.page):
                    lines.append(f"- **p.{h.page}** — {h.snippet}")
                lines.append("")
        lines.append("")
        lines.append("---")
        lines.append("")

    return "\n".join(lines)


def to_text(results: list[AnalysisResult], config: KeywordConfig) -> str:
    lines: list[str] = []
    for result in results:
        lines.append("=" * 70)
        lines.append(f"SOURCE: {result.source_file}")
        lines.append(f"Pages scanned: {result.page_count}   Total mentions: {result.total_hits()}")
        lines.append("=" * 70)

        ordered_keys = [k for k in CATEGORY_ORDER if k in result.category_hits] + [
            k for k in result.category_hits if k not in CATEGORY_ORDER
        ]
        for key in ordered_keys:
            hits = result.category_hits[key]
            label = _category_label(config, key)
            lines.append("")
            lines.append(f"-- {label} ({len(hits)}) " + "-" * max(0, 40 - len(label)))
            if not hits:
                lines.append("  (none found)")
            for h in sorted(hits, key=lambda x: x.page):
                lines.append(f"  p.{h.page}: {h.snippet}")

        keyword_hits = {k: v for k, v in result.keyword_hits.items() if v}
        lines.append("")
        lines.append(f"-- Keywords ({sum(len(v) for v in keyword_hits.values())} mentions) " + "-" * 20)
        if not keyword_hits:
            lines.append("  (none found)")
        for label in sorted(keyword_hits):
            hits = keyword_hits[label]
            lines.append(f"  [{label}] ({len(hits)})")
            for h in sorted(hits, key=lambda x: x.page):
                lines.append(f"    p.{h.page}: {h.snippet}")
        lines.append("")

    return "\n".join(lines)


def to_excel(results: list[AnalysisResult], config: KeywordConfig, out_path: Path) -> None:
    import openpyxl
    from openpyxl.styles import Font

    wb = openpyxl.Workbook()
    summary_ws = wb.active
    summary_ws.title = "Summary"
    summary_ws.append(["File", "Pages", "Total Mentions"] + [
        _category_label(config, k) for k in CATEGORY_ORDER
    ] + ["Keyword Mentions"])
    for cell in summary_ws[1]:
        cell.font = Font(bold=True)
    for result in results:
        row = [result.source_file, result.page_count, result.total_hits()]
        for key in CATEGORY_ORDER:
            row.append(len(result.category_hits.get(key, [])))
        row.append(sum(len(v) for v in result.keyword_hits.values()))
        summary_ws.append(row)

    for result in results:
        ws_name = result.source_file[:28] if result.source_file else "Detail"
        ws = wb.create_sheet(title=_safe_sheet_name(wb, ws_name))
        ws.append(["Category", "Page", "Context"])
        for cell in ws[1]:
            cell.font = Font(bold=True)

        ordered_keys = [k for k in CATEGORY_ORDER if k in result.category_hits] + [
            k for k in result.category_hits if k not in CATEGORY_ORDER
        ]
        for key in ordered_keys:
            label = _category_label(config, key)
            for h in sorted(result.category_hits[key], key=lambda x: x.page):
                ws.append([label, h.page, h.snippet])
        for label in sorted(result.keyword_hits):
            for h in sorted(result.keyword_hits[label], key=lambda x: x.page):
                ws.append([f"Keyword: {label}", h.page, h.snippet])

        for col_idx, width in zip("ABC", (28, 8, 100)):
            ws.column_dimensions[col_idx].width = width

    wb.save(out_path)


def _safe_sheet_name(wb, name: str) -> str:
    base = "".join(c for c in name if c not in "[]:*?/\\") or "Detail"
    candidate = base
    n = 2
    existing = set(wb.sheetnames)
    while candidate in existing:
        suffix = f" ({n})"
        candidate = base[: 31 - len(suffix)] + suffix
        n += 1
    return candidate[:31]
