-- SQL schema and sample data for Student Management System

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
    faculty_id INT NULL,
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

-- Sample data
INSERT IGNORE INTO admin (username, password) VALUES ('admin', 'admin123');
INSERT IGNORE INTO faculty (faculty_name, email, department, phone, password) VALUES ('Dr. Maya Singh', 'maya.singh@example.com', 'Computer Science', '9876543210', 'faculty123');
INSERT IGNORE INTO students (roll_no, name, gender, dob, department, year, semester, email, phone, address, admission_date) VALUES ('CS1001', 'Aarav Sharma', 'Male', '2003-04-12', 'Computer Science', 3, 5, 'aarav.sharma@example.com', '9876501234', '123 Green Street', '2021-07-15');
INSERT IGNORE INTO attendance (student_id, date, status, faculty_id) VALUES (1, '2026-08-02', 'Present', 1);
INSERT IGNORE INTO marks (student_id, subject, internal_marks, external_marks, total, grade, semester) VALUES (1, 'Mathematics', 45, 42, 87, 'A', 5);
INSERT IGNORE INTO fees (student_id, total_fee, paid_fee, remaining_fee, payment_date, status) VALUES (1, 50000.00, 30000.00, 20000.00, '2026-08-02', 'Partial');
