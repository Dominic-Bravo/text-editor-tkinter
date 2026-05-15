"""Main application shell."""

from __future__ import annotations

import subprocess
import sys
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from .config import APP_TITLE, PYTHON_FILE_TYPES, WINDOW_SIZE
from .file_tree import FileTree
from .theme import COLORS, apply_theme
from .widgets.code_editor import CodeEditor
from .widgets.terminal import TerminalFrame


class AICodingIDE:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry(WINDOW_SIZE)

        apply_theme(self.root)
        self.create_layout()
        self.create_menu()

    def create_layout(self) -> None:
        self.main_pane = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.main_pane.pack(fill="both", expand=True)

        self.sidebar = ttk.Frame(self.main_pane, width=300, style="Dark.TFrame")
        self.main_pane.add(self.sidebar, weight=1)

        self.tree = ttk.Treeview(self.sidebar)
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<Double-1>", self.open_selected_file)
        self.file_tree = FileTree(self.tree)

        self.right_side = ttk.PanedWindow(self.main_pane, orient=tk.VERTICAL)
        self.main_pane.add(self.right_side, weight=4)

        self.notebook = ttk.Notebook(self.right_side)
        self.right_side.add(self.notebook, weight=4)

        self.terminal = TerminalFrame(self.right_side)
        self.right_side.add(self.terminal, weight=1)

    def create_menu(self) -> None:
        menubar = tk.Menu(
            self.root,
            background=COLORS["tab_background"],
            foreground="white",
            activebackground=COLORS["active"],
            activeforeground="white",
            borderwidth=0,
        )

        file_menu = self.create_dark_menu(menubar)
        file_menu.add_command(label="Open Folder", command=self.open_folder)
        file_menu.add_command(label="Open File", command=self.open_file_dialog)
        file_menu.add_command(label="New File", command=self.new_file)
        file_menu.add_command(label="Save", command=self.save_current_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)

        run_menu = self.create_dark_menu(menubar)
        run_menu.add_command(label="Run Python File", command=self.run_current_file)
        run_menu.add_command(label="Clear Terminal", command=self.terminal.clear)
        menubar.add_cascade(label="Run", menu=run_menu)

        self.root.config(menu=menubar)

    def create_dark_menu(self, parent: tk.Menu) -> tk.Menu:
        return tk.Menu(
            parent,
            tearoff=0,
            background=COLORS["tab_background"],
            foreground="white",
            activebackground=COLORS["active"],
            activeforeground="white",
            borderwidth=0,
        )

    def open_folder(self) -> None:
        folder = filedialog.askdirectory()
        if folder:
            self.file_tree.load_folder(folder)

    def open_selected_file(self, event=None) -> None:
        filepath = self.file_tree.selected_path()
        if filepath and filepath.is_file():
            self.open_file(filepath)

    def open_file_dialog(self) -> None:
        filepath = filedialog.askopenfilename(filetypes=PYTHON_FILE_TYPES)
        if filepath:
            self.open_file(filepath)

    def new_file(self) -> None:
        editor = CodeEditor(self.notebook)
        self.notebook.add(editor, text=editor.display_name)
        self.notebook.select(editor)

    def open_file(self, filepath: str | Path) -> None:
        path = Path(filepath)

        try:
            content = path.read_text(encoding="utf-8")
        except OSError as error:
            messagebox.showerror("Error", str(error))
            return

        editor = CodeEditor(self.notebook, filepath=path)
        editor.set_content(content)
        self.notebook.add(editor, text=editor.display_name)
        self.notebook.select(editor)
        self.terminal.write(f"Opened: {path}\n")

    def get_current_editor(self) -> CodeEditor | None:
        current = self.notebook.select()
        if not current:
            return None

        widget = self.notebook.nametowidget(current)
        return widget if isinstance(widget, CodeEditor) else None

    def save_current_file(self) -> bool:
        editor = self.get_current_editor()
        if not editor:
            return False

        if not editor.filepath:
            filepath = filedialog.asksaveasfilename(filetypes=PYTHON_FILE_TYPES)
            if not filepath:
                return False
            editor.filepath = Path(filepath)

        try:
            editor.filepath.write_text(editor.get_content(), encoding="utf-8")
        except OSError as error:
            messagebox.showerror("Error", str(error))
            return False

        self.notebook.tab(editor, text=editor.display_name)
        self.terminal.write(f"Saved: {editor.filepath}\n")
        return True

    def run_current_file(self) -> None:
        editor = self.get_current_editor()
        if not editor:
            return

        if not editor.filepath:
            messagebox.showwarning("Warning", "Save file first.")
            return

        if not self.save_current_file():
            return

        self.terminal.write("\n==============================\n")
        self.terminal.write(f"Running: {editor.filepath}\n")
        self.terminal.write("==============================\n")

        try:
            process = subprocess.run(
                [sys.executable, str(editor.filepath)],
                capture_output=True,
                text=True,
                check=False,
            )
        except OSError as error:
            self.terminal.write(f"ERROR: {error}\n")
            return

        if process.stdout:
            self.terminal.write(process.stdout)
        if process.stderr:
            self.terminal.write(process.stderr)

        self.terminal.write("\nExecution Finished.\n\n")
