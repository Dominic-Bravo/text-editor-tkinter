"""Application entry point for the Tkinter code editor."""

import tkinter as tk

from ai_coding_ide.app import AICodingIDE


def main() -> None:
    root = tk.Tk()
    AICodingIDE(root)
    root.mainloop()


if __name__ == "__main__":
    main()
