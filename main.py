"""
Main launcher for Student Management System.
Starts the login screen and initializes the application.
"""

import tkinter as tk
from login import LoginApp


def main():
    root = tk.Tk()
    LoginApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
