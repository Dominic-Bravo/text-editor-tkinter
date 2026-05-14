import keyword
import os
import re
import subprocess
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

# =========================================================
# ADVANCED AI CODING EDITOR
# =========================================================
# FEATURES
# ---------------------------------------------------------
# ✓ File Explorer
# ✓ Multi Tabs
# ✓ Terminal
# ✓ Run Python
# ✓ Save/Open Files
# ✓ Dark Theme
# ✓ Line Numbers
# ✓ Syntax Highlighting
# ✓ Auto Highlight Updates
# ✓ Scrollbars
# ✓ Better Layout
#
# FUTURE IDEAS
# ---------------------------------------------------------
# - AI Chat Panel
# - Streaming AI Tokens
# - Auto Complete
# - Git Integration
# - Diff Viewer
# - Vector Search
# - Agent Task Runner
# =========================================================


class TerminalFrame(ttk.Frame):

    def __init__(self, parent):
        super().__init__(parent)

        self.output = tk.Text(
            self,
            bg="#111111",
            fg="#00ff88",
            insertbackground="white",
            font=("Consolas", 10),
            wrap="word"
        )

        self.output.pack(fill="both", expand=True)

        scrollbar = ttk.Scrollbar(
            self,
            orient="vertical",
            command=self.output.yview
        )

        scrollbar.pack(side="right", fill="y")

        self.output.configure(yscrollcommand=scrollbar.set)

        self.write("Terminal Ready...\n")

    def write(self, text):

        self.output.insert("end", text)
        self.output.see("end")

    def clear(self):

        self.output.delete("1.0", "end")


class CodeEditor(ttk.Frame):

    def __init__(self, parent):
        super().__init__(parent)

        self.filepath = None

        # =====================================================
        # LEFT SIDE - LINE NUMBERS
        # =====================================================

        self.line_numbers = tk.Text(
            self,
            width=5,
            padx=5,
            takefocus=0,
            border=0,
            background="#1b1b1b",
            foreground="#5c6370",
            state="disabled",
            font=("Consolas", 12)
        )

        self.line_numbers.pack(side="left", fill="y")

        # =====================================================
        # MAIN TEXT EDITOR
        # =====================================================

        self.text = tk.Text(
            self,
            wrap="none",
            undo=True,
            bg="#1e1e1e",
            fg="#d4d4d4",
            insertbackground="white",
            selectbackground="#264f78",
            font=("Consolas", 12),
            padx=10,
            pady=10
        )

        self.text.pack(side="left", fill="both", expand=True)

        # =====================================================
        # SCROLLBARS
        # =====================================================

        y_scroll = ttk.Scrollbar(
            self,
            orient="vertical",
            command=self.sync_scroll
        )

        y_scroll.pack(side="right", fill="y")

        x_scroll = ttk.Scrollbar(
            self,
            orient="horizontal",
            command=self.text.xview
        )

        x_scroll.pack(side="bottom", fill="x")

        self.text.configure(
            yscrollcommand=y_scroll.set,
            xscrollcommand=x_scroll.set
        )

        # =====================================================
        # SYNTAX TAG COLORS
        # =====================================================

        self.configure_tags()

        # =====================================================
        # EVENTS
        # =====================================================

        self.text.bind("<KeyRelease>", self.on_key_release)
        self.text.bind("<MouseWheel>", self.update_line_numbers)

        self.update_line_numbers()

    # =====================================================
    # TAG CONFIGURATION
    # =====================================================

    def configure_tags(self):

        # Keywords
        self.text.tag_configure(
            "keyword",
            foreground="#c678dd"
        )

        # Strings
        self.text.tag_configure(
            "string",
            foreground="#98c379"
        )

        # Comments
        self.text.tag_configure(
            "comment",
            foreground="#5c6370"
        )

        # Numbers
        self.text.tag_configure(
            "number",
            foreground="#d19a66"
        )

        # Functions
        self.text.tag_configure(
            "function",
            foreground="#61afef"
        )

        # Class Names
        self.text.tag_configure(
            "class",
            foreground="#e5c07b"
        )

    # =====================================================
    # EVENT HANDLING
    # =====================================================

    def on_key_release(self, event=None):

        self.update_line_numbers()
        self.highlight_syntax()

    # =====================================================
    # LINE NUMBERS
    # =====================================================

    def sync_scroll(self, *args):

        self.text.yview(*args)
        self.line_numbers.yview(*args)

    def update_line_numbers(self, event=None):

        lines = self.text.get("1.0", "end-1c").split("\n")

        line_text = "\n".join(
            str(i + 1)
            for i in range(len(lines))
        )

        self.line_numbers.config(state="normal")

        self.line_numbers.delete("1.0", "end")

        self.line_numbers.insert("1.0", line_text)

        self.line_numbers.config(state="disabled")

    # =====================================================
    # SYNTAX HIGHLIGHTING
    # =====================================================

    def clear_tags(self):

        for tag in self.text.tag_names():

            self.text.tag_remove(
                tag,
                "1.0",
                "end"
            )

    def highlight_pattern(self, pattern, tag):

        start = "1.0"

        while True:

            match = self.text.search(
                pattern,
                start,
                stopindex="end",
                regexp=True
            )

            if not match:
                break

            end = f"{match}+{len(self.text.get(match, f'{match} wordend'))}c"

            self.text.tag_add(tag, match, end)

            start = end

    def highlight_syntax(self):

        self.clear_tags()

        content = self.text.get("1.0", "end-1c")

        # -------------------------------------------------
        # COMMENTS
        # -------------------------------------------------

        for match in re.finditer(r"#.*", content):

            start = f"1.0+{match.start()}c"
            end = f"1.0+{match.end()}c"

            self.text.tag_add("comment", start, end)

        # -------------------------------------------------
        # STRINGS
        # -------------------------------------------------

        string_patterns = [
            r'".*?"',
            r"'.*?'"
        ]

        for pattern in string_patterns:

            for match in re.finditer(pattern, content):

                start = f"1.0+{match.start()}c"
                end = f"1.0+{match.end()}c"

                self.text.tag_add("string", start, end)

        # -------------------------------------------------
        # NUMBERS
        # -------------------------------------------------

        for match in re.finditer(r"\b\d+\b", content):

            start = f"1.0+{match.start()}c"
            end = f"1.0+{match.end()}c"

            self.text.tag_add("number", start, end)

        # -------------------------------------------------
        # KEYWORDS
        # -------------------------------------------------

        for kw in keyword.kwlist:

            pattern = rf"\b{kw}\b"

            start = "1.0"

            while True:

                pos = self.text.search(
                    pattern,
                    start,
                    stopindex="end",
                    regexp=True
                )

                if not pos:
                    break

                end = f"{pos}+{len(kw)}c"

                self.text.tag_add(
                    "keyword",
                    pos,
                    end
                )

                start = end

        # -------------------------------------------------
        # FUNCTIONS
        # -------------------------------------------------

        for match in re.finditer(
            r"def\s+([a-zA-Z_][a-zA-Z0-9_]*)",
            content
        ):

            start = f"1.0+{match.start(1)}c"
            end = f"1.0+{match.end(1)}c"

            self.text.tag_add(
                "function",
                start,
                end
            )

        # -------------------------------------------------
        # CLASSES
        # -------------------------------------------------

        for match in re.finditer(
            r"class\s+([a-zA-Z_][a-zA-Z0-9_]*)",
            content
        ):

            start = f"1.0+{match.start(1)}c"
            end = f"1.0+{match.end(1)}c"

            self.text.tag_add(
                "class",
                start,
                end
            )

    # =====================================================
    # CONTENT HELPERS
    # =====================================================

    def get_content(self):

        return self.text.get("1.0", "end-1c")

    def set_content(self, content):

        self.text.delete("1.0", "end")

        self.text.insert("1.0", content)

        self.update_line_numbers()

        self.highlight_syntax()


