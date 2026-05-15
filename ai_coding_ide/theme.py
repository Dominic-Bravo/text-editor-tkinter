"""Tkinter theme setup and shared colors."""

import tkinter as tk
from tkinter import ttk

COLORS = {
    "app_background": "#181818",
    "editor_background": "#1e1e1e",
    "editor_foreground": "#d4d4d4",
    "line_number_background": "#1b1b1b",
    "line_number_foreground": "#5c6370",
    "border": "#333333",
    "hover": "#353535",
    "active": "#3c3c3c",
    "selection": "#264f78",
    "terminal_background": "#111111",
    "terminal_foreground": "#00ff88",
    "tree_background": "#252526",
    "tree_selection": "#37373d",
    "tab_background": "#2d2d2d",
    "tab_selected": "#1e1e1e",
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


def apply_theme(root: tk.Tk | None = None) -> None:
    style = ttk.Style()
    style.theme_use("clam")

    if root:
        root.configure(bg=COLORS["app_background"])
        root.option_add("*Menu.background", COLORS["tab_background"])
        root.option_add("*Menu.foreground", "white")
        root.option_add("*Menu.activeBackground", COLORS["active"])
        root.option_add("*Menu.activeForeground", "white")
        root.option_add("*Menu.borderWidth", 0)

    style.configure(
        ".",
        background=COLORS["app_background"],
        foreground="white",
        bordercolor=COLORS["border"],
        darkcolor=COLORS["border"],
        lightcolor=COLORS["border"],
        troughcolor=COLORS["app_background"],
    )
    style.configure("TFrame", background=COLORS["app_background"])
    style.configure("Dark.TFrame", background=COLORS["app_background"])
    style.configure("TPanedwindow", background=COLORS["app_background"])
    style.configure("Sash", background=COLORS["border"])

    style.configure(
        "Treeview",
        background=COLORS["tree_background"],
        foreground="white",
        fieldbackground=COLORS["tree_background"],
        bordercolor=COLORS["border"],
        lightcolor=COLORS["border"],
        darkcolor=COLORS["border"],
        rowheight=28,
    )
    style.map(
        "Treeview",
        background=[("selected", COLORS["tree_selection"])],
        foreground=[("selected", "white")],
    )
    style.configure(
        "TNotebook",
        background=COLORS["app_background"],
        bordercolor=COLORS["border"],
        tabmargins=[0, 0, 0, 0],
    )
    style.configure(
        "TNotebook.Tab",
        background=COLORS["tab_background"],
        foreground="white",
        bordercolor=COLORS["border"],
        padding=[12, 6],
    )
    style.map(
        "TNotebook.Tab",
        background=[
            ("selected", COLORS["tab_selected"]),
            ("active", COLORS["hover"]),
        ],
        foreground=[("selected", "white"), ("active", "white")],
    )
    style.configure(
        "Vertical.TScrollbar",
        background=COLORS["tab_background"],
        troughcolor=COLORS["app_background"],
        bordercolor=COLORS["border"],
        arrowcolor="white",
    )
    style.configure(
        "Horizontal.TScrollbar",
        background=COLORS["tab_background"],
        troughcolor=COLORS["app_background"],
        bordercolor=COLORS["border"],
        arrowcolor="white",
    )
    style.map(
        "TScrollbar",
        background=[("active", COLORS["hover"]), ("pressed", COLORS["active"])],
    )
