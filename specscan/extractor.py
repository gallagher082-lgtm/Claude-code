"""Extracts page-numbered text from spec documents (PDF, DOCX, TXT)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class Page:
    number: int  # 1-based
    text: str


class UnsupportedFileType(Exception):
    pass


def extract_pages(path: Path) -> list[Page]:
    """Return a list of Page objects for the given file.

    DOCX and TXT files don't have a native concept of "page", so they are
    split into pseudo-pages by form-feed characters if present, otherwise
    treated as a single page.
    """
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        return _extract_pdf(path)
    if suffix == ".docx":
        return _extract_docx(path)
    if suffix in (".txt", ".md"):
        return _extract_txt(path)
    raise UnsupportedFileType(
        f"Unsupported file type '{suffix}' for {path.name}. "
        "Supported: .pdf, .docx, .txt, .md"
    )


def _extract_pdf(path: Path) -> list[Page]:
    import pdfplumber

    pages: list[Page] = []
    with pdfplumber.open(path) as pdf:
        for i, pdf_page in enumerate(pdf.pages, start=1):
            text = pdf_page.extract_text() or ""
            pages.append(Page(number=i, text=text))
    return pages


def _extract_docx(path: Path) -> list[Page]:
    import docx

    document = docx.Document(str(path))
    full_text = "\n".join(p.text for p in document.paragraphs)
    chunks = full_text.split("\x0c")  # form feed = manual page break marker
    if len(chunks) <= 1:
        return [Page(number=1, text=full_text)]
    return [Page(number=i, text=chunk) for i, chunk in enumerate(chunks, start=1)]


def _extract_txt(path: Path) -> list[Page]:
    text = path.read_text(encoding="utf-8", errors="replace")
    chunks = text.split("\x0c")
    if len(chunks) <= 1:
        return [Page(number=1, text=text)]
    return [Page(number=i, text=chunk) for i, chunk in enumerate(chunks, start=1)]
