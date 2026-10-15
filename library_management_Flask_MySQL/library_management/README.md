# BookNest | Library Management

A simple Flask + MySQL (XAMPP) classroom database project with a professional Bootstrap interface.

## Features
- Add, search, edit and delete books.
- Create and delete borrowings.
- Relational MySQL tables with primary keys, foreign keys and CRUD queries.
- Automatically creates `library_db` and its two tables on startup.
- Manage library books and borrowing records. Each borrowing references one book through a foreign key.

## Run on Windows
1. Start MySQL from XAMPP Control Panel. Apache is not necessary for Flask, but useful for phpMyAdmin.
2. Open the project folder in VS Code.
3. Run `pip install -r requirements.txt`.
4. Run `python app.py`.
5. Open http://127.0.0.1:5000

## XAMPP connection
By default, `app.py` uses MySQL at `127.0.0.1:3306`, user `root`, password blank. If yours is on port 3307, or root has a password, update the `CONFIG` dictionary.

## Teaching notes
- In the `books` table, `id` is `PRIMARY KEY AUTO_INCREMENT`.
- In the `borrowings` table, `id` is its primary key and `book_id` is a foreign key referencing `books(id)`.
- Practice `CREATE`, `SELECT`, `INSERT`, `UPDATE`, `DELETE` and `JOIN`.
- Deleting a parent with linked records is blocked by the foreign key.
- This application is for local teaching only. It has no authentication and uses Flask debug mode.
