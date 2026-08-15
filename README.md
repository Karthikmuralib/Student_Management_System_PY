# Student Management System

A complete desktop-based Student Management System built with Python, Tkinter, and MySQL.

## Project Description

This application provides secure login support for admin and faculty users, and includes modules for managing students, faculty, attendance, marks, fees, and reports. The system uses a modular, object-oriented architecture and stores data in a MySQL database.

## Installation Steps

1. Install Python 3.x from https://python.org.
2. Install MySQL and create a database user with proper permissions.
3. Clone or download this repository.
4. Navigate to the project folder:
   ```bash
   cd d:\Student_Management_System_PY
   ```
5. Install the required Python package:
   ```bash
   pip install -r requirements.txt
   ```

## Database Setup

1. Start MySQL server.
2. Create the database using the provided SQL file:
   ```sql
   SOURCE database/student_management.sql;
   ```
3. Or use the `Database.create_database_schema()` method after updating your database credentials in `config.py`.
4. Update `config.py` with your MySQL host, user, password, and port.

## Required Packages

- `mysql-connector-python`

## How to Run

Run the application from the project root:

```bash
python main.py
```

##  Project Demo
https://youtu.be/004qBD4A8C8



## Future Enhancements

- Add password hashing for login credentials.
- Add role-based access control for faculty and admin features.
- Add a dedicated student details view and profile page.
- Implement automatic attendance notifications.
- Add charts and visual dashboards for analytics.
- Add backup and restore support for the database.
