"""
Utility helper module for Student Management System.
Contains reusable validation, formatting, export, and dashboard support functions.
"""

import csv
import os
from datetime import datetime
from tkinter import messagebox

from config import EXPORT_FOLDER, GRADE_RULES


def validate_non_empty(*args):
    """Return True if every provided value is non-empty after stripping."""
    return all(str(value).strip() for value in args)


def show_info(message, title="Information"):
    """Show an informational message box."""
    messagebox.showinfo(title, message)


def show_warning(message, title="Warning"):
    """Show a warning message box."""
    messagebox.showwarning(title, message)


def show_error(message, title="Error"):
    """Show an error message box."""
    messagebox.showerror(title, message)


def get_current_datetime():
    """Return the current date and time as a formatted string."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def calculate_grade(internal_marks, external_marks):
    """Calculate total marks, percentage, and grade based on provided rules."""
    try:
        internal = int(internal_marks)
        external = int(external_marks)
    except (TypeError, ValueError):
        return None, None, None
    total = internal + external
    percentage = round((total / 200) * 100, 2)
    grade = "F"
    for threshold, grade_label in GRADE_RULES:
        if percentage >= threshold:
            grade = grade_label
            break
    return total, percentage, grade


def ensure_export_folder():
    """Create the export folder if it does not exist."""
    if not os.path.exists(EXPORT_FOLDER):
        os.makedirs(EXPORT_FOLDER)


def export_to_csv(filename, headers, data_rows):
    """Export report data to a CSV file."""
    ensure_export_folder()
    file_path = os.path.join(EXPORT_FOLDER, filename)
    try:
        with open(file_path, mode="w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(headers)
            writer.writerows(data_rows)
        return file_path
    except Exception as error:
        show_error(f"Failed to export report: {error}")
        return None


def generate_student_id(name, roll_no):
    """Generate a unique student identifier based on name and roll number."""
    normalized = str(name).strip().upper().replace(" ", "")
    roll = str(roll_no).strip().upper()
    return f"STU{roll[:4]}{normalized[:3]}" if normalized and roll else roll
