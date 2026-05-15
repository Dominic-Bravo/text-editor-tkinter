"""Tkinter theme setup and shared colors."""

from tkinter import ttk

COLORS = {
    "editor_background": "#1e1e1e",
    "editor_foreground": "#d4d4d4",
    "line_number_background": "#1b1b1b",
    "line_number_foreground": "#5c6370",
    "selection": "#264f78",
    "terminal_background": "#111111",
    "terminal_foreground": "#00ff88",
    "tree_background": "#252526",
    "tab_background": "#2d2d2d",
}

SYNTAX_COLORS = {
    "keyword": "#c678dd",
    "string": "#98c379",
    "comment": "#5c6370",
    "number": "#d19a66",
    "function": "#61afef",
    "class": "#e5c07b",
}

EDITOR_FONT = ("Consolas", 12)
TERMINAL_FONT = ("Consolas", 10)


def apply_theme() -> None:
    style = ttk.Style()
    style.theme_use("clam")

    style.configure(
        "Treeview",
        background=COLORS["tree_background"],
        foreground="white",
        fieldbackground=COLORS["tree_background"],
        rowheight=28,
    )
    style.configure("TNotebook", background=COLORS["editor_background"])
    style.configure(
        "TNotebook.Tab",
        background=COLORS["tab_background"],
        foreground="white",
        padding=[12, 6],
    )

