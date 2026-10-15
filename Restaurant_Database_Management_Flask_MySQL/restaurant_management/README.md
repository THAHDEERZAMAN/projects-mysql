# RestoFlow — Restaurant Database Management System

Simple college RDBMS project built with Flask, MySQL (XAMPP), Bootstrap, and CSS.

## Setup

1. Extract the ZIP and open this folder in VS Code.
2. Start MySQL in the XAMPP Control Panel. Apache is not required for Flask (except to access phpMyAdmin).
3. Open a terminal here and install: `pip install -r requirements.txt`
4. Run: `python app.py`
5. Visit: http://127.0.0.1:5000

The app automatically creates `restaurant_db` with two tables: `menu` and `orders`.

## MySQL configuration

In `app.py`, edit the `config` dictionary if XAMPP uses a different port (e.g. 3307), username, or password. The default assumes port 3306, root, and a blank password.

## Topics demonstrated

- `CREATE DATABASE`, `CREATE TABLE`
- `PRIMARY KEY`, `AUTO_INCREMENT`, `FOREIGN KEY`
- `INSERT`, `SELECT`, `UPDATE`, `DELETE`
- SQL `JOIN`, `COUNT`

## Notes

- Each order refers to one menu item, with a selected quantity.
- An ordered item cannot be removed from the menu while related orders exist, due to the foreign key.
- Order totals on the dashboard use the **current** menu price. For real restaurant billing, the sold price must be stored at order time.
- This is for local classroom demonstration only. It has no login or CSRF protection, and `debug=True` must not be used on a public server.
