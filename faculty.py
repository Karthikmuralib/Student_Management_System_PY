"""
Faculty management module for Student Management System.
Provides faculty add, update, delete, and search operations.
"""

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

from database import Database
from utils import validate_non_empty, show_info, show_warning, show_error


class FacultyManagement:
    def __init__(self, parent):
        self.parent = parent
        self.db = Database()
        self.window = tk.Toplevel(parent)
        self.window.title("Faculty Management")
        self.window.geometry("1100x650")
        self.window.configure(bg="#f6f8fb")

        self.selected_faculty = None
        self.search_var = tk.StringVar()
        self.search_by_var = tk.StringVar(value="Name")

        self.setup_ui()
        self.load_faculty_list()

    def setup_ui(self):
        header = tk.Label(
            self.window,
            text="Faculty Management",
            font=("Arial", 18, "bold"),
            bg="#f6f8fb",
            fg="#153e6f",
        )
        header.pack(pady=10)

        search_frame = tk.Frame(self.window, bg="#f6f8fb")
        search_frame.pack(fill=tk.X, padx=20, pady=8)

        ttk.Label(search_frame, text="Search by:").grid(row=0, column=0, padx=5, pady=5)
        search_options = ["Name", "Department", "Email"]
        ttk.Combobox(
            search_frame,
            values=search_options,
            textvariable=self.search_by_var,
            state="readonly",
            width=15,
        ).grid(row=0, column=1, padx=5, pady=5)
        ttk.Entry(search_frame, textvariable=self.search_var, width=30).grid(row=0, column=2, padx=5, pady=5)
        tk.Button(
            search_frame,
            text="Search",
            command=self.search_faculty,
            bg="#1976d2",
            fg="#ffffff",
            width=12,
        ).grid(row=0, column=3, padx=5, pady=5)
        tk.Button(
            search_frame,
            text="Reset",
            command=self.load_faculty_list,
            bg="#6c757d",
            fg="#ffffff",
            width=12,
        ).grid(row=0, column=4, padx=5, pady=5)

        form_frame = tk.LabelFrame(self.window, text="Faculty Details", bg="#ffffff", font=("Arial", 12, "bold"))
        form_frame.pack(fill=tk.X, padx=20, pady=10)

        self.name_var = tk.StringVar()
        self.email_var = tk.StringVar()
        self.department_var = tk.StringVar()
        self.phone_var = tk.StringVar()
        self.password_var = tk.StringVar()

        labels = ["Name", "Email", "Department", "Phone", "Password"]
        vars = [self.name_var, self.email_var, self.department_var, self.phone_var, self.password_var]

        for idx, (label_text, var) in enumerate(zip(labels, vars)):
            row = idx // 2
            col = (idx % 2) * 2
            ttk.Label(form_frame, text=label_text + ":").grid(row=row, column=col, padx=5, pady=8, sticky=tk.W)
            ttk.Entry(form_frame, textvariable=var, width=30, show="*" if label_text == "Password" else ""
                         ).grid(row=row, column=col + 1, padx=5, pady=8, sticky=tk.W)

        button_frame = tk.Frame(form_frame, bg="#ffffff")
        button_frame.grid(row=3, column=0, columnspan=4, pady=12)

        tk.Button(button_frame, text="Add Faculty", command=self.add_faculty, bg="#2e7d32", fg="#ffffff", width=14).grid(
            row=0, column=0, padx=6
        )
        tk.Button(button_frame, text="Update Faculty", command=self.update_faculty, bg="#0d47a1", fg="#ffffff", width=14).grid(
            row=0, column=1, padx=6
        )
        tk.Button(button_frame, text="Delete Faculty", command=self.delete_faculty, bg="#c62828", fg="#ffffff", width=14).grid(
            row=0, column=2, padx=6
        )
        tk.Button(button_frame, text="Clear Fields", command=self.clear_fields, bg="#6c757d", fg="#ffffff", width=14).grid(
            row=0, column=3, padx=6
        )

        table_frame = tk.Frame(self.window, bg="#f6f8fb")
        table_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        columns = ("faculty_id", "faculty_name", "email", "department", "phone")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")
        for col in columns:
            self.tree.heading(col, text=col.replace("_", " ").title())
            self.tree.column(col, width=180, anchor=tk.CENTER)

        scrollbar_y = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar_x = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscroll=scrollbar_y.set, xscroll=scrollbar_x.set)
        self.tree.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)

        self.tree.bind("<ButtonRelease-1>", self.on_tree_select)

    def load_faculty_list(self):
        """Load all faculty records into the Treeview."""
        try:
            records = self.db.execute_read_query("SELECT faculty_id, faculty_name, email, department, phone FROM faculty ORDER BY faculty_id DESC")
            self.populate_tree(records)
            self.clear_fields()
        except Exception as error:
            show_error(f"Unable to load faculty records: {error}")

    def populate_tree(self, records):
        """Populate Treeview with faculty records."""
        for row in self.tree.get_children():
            self.tree.delete(row)
        for record in records:
            self.tree.insert(
                "",
                tk.END,
                values=(
                    record["faculty_id"],
                    record["faculty_name"],
                    record["email"],
                    record["department"],
                    record["phone"],
                ),
            )

    def on_tree_select(self, event):
        """Populate faculty detail fields when a row is selected."""
        selected_item = self.tree.focus()
        if selected_item:
            values = self.tree.item(selected_item, "values")
            if values:
                self.selected_faculty = values[0]
                self.name_var.set(values[1])
                self.email_var.set(values[2])
                self.department_var.set(values[3])
                self.phone_var.set(values[4])
                self.password_var.set("")

    def add_faculty(self):
        """Add new faculty record."""
        if not validate_non_empty(
            self.name_var.get(),
            self.email_var.get(),
            self.department_var.get(),
            self.phone_var.get(),
            self.password_var.get(),
        ):
            show_warning("All fields are required for faculty registration.")
            return

        try:
            existing_email = self.db.execute_read_one("SELECT faculty_id FROM faculty WHERE email = %s", (self.email_var.get().strip(),))
            if existing_email:
                show_warning("A faculty member with this email already exists.")
                return

            self.db.execute_query(
                "INSERT INTO faculty (faculty_name, email, department, phone, password) VALUES (%s, %s, %s, %s, %s)",
                (
                    self.name_var.get().strip(),
                    self.email_var.get().strip(),
                    self.department_var.get().strip(),
                    self.phone_var.get().strip(),
                    self.password_var.get().strip(),
                ),
            )
            show_info("Faculty member added successfully.")
            self.load_faculty_list()
        except Exception as error:
            show_error(f"Failed to add faculty: {error}")

    def update_faculty(self):
        """Update the selected faculty record."""
        if not self.selected_faculty:
            show_warning("Please select a faculty record to update.")
            return

        if not validate_non_empty(
            self.name_var.get(),
            self.email_var.get(),
            self.department_var.get(),
            self.phone_var.get(),
        ):
            show_warning("Name, email, department, and phone are required.")
            return

        try:
            password_value = self.password_var.get().strip()
            if password_value:
                update_query = "UPDATE faculty SET faculty_name=%s, email=%s, department=%s, phone=%s, password=%s WHERE faculty_id=%s"
                values = (
                    self.name_var.get().strip(),
                    self.email_var.get().strip(),
                    self.department_var.get().strip(),
                    self.phone_var.get().strip(),
                    password_value,
                    self.selected_faculty,
                )
            else:
                update_query = "UPDATE faculty SET faculty_name=%s, email=%s, department=%s, phone=%s WHERE faculty_id=%s"
                values = (
                    self.name_var.get().strip(),
                    self.email_var.get().strip(),
                    self.department_var.get().strip(),
                    self.phone_var.get().strip(),
                    self.selected_faculty,
                )
            self.db.execute_query(update_query, values)
            show_info("Faculty updated successfully.")
            self.load_faculty_list()
        except Exception as error:
            show_error(f"Failed to update faculty: {error}")

    def delete_faculty(self):
        """Delete the selected faculty record with confirmation."""
        if not self.selected_faculty:
            show_warning("Please select a faculty record to delete.")
            return

        if not messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this faculty member?"):
            return

        try:
            self.db.execute_query("DELETE FROM faculty WHERE faculty_id = %s", (self.selected_faculty,))
            show_info("Faculty member deleted successfully.")
            self.load_faculty_list()
        except Exception as error:
            show_error(f"Failed to delete faculty: {error}")

    def search_faculty(self):
        """Search faculty records by selected field."""
        value = self.search_var.get().strip()
        if not value:
            show_warning("Please enter a search value.")
            return

        field_map = {
            "Name": "faculty_name",
            "Department": "department",
            "Email": "email",
        }
        search_field = field_map.get(self.search_by_var.get(), "faculty_name")
        query = f"SELECT faculty_id, faculty_name, email, department, phone FROM faculty WHERE {search_field} LIKE %s ORDER BY faculty_id DESC"

        try:
            records = self.db.execute_read_query(query, (f"%{value}%",))
            self.populate_tree(records)
        except Exception as error:
            show_error(f"Search failed: {error}")

    def clear_fields(self):
        """Reset the form controls."""
        self.selected_faculty = None
        self.name_var.set("")
        self.email_var.set("")
        self.department_var.set("")
        self.phone_var.set("")
        self.password_var.set("")
