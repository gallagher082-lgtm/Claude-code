"""Loads keyword/category definitions from config/keywords.json (or a
user-supplied override file), and compiles them into regexes."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from importlib import resources
from pathlib import Path

DEFAULT_CONFIG_NAME = "keywords.json"


@dataclass
class Category:
    key: str
    label: str
    patterns: list[re.Pattern]


@dataclass
class KeywordRule:
    label: str
    pattern: re.Pattern


@dataclass
class KeywordConfig:
    keywords: list[KeywordRule]
    categories: list[Category]


def _phrase_to_pattern(phrase: str) -> re.Pattern:
    escaped = re.escape(phrase.strip())
    escaped = escaped.replace(r"\ ", r"\s+")
    return re.compile(rf"\b{escaped}\b", re.IGNORECASE)


def load_config(path: Path | None = None) -> KeywordConfig:
    """Load keyword config from `path`, or the bundled default if omitted."""
    if path is not None:
        raw = json.loads(Path(path).read_text(encoding="utf-8"))
    else:
        text = resources.files("specscan.config").joinpath(DEFAULT_CONFIG_NAME).read_text(
            encoding="utf-8"
        )
        raw = json.loads(text)

    keywords: list[KeywordRule] = []
    for entry in raw.get("keywords", []):
        if isinstance(entry, str):
            keywords.append(KeywordRule(label=entry, pattern=_phrase_to_pattern(entry)))
        elif isinstance(entry, dict):
            label = entry["label"]
            pattern = re.compile(entry["pattern"], re.IGNORECASE)
            keywords.append(KeywordRule(label=label, pattern=pattern))

    categories: list[Category] = []
    for key, cat in raw.get("categories", {}).items():
        patterns = [re.compile(p, re.IGNORECASE) for p in cat.get("patterns", [])]
        categories.append(Category(key=key, label=cat.get("label", key), patterns=patterns))

    return KeywordConfig(keywords=keywords, categories=categories)
