# SpecScan — Construction Spec Analyzer

A small, offline desktop tool that reads construction specification files
(PDF, DOCX, TXT) and pulls out the things you typically go hunting for:

- **Alternates** (Alternate No. X, Add/Deduct/Voluntary Alternate, Section 01 23 00)
- **Basis of Design** mentions (named manufacturers, "BOD", acknowledged manufacturer)
- **Base Bid** references
- **Attic Stock** / spare parts / maintenance materials requirements
- A configurable list of **other keywords** (allowances, unit prices, or-equal,
  substitutions, liquidated damages, warranty, shop drawings, LEED, etc.)

Everything runs locally on your machine. There is no network call and no AI
service involved — it's plain text extraction plus keyword/regex matching,
so it works completely offline and your specs never leave your computer.

## 1. One-time setup

You need Python 3.10+ installed ([python.org/downloads](https://www.python.org/downloads/)
— on Windows, check "Add python.exe to PATH" during install).

Open a terminal (Command Prompt/PowerShell on Windows, Terminal on macOS) in
this folder and run:

```
pip install -r requirements.txt
```

That installs the three libraries used for reading PDFs/Word docs and
writing Excel reports.

## 2. Run it

### Desktop GUI (recommended)

- **Windows:** double-click `run_gui.bat`
- **macOS/Linux:** run `./run_gui.sh` (or `python3 -m specscan.gui`)

In the window: click **Choose Spec File(s)...**, pick one or more PDFs,
click **Run Analysis**, review the results, then optionally
**Export to Excel...** or **Save as Markdown...**.

### Command line

```
python -m specscan.cli "MySpec.pdf"
python -m specscan.cli specs/*.pdf --format markdown --out report.md
python -m specscan.cli specs/*.pdf --format excel --out report.xlsx
```

## 3. Customize what it looks for

Edit `specscan/config/keywords.json` — no coding required:

- `"keywords"` is a flat list of phrases to flag anywhere in the document
  (add/remove freely, e.g. add project-specific terms you always check for).
- `"categories"` holds the four structured sections (alternates, basis of
  design, base bid, attic stock) as regex patterns, in case your specs use
  different phrasing you want to also catch.

You can also point the tool at a completely separate keywords file without
touching the bundled one:

```
python -m specscan.cli spec.pdf --keywords my_keywords.json
```
(or use **Use Custom Keywords File...** in the GUI)

## 4. Turn it into a standalone .exe (optional)

If you want to run SpecScan without opening a terminal or having Python
"visible", package it with [PyInstaller](https://pyinstaller.org/):

```
pip install pyinstaller
pyinstaller --onefile --windowed --name SpecScan --add-data "specscan/config;specscan/config" -m specscan.gui
```

(On macOS/Linux, use `--add-data "specscan/config:specscan/config"` — colon,
not semicolon.) The resulting executable will be in `dist/`.

## 5. Project layout

```
specscan/
  extractor.py   # reads PDF/DOCX/TXT into page-numbered text
  keywords.py     # loads keywords.json into compiled regex rules
  analyzer.py      # scans pages, collects hits with page + context snippet
  report.py         # renders results as text / markdown / Excel
  cli.py              # command-line interface
  gui.py               # Tkinter desktop GUI
  config/keywords.json # editable keyword/category definitions
tests/
  test_analyzer.py   # sanity tests for the extraction logic
```

## Notes / limitations

- Scanned (image-only) PDFs have no extractable text layer; `pdfplumber`
  won't find text on those pages. If your specs are scans, run them through
  OCR first (e.g. Adobe Acrobat's "Recognize Text", or a tool like
  `ocrmypdf`) before scanning with SpecScan.
- Matching is keyword/regex based, not semantic — it will find every
  mention of "basis of design", "attic stock", etc., with surrounding
  context so you can quickly judge relevance, but it doesn't attempt to
  "understand" the spec. Add project-specific phrasing to `keywords.json`
  as you notice gaps.
