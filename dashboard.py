"""
Dashboard module for Student Management System.
Displays dashboard statistics and navigation buttons.
"""

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

from database import Database
from student import StudentManagement
from faculty import FacultyManagement
from attendance import AttendanceManagement
from marks import MarksManagement
from fees import FeesManagement
from reports import ReportsManagement
from utils import get_current_datetime, show_info


class Dashboard:
    def __init__(self, root, role, user):
        self.root = root
        self.role = role
        self.user = user
        self.db = Database()
        self.root.title("Dashboard - Student Management System")
        self.root.geometry("1240x760")
        self.root.configure(bg="#e8eef5")

        self.setup_ui()
        self.update_statistics()

    def setup_ui(self):
        header_frame = tk.Frame(self.root, bg="#2c3e50", height=90)
        header_frame.pack(fill=tk.X)

        title_label = tk.Label(
            header_frame,
            text="Student Management Dashboard",
            bg="#2c3e50",
            fg="#ffffff",
            font=("Arial", 20, "bold"),
        )
        title_label.place(x=20, y=20)

        role_label = tk.Label(
            header_frame,
            text=f"Logged in as: {self.role}",
            bg="#2c3e50",
            fg="#d1d8e0",
            font=("Arial", 12),
        )
        role_label.place(x=20, y=58)

        time_label = tk.Label(
            header_frame,
            text=f"Current time: {get_current_datetime()}",
            bg="#2c3e50",
            fg="#d1d8e0",
            font=("Arial", 12),
        )
        time_label.place(x=860, y=40)

        button_frame = tk.Frame(self.root, bg="#e8eef5")
        button_frame.pack(fill=tk.X, pady=20, padx=20)

        button_names = [
            ("Student Management", self.open_student_module),
            ("Faculty Management", self.open_faculty_module),
            ("Attendance", self.open_attendance_module),
            ("Marks", self.open_marks_module),
            ("Fees", self.open_fees_module),
            ("Reports", self.open_reports_module),
            ("Logout", self.handle_logout),
        ]

        for index, (text, command) in enumerate(button_names):
            button = tk.Button(
                button_frame,
                text=text,
                command=command,
                bg="#1976d2",
                fg="#ffffff",
                font=("Arial", 11, "bold"),
                width=18,
                height=2,
            )
            button.grid(row=0, column=index, padx=8, pady=10)

        stats_frame = tk.LabelFrame(self.root, text="Key Metrics", bg="#ffffff", font=("Arial", 14, "bold"))
        stats_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        self.stats = {}
        stat_titles = [
            "Total Students",
            "Total Faculty",
            "Students Present Today",
            "Students Absent Today",
            "Pending Fees",
            "Average Marks",
        ]
        for idx, title in enumerate(stat_titles):
            frame = tk.Frame(stats_frame, bg="#f7f9fc", bd=1, relief=tk.RIDGE)
            frame.grid(row=idx // 3, column=idx % 3, padx=10, pady=10, sticky="nsew")
            frame.columnconfigure(0, weight=1)
            frame.rowconfigure(0, weight=1)

            label_title = tk.Label(frame, text=title, font=("Arial", 12, "bold"), bg="#f7f9fc")
            label_title.pack(pady=12)
            value_label = tk.Label(frame, text="Loading...", font=("Arial", 18, "bold"), bg="#f7f9fc", fg="#1c3d6d")
            value_label.pack(pady=10)
            self.stats[title] = value_label

        for idx in range(2):
            stats_frame.rowconfigure(idx, weight=1)
        for idx in range(3):
            stats_frame.columnconfigure(idx, weight=1)

    def update_statistics(self):
        """Retrieve and display the most recent dashboard statistics."""
        try:
            total_students = self.db.execute_read_query("SELECT COUNT(*) AS count FROM students")[0]["count"]
            total_faculty = self.db.execute_read_query("SELECT COUNT(*) AS count FROM faculty")[0]["count"]
            present_today = self.db.execute_read_query(
                "SELECT COUNT(*) AS count FROM attendance WHERE date = CURDATE() AND status = 'Present'"
            )[0]["count"]
            absent_today = self.db.execute_read_query(
                "SELECT COUNT(*) AS count FROM attendance WHERE date = CURDATE() AND status = 'Absent'"
            )[0]["count"]
            pending_fees = self.db.execute_read_query(
                "SELECT COUNT(*) AS count FROM fees WHERE status != 'Paid'"
            )[0]["count"]
            average_marks_result = self.db.execute_read_query(
                "SELECT AVG(total) AS average FROM marks"
            )[0]["average"]
            average_marks = round(average_marks_result or 0, 2)

            self.stats["Total Students"].config(text=total_students)
            self.stats["Total Faculty"].config(text=total_faculty)
            self.stats["Students Present Today"].config(text=present_today)
            self.stats["Students Absent Today"].config(text=absent_today)
            self.stats["Pending Fees"].config(text=pending_fees)
            self.stats["Average Marks"].config(text=average_marks)
        except Exception as error:
            messagebox.showerror("Dashboard Error", f"Unable to load statistics: {error}")

    def open_student_module(self):
        StudentManagement(self.root)

    def open_faculty_module(self):
        FacultyManagement(self.root)

    def open_attendance_module(self):
        AttendanceManagement(self.root)

    def open_marks_module(self):
        MarksManagement(self.root)

    def open_fees_module(self):
        FeesManagement(self.root)

    def open_reports_module(self):
        ReportsManagement(self.root)

    def handle_logout(self):
        if messagebox.askyesno("Logout", "Do you want to logout?"):
            self.root.destroy()
            from login import launch_login

            launch_login()
