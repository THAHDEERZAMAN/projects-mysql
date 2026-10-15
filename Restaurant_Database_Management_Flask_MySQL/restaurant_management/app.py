from flask import Flask, render_template, request, redirect, flash
import mysql.connector

app = Flask(__name__)
app.secret_key = 'local-classroom-example'

# Change these if your XAMPP MySQL port or password is different.
config = {'host': '127.0.0.1', 'user': 'root', 'password': '', 'port': 3306}


def create_database():
    db = mysql.connector.connect(**config)
    cursor = db.cursor()
    cursor.execute('CREATE DATABASE IF NOT EXISTS restaurant_db')
    cursor.execute('USE restaurant_db')
    cursor.execute('''CREATE TABLE IF NOT EXISTS menu (
        id INT AUTO_INCREMENT PRIMARY KEY,
        food_name VARCHAR(100) NOT NULL,
        category VARCHAR(50) NOT NULL,
        price DECIMAL(10,2) NOT NULL
    ) ENGINE=InnoDB''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS orders (
        id INT AUTO_INCREMENT PRIMARY KEY,
        customer_name VARCHAR(100) NOT NULL,
        menu_id INT NOT NULL,
        quantity INT NOT NULL,
        status VARCHAR(30) DEFAULT 'Pending',
        order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (menu_id) REFERENCES menu(id)
    ) ENGINE=InnoDB''')
    db.commit()
    cursor.close()
    db.close()


def connect_db():
    return mysql.connector.connect(**config, database='restaurant_db')


@app.route('/')
def index():
    db = connect_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute('SELECT * FROM menu ORDER BY id DESC')
    menu_items = cursor.fetchall()
    cursor.execute('''SELECT orders.id, orders.customer_name, menu.food_name,
        orders.quantity, menu.price * orders.quantity AS total,
        orders.status, orders.order_date
        FROM orders JOIN menu ON orders.menu_id = menu.id
        ORDER BY orders.id DESC''')
    orders = cursor.fetchall()
    cursor.execute('SELECT COUNT(*) AS total FROM menu')
    total_menu = cursor.fetchone()['total']
    cursor.execute('SELECT COUNT(*) AS total FROM orders')
    total_orders = cursor.fetchone()['total']
    cursor.close()
    db.close()
    return render_template('index.html', menu_items=menu_items, orders=orders,
                           total_menu=total_menu, total_orders=total_orders)


@app.route('/add_menu', methods=['GET', 'POST'])
def add_menu():
    if request.method == 'POST':
        name = request.form['food_name'].strip()
        category = request.form['category']
        price = request.form['price']
        if not name or not category:
            return 'Food name and category are required', 400
        db = connect_db()
        cursor = db.cursor()
        cursor.execute('INSERT INTO menu (food_name, category, price) VALUES (%s,%s,%s)',
                       (name, category, price))
        db.commit()
        cursor.close()
        db.close()
        flash('Menu item added successfully!')
        return redirect('/')
    return render_template('add_menu.html')


@app.route('/edit_menu/<int:id>', methods=['GET', 'POST'])
def edit_menu(id):
    db = connect_db()
    cursor = db.cursor(dictionary=True)
    if request.method == 'POST':
        name = request.form['food_name'].strip()
        category = request.form['category']
        price = request.form['price']
        if not name or not category:
            cursor.close()
            db.close()
            return 'Food name and category are required', 400
        cursor.execute('''UPDATE menu SET food_name=%s, category=%s, price=%s
                          WHERE id=%s''', (name, category, price, id))
        db.commit()
        cursor.close()
        db.close()
        flash('Menu item updated!')
        return redirect('/')
    cursor.execute('SELECT * FROM menu WHERE id=%s', (id,))
    item = cursor.fetchone()
    cursor.close()
    db.close()
    if item is None:
        return 'Menu item not found', 404
    return render_template('edit_menu.html', item=item)


@app.route('/delete_menu/<int:id>', methods=['POST'])
def delete_menu(id):
    db = connect_db()
    cursor = db.cursor()
    try:
        cursor.execute('DELETE FROM menu WHERE id=%s', (id,))
        db.commit()
        flash('Menu item deleted!')
    except mysql.connector.IntegrityError:
        db.rollback()
        flash('Cannot delete food used in existing orders.')
    finally:
        cursor.close()
        db.close()
    return redirect('/')


@app.route('/add_order', methods=['GET', 'POST'])
def add_order():
    db = connect_db()
    cursor = db.cursor(dictionary=True)
    if request.method == 'POST':
        customer = request.form['customer_name'].strip()
        menu_id = request.form['menu_id']
        try:
            quantity = int(request.form['quantity'])
        except ValueError:
            quantity = 0
        if not customer or quantity < 1:
            cursor.close()
            db.close()
            return 'Enter a customer name and valid quantity', 400
        try:
            cursor.execute('''INSERT INTO orders (customer_name, menu_id, quantity)
                              VALUES (%s, %s, %s)''', (customer, menu_id, quantity))
            db.commit()
            flash('Order placed successfully!')
        except mysql.connector.IntegrityError:
            db.rollback()
            flash('Selected menu item is unavailable.')
        finally:
            cursor.close()
            db.close()
        return redirect('/')
    cursor.execute('SELECT * FROM menu ORDER BY food_name')
    menu_items = cursor.fetchall()
    cursor.close()
    db.close()
    return render_template('add_order.html', menu_items=menu_items)


@app.route('/update_status/<int:id>', methods=['POST'])
def update_status(id):
    status = request.form['status']
    if status not in ('Pending', 'Preparing', 'Completed'):
        return 'Invalid order status', 400
    db = connect_db()
    cursor = db.cursor()
    cursor.execute('UPDATE orders SET status=%s WHERE id=%s', (status, id))
    db.commit()
    cursor.close()
    db.close()
    return redirect('/')


@app.route('/delete_order/<int:id>', methods=['POST'])
def delete_order(id):
    db = connect_db()
    cursor = db.cursor()
    cursor.execute('DELETE FROM orders WHERE id=%s', (id,))
    db.commit()
    cursor.close()
    db.close()
    flash('Order deleted!')
    return redirect('/')


if __name__ == '__main__':
    create_database()
    app.run(debug=True)
