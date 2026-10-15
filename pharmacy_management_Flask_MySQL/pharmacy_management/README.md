# PharmaCare | Pharmacy Management

A simple Flask + MySQL (XAMPP) classroom database project with a professional Bootstrap interface.

## Features
- Add, search, edit and delete medicines.
- Create and delete sales.
- Relational MySQL tables with primary keys, foreign keys and CRUD queries.
- Automatically creates `pharmacy_db` and its two tables on startup.
- Manage medicines, stock quantities, and sales. Each sale references a medicine using a foreign key.

## Run on Windows
1. Start MySQL from XAMPP Control Panel. Apache is not necessary for Flask, but useful for phpMyAdmin.
2. Open the project folder in VS Code.
3. Run `pip install -r requirements.txt`.
4. Run `python app.py`.
5. Open http://127.0.0.1:5000

## XAMPP connection
By default, `app.py` uses MySQL at `127.0.0.1:3306`, user `root`, password blank. If yours is on port 3307, or root has a password, update the `CONFIG` dictionary.

## Teaching notes
- In the `medicines` table, `id` is `PRIMARY KEY AUTO_INCREMENT`.
- In the `sales` table, `id` is its primary key and `medicine_id` is a foreign key referencing `medicines(id)`.
- Practice `CREATE`, `SELECT`, `INSERT`, `UPDATE`, `DELETE` and `JOIN`.
- Deleting a parent with linked records is blocked by the foreign key.
- This application is for local teaching only. It has no authentication and uses Flask debug mode.
- Stock decreases when a sale is made and is restored if a sale is deleted. Sale unit price is saved at time of purchase.
