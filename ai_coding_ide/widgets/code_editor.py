"""Code editor widget with line numbers and syntax highlighting."""
# a ui for ai code comaprison 
# implement my own ai coding agent 
# before applying  it must be accepted before updating it 
# on comapring it must highlight what chabge from code and the ai generated code 
.
from __future__ import annotations

import tkinter as tk
from tkinter import font
from pathlib import Path
from tkinter import ttk

from ..syntax import configure_python_tags, highlight_python
from ..theme import COLORS, EDITOR_FONT

INDENT = "    "


class CodeEditor(ttk.Frame):
    def __init__(self, parent, filepath: str | Path | None = None):
        super().__init__(parent)
        self.filepath = Path(filepath).resolve() if filepath else None

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
        self.configure_tab_width()

        y_scroll = ttk.Scrollbar(self, orient="vertical", command=self.sync_vertical_scroll)
        y_scroll.pack(side="right", fill="y")

        x_scroll = ttk.Scrollbar(self, orient="horizontal", command=self.text.xview)
        x_scroll.pack(side="bottom", fill="x")

        self.text.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)
        configure_python_tags(self.text)

        self.text.bind("<KeyRelease>", self.on_content_changed)
        self.text.bind("<Tab>", self.indent_selection_or_line)
        self.text.bind("<Shift-Tab>", self.unindent_selection_or_line)
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

    def configure_tab_width(self) -> None:
        editor_font = font.Font(font=EDITOR_FONT)
        self.text.configure(tabs=(editor_font.measure(INDENT),))

    def indent_selection_or_line(self, event=None) -> str:
        start_line, end_line = self.get_selected_line_range()

        for line_number in range(start_line, end_line + 1):
            self.text.insert(f"{line_number}.0", INDENT)

        self.on_content_changed()
        return "break"

    def unindent_selection_or_line(self, event=None) -> str:
        start_line, end_line = self.get_selected_line_range()

        for line_number in range(start_line, end_line + 1):
            line_start = f"{line_number}.0"
            line_prefix = self.text.get(line_start, f"{line_start}+{len(INDENT)}c")

            if line_prefix.startswith(INDENT):
                self.text.delete(line_start, f"{line_start}+{len(INDENT)}c")
            elif line_prefix.startswith("\t"):
                self.text.delete(line_start, f"{line_start}+1c")

        self.on_content_changed()
        return "break"

    def get_selected_line_range(self) -> tuple[int, int]:
        try:
            start = self.text.index("sel.first")
            end = self.text.index("sel.last")
        except tk.TclError:
            current_line = int(self.text.index("insert").split(".")[0])
            return current_line, current_line

        start_line = int(start.split(".")[0])
        end_line, end_column = (int(part) for part in end.split("."))

        if end_column == 0 and end_line > start_line:
            end_line -= 1

        return start_line, end_line

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
