"""Application entry point for the Tkinter code editor."""

import tkinter as tk

from ai_coding_ide.app import AICodingIDE


def main() -> None:
    # root
    root = tk.Tk()
    # imported widget
    AICodingIDE(root)
    
    root.mainloop()

    # soon add front ui and configs


if __name__ == "__main__":
    main()
