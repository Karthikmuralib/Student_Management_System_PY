"""
Configuration module for Student Management System.
Contains database settings and reusable constants.
"""

import os

# MySQL database configuration
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "student_management"),
    "port": int(os.getenv("DB_PORT", "3306")),
}

# GUI settings
APP_TITLE = "Student Management System"
WINDOW_SIZE = "1200x700"
BG_COLOR = "#f0f4f7"
FONT_FAMILY = "Arial"
HEADER_COLOR = "#283593"
BUTTON_COLOR = "#1976d2"
BUTTON_TEXT_COLOR = "#ffffff"
FRAME_BG_COLOR = "#ffffff"

# Report export settings
EXPORT_FOLDER = "reports"

# Grade boundaries
GRADE_RULES = [
    (90, "A+"),
    (80, "A"),
    (70, "B"),
    (60, "C"),
    (50, "D"),
    (0, "F"),
]
