import sqlite3
from werkzeug.security import generate_password_hash

connection = sqlite3.connect("database.db")
connection.execute("PRAGMA foreign_keys = ON")

connection.execute(
    "CREATE TABLE IF NOT EXISTS users ("
    "id INTEGER PRIMARY KEY AUTOINCREMENT, "
    "full_name TEXT NOT NULL, "
    "email TEXT NOT NULL UNIQUE, "
    "password TEXT NOT NULL, "
    "role TEXT NOT NULL)"
)

connection.execute(
    "CREATE TABLE IF NOT EXISTS employees ("
    "id INTEGER PRIMARY KEY AUTOINCREMENT, "
    "user_id INTEGER NOT NULL UNIQUE, "
    "employee_code TEXT NOT NULL UNIQUE, "
    "department TEXT NOT NULL, "
    "job_title TEXT NOT NULL, "
    "hire_date TEXT NOT NULL, "
    "supervisor_id INTEGER, "
    "status TEXT NOT NULL DEFAULT 'Active', "
    "FOREIGN KEY (user_id) REFERENCES users(id), "
    "FOREIGN KEY (supervisor_id) REFERENCES users(id))"
)

connection.execute(
    "INSERT OR IGNORE INTO users (full_name, email, password, role) VALUES (?, ?, ?, ?)",
    ("Altrium HR Admin", "hr@altrium.com", generate_password_hash("Admin123!"), "HR")
)
connection.execute(
    "INSERT OR IGNORE INTO users (full_name, email, password, role) VALUES (?, ?, ?, ?)",
    ("Sarah Perera", "supervisor@altrium.com", generate_password_hash("Supervisor123!"), "Supervisor")
)

connection.commit()
connection.close()
print("Database initialized successfully.")
