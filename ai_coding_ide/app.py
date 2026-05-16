"""Main application shell."""
# add simple debuggings and loggings
from __future__ import annotations

import tkinter as tk
import shutil
import subprocess
import sys
from pathlib import Path
from tkinter import filedialog, messagebox, simpledialog, ttk

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
        self.create_toolbar()
        self.create_layout()
        self.create_menu()

    def create_toolbar(self) -> None:
        toolbar = ttk.Frame(self.root, style="Toolbar.TFrame", padding=(8, 6))
        toolbar.pack(side="top", fill="x")

        buttons = (
            ("Open Folder", self.open_folder),
            ("Open File", self.open_file_dialog),
            ("Save", self.save_current_file),
            ("Close File", self.close_current_file),
        )

        for label, command in buttons:
            button = ttk.Button(toolbar, text=label, command=command, style="Toolbar.TButton")
            button.pack(side="left", padx=(0, 6))

    def create_layout(self) -> None:
        self.main_pane = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.main_pane.pack(fill="both", expand=True)

        self.sidebar = ttk.Frame(self.main_pane, width=300, style="Dark.TFrame")
        self.main_pane.add(self.sidebar, weight=1)

        self.tree = ttk.Treeview(self.sidebar)
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<Double-1>", self.open_selected_file)
        self.file_tree = FileTree(self.tree)
        self.create_file_tree_context_menu()
        self.tree.bind("<Button-3>", self.show_file_tree_context_menu)

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
        file_menu.add_command(label="Save", command=self.save_current_file)
        file_menu.add_command(label="Close File", command=self.close_current_file)
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

    def create_file_tree_context_menu(self) -> None:
        self.file_tree_menu_indexes = {
            "open": 0,
            "copy_path": 2,
            "rename": 7,
            "delete": 8,
        }
        self.file_tree_menu = self.create_dark_menu(self.root)
        self.file_tree_menu.add_command(label="Open", command=self.open_selected_file)
        self.file_tree_menu.add_separator()
        self.file_tree_menu.add_command(label="Copy Path", command=self.copy_selected_item_path)
        self.file_tree_menu.add_separator()
        self.file_tree_menu.add_command(label="New File", command=self.create_file)
        self.file_tree_menu.add_command(label="New Folder", command=self.create_folder)
        self.file_tree_menu.add_separator()
        self.file_tree_menu.add_command(label="Rename", command=self.rename_selected_item)
        self.file_tree_menu.add_command(label="Delete", command=self.delete_selected_item)

    def show_file_tree_context_menu(self, event: tk.Event) -> None:
        item_id = self.tree.identify_row(event.y)
        if not item_id:
            return

        self.tree.selection_set(item_id)
        selected_path = self.file_tree.selected_item_path()
        if not selected_path:
            return

        can_open = selected_path.is_file()
        can_modify = selected_path != self.file_tree.root_path

        self.file_tree_menu.entryconfigure(
            self.file_tree_menu_indexes["open"],
            state="normal" if can_open else "disabled",
        )
        self.file_tree_menu.entryconfigure(
            self.file_tree_menu_indexes["rename"],
            state="normal" if can_modify else "disabled",
        )
        self.file_tree_menu.entryconfigure(
            self.file_tree_menu_indexes["delete"],
            state="normal" if can_modify else "disabled",
        )

        self.file_tree_menu.tk_popup(event.x_root, event.y_root)
        self.file_tree_menu.grab_release()

    def copy_selected_item_path(self) -> None:
        selected_path = self.file_tree.selected_item_path()
        if not selected_path:
            return

        path_text = str(selected_path.resolve())
        self.root.clipboard_clear()
        self.root.clipboard_append(path_text)
        self.terminal.write(f"Copied path: {path_text}\n")

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

    def create_file(self) -> None:
        target_directory = self.file_tree.selected_directory()
        if not target_directory:
            self.new_file()
            return

        filename = simpledialog.askstring("New File", "File name:")
        if not filename:
            return

        filepath = target_directory / filename
        if filepath.exists():
            messagebox.showwarning("Warning", "A file or folder with that name already exists.")
            return

        try:
            filepath.touch()
        except OSError as error:
            messagebox.showerror("Error", str(error))
            return

        self.file_tree.refresh()
        self.open_file(filepath)
        self.terminal.write(f"Created file: {filepath}\n")

    def create_folder(self) -> None:
        target_directory = self.file_tree.selected_directory()
        if not target_directory:
            messagebox.showwarning("Warning", "Open a folder first.")
            return

        folder_name = simpledialog.askstring("New Folder", "Folder name:")
        if not folder_name:
            return

        folder_path = target_directory / folder_name
        if folder_path.exists():
            messagebox.showwarning("Warning", "A file or folder with that name already exists.")
            return

        try:
            folder_path.mkdir()
        except OSError as error:
            messagebox.showerror("Error", str(error))
            return

        self.file_tree.refresh()
        self.terminal.write(f"Created folder: {folder_path}\n")

    def rename_selected_item(self) -> None:
        selected_path = self.get_selected_project_item("rename")
        if not selected_path:
            return

        new_name = simpledialog.askstring(
            "Rename",
            "New name:",
            initialvalue=selected_path.name,
        )
        if not new_name or new_name == selected_path.name:
            return

        if not self.is_valid_item_name(new_name):
            messagebox.showwarning("Warning", "Use a simple file or folder name.")
            return

        new_path = selected_path.with_name(new_name)
        if new_path.exists():
            messagebox.showwarning("Warning", "A file or folder with that name already exists.")
            return

        try:
            selected_path.rename(new_path)
        except OSError as error:
            messagebox.showerror("Error", str(error))
            return

        self.update_open_editor_paths(selected_path, new_path)
        self.file_tree.refresh()
        self.terminal.write(f"Renamed: {selected_path} -> {new_path}\n")

    def delete_selected_item(self) -> None:
        selected_path = self.get_selected_project_item("delete")
        if not selected_path:
            return

        item_type = "folder" if selected_path.is_dir() else "file"
        confirmed = messagebox.askyesno(
            "Confirm Delete",
            f"Delete this {item_type}?\n\n{selected_path}",
        )
        if not confirmed:
            return

        try:
            if selected_path.is_dir():
                shutil.rmtree(selected_path)
            else:
                selected_path.unlink()
        except OSError as error:
            messagebox.showerror("Error", str(error))
            return

        self.close_editors_for_path(selected_path)
        self.file_tree.refresh()
        self.terminal.write(f"Deleted {item_type}: {selected_path}\n")

    def get_selected_project_item(self, action: str) -> Path | None:
        selected_path = self.file_tree.selected_item_path()
        if not selected_path:
            messagebox.showwarning("Warning", f"Select a file or folder to {action}.")
            return None

        if selected_path == self.file_tree.root_path:
            messagebox.showwarning("Warning", f"Cannot {action} the opened project root.")
            return None

        return selected_path

    def is_valid_item_name(self, name: str) -> bool:
        return name.strip() == name and name not in {"", ".", ".."} and "/" not in name and "\\" not in name

    def open_file(self, filepath: str | Path) -> None:
        path = Path(filepath).resolve()

        if self.select_open_editor(path):
            self.terminal.write(f"Focused: {path}\n")
            return

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

    def select_open_editor(self, filepath: Path) -> bool:
        for editor in self.get_open_editors():
            if editor.filepath and editor.filepath.resolve() == filepath:
                self.notebook.select(editor)
                editor.text.focus_set()
                return True

        return False

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
            editor.filepath = Path(filepath).resolve()

        try:
            editor.filepath.write_text(editor.get_content(), encoding="utf-8")
        except OSError as error:
            messagebox.showerror("Error", str(error))
            return False

        self.notebook.tab(editor, text=editor.display_name)
        self.terminal.write(f"Saved: {editor.filepath}\n")
        return True

    def close_current_file(self) -> None:
        current = self.notebook.select()
        if not current:
            return

        editor = self.get_current_editor()
        display_name = editor.display_name if editor else "file"
        self.notebook.forget(current)
        self.terminal.write(f"Closed: {display_name}\n")

    def update_open_editor_paths(self, old_path: Path, new_path: Path) -> None:
        for editor in self.get_open_editors():
            if not editor.filepath:
                continue

            if editor.filepath == old_path:
                editor.filepath = new_path.resolve()
            elif self.is_inside_path(editor.filepath, old_path):
                editor.filepath = (new_path / editor.filepath.relative_to(old_path)).resolve()
            else:
                continue

            self.notebook.tab(editor, text=editor.display_name)

    def close_editors_for_path(self, deleted_path: Path) -> None:
        for editor in self.get_open_editors():
            if not editor.filepath:
                continue

            if editor.filepath == deleted_path or self.is_inside_path(editor.filepath, deleted_path):
                self.notebook.forget(editor)

    def get_open_editors(self) -> list[CodeEditor]:
        editors = []
        for tab_id in self.notebook.tabs():
            widget = self.notebook.nametowidget(tab_id)
            if isinstance(widget, CodeEditor):
                editors.append(widget)

        return editors

    def is_inside_path(self, path: Path, parent: Path) -> bool:
        try:
            path.relative_to(parent)
        except ValueError:
            return False

        return path != parent

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