class AICodingIDE:

    def __init__(self, root):

        self.root = root

        self.root.title("AI Coding IDE")

        self.root.geometry("1600x900")

        self.setup_theme()

        self.create_layout()

        self.create_menu()

    # =====================================================
    # THEME
    # =====================================================

    def setup_theme(self):

        style = ttk.Style()

        style.theme_use("clam")

        style.configure(
            "Treeview",
            background="#252526",
            foreground="white",
            fieldbackground="#252526",
            rowheight=28
        )

        style.configure(
            "TNotebook",
            background="#1e1e1e"
        )

        style.configure(
            "TNotebook.Tab",
            background="#2d2d2d",
            foreground="white",
            padding=[12, 6]
        )

    # =====================================================
    # MAIN LAYOUT
    # =====================================================

    def create_layout(self):

        # -------------------------------------------------
        # MAIN HORIZONTAL SPLIT
        # -------------------------------------------------

        self.main_pane = ttk.PanedWindow(
            self.root,
            orient=tk.HORIZONTAL
        )

        self.main_pane.pack(fill="both", expand=True)

        # -------------------------------------------------
        # SIDEBAR
        # -------------------------------------------------

        self.sidebar = ttk.Frame(
            self.main_pane,
            width=300
        )

        self.main_pane.add(
            self.sidebar,
            weight=1
        )

        # -------------------------------------------------
        # FILE TREE
        # -------------------------------------------------

        self.tree = ttk.Treeview(
            self.sidebar
        )

        self.tree.pack(fill="both", expand=True)

        self.tree.bind(
            "<Double-1>",
            self.open_selected_file
        )

        # -------------------------------------------------
        # RIGHT SIDE
        # -------------------------------------------------

        self.right_side = ttk.PanedWindow(
            self.main_pane,
            orient=tk.VERTICAL
        )

        self.main_pane.add(
            self.right_side,
            weight=4
        )

        # -------------------------------------------------
        # NOTEBOOK
        # -------------------------------------------------

        self.notebook = ttk.Notebook(
            self.right_side
        )

        self.right_side.add(
            self.notebook,
            weight=4
        )

        # -------------------------------------------------
        # TERMINAL
        # -------------------------------------------------

        self.terminal = TerminalFrame(
            self.right_side
        )

        self.right_side.add(
            self.terminal,
            weight=1
        )

    # =====================================================
    # MENU
    # =====================================================

    def create_menu(self):

        menubar = tk.Menu(self.root)

        # -------------------------------------------------
        # FILE MENU
        # -------------------------------------------------

        file_menu = tk.Menu(
            menubar,
            tearoff=0
        )

        file_menu.add_command(
            label="Open Folder",
            command=self.open_folder
        )

        file_menu.add_command(
            label="Open File",
            command=self.open_file_dialog
        )

        file_menu.add_command(
            label="Save",
            command=self.save_current_file
        )

        file_menu.add_separator()

        file_menu.add_command(
            label="Exit",
            command=self.root.quit
        )

        menubar.add_cascade(
            label="File",
            menu=file_menu
        )

        # -------------------------------------------------
        # RUN MENU
        # -------------------------------------------------

        run_menu = tk.Menu(
            menubar,
            tearoff=0
        )

        run_menu.add_command(
            label="Run Python File",
            command=self.run_current_file
        )

        run_menu.add_command(
            label="Clear Terminal",
            command=self.terminal.clear
        )

        menubar.add_cascade(
            label="Run",
            menu=run_menu
        )

        self.root.config(menu=menubar)

    # =====================================================
    # PROJECT EXPLORER
    # =====================================================

    def open_folder(self):

        folder = filedialog.askdirectory()

        if not folder:
            return

        self.tree.delete(*self.tree.get_children())

        root_node = self.tree.insert(
            "",
            "end",
            text=os.path.basename(folder),
            open=True,
            values=[folder]
        )

        self.load_directory(
            root_node,
            folder
        )

    def load_directory(self, parent, path):

        try:

            for item in os.listdir(path):

                full = os.path.join(
                    path,
                    item
                )

                node = self.tree.insert(
                    parent,
                    "end",
                    text=item,
                    values=[full]
                )

                if os.path.isdir(full):

                    self.load_directory(
                        node,
                        full
                    )

        except PermissionError:
            pass

    # =====================================================
    # FILE OPENING
    # =====================================================

    def open_selected_file(self, event):

        selected = self.tree.selection()

        if not selected:
            return

        node = selected[0]

        filepath = self.tree.item(
            node,
            "values"
        )[0]

        if os.path.isdir(filepath):
            return

        self.open_file(filepath)

    def open_file_dialog(self):

        filepath = filedialog.askopenfilename()

        if filepath:

            self.open_file(filepath)

    def open_file(self, filepath):

        try:

            with open(
                filepath,
                "r",
                encoding="utf-8"
            ) as file:

                content = file.read()

            editor = CodeEditor(
                self.notebook
            )

            editor.filepath = filepath

            editor.set_content(content)

            filename = os.path.basename(
                filepath
            )

            self.notebook.add(
                editor,
                text=filename
            )

            self.notebook.select(editor)

            self.terminal.write(
                f"Opened: {filepath}\n"
            )

        except Exception as e:

            messagebox.showerror(
                "Error",
                str(e)
            )

    # =====================================================
    # SAVE FILE
    # =====================================================

    def get_current_editor(self):

        current = self.notebook.select()

        if not current:
            return None

        return self.notebook.nametowidget(current)

    def save_current_file(self):

        editor = self.get_current_editor()

        if not editor:
            return

        filepath = editor.filepath

        if not filepath:

            filepath = filedialog.asksaveasfilename()

            if not filepath:
                return

            editor.filepath = filepath

        with open(
            filepath,
            "w",
            encoding="utf-8"
        ) as file:

            file.write(
                editor.get_content()
            )

        self.terminal.write(
            f"Saved: {filepath}\n"
        )

    # =====================================================
    # RUN FILE
    # =====================================================

    def run_current_file(self):

        editor = self.get_current_editor()

        if not editor:
            return

        filepath = editor.filepath

        if not filepath:

            messagebox.showwarning(
                "Warning",
                "Save file first."
            )

            return

        self.save_current_file()

        self.terminal.write(
            "\n==============================\n"
        )

        self.terminal.write(
            f"Running: {filepath}\n"
        )

        self.terminal.write(
            "==============================\n"
        )

        try:

            process = subprocess.Popen(
                ["python", filepath],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            stdout, stderr = process.communicate()

            if stdout:
                self.terminal.write(stdout)

            if stderr:
                self.terminal.write(stderr)

            self.terminal.write(
                "\nExecution Finished.\n\n"
            )

        except Exception as e:

            self.terminal.write(
                f"ERROR: {str(e)}\n"
            )


# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":

    root = tk.Tk()

    app = AICodingIDE(root)

    root.mainloop()