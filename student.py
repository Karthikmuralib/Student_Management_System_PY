"""
Student management module for Student Management System.
Provides student add, update, delete, search, and list operations.
"""

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

from database import Database
from utils import validate_non_empty, show_info, show_error


class StudentManagement:
    def __init__(self, parent):
        self.parent = parent
        self.db = Database()
        self.window = tk.Toplevel(parent)
        self.window.title("Student Management")
        self.window.geometry("1150x680")
        self.window.configure(bg="#f5f7fb")

        self.search_var = tk.StringVar()
        self.search_by_var = tk.StringVar(value="Roll Number")
        self.student_data = None

        self.setup_ui()
        self.load_students()

    def setup_ui(self):
        header = tk.Label(
            self.window,
            text="Student Management",
            font=("Arial", 18, "bold"),
            bg="#f5f7fb",
            fg="#1a3f66",
        )
        header.pack(pady=10)

        search_frame = tk.Frame(self.window, bg="#f5f7fb")
        search_frame.pack(fill=tk.X, padx=20, pady=8)

        ttk.Label(search_frame, text="Search by:").grid(row=0, column=0, padx=5, pady=5)
        search_options = ["Roll Number", "Name", "Department", "Semester"]
        ttk.Combobox(search_frame, values=search_options, textvariable=self.search_by_var, state="readonly").grid(
            row=0, column=1, padx=5, pady=5
        )
        ttk.Entry(search_frame, textvariable=self.search_var, width=30).grid(row=0, column=2, padx=5, pady=5)
        tk.Button(
            search_frame,
            text="Search",
            command=self.search_students,
            bg="#1976d2",
            fg="#ffffff",
            width=12,
        ).grid(row=0, column=3, padx=5, pady=5)
        tk.Button(
            search_frame,
            text="Reset",
            command=self.load_students,
            bg="#6c757d",
            fg="#ffffff",
            width=12,
        ).grid(row=0, column=4, padx=5, pady=5)

        form_frame = tk.LabelFrame(self.window, text="Student Details", bg="#ffffff", font=("Arial", 12, "bold"))
        form_frame.pack(fill=tk.X, padx=20, pady=10)

        self.roll_no_var = tk.StringVar()
        self.name_var = tk.StringVar()
        self.gender_var = tk.StringVar(value="Male")
        self.dob_var = tk.StringVar()
        self.department_var = tk.StringVar()
        self.year_var = tk.StringVar()
        self.semester_var = tk.StringVar()
        self.email_var = tk.StringVar()
        self.phone_var = tk.StringVar()
        self.address_var = tk.StringVar()
        self.admission_date_var = tk.StringVar()

        field_data = [
            ("Roll Number", self.roll_no_var, 0, 0),
            ("Name", self.name_var, 0, 2),
            ("Gender", self.gender_var, 0, 4),
            ("Date of Birth", self.dob_var, 1, 0),
            ("Department", self.department_var, 1, 2),
            ("Year", self.year_var, 1, 4),
            ("Semester", self.semester_var, 2, 0),
            ("Email", self.email_var, 2, 2),
            ("Phone", self.phone_var, 2, 4),
            ("Address", self.address_var, 3, 0),
            ("Admission Date", self.admission_date_var, 3, 2),
        ]

        for label_text, var, row, col in field_data:
            ttk.Label(form_frame, text=label_text + ":").grid(row=row, column=col, padx=5, pady=6, sticky=tk.W)
            entry = ttk.Entry(form_frame, textvariable=var, width=28)
            entry.grid(row=row, column=col + 1, padx=5, pady=6, sticky=tk.W)

        button_frame = tk.Frame(form_frame, bg="#ffffff")
        button_frame.grid(row=4, column=0, columnspan=6, pady=12)

        tk.Button(button_frame, text="Add Student", command=self.add_student, bg="#2e7d32", fg="#ffffff", width=14).grid(
            row=0, column=0, padx=6
        )
        tk.Button(button_frame, text="Update Student", command=self.update_student, bg="#0d47a1", fg="#ffffff", width=14).grid(
            row=0, column=1, padx=6
        )
        tk.Button(button_frame, text="Delete Student", command=self.delete_student, bg="#c62828", fg="#ffffff", width=14).grid(
            row=0, column=2, padx=6
        )
        tk.Button(button_frame, text="Clear Fields", command=self.clear_fields, bg="#6c757d", fg="#ffffff", width=14).grid(
            row=0, column=3, padx=6
        )

        table_frame = tk.Frame(self.window, bg="#f5f7fb")
        table_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        columns = (
            "student_id",
            "roll_no",
            "name",
            "gender",
            "dob",
            "department",
            "year",
            "semester",
            "email",
            "phone",
            "address",
            "admission_date",
        )
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")
        for col in columns:
            self.tree.heading(col, text=col.replace("_", " ").title())
            self.tree.column(col, width=100, anchor=tk.CENTER)

        scrollbar_y = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar_x = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscroll=scrollbar_y.set, xscroll=scrollbar_x.set)
        self.tree.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)

        self.tree.bind("<ButtonRelease-1>", self.on_tree_select)

    def load_students(self):
        """Load all student records into the Treeview."""
        try:
            records = self.db.execute_read_query("SELECT * FROM students ORDER BY student_id DESC")
            self.populate_tree(records)
            self.clear_fields()
        except Exception as error:
            show_error(f"Unable to load student data: {error}")

    def populate_tree(self, records):
        """Populate Treeview with provided records."""
        for row in self.tree.get_children():
            self.tree.delete(row)
        for record in records:
            self.tree.insert(
                "",
                tk.END,
                values=(
                    record["student_id"],
                    record["roll_no"],
                    record["name"],
                    record["gender"],
                    record["dob"],
                    record["department"],
                    record["year"],
                    record["semester"],
                    record["email"],
                    record["phone"],
                    record["address"],
                    record["admission_date"],
                ),
            )

    def on_tree_select(self, event):
        """Handle selecting a student row and populate form fields."""
        selected_item = self.tree.focus()
        if selected_item:
            item_values = self.tree.item(selected_item, "values")
            if item_values:
                self.student_data = item_values
                self.roll_no_var.set(item_values[1])
                self.name_var.set(item_values[2])
                self.gender_var.set(item_values[3])
                self.dob_var.set(item_values[4])
                self.department_var.set(item_values[5])
                self.year_var.set(item_values[6])
                self.semester_var.set(item_values[7])
                self.email_var.set(item_values[8])
                self.phone_var.set(item_values[9])
                self.address_var.set(item_values[10])
                self.admission_date_var.set(item_values[11])

    def add_student(self):
        """Add a new student record to the database."""
        if not self.validate_fields():
            return

        try:
            existing_roll = self.db.execute_read_one(
                "SELECT student_id FROM students WHERE roll_no = %s", (self.roll_no_var.get().strip(),)
            )
            if existing_roll:
                show_warning("Duplicate roll number found. Please use a unique roll number.")
                return
            self.db.execute_query(
                "INSERT INTO students (roll_no, name, gender, dob, department, year, semester, email, phone, address, admission_date) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (
                    self.roll_no_var.get().strip(),
                    self.name_var.get().strip(),
                    self.gender_var.get().strip(),
                    self.dob_var.get().strip(),
                    self.department_var.get().strip(),
                    int(self.year_var.get().strip()),
                    int(self.semester_var.get().strip()),
                    self.email_var.get().strip(),
                    self.phone_var.get().strip(),
                    self.address_var.get().strip(),
                    self.admission_date_var.get().strip(),
                ),
            )
            show_info("Student added successfully.")
            self.load_students()
        except Exception as error:
            show_error(f"Failed to add student: {error}")

    def update_student(self):
        """Update the selected student record."""
        if not self.student_data:
            show_warning("Please select a student record to update.")
            return
        if not self.validate_fields():
            return

        student_id = self.student_data[0]
        try:
            self.db.execute_query(
                "UPDATE students SET roll_no=%s, name=%s, gender=%s, dob=%s, department=%s, year=%s, semester=%s, email=%s, phone=%s, address=%s, admission_date=%s WHERE student_id=%s",
                (
                    self.roll_no_var.get().strip(),
                    self.name_var.get().strip(),
                    self.gender_var.get().strip(),
                    self.dob_var.get().strip(),
                    self.department_var.get().strip(),
                    int(self.year_var.get().strip()),
                    int(self.semester_var.get().strip()),
                    self.email_var.get().strip(),
                    self.phone_var.get().strip(),
                    self.address_var.get().strip(),
                    self.admission_date_var.get().strip(),
                    student_id,
                ),
            )
            show_info("Student record updated successfully.")
            self.load_students()
        except Exception as error:
            show_error(f"Failed to update student: {error}")

    def delete_student(self):
        """Delete the selected student record after confirmation."""
        if not self.student_data:
            show_warning("Please select a student record to delete.")
            return

        if not messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this student?"):
            return

        try:
            self.db.execute_query("DELETE FROM students WHERE student_id = %s", (self.student_data[0],))
            show_info("Student deleted successfully.")
            self.load_students()
        except Exception as error:
            show_error(f"Failed to delete student: {error}")

    def search_students(self):
        """Search for students by selected field and search term."""
        value = self.search_var.get().strip()
        if not value:
            show_warning("Please enter a search value.")
            return

        field_map = {
            "Roll Number": "roll_no",
            "Name": "name",
            "Department": "department",
            "Semester": "semester",
        }
        search_field = field_map.get(self.search_by_var.get(), "roll_no")
        query = f"SELECT * FROM students WHERE {search_field} LIKE %s ORDER BY student_id DESC"
        try:
            results = self.db.execute_read_query(query, (f"%{value}%",))
            self.populate_tree(results)
        except Exception as error:
            show_error(f"Search failed: {error}")

    def clear_fields(self):
        """Clear the student form fields."""
        self.student_data = None
        self.roll_no_var.set("")
        self.name_var.set("")
        self.gender_var.set("Male")
        self.dob_var.set("")
        self.department_var.set("")
        self.year_var.set("")
        self.semester_var.set("")
        self.email_var.set("")
        self.phone_var.set("")
        self.address_var.set("")
        self.admission_date_var.set("")

    def validate_fields(self):
        """Validate required student fields before saving."""
        if not validate_non_empty(
            self.roll_no_var.get(),
            self.name_var.get(),
            self.gender_var.get(),
            self.dob_var.get(),
            self.department_var.get(),
            self.year_var.get(),
            self.semester_var.get(),
            self.email_var.get(),
            self.phone_var.get(),
            self.admission_date_var.get(),
        ):
            show_warning("All fields are required except address.")
            return False

        try:
            int(self.year_var.get())
            int(self.semester_var.get())
        except ValueError:
            show_warning("Year and Semester must be valid integers.")
            return False

        return True
