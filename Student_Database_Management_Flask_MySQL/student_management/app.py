from flask import Flask, render_template, request, redirect
import mysql.connector

app = Flask(__name__)


def connect_db():
    return mysql.connector.connect(
        host="localhost", user="root", password="", database="student_db1"
    )


def create_database():
    db = mysql.connector.connect(host="localhost", user="root", password="")
    cursor = db.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS student_db1")
    cursor.execute("USE student_db1")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            roll_no VARCHAR(30) NOT NULL UNIQUE,
            email VARCHAR(100),
            department VARCHAR(50) NOT NULL
        )
    """)
    db.commit()
    cursor.close()
    db.close()


@app.route("/")
def index():
    db = connect_db()
    cursor = db.cursor(dictionary=True)
    search = request.args.get("search", "").strip()
    cursor.execute("SELECT COUNT(*) AS total FROM students")
    total = cursor.fetchone()["total"]
    cursor.execute("SELECT COUNT(DISTINCT department) AS total FROM students")
    departments = cursor.fetchone()["total"]
    if search:
        value = "%" + search + "%"
        cursor.execute("""
            SELECT * FROM students
            WHERE name LIKE %s OR roll_no LIKE %s
            ORDER BY id DESC
        """, (value, value))
    else:
        cursor.execute("SELECT * FROM students ORDER BY id DESC")
    students = cursor.fetchall()
    cursor.close()
    db.close()
    return render_template("index.html", students=students, total=total,
                           departments=departments, search=search)


@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        name = request.form["name"]
        roll_no = request.form["roll_no"]
        email = request.form["email"]
        department = request.form["department"]
        db = connect_db()
        cursor = db.cursor()
        try:
            cursor.execute("""
                INSERT INTO students (name, roll_no, email, department)
                VALUES (%s, %s, %s, %s)
            """, (name, roll_no, email, department))
            db.commit()
        except mysql.connector.IntegrityError:
            db.rollback()
            return "Roll number already exists!", 409
        finally:
            cursor.close()
            db.close()
        return redirect("/")
    return render_template("add.html")


@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    db = connect_db()
    cursor = db.cursor(dictionary=True)
    if request.method == "POST":
        name = request.form["name"]
        roll_no = request.form["roll_no"]
        email = request.form["email"]
        department = request.form["department"]
        try:
            cursor.execute("""
                UPDATE students SET name=%s, roll_no=%s,
                email=%s, department=%s WHERE id=%s
            """, (name, roll_no, email, department, id))
            db.commit()
        except mysql.connector.IntegrityError:
            db.rollback()
            return "Roll number already exists!", 409
        finally:
            cursor.close()
            db.close()
        return redirect("/")
    cursor.execute("SELECT * FROM students WHERE id=%s", (id,))
    student = cursor.fetchone()
    cursor.close()
    db.close()
    if student is None:
        return "Student not found", 404
    return render_template("edit.html", student=student)


@app.route("/delete/<int:id>", methods=["POST"])
def delete(id):
    db = connect_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM students WHERE id=%s", (id,))
    db.commit()
    cursor.close()
    db.close()
    return redirect("/")


if __name__ == "__main__":
    create_database()
    app.run(debug=True)
