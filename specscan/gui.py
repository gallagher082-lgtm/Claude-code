"""Minimal desktop GUI for SpecScan (Tkinter, no extra dependencies).

Run with:  python -m specscan.gui
"""

from __future__ import annotations

import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, scrolledtext, ttk

from .analyzer import analyze_file
from .keywords import load_config
from .report import to_excel, to_markdown


class SpecScanApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("SpecScan - Construction Spec Analyzer")
        self.geometry("900x650")

        self.selected_files: list[Path] = []
        self.custom_keywords_path: Path | None = None
        self.last_results = None
        self.last_config = None

        self._build_widgets()

    def _build_widgets(self) -> None:
        top = ttk.Frame(self, padding=10)
        top.pack(fill="x")

        ttk.Button(top, text="Choose Spec File(s)...", command=self._choose_files).pack(side="left")
        ttk.Button(top, text="Use Custom Keywords File...", command=self._choose_keywords).pack(
            side="left", padx=(8, 0)
        )
        self.files_label = ttk.Label(top, text="No files selected")
        self.files_label.pack(side="left", padx=(12, 0))

        run_frame = ttk.Frame(self, padding=(10, 0))
        run_frame.pack(fill="x")
        ttk.Button(run_frame, text="Run Analysis", command=self._run_analysis).pack(side="left")
        ttk.Button(run_frame, text="Export to Excel...", command=self._export_excel).pack(
            side="left", padx=(8, 0)
        )
        ttk.Button(run_frame, text="Save as Markdown...", command=self._export_markdown).pack(
            side="left", padx=(8, 0)
        )
        self.status_label = ttk.Label(run_frame, text="")
        self.status_label.pack(side="left", padx=(12, 0))

        self.output = scrolledtext.ScrolledText(self, wrap="word", font=("Consolas", 10))
        self.output.pack(fill="both", expand=True, padx=10, pady=10)

    def _choose_files(self) -> None:
        paths = filedialog.askopenfilenames(
            title="Select specification file(s)",
            filetypes=[("Spec documents", "*.pdf *.docx *.txt"), ("All files", "*.*")],
        )
        if paths:
            self.selected_files = [Path(p) for p in paths]
            self.files_label.config(text=f"{len(self.selected_files)} file(s) selected")

    def _choose_keywords(self) -> None:
        path = filedialog.askopenfilename(
            title="Select keywords.json", filetypes=[("JSON", "*.json"), ("All files", "*.*")]
        )
        if path:
            self.custom_keywords_path = Path(path)
            messagebox.showinfo("SpecScan", f"Using custom keywords file:\n{path}")

    def _run_analysis(self) -> None:
        if not self.selected_files:
            messagebox.showwarning("SpecScan", "Choose at least one spec file first.")
            return
        self.status_label.config(text="Scanning...")
        self.output.delete("1.0", tk.END)
        threading.Thread(target=self._run_analysis_worker, daemon=True).start()

    def _run_analysis_worker(self) -> None:
        try:
            config = load_config(self.custom_keywords_path)
            results = []
            errors = []
            for path in self.selected_files:
                try:
                    results.append(analyze_file(path, config))
                except Exception as exc:  # noqa: BLE001
                    errors.append(f"{path.name}: {exc}")
            text = to_markdown(results, config) if results else ""
            self.last_results = results
            self.last_config = config
        except Exception as exc:  # noqa: BLE001
            self.after(0, lambda: self._show_error(str(exc)))
            return

        def finish() -> None:
            self.output.insert("1.0", text)
            if errors:
                self.output.insert(tk.END, "\n\nErrors:\n" + "\n".join(errors))
            self.status_label.config(text=f"Done. {len(results)} file(s) scanned.")

        self.after(0, finish)

    def _show_error(self, msg: str) -> None:
        self.status_label.config(text="Error")
        messagebox.showerror("SpecScan", msg)

    def _export_excel(self) -> None:
        if not self.last_results:
            messagebox.showwarning("SpecScan", "Run an analysis first.")
            return
        out = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel", "*.xlsx")])
        if out:
            to_excel(self.last_results, self.last_config, Path(out))
            messagebox.showinfo("SpecScan", f"Saved to {out}")

    def _export_markdown(self) -> None:
        if not self.last_results:
            messagebox.showwarning("SpecScan", "Run an analysis first.")
            return
        out = filedialog.asksaveasfilename(defaultextension=".md", filetypes=[("Markdown", "*.md")])
        if out:
            Path(out).write_text(to_markdown(self.last_results, self.last_config), encoding="utf-8")
            messagebox.showinfo("SpecScan", f"Saved to {out}")


def main() -> None:
    app = SpecScanApp()
    app.mainloop()


if __name__ == "__main__":
    main()
