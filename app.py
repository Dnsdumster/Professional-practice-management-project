import sqlite3
from flask import Flask, render_template, request, session, redirect, url_for, flash
from werkzeug.security import check_password_hash, generate_password_hash
from database import get_db_connection

app = Flask(__name__)
app.secret_key = "change-this-development-key"

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        connection = get_db_connection()
        user = connection.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        connection.close()
        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            session["user_name"] = user["full_name"]
            session["user_role"] = user["role"]
            return redirect(url_for("dashboard"))
        flash("Invalid email or password.", "error")
    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))
    employee_count = 0
    if session["user_role"] == "HR":
        connection = get_db_connection()
        employee_count = connection.execute(
            "SELECT COUNT(*) AS total FROM employees WHERE status = 'Active'"
        ).fetchone()["total"]
        connection.close()
    return render_template(
        "dashboard.html",
        employee_count=employee_count,
        user_name=session["user_name"],
        user_role=session["user_role"]
    )

@app.route("/employees")
def employees():
    if "user_id" not in session:
        return redirect(url_for("login"))
    if session["user_role"] != "HR":
        return redirect(url_for("dashboard"))
    connection = get_db_connection()
    employee_rows = connection.execute(
        "SELECT employees.id, employees.employee_code, employees.department, employees.job_title, "
        "employees.hire_date, employees.status, users.full_name, users.email, "
        "supervisor.full_name AS supervisor_name "
        "FROM employees JOIN users ON employees.user_id = users.id "
        "LEFT JOIN users AS supervisor ON employees.supervisor_id = supervisor.id "
        "ORDER BY users.full_name"
    ).fetchall()
    supervisors = connection.execute(
        "SELECT id, full_name FROM users WHERE role = 'Supervisor' ORDER BY full_name"
    ).fetchall()
    connection.close()
    return render_template(
        "employees.html",
        employees=employee_rows,
        supervisors=supervisors,
        user_name=session["user_name"],
        user_role=session["user_role"]
    )

@app.route("/employees/add", methods=["POST"])
def add_employee():
    if "user_id" not in session:
        return redirect(url_for("login"))
    if session["user_role"] != "HR":
        return redirect(url_for("dashboard"))

    full_name = request.form.get("full_name", "").strip()
    employee_code = request.form.get("employee_code", "").strip()
    email = request.form.get("email", "").strip().lower()
    department = request.form.get("department", "").strip()
    job_title = request.form.get("job_title", "").strip()
    hire_date = request.form.get("hire_date", "").strip()
    supervisor_id = request.form.get("supervisor_id") or None
    temporary_password = request.form.get("temporary_password", "")

    if not all([full_name, employee_code, email, department, job_title, hire_date, temporary_password]):
        flash("Please complete all required fields.", "error")
        return redirect(url_for("employees"))

    if len(temporary_password) < 8:
        flash("Temporary password must contain at least 8 characters.", "error")
        return redirect(url_for("employees"))

    connection = get_db_connection()
    try:
        user_cursor = connection.execute(
            "INSERT INTO users (full_name, email, password, role) VALUES (?, ?, ?, ?)",
            (full_name, email, generate_password_hash(temporary_password), "Employee")
        )
        user_id = user_cursor.lastrowid
        connection.execute(
            "INSERT INTO employees (user_id, employee_code, department, job_title, hire_date, supervisor_id, status) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (user_id, employee_code, department, job_title, hire_date, supervisor_id, "Active")
        )
        connection.commit()
        flash("Employee created successfully.", "success")
    except sqlite3.IntegrityError:
        connection.rollback()
        flash("Employee ID or email already exists.", "error")
    finally:
        connection.close()
    return redirect(url_for("employees"))

@app.route("/my-team")
def my_team():
    if "user_id" not in session:
        return redirect(url_for("login"))
    if session["user_role"] != "Supervisor":
        return redirect(url_for("dashboard"))
    connection = get_db_connection()
    team_members = connection.execute(
        "SELECT employees.id, employees.employee_code, employees.department, employees.job_title, "
        "employees.status, users.full_name, users.email FROM employees "
        "JOIN users ON employees.user_id = users.id "
        "WHERE employees.supervisor_id = ? ORDER BY users.full_name",
        (session["user_id"],)
    ).fetchall()
    connection.close()
    return render_template(
        "my_team.html",
        team_members=team_members,
        user_name=session["user_name"],
        user_role=session["user_role"]
    )

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)
