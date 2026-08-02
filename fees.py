"""
Fees management module for Student Management System.
Handles fee records, payment updates, balance tracking, and receipt generation.
"""

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from datetime import datetime

from database import Database
from utils import validate_non_empty, show_info, show_error


class FeesManagement:
    def __init__(self, parent):
        self.parent = parent
        self.db = Database()
        self.window = tk.Toplevel(parent)
        self.window.title("Fees Management")
        self.window.geometry("1140x670")
        self.window.configure(bg="#eef2f4")

        self.selected_fee = None
        self.search_var = tk.StringVar()
        self.search_by_var = tk.StringVar(value="Roll Number")
        self.student_var = tk.StringVar()
        self.total_fee_var = tk.StringVar()
        self.paid_fee_var = tk.StringVar()
        self.payment_date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))

        self.setup_ui()
        self.load_student_dropdown()
        self.load_fees()

    def setup_ui(self):
        header = tk.Label(
            self.window,
            text="Fees Management",
            font=("Arial", 18, "bold"),
            bg="#eef2f4",
            fg="#163f62",
        )
        header.pack(pady=10)

        search_frame = tk.Frame(self.window, bg="#eef2f4")
        search_frame.pack(fill=tk.X, padx=20, pady=8)

        ttk.Label(search_frame, text="Search by:").grid(row=0, column=0, padx=5, pady=5)
        ttk.Combobox(
            search_frame,
            values=["Roll Number", "Status"],
            textvariable=self.search_by_var,
            state="readonly",
            width=15,
        ).grid(row=0, column=1, padx=5, pady=5)
        ttk.Entry(search_frame, textvariable=self.search_var, width=30).grid(row=0, column=2, padx=5, pady=5)
        tk.Button(search_frame, text="Search", command=self.search_fees, bg="#1976d2", fg="#ffffff", width=12).grid(
            row=0, column=3, padx=5, pady=5
        )
        tk.Button(search_frame, text="Reset", command=self.load_fees, bg="#6c757d", fg="#ffffff", width=12).grid(
            row=0, column=4, padx=5, pady=5
        )

        form_frame = tk.LabelFrame(self.window, text="Fee Details", bg="#ffffff", font=("Arial", 12, "bold"))
        form_frame.pack(fill=tk.X, padx=20, pady=10)

        labels = ["Student Roll", "Total Fee", "Paid Fee", "Payment Date"]
        vars = [self.student_var, self.total_fee_var, self.paid_fee_var, self.payment_date_var]

        for idx, (label_text, var) in enumerate(zip(labels, vars)):
            row = idx // 2
            col = (idx % 2) * 2
            ttk.Label(form_frame, text=label_text + ":").grid(row=row, column=col, padx=5, pady=8, sticky=tk.W)
            ttk.Entry(form_frame, textvariable=var, width=30).grid(row=row, column=col + 1, padx=5, pady=8, sticky=tk.W)

        button_frame = tk.Frame(form_frame, bg="#ffffff")
        button_frame.grid(row=2, column=0, columnspan=4, pady=12)

        tk.Button(button_frame, text="Add Fee", command=self.add_fee, bg="#2e7d32", fg="#ffffff", width=14).grid(
            row=0, column=0, padx=6
        )
        tk.Button(button_frame, text="Update Payment", command=self.update_payment, bg="#0d47a1", fg="#ffffff", width=14).grid(
            row=0, column=1, padx=6
        )
        tk.Button(button_frame, text="Delete Fee", command=self.delete_fee, bg="#c62828", fg="#ffffff", width=14).grid(
            row=0, column=2, padx=6
        )
        tk.Button(button_frame, text="Clear Fields", command=self.clear_fields, bg="#6c757d", fg="#ffffff", width=14).grid(
            row=0, column=3, padx=6
        )

        table_frame = tk.Frame(self.window, bg="#eef2f4")
        table_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        columns = ("fee_id", "student_id", "roll_no", "total_fee", "paid_fee", "remaining_fee", "payment_date", "status")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")
        for col in columns:
            self.tree.heading(col, text=col.replace("_", " ").title())
            self.tree.column(col, width=140, anchor=tk.CENTER)

        scrollbar_y = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar_x = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscroll=scrollbar_y.set, xscroll=scrollbar_x.set)
        self.tree.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)

        self.tree.bind("<ButtonRelease-1>", self.on_tree_select)

    def load_student_dropdown(self):
        """Load student roll numbers for fee assignment."""
        try:
            students = self.db.execute_read_query("SELECT student_id, roll_no FROM students ORDER BY roll_no")
            self.student_mapping = {item["roll_no"]: item["student_id"] for item in students}
        except Exception as error:
            show_error(f"Unable to load students: {error}")

    def load_fees(self):
        """Load fee records into the table."""
        try:
            records = self.db.execute_read_query(
                "SELECT f.fee_id, f.student_id, s.roll_no, f.total_fee, f.paid_fee, f.remaining_fee, f.payment_date, f.status FROM fees f JOIN students s ON f.student_id = s.student_id ORDER BY f.fee_id DESC"
            )
            self.populate_tree(records)
            self.clear_fields()
        except Exception as error:
            show_error(f"Unable to load fee records: {error}")

    def populate_tree(self, records):
        """Populate fee table records."""
        for row in self.tree.get_children():
            self.tree.delete(row)
        for record in records:
            self.tree.insert(
                "",
                tk.END,
                values=(
                    record["fee_id"],
                    record["student_id"],
                    record["roll_no"],
                    record["total_fee"],
                    record["paid_fee"],
                    record["remaining_fee"],
                    record["payment_date"],
                    record["status"],
                ),
            )

    def on_tree_select(self, event):
        """Populate form fields from selected fee record."""
        selected = self.tree.focus()
        if selected:
            values = self.tree.item(selected, "values")
            if values:
                self.selected_fee = values[0]
                self.student_var.set(values[2])
                self.total_fee_var.set(values[3])
                self.paid_fee_var.set(values[4])
                self.payment_date_var.set(values[6])

    def validate_fields(self):
        """Validate fee entry fields."""
        if not validate_non_empty(self.student_var.get(), self.total_fee_var.get(), self.paid_fee_var.get(), self.payment_date_var.get()):
            show_error("All fields are required for fee processing.")
            return False
        if self.student_var.get() not in self.student_mapping:
            show_error("Please select a valid student roll number.")
            return False
        try:
            float(self.total_fee_var.get())
            float(self.paid_fee_var.get())
        except ValueError:
            show_error("Total fee and paid fee must be valid amounts.")
            return False
        return True

    def add_fee(self):
        """Create a new fee record."""
        if not self.validate_fields():
            return

        student_id = self.student_mapping[self.student_var.get()]
        total_fee = float(self.total_fee_var.get())
        paid_fee = float(self.paid_fee_var.get())
        remaining_fee = round(max(total_fee - paid_fee, 0.0), 2)
        status = self.compute_status(remaining_fee)

        try:
            self.db.execute_query(
                "INSERT INTO fees (student_id, total_fee, paid_fee, remaining_fee, payment_date, status) VALUES (%s, %s, %s, %s, %s, %s)",
                (student_id, total_fee, paid_fee, remaining_fee, self.payment_date_var.get().strip(), status),
            )
            show_info("Fee record added successfully.")
            self.load_fees()
        except Exception as error:
            show_error(f"Failed to add fee record: {error}")

    def update_payment(self):
        """Update an existing payment and remaining balance."""
        if not self.selected_fee:
            show_error("Please select a fee record to update.")
            return
        if not self.validate_fields():
            return

        total_fee = float(self.total_fee_var.get())
        paid_fee = float(self.paid_fee_var.get())
        remaining_fee = round(max(total_fee - paid_fee, 0.0), 2)
        status = self.compute_status(remaining_fee)

        try:
            self.db.execute_query(
                "UPDATE fees SET total_fee=%s, paid_fee=%s, remaining_fee=%s, payment_date=%s, status=%s WHERE fee_id=%s",
                (total_fee, paid_fee, remaining_fee, self.payment_date_var.get().strip(), status, self.selected_fee),
            )
            show_info("Fee payment updated successfully.")
            self.load_fees()
        except Exception as error:
            show_error(f"Failed to update fee: {error}")

    def delete_fee(self):
        """Delete selected fee record after confirmation."""
        if not self.selected_fee:
            show_error("Please select a fee record to delete.")
            return
        if not messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this fee record?"):
            return

        try:
            self.db.execute_query("DELETE FROM fees WHERE fee_id = %s", (self.selected_fee,))
            show_info("Fee record deleted successfully.")
            self.load_fees()
        except Exception as error:
            show_error(f"Failed to delete fee record: {error}")

    def search_fees(self):
        """Search fees by student roll or payment status."""
        value = self.search_var.get().strip()
        if not value:
            show_error("Please enter a search term.")
            return

        if self.search_by_var.get() == "Roll Number":
            query = "SELECT f.fee_id, f.student_id, s.roll_no, f.total_fee, f.paid_fee, f.remaining_fee, f.payment_date, f.status FROM fees f JOIN students s ON f.student_id = s.student_id WHERE s.roll_no LIKE %s ORDER BY f.fee_id DESC"
        else:
            query = "SELECT f.fee_id, f.student_id, s.roll_no, f.total_fee, f.paid_fee, f.remaining_fee, f.payment_date, f.status FROM fees f JOIN students s ON f.student_id = s.student_id WHERE f.status LIKE %s ORDER BY f.fee_id DESC"

        try:
            records = self.db.execute_read_query(query, (f"%{value}%",))
            self.populate_tree(records)
        except Exception as error:
            show_error(f"Search failed: {error}")

    def compute_status(self, remaining_fee):
        """Determine payment status from remaining amount."""
        if remaining_fee <= 0:
            return "Paid"
        if remaining_fee < float(self.total_fee_var.get()):
            return "Partial"
        return "Pending"

    def clear_fields(self):
        """Reset fees form fields."""
        self.selected_fee = None
        self.student_var.set("")
        self.total_fee_var.set("")
        self.paid_fee_var.set("")
        self.payment_date_var.set(datetime.now().strftime("%Y-%m-%d"))
