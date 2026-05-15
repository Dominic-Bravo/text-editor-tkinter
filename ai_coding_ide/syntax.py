"""Simple Python syntax highlighting rules."""

from __future__ import annotations

import keyword
import re
import tkinter as tk

from .theme import SYNTAX_COLORS

TAG_NAMES = tuple(SYNTAX_COLORS)
STRING_PATTERN = re.compile(r"(\".*?\"|'.*?')")
COMMENT_PATTERN = re.compile(r"#.*")
NUMBER_PATTERN = re.compile(r"\b\d+\b")
FUNCTION_PATTERN = re.compile(r"def\s+([a-zA-Z_][a-zA-Z0-9_]*)")
CLASS_PATTERN = re.compile(r"class\s+([a-zA-Z_][a-zA-Z0-9_]*)")


def configure_python_tags(text_widget: tk.Text) -> None:
    for tag_name, color in SYNTAX_COLORS.items():
        text_widget.tag_configure(tag_name, foreground=color)


def highlight_python(text_widget: tk.Text) -> None:
    content = text_widget.get("1.0", "end-1c")
    clear_python_tags(text_widget)

    _highlight_matches(text_widget, COMMENT_PATTERN.finditer(content), "comment")
    _highlight_matches(text_widget, STRING_PATTERN.finditer(content), "string")
    _highlight_matches(text_widget, NUMBER_PATTERN.finditer(content), "number")
    _highlight_keywords(text_widget)
    _highlight_named_groups(text_widget, FUNCTION_PATTERN.finditer(content), "function")
    _highlight_named_groups(text_widget, CLASS_PATTERN.finditer(content), "class")


def clear_python_tags(text_widget: tk.Text) -> None:
    for tag_name in TAG_NAMES:
        text_widget.tag_remove(tag_name, "1.0", "end")


def _highlight_matches(text_widget: tk.Text, matches, tag_name: str) -> None:
    for match in matches:
        start, end = _range_to_text_indexes(match.start(), match.end())
        text_widget.tag_add(tag_name, start, end)


def _highlight_named_groups(text_widget: tk.Text, matches, tag_name: str) -> None:
    for match in matches:
        start, end = _range_to_text_indexes(match.start(1), match.end(1))
        text_widget.tag_add(tag_name, start, end)


def _highlight_keywords(text_widget: tk.Text) -> None:
    for word in keyword.kwlist:
        start = "1.0"
        pattern = rf"\b{word}\b"

        while True:
            position = text_widget.search(pattern, start, stopindex="end", regexp=True)
            if not position:
                break

            end = f"{position}+{len(word)}c"
            text_widget.tag_add("keyword", position, end)
            start = end


def _range_to_text_indexes(start_offset: int, end_offset: int) -> tuple[str, str]:
    return f"1.0+{start_offset}c", f"1.0+{end_offset}c"

