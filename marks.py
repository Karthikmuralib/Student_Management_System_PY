"""
Marks management module for Student Management System.
Handles adding, updating, deleting marks and automatic grade calculation.
"""

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

from database import Database
from utils import calculate_grade, validate_non_empty, show_info, show_warning, show_error


class MarksManagement:
    def __init__(self, parent):
        self.parent = parent
        self.db = Database()
        self.window = tk.Toplevel(parent)
        self.window.title("Marks Management")
        self.window.geometry("1160x670")
        self.window.configure(bg="#eef2f4")

        self.selected_mark = None
        self.search_var = tk.StringVar()
        self.search_by_var = tk.StringVar(value="Roll Number")
        self.student_var = tk.StringVar()
        self.subject_var = tk.StringVar()
        self.internal_var = tk.StringVar()
        self.external_var = tk.StringVar()
        self.semester_var = tk.StringVar()

        self.setup_ui()
        self.load_student_dropdown()
        self.load_marks()

    def setup_ui(self):
        header = tk.Label(
            self.window,
            text="Marks Management",
            font=("Arial", 18, "bold"),
            bg="#eef2f4",
            fg="#153d62",
        )
        header.pack(pady=10)

        search_frame = tk.Frame(self.window, bg="#eef2f4")
        search_frame.pack(fill=tk.X, padx=20, pady=8)

        ttk.Label(search_frame, text="Search by:").grid(row=0, column=0, padx=5, pady=5)
        ttk.Combobox(
            search_frame,
            values=["Roll Number", "Subject", "Semester"],
            textvariable=self.search_by_var,
            state="readonly",
            width=15,
        ).grid(row=0, column=1, padx=5, pady=5)
        ttk.Entry(search_frame, textvariable=self.search_var, width=30).grid(row=0, column=2, padx=5, pady=5)
        tk.Button(search_frame, text="Search", command=self.search_marks, bg="#1976d2", fg="#ffffff", width=12).grid(
            row=0, column=3, padx=5, pady=5
        )
        tk.Button(search_frame, text="Reset", command=self.load_marks, bg="#6c757d", fg="#ffffff", width=12).grid(
            row=0, column=4, padx=5, pady=5
        )

        form_frame = tk.LabelFrame(self.window, text="Marks Details", bg="#ffffff", font=("Arial", 12, "bold"))
        form_frame.pack(fill=tk.X, padx=20, pady=10)

        labels = ["Student Roll", "Subject", "Internal Marks", "External Marks", "Semester"]
        vars = [self.student_var, self.subject_var, self.internal_var, self.external_var, self.semester_var]

        for idx, (label_text, var) in enumerate(zip(labels, vars)):
            row = idx // 3
            col = (idx % 3) * 2
            ttk.Label(form_frame, text=label_text + ":").grid(row=row, column=col, padx=5, pady=8, sticky=tk.W)
            ttk.Entry(form_frame, textvariable=var, width=30).grid(row=row, column=col + 1, padx=5, pady=8, sticky=tk.W)

        button_frame = tk.Frame(form_frame, bg="#ffffff")
        button_frame.grid(row=2, column=0, columnspan=6, pady=12)

        tk.Button(button_frame, text="Add Marks", command=self.add_marks, bg="#2e7d32", fg="#ffffff", width=14).grid(
            row=0, column=0, padx=6
        )
        tk.Button(button_frame, text="Update Marks", command=self.update_marks, bg="#0d47a1", fg="#ffffff", width=14).grid(
            row=0, column=1, padx=6
        )
        tk.Button(button_frame, text="Delete Marks", command=self.delete_marks, bg="#c62828", fg="#ffffff", width=14).grid(
            row=0, column=2, padx=6
        )
        tk.Button(button_frame, text="Clear Fields", command=self.clear_fields, bg="#6c757d", fg="#ffffff", width=14).grid(
            row=0, column=3, padx=6
        )

        table_frame = tk.Frame(self.window, bg="#eef2f4")
        table_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        columns = ("mark_id", "student_id", "roll_no", "subject", "internal_marks", "external_marks", "total", "grade", "semester")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")
        for col in columns:
            self.tree.heading(col, text=col.replace("_", " ").title())
            self.tree.column(col, width=120, anchor=tk.CENTER)

        scrollbar_y = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar_x = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscroll=scrollbar_y.set, xscroll=scrollbar_x.set)
        self.tree.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)

        self.tree.bind("<ButtonRelease-1>", self.on_tree_select)

    def load_student_dropdown(self):
        """Load student roll numbers for mark entry."""
        try:
            students = self.db.execute_read_query("SELECT student_id, roll_no FROM students ORDER BY roll_no")
            self.student_mapping = {item["roll_no"]: item["student_id"] for item in students}
        except Exception as error:
            show_error(f"Failed to load students: {error}")

    def load_marks(self):
        """Populate the marks table."""
        try:
            records = self.db.execute_read_query(
                "SELECT m.mark_id, m.student_id, s.roll_no, m.subject, m.internal_marks, m.external_marks, m.total, m.grade, m.semester FROM marks m JOIN students s ON m.student_id = s.student_id ORDER BY m.mark_id DESC"
            )
            self.populate_tree(records)
            self.clear_fields()
        except Exception as error:
            show_error(f"Unable to load marks: {error}")

    def populate_tree(self, records):
        """Populate Treeview with marks records."""
        for row in self.tree.get_children():
            self.tree.delete(row)
        for record in records:
            self.tree.insert(
                "",
                tk.END,
                values=(
                    record["mark_id"],
                    record["student_id"],
                    record["roll_no"],
                    record["subject"],
                    record["internal_marks"],
                    record["external_marks"],
                    record["total"],
                    record["grade"],
                    record["semester"],
                ),
            )

    def on_tree_select(self, event):
        """Populate form fields with selected marks record."""
        selected = self.tree.focus()
        if selected:
            values = self.tree.item(selected, "values")
            if values:
                self.selected_mark = values[0]
                self.student_var.set(values[2])
                self.subject_var.set(values[3])
                self.internal_var.set(values[4])
                self.external_var.set(values[5])
                self.semester_var.set(values[8])

    def validate_fields(self):
        """Validate student marks form fields."""
        if not validate_non_empty(self.student_var.get(), self.subject_var.get(), self.internal_var.get(), self.external_var.get(), self.semester_var.get()):
            show_error("All fields are required to record marks.")
            return False
        if self.student_var.get() not in self.student_mapping:
            show_error("Please select a valid student roll number.")
            return False
        try:
            int(self.internal_var.get())
            int(self.external_var.get())
            int(self.semester_var.get())
        except ValueError:
            show_error("Internal, external marks, and semester must be valid integers.")
            return False
        return True

    def add_marks(self):
        """Add new marks record."""
        if not self.validate_fields():
            return
        student_id = self.student_mapping[self.student_var.get()]
        total, percentage, grade = calculate_grade(self.internal_var.get(), self.external_var.get())
        if total is None:
            show_error("Marks must be valid numeric values.")
            return

        try:
            self.db.execute_query(
                "INSERT INTO marks (student_id, subject, internal_marks, external_marks, total, grade, semester) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (
                    student_id,
                    self.subject_var.get().strip(),
                    int(self.internal_var.get().strip()),
                    int(self.external_var.get().strip()),
                    total,
                    grade,
                    int(self.semester_var.get().strip()),
                ),
            )
            show_info(f"Marks recorded successfully. Total: {total}, Grade: {grade}, Percentage: {percentage}%")
            self.load_marks()
        except Exception as error:
            show_error(f"Failed to add marks: {error}")

    def update_marks(self):
        """Update the selected marks record."""
        if not self.selected_mark:
            show_warning("Please select a marks record to update.")
            return
        if not self.validate_fields():
            return

        student_id = self.student_mapping[self.student_var.get()]
        total, percentage, grade = calculate_grade(self.internal_var.get(), self.external_var.get())
        if total is None:
            show_error("Marks must be valid numeric values.")
            return

        try:
            self.db.execute_query(
                "UPDATE marks SET student_id=%s, subject=%s, internal_marks=%s, external_marks=%s, total=%s, grade=%s, semester=%s WHERE mark_id=%s",
                (
                    student_id,
                    self.subject_var.get().strip(),
                    int(self.internal_var.get().strip()),
                    int(self.external_var.get().strip()),
                    total,
                    grade,
                    int(self.semester_var.get().strip()),
                    self.selected_mark,
                ),
            )
            show_info(f"Marks updated successfully. Total: {total}, Grade: {grade}, Percentage: {percentage}%")
            self.load_marks()
        except Exception as error:
            show_error(f"Failed to update marks: {error}")

    def delete_marks(self):
        """Delete the selected marks record."""
        if not self.selected_mark:
            show_warning("Please select a marks record to delete.")
            return
        if not messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this marks record?"):
            return

        try:
            self.db.execute_query("DELETE FROM marks WHERE mark_id = %s", (self.selected_mark,))
            show_info("Marks record deleted successfully.")
            self.load_marks()
        except Exception as error:
            show_error(f"Failed to delete marks: {error}")

    def search_marks(self):
        """Search marks by roll number, subject, or semester."""
        value = self.search_var.get().strip()
        if not value:
            show_warning("Please enter a search value.")
            return
        search_field = self.search_by_var.get()
        if search_field == "Roll Number":
            query = "SELECT m.mark_id, m.student_id, s.roll_no, m.subject, m.internal_marks, m.external_marks, m.total, m.grade, m.semester FROM marks m JOIN students s ON m.student_id = s.student_id WHERE s.roll_no LIKE %s ORDER BY m.mark_id DESC"
        elif search_field == "Subject":
            query = "SELECT m.mark_id, m.student_id, s.roll_no, m.subject, m.internal_marks, m.external_marks, m.total, m.grade, m.semester FROM marks m JOIN students s ON m.student_id = s.student_id WHERE m.subject LIKE %s ORDER BY m.mark_id DESC"
        else:
            query = "SELECT m.mark_id, m.student_id, s.roll_no, m.subject, m.internal_marks, m.external_marks, m.total, m.grade, m.semester FROM marks m JOIN students s ON m.student_id = s.student_id WHERE m.semester = %s ORDER BY m.mark_id DESC"

        try:
            records = self.db.execute_read_query(query, (f"%{value}%",) if search_field != "Semester" else (value,))
            self.populate_tree(records)
        except Exception as error:
            show_error(f"Search failed: {error}")

    def clear_fields(self):
        """Clear form inputs."""
        self.selected_mark = None
        self.student_var.set("")
        self.subject_var.set("")
        self.internal_var.set("")
        self.external_var.set("")
        self.semester_var.set("")
