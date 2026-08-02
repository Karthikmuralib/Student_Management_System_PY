"""
Attendance module for Student Management System.
Handles student attendance marking, updating, and reporting.
"""

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from datetime import datetime

from database import Database
from utils import validate_non_empty, show_info, show_warning, show_error


class AttendanceManagement:
    def __init__(self, parent):
        self.parent = parent
        self.db = Database()
        self.window = tk.Toplevel(parent)
        self.window.title("Attendance Management")
        self.window.geometry("1120x660")
        self.window.configure(bg="#f4f7fb")

        self.selected_attendance = None
        self.search_var = tk.StringVar()
        self.search_by_var = tk.StringVar(value="Roll Number")
        self.attendance_date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        self.status_var = tk.StringVar(value="Present")

        self.setup_ui()
        self.load_attendance_records()
        self.load_student_dropdown()
        self.load_faculty_dropdown()

    def setup_ui(self):
        header = tk.Label(
            self.window,
            text="Attendance Management",
            font=("Arial", 18, "bold"),
            bg="#f4f7fb",
            fg="#1f3f66",
        )
        header.pack(pady=10)

        top_frame = tk.Frame(self.window, bg="#f4f7fb")
        top_frame.pack(fill=tk.X, padx=20, pady=8)

        ttk.Label(top_frame, text="Search by:").grid(row=0, column=0, padx=5, pady=5)
        ttk.Combobox(
            top_frame,
            values=["Roll Number", "Name", "Date"],
            textvariable=self.search_by_var,
            state="readonly",
            width=14,
        ).grid(row=0, column=1, padx=5, pady=5)
        ttk.Entry(top_frame, textvariable=self.search_var, width=28).grid(row=0, column=2, padx=5, pady=5)
        tk.Button(top_frame, text="Search", command=self.search_attendance, bg="#1976d2", fg="#ffffff", width=12).grid(
            row=0, column=3, padx=5, pady=5
        )
        tk.Button(top_frame, text="Reset", command=self.load_attendance_records, bg="#6c757d", fg="#ffffff", width=12).grid(
            row=0, column=4, padx=5, pady=5
        )

        form_frame = tk.LabelFrame(self.window, text="Attendance Details", bg="#ffffff", font=("Arial", 12, "bold"))
        form_frame.pack(fill=tk.X, padx=20, pady=10)

        self.student_var = tk.StringVar()
        self.faculty_var = tk.StringVar()

        labels = ["Student Roll","Date","Status","Faculty"]
        widget_vars = [self.student_var, self.attendance_date_var, self.status_var, self.faculty_var]

        for idx, (label_text, var) in enumerate(zip(labels, widget_vars)):
            ttk.Label(form_frame, text=label_text + ":").grid(row=idx // 2, column=(idx % 2) * 2, padx=5, pady=8, sticky=tk.W)
            if label_text == "Status":
                ttk.Combobox(form_frame, values=["Present","Absent"], textvariable=var, state="readonly", width=28).grid(
                    row=idx // 2, column=(idx % 2) * 2 + 1, padx=5, pady=8, sticky=tk.W
                )
            else:
                ttk.Entry(form_frame, textvariable=var, width=30).grid(row=idx // 2, column=(idx % 2) * 2 + 1, padx=5, pady=8, sticky=tk.W)

        button_frame = tk.Frame(form_frame, bg="#ffffff")
        button_frame.grid(row=2, column=0, columnspan=4, pady=12)

        tk.Button(button_frame, text="Mark Attendance", command=self.mark_attendance, bg="#2e7d32", fg="#ffffff", width=16).grid(
            row=0, column=0, padx=6
        )
        tk.Button(button_frame, text="Update Attendance", command=self.update_attendance, bg="#0d47a1", fg="#ffffff", width=16).grid(
            row=0, column=1, padx=6
        )
        tk.Button(button_frame, text="View Report", command=self.open_attendance_report, bg="#4b2e83", fg="#ffffff", width=16).grid(
            row=0, column=2, padx=6
        )
        tk.Button(button_frame, text="Clear Fields", command=self.clear_fields, bg="#6c757d", fg="#ffffff", width=16).grid(
            row=0, column=3, padx=6
        )

        table_frame = tk.Frame(self.window, bg="#f4f7fb")
        table_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        columns = ("attendance_id", "student_id", "student_roll", "date", "status", "faculty_name")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")
        for col in columns:
            heading = col.replace("_", " ").title()
            self.tree.heading(col, text=heading)
            self.tree.column(col, width=140, anchor=tk.CENTER)

        scrollbar_y = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar_x = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscroll=scrollbar_y.set, xscroll=scrollbar_x.set)
        self.tree.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)

        self.tree.bind("<ButtonRelease-1>", self.on_tree_select)

    def load_student_dropdown(self):
        """Load student roll numbers and IDs for attendance selection."""
        try:
            students = self.db.execute_read_query("SELECT student_id, roll_no FROM students ORDER BY roll_no")
            self.student_mapping = {f"{item['roll_no']}": item['student_id'] for item in students}
        except Exception as error:
            show_error(f"Unable to load students: {error}")

    def load_faculty_dropdown(self):
        """Load faculty names for attendance assignment."""
        try:
            faculty_records = self.db.execute_read_query("SELECT faculty_id, faculty_name FROM faculty ORDER BY faculty_name")
            self.faculty_mapping = {item['faculty_name']: item['faculty_id'] for item in faculty_records}
        except Exception as error:
            show_error(f"Unable to load faculty list: {error}")

    def load_attendance_records(self):
        """Load attendance records into the table."""
        try:
            records = self.db.execute_read_query(
                "SELECT a.attendance_id, a.student_id, s.roll_no AS student_roll, a.date, a.status, f.faculty_name FROM attendance a LEFT JOIN students s ON a.student_id = s.student_id LEFT JOIN faculty f ON a.faculty_id = f.faculty_id ORDER BY a.date DESC"
            )
            self.populate_tree(records)
            self.clear_fields()
        except Exception as error:
            show_error(f"Unable to load attendance records: {error}")

    def populate_tree(self, records):
        """Populate attendance table."""
        for row in self.tree.get_children():
            self.tree.delete(row)
        for record in records:
            self.tree.insert(
                "",
                tk.END,
                values=(
                    record["attendance_id"],
                    record["student_id"],
                    record["student_roll"],
                    record["date"],
                    record["status"],
                    record["faculty_name"],
                ),
            )

    def on_tree_select(self, event):
        """Populate attendance form from selected row."""
        selected_item = self.tree.focus()
        if selected_item:
            item_values = self.tree.item(selected_item, "values")
            if item_values:
                self.selected_attendance = item_values[0]
                self.student_var.set(item_values[2])
                self.attendance_date_var.set(item_values[3])
                self.status_var.set(item_values[4])
                self.faculty_var.set(item_values[5] or "")

    def validate_fields(self):
        """Ensure required attendance fields are provided."""
        if not validate_non_empty(self.student_var.get(), self.attendance_date_var.get(), self.status_var.get(), self.faculty_var.get()):
            show_warning("All attendance fields are required.")
            return False
        return True

    def mark_attendance(self):
        """Mark attendance for a student on a selected date."""
        if not self.validate_fields():
            return
        if self.student_var.get() not in self.student_mapping:
            show_warning("Please select a valid student roll number.")
            return
        if self.faculty_var.get() not in self.faculty_mapping:
            show_warning("Please select a valid faculty name.")
            return

        student_id = self.student_mapping[self.student_var.get()]
        faculty_id = self.faculty_mapping[self.faculty_var.get()]

        try:
            self.db.execute_query(
                "INSERT INTO attendance (student_id, date, status, faculty_id) VALUES (%s, %s, %s, %s)",
                (student_id, self.attendance_date_var.get().strip(), self.status_var.get().strip(), faculty_id),
            )
            show_info("Attendance marked successfully.")
            self.load_attendance_records()
        except Exception as error:
            show_error(f"Failed to mark attendance: {error}")

    def update_attendance(self):
        """Update an existing attendance record."""
        if not self.selected_attendance:
            show_warning("Select a record to update.")
            return
        if not self.validate_fields():
            return
        if self.student_var.get() not in self.student_mapping:
            show_warning("Please select a valid student roll number.")
            return
        if self.faculty_var.get() not in self.faculty_mapping:
            show_warning("Please select a valid faculty name.")
            return

        student_id = self.student_mapping[self.student_var.get()]
        faculty_id = self.faculty_mapping[self.faculty_var.get()]

        try:
            self.db.execute_query(
                "UPDATE attendance SET student_id=%s, date=%s, status=%s, faculty_id=%s WHERE attendance_id=%s",
                (student_id, self.attendance_date_var.get().strip(), self.status_var.get().strip(), faculty_id, self.selected_attendance),
            )
            show_info("Attendance updated successfully.")
            self.load_attendance_records()
        except Exception as error:
            show_error(f"Failed to update attendance: {error}")

    def search_attendance(self):
        """Search attendance records by roll number, student name, or date."""
        value = self.search_var.get().strip()
        if not value:
            show_warning("Please enter a search value.")
            return

        search_field = self.search_by_var.get()
        if search_field == "Roll Number":
            query = "SELECT a.attendance_id, a.student_id, s.roll_no AS student_roll, a.date, a.status, f.faculty_name FROM attendance a LEFT JOIN students s ON a.student_id = s.student_id LEFT JOIN faculty f ON a.faculty_id = f.faculty_id WHERE s.roll_no LIKE %s ORDER BY a.date DESC"
        elif search_field == "Name":
            query = "SELECT a.attendance_id, a.student_id, s.roll_no AS student_roll, a.date, a.status, f.faculty_name FROM attendance a LEFT JOIN students s ON a.student_id = s.student_id LEFT JOIN faculty f ON a.faculty_id = f.faculty_id WHERE s.name LIKE %s ORDER BY a.date DESC"
        else:
            query = "SELECT a.attendance_id, a.student_id, s.roll_no AS student_roll, a.date, a.status, f.faculty_name FROM attendance a LEFT JOIN students s ON a.student_id = s.student_id LEFT JOIN faculty f ON a.faculty_id = f.faculty_id WHERE a.date = %s ORDER BY a.date DESC"

        try:
            records = self.db.execute_read_query(query, (f"%{value}%",) if search_field != "Date" else (value,))
            self.populate_tree(records)
        except Exception as error:
            show_error(f"Search failed: {error}")

    def open_attendance_report(self):
        """Show a summary of attendance percentages."""
        try:
            report_data = self.db.execute_read_query(
                "SELECT s.roll_no, s.name, COUNT(CASE WHEN a.status = 'Present' THEN 1 END) AS present_count, COUNT(CASE WHEN a.status = 'Absent' THEN 1 END) AS absent_count, COUNT(a.attendance_id) AS total_days FROM attendance a JOIN students s ON a.student_id = s.student_id GROUP BY s.student_id ORDER BY s.roll_no"
            )
            content = [
                f"Roll No: {row['roll_no']}, Name: {row['name']}, Present: {row['present_count']}, Absent: {row['absent_count']}, Attendance %: {round((row['present_count'] / row['total_days']) * 100, 2) if row['total_days'] else 0}%"
                for row in report_data
            ]
            if content:
                messagebox.showinfo("Attendance Report", "\n".join(content))
            else:
                messagebox.showinfo("Attendance Report", "No attendance records available.")
        except Exception as error:
            show_error(f"Attendance report error: {error}")

    def clear_fields(self):
        """Reset the attendance form fields."""
        self.selected_attendance = None
        self.student_var.set("")
        self.attendance_date_var.set(datetime.now().strftime("%Y-%m-%d"))
        self.status_var.set("Present")
        self.faculty_var.set("")
