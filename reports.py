"""
Reports module for Student Management System.
Creates student, attendance, marks, fee, and department/semester reports with CSV export support.
"""

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

from database import Database
from utils import export_to_csv, show_error, show_info


class ReportsManagement:
    def __init__(self, parent):
        self.parent = parent
        self.db = Database()
        self.window = tk.Toplevel(parent)
        self.window.title("Reports")
        self.window.geometry("1080x650")
        self.window.configure(bg="#eef0f4")

        self.search_var = tk.StringVar()
        self.search_by_var = tk.StringVar(value="Department")

        self.setup_ui()

    def setup_ui(self):
        header = tk.Label(
            self.window,
            text="Reports and Export",
            font=("Arial", 18, "bold"),
            bg="#eef0f4",
            fg="#163c67",
        )
        header.pack(pady=10)

        button_frame = tk.Frame(self.window, bg="#eef0f4")
        button_frame.pack(fill=tk.X, padx=20, pady=10)

        report_buttons = [
            ("Student Report", self.generate_student_report),
            ("Attendance Report", self.generate_attendance_report),
            ("Marks Report", self.generate_marks_report),
            ("Fees Report", self.generate_fees_report),
            ("Department-wise Report", self.generate_department_report),
            ("Semester-wise Report", self.generate_semester_report),
            ("Top Students", self.generate_top_students_report),
            ("Low Attendance", self.generate_low_attendance_report),
            ("Pending Fees", self.generate_pending_fees_report),
        ]

        for idx, (label, command) in enumerate(report_buttons):
            btn = tk.Button(button_frame, text=label, command=command, bg="#1976d2", fg="#ffffff", width=14, height=2)
            btn.grid(row=idx // 3, column=idx % 3, padx=6, pady=6)

    def export_report(self, filename, headers, rows):
        file_path = export_to_csv(filename, headers, rows)
        if file_path:
            show_info(f"Report exported to {file_path}")

    def generate_student_report(self):
        try:
            records = self.db.execute_read_query("SELECT roll_no, name, gender, dob, department, year, semester, email, phone, admission_date FROM students ORDER BY roll_no")
            headers = ["Roll No", "Name", "Gender", "Date of Birth", "Department", "Year", "Semester", "Email", "Phone", "Admission Date"]
            rows = [
                [r["roll_no"], r["name"], r["gender"], r["dob"], r["department"], r["year"], r["semester"], r["email"], r["phone"], r["admission_date"]]
                for r in records
            ]
            self.export_report("student_report.csv", headers, rows)
        except Exception as error:
            show_error(f"Student report error: {error}")

    def generate_attendance_report(self):
        try:
            records = self.db.execute_read_query(
                "SELECT s.roll_no, s.name, a.date, a.status, f.faculty_name FROM attendance a JOIN students s ON a.student_id = s.student_id LEFT JOIN faculty f ON a.faculty_id = f.faculty_id ORDER BY a.date DESC"
            )
            headers = ["Roll No", "Name", "Date", "Status", "Faculty"]
            rows = [[r["roll_no"], r["name"], r["date"], r["status"], r["faculty_name"]] for r in records]
            self.export_report("attendance_report.csv", headers, rows)
        except Exception as error:
            show_error(f"Attendance report error: {error}")

    def generate_marks_report(self):
        try:
            records = self.db.execute_read_query(
                "SELECT s.roll_no, s.name, m.subject, m.internal_marks, m.external_marks, m.total, m.grade, m.semester FROM marks m JOIN students s ON m.student_id = s.student_id ORDER BY m.semester DESC"
            )
            headers = ["Roll No", "Name", "Subject", "Internal Marks", "External Marks", "Total", "Grade", "Semester"]
            rows = [[r["roll_no"], r["name"], r["subject"], r["internal_marks"], r["external_marks"], r["total"], r["grade"], r["semester"]] for r in records]
            self.export_report("marks_report.csv", headers, rows)
        except Exception as error:
            show_error(f"Marks report error: {error}")

    def generate_fees_report(self):
        try:
            records = self.db.execute_read_query(
                "SELECT s.roll_no, s.name, f.total_fee, f.paid_fee, f.remaining_fee, f.payment_date, f.status FROM fees f JOIN students s ON f.student_id = s.student_id ORDER BY f.payment_date DESC"
            )
            headers = ["Roll No", "Name", "Total Fee", "Paid Fee", "Remaining Fee", "Payment Date", "Status"]
            rows = [[r["roll_no"], r["name"], r["total_fee"], r["paid_fee"], r["remaining_fee"], r["payment_date"], r["status"]] for r in records]
            self.export_report("fees_report.csv", headers, rows)
        except Exception as error:
            show_error(f"Fees report error: {error}")

    def generate_department_report(self):
        try:
            records = self.db.execute_read_query(
                "SELECT department, COUNT(*) AS count FROM students GROUP BY department ORDER BY count DESC"
            )
            headers = ["Department", "Student Count"]
            rows = [[r["department"], r["count"]] for r in records]
            self.export_report("department_report.csv", headers, rows)
        except Exception as error:
            show_error(f"Department report error: {error}")

    def generate_semester_report(self):
        try:
            records = self.db.execute_read_query(
                "SELECT semester, COUNT(*) AS count FROM students GROUP BY semester ORDER BY semester"
            )
            headers = ["Semester", "Student Count"]
            rows = [[r["semester"], r["count"]] for r in records]
            self.export_report("semester_report.csv", headers, rows)
        except Exception as error:
            show_error(f"Semester report error: {error}")

    def generate_top_students_report(self):
        try:
            records = self.db.execute_read_query(
                "SELECT s.roll_no, s.name, AVG(m.total) AS average_marks FROM marks m JOIN students s ON m.student_id = s.student_id GROUP BY s.student_id ORDER BY average_marks DESC LIMIT 10"
            )
            headers = ["Roll No", "Name", "Average Marks"]
            rows = [[r["roll_no"], r["name"], round(r["average_marks"], 2)] for r in records]
            self.export_report("top_students_report.csv", headers, rows)
        except Exception as error:
            show_error(f"Top students report error: {error}")

    def generate_low_attendance_report(self):
        try:
            records = self.db.execute_read_query(
                "SELECT s.roll_no, s.name, SUM(a.status = 'Present') AS present_count, COUNT(a.attendance_id) AS total_days, ROUND((SUM(a.status = 'Present') / COUNT(a.attendance_id)) * 100, 2) AS attendance_percentage FROM attendance a JOIN students s ON a.student_id = s.student_id GROUP BY s.student_id HAVING attendance_percentage < 75 ORDER BY attendance_percentage ASC"
            )
            headers = ["Roll No", "Name", "Present Count", "Total Days", "Attendance %"]
            rows = [[r["roll_no"], r["name"], r["present_count"], r["total_days"], r["attendance_percentage"]] for r in records]
            self.export_report("low_attendance_report.csv", headers, rows)
        except Exception as error:
            show_error(f"Low attendance report error: {error}")

    def generate_pending_fees_report(self):
        try:
            records = self.db.execute_read_query(
                "SELECT s.roll_no, s.name, f.total_fee, f.paid_fee, f.remaining_fee, f.status FROM fees f JOIN students s ON f.student_id = s.student_id WHERE f.status != 'Paid' ORDER BY f.remaining_fee DESC"
            )
            headers = ["Roll No", "Name", "Total Fee", "Paid Fee", "Remaining Fee", "Status"]
            rows = [[r["roll_no"], r["name"], r["total_fee"], r["paid_fee"], r["remaining_fee"], r["status"]] for r in records]
            self.export_report("pending_fees_report.csv", headers, rows)
        except Exception as error:
            show_error(f"Pending fees report error: {error}")
