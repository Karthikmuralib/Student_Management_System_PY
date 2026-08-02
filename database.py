"""
Database access layer for Student Management System.
Handles connection management, parameterized queries, transactions, and error handling.
"""

import mysql.connector
from mysql.connector import Error
from config import DB_CONFIG


class Database:
    def __init__(self):
        self.connection = None

    def connect(self):
        """Establish connection to the MySQL database."""
        try:
            self.connection = mysql.connector.connect(**DB_CONFIG)
            if self.connection.is_connected():
                return True
            return False
        except Error as error:
            print(f"Database connection error: {error}")
            return False

    def close(self):
        """Close the database connection."""
        if self.connection and self.connection.is_connected():
            self.connection.close()

    def execute_query(self, query, params=None):
        """Execute insert, update, delete queries with transaction support."""
        cursor = None
        try:
            if not self.connection or not self.connection.is_connected():
                self.connect()
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query, params or ())
            self.connection.commit()
            return cursor.lastrowid
        except Error as error:
            if self.connection:
                self.connection.rollback()
            print(f"SQL execution error: {error}")
            raise
        finally:
            if cursor:
                cursor.close()

    def execute_read_query(self, query, params=None):
        """Execute select queries and return all rows."""
        cursor = None
        result = []
        try:
            if not self.connection or not self.connection.is_connected():
                self.connect()
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query, params or ())
            result = cursor.fetchall()
            return result
        except Error as error:
            print(f"SQL read error: {error}")
            raise
        finally:
            if cursor:
                cursor.close()

    def execute_read_one(self, query, params=None):
        """Execute select query and return a single row."""
        cursor = None
        try:
            if not self.connection or not self.connection.is_connected():
                self.connect()
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query, params or ())
            return cursor.fetchone()
        except Error as error:
            print(f"SQL read one error: {error}")
            raise
        finally:
            if cursor:
                cursor.close()

    def connect_to_server(self):
        """Connect to MySQL server without selecting a specific database."""
        try:
            server_config = DB_CONFIG.copy()
            server_config.pop("database", None)
            self.connection = mysql.connector.connect(**server_config)
            return self.connection.is_connected()
        except Error as error:
            print(f"Server connection error: {error}")
            return False

    def create_database_schema(self):
        """Create the database schema if it does not exist."""
        schema_sql = """
        CREATE DATABASE IF NOT EXISTS student_management;
        USE student_management;

        CREATE TABLE IF NOT EXISTS admin (
            admin_id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(100) NOT NULL UNIQUE,
            password VARCHAR(255) NOT NULL
        );

        CREATE TABLE IF NOT EXISTS faculty (
            faculty_id INT AUTO_INCREMENT PRIMARY KEY,
            faculty_name VARCHAR(150) NOT NULL,
            email VARCHAR(150) NOT NULL UNIQUE,
            department VARCHAR(100) NOT NULL,
            phone VARCHAR(20) NOT NULL,
            password VARCHAR(255) NOT NULL
        );

        CREATE TABLE IF NOT EXISTS students (
            student_id INT AUTO_INCREMENT PRIMARY KEY,
            roll_no VARCHAR(50) NOT NULL UNIQUE,
            name VARCHAR(150) NOT NULL,
            gender ENUM('Male','Female','Other') NOT NULL,
            dob DATE NOT NULL,
            department VARCHAR(100) NOT NULL,
            year INT NOT NULL,
            semester INT NOT NULL,
            email VARCHAR(150) NOT NULL UNIQUE,
            phone VARCHAR(20) NOT NULL,
            address TEXT,
            admission_date DATE NOT NULL
        );

        CREATE TABLE IF NOT EXISTS attendance (
            attendance_id INT AUTO_INCREMENT PRIMARY KEY,
            student_id INT NOT NULL,
            date DATE NOT NULL,
            status ENUM('Present', 'Absent') NOT NULL,
            faculty_id INT NOT NULL,
            FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
            FOREIGN KEY (faculty_id) REFERENCES faculty(faculty_id) ON DELETE SET NULL
        );

        CREATE TABLE IF NOT EXISTS marks (
            mark_id INT AUTO_INCREMENT PRIMARY KEY,
            student_id INT NOT NULL,
            subject VARCHAR(150) NOT NULL,
            internal_marks INT NOT NULL,
            external_marks INT NOT NULL,
            total INT NOT NULL,
            grade VARCHAR(4) NOT NULL,
            semester INT NOT NULL,
            FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS fees (
            fee_id INT AUTO_INCREMENT PRIMARY KEY,
            student_id INT NOT NULL,
            total_fee DECIMAL(10, 2) NOT NULL,
            paid_fee DECIMAL(10, 2) NOT NULL,
            remaining_fee DECIMAL(10, 2) NOT NULL,
            payment_date DATE NOT NULL,
            status ENUM('Paid', 'Partial', 'Pending') NOT NULL,
            FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE
        );
        """
        cursor = None
        try:
            if not self.connection or not self.connection.is_connected():
                if not self.connect_to_server():
                    raise Error("Unable to connect to MySQL server")
            cursor = self.connection.cursor()
            for statement in schema_sql.split(";"):
                stripped = statement.strip()
                if stripped:
                    cursor.execute(stripped)
            self.connection.commit()
        except Error as error:
            print(f"Schema creation error: {error}")
            raise
        finally:
            if cursor:
                cursor.close()

    def insert_sample_data(self):
        """Insert sample data into the database for initial testing."""
        try:
            self.execute_query(
                "INSERT IGNORE INTO admin (username, password) VALUES (%s, %s)",
                ("admin", "admin123"),
            )
            self.execute_query(
                "INSERT IGNORE INTO faculty (faculty_name, email, department, phone, password) VALUES (%s, %s, %s, %s, %s)",
                ("Dr. Maya Singh", "maya.singh@example.com", "Computer Science", "9876543210", "faculty123"),
            )
            self.execute_query(
                "INSERT IGNORE INTO students (roll_no, name, gender, dob, department, year, semester, email, phone, address, admission_date) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                ("CS1001", "Aarav Sharma", "Male", "2003-04-12", "Computer Science", 3, 5, "aarav.sharma@example.com", "9876501234", "123 Green Street", "2021-07-15"),
            )
            self.execute_query(
                "INSERT IGNORE INTO attendance (student_id, date, status, faculty_id) VALUES (%s, %s, %s, %s)",
                (1, "2026-08-02", "Present", 1),
            )
            self.execute_query(
                "INSERT IGNORE INTO marks (student_id, subject, internal_marks, external_marks, total, grade, semester) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (1, "Mathematics", 45, 42, 87, "A", 5),
            )
            self.execute_query(
                "INSERT IGNORE INTO fees (student_id, total_fee, paid_fee, remaining_fee, payment_date, status) VALUES (%s, %s, %s, %s, %s, %s)",
                (1, 50000.00, 30000.00, 20000.00, "2026-08-02", "Partial"),
            )
        except Error as error:
            print(f"Sample data insertion error: {error}")
            raise
