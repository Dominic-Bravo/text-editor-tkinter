"""Project explorer helpers."""
# update explorer mak eit more comprehensive
# add simple icons or svg for each folder
from __future__ import annotations

from pathlib import Path
from tkinter import ttk

from .config import IGNORED_DIRECTORIES


class FileTree:
    def __init__(self, tree: ttk.Treeview):
        self.tree = tree
        self.root_path: Path | None = None

    def load_folder(self, folder: str | Path) -> None:
        root_path = Path(folder)
        self.root_path = root_path
        self.tree.delete(*self.tree.get_children())

        root_node = self.tree.insert(
            "",
            "end",
            text=root_path.name,
            open=True,
            values=[str(root_path)],
        )
        self._load_directory(root_node, root_path)

    def selected_path(self) -> Path | None:
        selected = self.tree.selection()
        if not selected:
            return self.root_path

        values = self.tree.item(selected[0], "values")
        if not values:
            return self.root_path

        return Path(values[0])

    def selected_item_path(self) -> Path | None:
        selected = self.tree.selection()
        if not selected:
            return None

        values = self.tree.item(selected[0], "values")
        if not values:
            return None

        return Path(values[0])

    def selected_directory(self) -> Path | None:
        selected_path = self.selected_path()
        if not selected_path:
            return None

        if selected_path.is_dir():
            return selected_path

        return selected_path.parent

    def refresh(self) -> None:
        if self.root_path:
            self.load_folder(self.root_path)

    def _load_directory(self, parent: str, path: Path) -> None:
        try:
            children = sorted(path.iterdir(), key=lambda item: (item.is_file(), item.name.lower()))
        except PermissionError:
            return

        for child in children:
            if child.is_dir() and child.name in IGNORED_DIRECTORIES:
                continue

            node = self.tree.insert(parent, "end", text=child.name, values=[str(child)])
            if child.is_dir():
                self._load_directory(node, child)
