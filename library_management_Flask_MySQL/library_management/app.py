from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector

app = Flask(__name__)
app.secret_key = "local-classroom-demo-change-me"

# XAMPP defaults: change these settings if your MySQL port/password is different.
CONFIG = {"host": "127.0.0.1", "user": "root", "password": "", "port": 3306}
DATABASE = "library_db"


def setup_database():
    db = mysql.connector.connect(**CONFIG)
    cursor = db.cursor()
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DATABASE}")
    cursor.execute(f"USE {DATABASE}")
    cursor.execute("""CREATE TABLE IF NOT EXISTS books (
            id INT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(120) NOT NULL,
            author VARCHAR(120) NOT NULL,
            isbn VARCHAR(120) NOT NULL UNIQUE,
            copies INT NOT NULL
        )""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS borrowings (
            id INT AUTO_INCREMENT PRIMARY KEY,
            book_id INT NOT NULL,
            borrower VARCHAR(100) NOT NULL,
            borrow_date DATE NOT NULL,
            status VARCHAR(25) NOT NULL DEFAULT 'Scheduled',
            FOREIGN KEY (book_id) REFERENCES books(id)
        )""")
    db.commit()
    cursor.close()
    db.close()


def connect_db():
    return mysql.connector.connect(**CONFIG, database=DATABASE)


@app.route("/")
def index():
    db = connect_db()
    cursor = db.cursor(dictionary=True)
    search = request.args.get("search", "").strip()
    if search:
        cursor.execute("SELECT * FROM books WHERE title LIKE %s ORDER BY id DESC", ("%" + search + "%",))
    else:
        cursor.execute("SELECT * FROM books ORDER BY id DESC")
    items = cursor.fetchall()
    cursor.execute("SELECT COUNT(*) AS n FROM books")
    total_items = cursor.fetchone()["n"]
    cursor.execute("SELECT COUNT(*) AS n FROM borrowings")
    total_records = cursor.fetchone()["n"]
    cursor.execute("""SELECT r.*, m.title AS item_name
        FROM borrowings r JOIN books m ON r.book_id=m.id ORDER BY r.id DESC""")
    records = cursor.fetchall()
    cursor.close()
    db.close()
    return render_template("index.html", items=items, records=records,
                           total_items=total_items, total_records=total_records,
                           search=search)


@app.route("/add", methods=["GET", "POST"])
def add_item():
    if request.method == "POST":
        db = connect_db()
        cursor = db.cursor()
        try:
            cursor.execute("INSERT INTO books (title, author, isbn, copies) VALUES (%s, %s, %s, %s)", (request.form["title"], request.form["author"], request.form["isbn"], request.form["copies"],))
            db.commit()
            flash("Book added successfully.", "success")
        except mysql.connector.IntegrityError:
            db.rollback()
            flash("Could not add record. Check the entered values and duplicates.", "danger")
        finally:
            cursor.close()
            db.close()
        return redirect(url_for("index"))
    return render_template("item_form.html", item=None)


@app.route("/edit/<int:item_id>", methods=["GET", "POST"])
def edit_item(item_id):
    db = connect_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM books WHERE id=%s", (item_id,))
    item = cursor.fetchone()
    if item is None:
        db.close()
        return "Record not found", 404
    if request.method == "POST":
        try:
            cursor.execute("UPDATE books SET title=%s, author=%s, isbn=%s, copies=%s WHERE id=%s", (request.form["title"], request.form["author"], request.form["isbn"], request.form["copies"], item_id))
            db.commit()
            flash("Book updated successfully.", "success")
        except mysql.connector.IntegrityError:
            db.rollback()
            flash("Update failed. Check for duplicates or invalid values.", "danger")
        finally:
            cursor.close()
            db.close()
        return redirect(url_for("index"))
    cursor.close()
    db.close()
    return render_template("item_form.html", item=item)


@app.route("/delete/<int:item_id>", methods=["POST"])
def delete_item(item_id):
    db = connect_db()
    cursor = db.cursor()
    try:
        cursor.execute("DELETE FROM books WHERE id=%s", (item_id,))
        db.commit()
        flash("Book deleted.", "success")
    except mysql.connector.IntegrityError:
        db.rollback()
        flash("Cannot delete: this record is used in borrowings.", "danger")
    finally:
        cursor.close()
        db.close()
    return redirect(url_for("index"))


@app.route("/new-record", methods=["GET", "POST"])
def add_record():
    db = connect_db()
    cursor = db.cursor(dictionary=True)
    if request.method == "POST":
        try:
            cursor.execute("""INSERT INTO borrowings (book_id, borrower, borrow_date, status) VALUES (%s, %s, %s, %s)""",
                           (request.form["book_id"], request.form["borrower"], request.form["borrow_date"], request.form["status"],))
            db.commit()
            flash("Borrowing created successfully.", "success")
        except (mysql.connector.IntegrityError, ValueError):
            db.rollback()
            flash("Could not save the record. Check the selected item and values.", "danger")
        finally:
            cursor.close()
            db.close()
        return redirect(url_for("index"))
    cursor.execute("SELECT * FROM books ORDER BY title")
    items = cursor.fetchall()
    cursor.close()
    db.close()
    return render_template("record_form.html", items=items)


@app.route("/delete-record/<int:record_id>", methods=["POST"])
def delete_record(record_id):
    db = connect_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("DELETE FROM borrowings WHERE id=%s", (record_id,))
    db.commit()
    cursor.close()
    db.close()
    flash("Borrowing deleted.", "success")
    return redirect(url_for("index"))


@app.route("/status/<int:record_id>", methods=["POST"])
def update_status(record_id):
    status = request.form.get("status")
    if status not in ['Borrowed', 'Returned']:
        return "Invalid status", 400
    db = connect_db()
    cursor = db.cursor()
    cursor.execute("UPDATE borrowings SET status=%s WHERE id=%s", (status, record_id))
    db.commit()
    cursor.close()
    db.close()
    return redirect(url_for("index"))

if __name__ == "__main__":
    setup_database()
    app.run(debug=True)  # For local classroom use only.
