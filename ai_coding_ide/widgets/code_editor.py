"""Code editor widget with line numbers and syntax highlighting."""

from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import ttk

from ..syntax import configure_python_tags, highlight_python
from ..theme import COLORS, EDITOR_FONT


class CodeEditor(ttk.Frame):
    def __init__(self, parent, filepath: str | Path | None = None):
        super().__init__(parent)
        self.filepath = Path(filepath) if filepath else None

        self.line_numbers = tk.Text(
            self,
            width=5,
            padx=5,
            takefocus=0,
            border=0,
            background=COLORS["line_number_background"],
            foreground=COLORS["line_number_foreground"],
            state="disabled",
            font=EDITOR_FONT,
        )
        self.line_numbers.pack(side="left", fill="y")

        self.text = tk.Text(
            self,
            wrap="none",
            undo=True,
            bg=COLORS["editor_background"],
            fg=COLORS["editor_foreground"],
            insertbackground="white",
            selectbackground=COLORS["selection"],
            font=EDITOR_FONT,
            padx=10,
            pady=10,
        )
        self.text.pack(side="left", fill="both", expand=True)

        y_scroll = ttk.Scrollbar(self, orient="vertical", command=self.sync_vertical_scroll)
        y_scroll.pack(side="right", fill="y")

        x_scroll = ttk.Scrollbar(self, orient="horizontal", command=self.text.xview)
        x_scroll.pack(side="bottom", fill="x")

        self.text.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)
        configure_python_tags(self.text)

        self.text.bind("<KeyRelease>", self.on_content_changed)
        self.text.bind("<MouseWheel>", self.update_line_numbers)
        self.text.bind("<ButtonRelease-1>", self.update_line_numbers)

        self.update_line_numbers()

    @property
    def display_name(self) -> str:
        if self.filepath:
            return self.filepath.name
        return "Untitled"

    def on_content_changed(self, event=None) -> None:
        self.update_line_numbers()
        self.highlight_syntax()

    def sync_vertical_scroll(self, *args) -> None:
        self.text.yview(*args)
        self.line_numbers.yview(*args)

    def update_line_numbers(self, event=None) -> None:
        lines = self.text.get("1.0", "end-1c").split("\n")
        line_text = "\n".join(str(index + 1) for index in range(len(lines)))

        self.line_numbers.config(state="normal")
        self.line_numbers.delete("1.0", "end")
        self.line_numbers.insert("1.0", line_text)
        self.line_numbers.config(state="disabled")

    def highlight_syntax(self) -> None:
        highlight_python(self.text)

    def get_content(self) -> str:
        return self.text.get("1.0", "end-1c")

    def set_content(self, content: str) -> None:
        self.text.delete("1.0", "end")
        self.text.insert("1.0", content)
        self.update_line_numbers()
        self.highlight_syntax()

