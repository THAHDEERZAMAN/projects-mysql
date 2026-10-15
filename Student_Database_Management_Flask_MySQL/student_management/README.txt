STUDENT DATABASE MANAGEMENT SYSTEM
Flask + XAMPP MySQL

1. Open XAMPP Control Panel and start MySQL.
2. Open this folder in VS Code.
3. In a terminal, install dependencies:
   pip install -r requirements.txt
4. Run:
   python app.py
5. Visit http://127.0.0.1:5000

The app automatically creates database "student_db" and table "students".
Default connection settings: localhost, user root, blank password, port 3306.
If your MySQL configuration is different, update both mysql.connector.connect calls in app.py.

Features: add, view, search, edit, and delete students.
SQL topics: CREATE DATABASE, CREATE TABLE, PRIMARY KEY, AUTO_INCREMENT,
UNIQUE, INSERT, SELECT, WHERE, LIKE, UPDATE, DELETE, COUNT.

For local classroom demonstration only. No login/authentication is included.
Do not expose the Flask debug server on the public internet.
