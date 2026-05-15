"""Terminal-like output panel."""

import tkinter as tk
from tkinter import ttk

from ..theme import COLORS, TERMINAL_FONT


class TerminalFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self.output = tk.Text(
            self,
            bg=COLORS["terminal_background"],
            fg=COLORS["terminal_foreground"],
            insertbackground="white",
            font=TERMINAL_FONT,
            wrap="word",
        )
        self.output.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.output.yview)
        scrollbar.pack(side="right", fill="y")
        self.output.configure(yscrollcommand=scrollbar.set)

        self.write("Terminal Ready...\n")

    def write(self, text: str) -> None:
        self.output.insert("end", text)
        self.output.see("end")

    def clear(self) -> None:
        self.output.delete("1.0", "end")

