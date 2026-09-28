"""Core analysis: scan extracted pages against keyword/category rules and
collect structured hits for reporting."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from .extractor import Page, extract_pages
from .keywords import KeywordConfig, load_config

CONTEXT_CHARS = 160


@dataclass
class Hit:
    label: str
    page: int
    snippet: str


@dataclass
class AnalysisResult:
    source_file: str
    page_count: int
    category_hits: dict[str, list[Hit]] = field(default_factory=dict)
    keyword_hits: dict[str, list[Hit]] = field(default_factory=dict)

    def total_hits(self) -> int:
        return sum(len(v) for v in self.category_hits.values()) + sum(
            len(v) for v in self.keyword_hits.values()
        )


def _snippet(text: str, start: int, end: int) -> str:
    lo = max(0, start - CONTEXT_CHARS // 2)
    hi = min(len(text), end + CONTEXT_CHARS // 2)
    snippet = text[lo:hi].replace("\n", " ").strip()
    snippet = re.sub(r"\s+", " ", snippet)
    prefix = "..." if lo > 0 else ""
    suffix = "..." if hi < len(text) else ""
    return f"{prefix}{snippet}{suffix}"


def _dedupe(hits: list[Hit]) -> list[Hit]:
    seen: set[tuple[int, str]] = set()
    out: list[Hit] = []
    for h in hits:
        key = (h.page, h.snippet)
        if key not in seen:
            seen.add(key)
            out.append(h)
    return out


def analyze_pages(pages: list[Page], config: KeywordConfig, source_name: str) -> AnalysisResult:
    result = AnalysisResult(source_file=source_name, page_count=len(pages))

    for category in config.categories:
        hits: list[Hit] = []
        for page in pages:
            for pattern in category.patterns:
                for m in pattern.finditer(page.text):
                    hits.append(
                        Hit(
                            label=m.group(0),
                            page=page.number,
                            snippet=_snippet(page.text, m.start(), m.end()),
                        )
                    )
        result.category_hits[category.key] = _dedupe(hits)

    for rule in config.keywords:
        hits = []
        for page in pages:
            for m in rule.pattern.finditer(page.text):
                hits.append(
                    Hit(
                        label=rule.label,
                        page=page.number,
                        snippet=_snippet(page.text, m.start(), m.end()),
                    )
                )
        result.keyword_hits[rule.label] = _dedupe(hits)

    return result


def analyze_file(path: Path, config: KeywordConfig | None = None) -> AnalysisResult:
    config = config or load_config()
    pages = extract_pages(path)
    return analyze_pages(pages, config, source_name=path.name)
