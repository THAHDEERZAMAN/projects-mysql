from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector

app = Flask(__name__)
app.secret_key = "local-classroom-demo-change-me"

# XAMPP defaults: change these settings if your MySQL port/password is different.
CONFIG = {"host": "127.0.0.1", "user": "root", "password": "", "port": 3306}
DATABASE = "pharmacy_db"


def setup_database():
    db = mysql.connector.connect(**CONFIG)
    cursor = db.cursor()
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DATABASE}")
    cursor.execute(f"USE {DATABASE}")
    cursor.execute("""CREATE TABLE IF NOT EXISTS medicines (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(120) NOT NULL,
            manufacturer VARCHAR(120) NOT NULL,
            price DECIMAL(10,2) NOT NULL,
            stock INT NOT NULL
        )""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS sales (
            id INT AUTO_INCREMENT PRIMARY KEY,
            medicine_id INT NOT NULL,
            customer VARCHAR(100) NOT NULL,
            quantity INT NOT NULL,
            sale_date DATE NOT NULL,
            unit_price DECIMAL(10,2) NOT NULL,
            FOREIGN KEY (medicine_id) REFERENCES medicines(id)
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
        cursor.execute("SELECT * FROM medicines WHERE name LIKE %s ORDER BY id DESC", ("%" + search + "%",))
    else:
        cursor.execute("SELECT * FROM medicines ORDER BY id DESC")
    items = cursor.fetchall()
    cursor.execute("SELECT COUNT(*) AS n FROM medicines")
    total_items = cursor.fetchone()["n"]
    cursor.execute("SELECT COUNT(*) AS n FROM sales")
    total_records = cursor.fetchone()["n"]
    cursor.execute("""SELECT s.*, m.name AS item_name, s.quantity*s.unit_price AS total
        FROM sales s JOIN medicines m ON s.medicine_id=m.id ORDER BY s.id DESC""")
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
            cursor.execute("INSERT INTO medicines (name, manufacturer, price, stock) VALUES (%s, %s, %s, %s)", (request.form["name"], request.form["manufacturer"], request.form["price"], request.form["stock"],))
            db.commit()
            flash("Medicine added successfully.", "success")
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
    cursor.execute("SELECT * FROM medicines WHERE id=%s", (item_id,))
    item = cursor.fetchone()
    if item is None:
        db.close()
        return "Record not found", 404
    if request.method == "POST":
        try:
            cursor.execute("UPDATE medicines SET name=%s, manufacturer=%s, price=%s, stock=%s WHERE id=%s", (request.form["name"], request.form["manufacturer"], request.form["price"], request.form["stock"], item_id))
            db.commit()
            flash("Medicine updated successfully.", "success")
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
        cursor.execute("DELETE FROM medicines WHERE id=%s", (item_id,))
        db.commit()
        flash("Medicine deleted.", "success")
    except mysql.connector.IntegrityError:
        db.rollback()
        flash("Cannot delete: this record is used in sales.", "danger")
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
            medicine_id = int(request.form["medicine_id"])
            quantity = int(request.form["quantity"])
            if quantity <= 0:
                flash("Quantity must be positive.", "danger")
                return redirect(url_for("add_record"))
            cursor.execute("SELECT stock, price FROM medicines WHERE id=%s", (medicine_id,))
            medicine = cursor.fetchone()
            if medicine is None or medicine["stock"] < quantity:
                flash("Medicine not found or insufficient stock.", "danger")
                db.close()
                return redirect(url_for("add_record"))
            cursor.execute("UPDATE medicines SET stock=stock-%s WHERE id=%s", (quantity, medicine_id))
            cursor.execute("""INSERT INTO sales (medicine_id, customer, quantity, sale_date, unit_price)
                              VALUES (%s, %s, %s, %s, %s)""",
                           (medicine_id, request.form["customer"], quantity,
                            request.form["sale_date"], medicine["price"]))
            db.commit()
            flash("Sale created successfully.", "success")
        except (mysql.connector.IntegrityError, ValueError):
            db.rollback()
            flash("Could not save the record. Check the selected item and values.", "danger")
        finally:
            cursor.close()
            db.close()
        return redirect(url_for("index"))
    cursor.execute("SELECT * FROM medicines ORDER BY name")
    items = cursor.fetchall()
    cursor.close()
    db.close()
    return render_template("record_form.html", items=items)


@app.route("/delete-record/<int:record_id>", methods=["POST"])
def delete_record(record_id):
    db = connect_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT medicine_id, quantity FROM sales WHERE id=%s", (record_id,))
    sale = cursor.fetchone()
    if sale:
        cursor.execute("UPDATE medicines SET stock=stock+%s WHERE id=%s", (sale["quantity"], sale["medicine_id"]))
        cursor.execute("DELETE FROM sales WHERE id=%s", (record_id,))
    db.commit()
    cursor.close()
    db.close()
    flash("Sale deleted.", "success")
    return redirect(url_for("index"))

if __name__ == "__main__":
    setup_database()
    app.run(debug=True)  # For local classroom use only.
