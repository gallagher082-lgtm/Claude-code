"""Command-line entry point.

Usage:
    python -m specscan.cli SPEC1.pdf [SPEC2.pdf ...] [options]

Examples:
    python -m specscan.cli "Div 08 Openings.pdf"
    python -m specscan.cli specs/*.pdf --format excel --out report.xlsx
    python -m specscan.cli spec.pdf --keywords my_keywords.json
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .analyzer import analyze_file
from .keywords import load_config
from .report import to_excel, to_markdown, to_text


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="specscan",
        description="Scan construction specification files for alternates, "
        "basis-of-design mentions, base bid, attic stock, and other keywords.",
    )
    parser.add_argument("files", nargs="+", help="Spec file(s) to scan: .pdf, .docx, .txt")
    parser.add_argument(
        "--format",
        choices=["text", "markdown", "excel"],
        default="text",
        help="Output format (default: text, printed to stdout unless --out is set)",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Write report to this file instead of stdout (required for --format excel)",
    )
    parser.add_argument(
        "--keywords",
        type=Path,
        default=None,
        help="Path to a custom keywords.json (defaults to the bundled config)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    config = load_config(args.keywords)

    results = []
    had_error = False
    for file_str in args.files:
        path = Path(file_str)
        if not path.exists():
            print(f"ERROR: file not found: {path}", file=sys.stderr)
            had_error = True
            continue
        try:
            results.append(analyze_file(path, config))
        except Exception as exc:  # noqa: BLE001 - surface any extraction failure per-file
            print(f"ERROR: failed to scan {path.name}: {exc}", file=sys.stderr)
            had_error = True

    if not results:
        return 1

    if args.format == "excel":
        out_path = args.out or Path("specscan_report.xlsx")
        to_excel(results, config, out_path)
        print(f"Wrote {out_path}")
    else:
        text = to_markdown(results, config) if args.format == "markdown" else to_text(results, config)
        if args.out:
            args.out.write_text(text, encoding="utf-8")
            print(f"Wrote {args.out}")
        else:
            print(text)

    return 1 if had_error else 0


if __name__ == "__main__":
    raise SystemExit(main())
