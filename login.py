"""
Login module for Student Management System.
Handles admin and faculty authentication using Tkinter GUI.
"""

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

from database import Database
from dashboard import Dashboard
from utils import show_error, show_info


class LoginApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Login - Student Management System")
        self.root.geometry("500x420")
        self.root.configure(bg="#eef2f7")
        self.db = Database()

        self.current_user = None
        self.login_role = tk.StringVar(value="Admin")
        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()

        self.setup_ui()

    def setup_ui(self):
        """Create login screen controls."""
        header = tk.Label(
            self.root,
            text="Welcome to Student Management System",
            font=("Arial", 16, "bold"),
            bg="#eef2f7",
            fg="#1f4e79",
        )
        header.pack(pady=20)

        frame = ttk.Frame(self.root, padding=20)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        ttk.Label(frame, text="Login Role:").grid(row=0, column=0, sticky=tk.W, pady=8)
        role_menu = ttk.Combobox(
            frame,
            textvariable=self.login_role,
            values=["Admin", "Faculty"],
            state="readonly",
        )
        role_menu.grid(row=0, column=1, pady=8, sticky=tk.EW)

        ttk.Label(frame, text="Username:").grid(row=1, column=0, sticky=tk.W, pady=8)
        ttk.Entry(frame, textvariable=self.username_var).grid(row=1, column=1, pady=8, sticky=tk.EW)

        ttk.Label(frame, text="Password:").grid(row=2, column=0, sticky=tk.W, pady=8)
        ttk.Entry(frame, textvariable=self.password_var, show="*").grid(row=2, column=1, pady=8, sticky=tk.EW)

        self.error_label = tk.Label(frame, text="", fg="red", bg="#f0f0f0")
        self.error_label.grid(row=3, column=0, columnspan=2, pady=5)

        login_button = tk.Button(
            frame,
            text="Login",
            command=self.handle_login,
            bg="#1976d2",
            fg="#ffffff",
            font=("Arial", 11, "bold"),
        )
        login_button.grid(row=4, column=0, columnspan=2, pady=20, sticky=tk.EW)

        frame.columnconfigure(1, weight=1)

        footer = tk.Label(
            self.root,
            text="Enter admin or faculty credentials to continue.",
            bg="#eef2f7",
            fg="#4f5d75",
        )
        footer.pack(pady=10)

    def handle_login(self):
        """Validate credentials and navigate to dashboard."""
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()
        role = self.login_role.get()

        if not username or not password:
            self.error_label.config(text="Username and password cannot be empty.")
            return

        try:
            if role == "Admin":
                query = "SELECT * FROM admin WHERE username = %s AND password = %s"
            else:
                query = "SELECT * FROM faculty WHERE email = %s AND password = %s"

            user = self.db.execute_read_one(query, (username, password))
            if user:
                self.current_user = user
                self.open_dashboard(role)
            else:
                self.error_label.config(text="Invalid credentials. Please try again.")
        except Exception as error:
            show_error(f"Login error: {error}")

    def open_dashboard(self, role):
        """Close login screen and open dashboard."""
        show_info(f"Login successful as {role}.")
        self.root.destroy()
        dashboard_root = tk.Tk()
        Dashboard(dashboard_root, role, self.current_user)
        dashboard_root.mainloop()


def launch_login():
    root = tk.Tk()
    LoginApp(root)
    root.mainloop()
