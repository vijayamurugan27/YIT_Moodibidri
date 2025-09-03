from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

# Connect to the SQLite database
def get_db_connection():
    conn = sqlite3.connect('library.db')
    conn.row_factory = sqlite3.Row
    return conn

# Create tables if they don't exist
def create_tables():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS books
        (id INTEGER PRIMARY KEY, title TEXT, author TEXT, status TEXT)
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS students
        (id INTEGER PRIMARY KEY, name TEXT, email TEXT)
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS borrowings
        (id INTEGER PRIMARY KEY, book_id INTEGER, student_id INTEGER, borrow_date TEXT, return_date TEXT)
    ''')
    conn.close()

create_tables()

# Routes
@app.route('/')
def index():
    return render_template('index.html')

# Books
@app.route('/books')
def books():
    conn = get_db_connection()
    books = conn.execute('SELECT * FROM books').fetchall()
    conn.close()
    return render_template('books.html', books=books)

@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        status = request.form['status']
        conn = get_db_connection()
        conn.execute('INSERT INTO books (title, author, status) VALUES (?, ?, ?)', (title, author, status))
        conn.commit()
        conn.close()
        return redirect(url_for('books'))
    return render_template('add_book.html')

@app.route('/update_book/<int:id>', methods=['GET', 'POST'])
def update_book(id):
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        status = request.form['status']
        conn = get_db_connection()
        conn.execute('UPDATE books SET title = ?, author = ?, status = ? WHERE id = ?', (title, author, status, id))
        conn.commit()
        conn.close()
        return redirect(url_for('books'))
    conn = get_db_connection()
    book = conn.execute('SELECT * FROM books WHERE id = ?', (id,)).fetchone()
    conn.close()
    return render_template('update_book.html', book=book)

@app.route('/delete_book/<int:id>')
def delete_book(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM books WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('books'))

# Students
@app.route('/students')
def students():
    conn = get_db_connection()
    students = conn.execute('SELECT * FROM students').fetchall()
    conn.close()
    return render_template('students.html', students=students)

@app.route('/add_student', methods=['GET', 'POST'])
def add_student():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        conn = get_db_connection()
        conn.execute('INSERT INTO students (name, email) VALUES (?, ?)', (name, email))
        conn.commit()
        conn.close()
        return redirect(url_for('students'))
    return render_template('add_student.html')

@app.route('/update_student/<int:id>', methods=['GET', 'POST'])
def update_student(id):
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        conn = get_db_connection()
        conn.execute('UPDATE students SET name = ?, email = ? WHERE id = ?', (name, email, id))
        conn.commit()
        conn.close()
        return redirect(url_for('students'))
    conn = get_db_connection()
    student = conn.execute('SELECT * FROM students WHERE id = ?', (id,)).fetchone()
    conn.close()
    return render_template('update_student.html', student=student)

@app.route('/delete_student/<int:id>')
def delete_student(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM students WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('students'))

# Borrowings
@app.route('/borrowings')
def borrowings():
    conn = get_db_connection()
    borrowings = conn.execute('SELECT * FROM borrowings').fetchall()
    conn.close()
    return render_template('borrowings.html', borrowings=borrowings)

@app.route('/add_borrowing', methods=['GET', 'POST'])
def add_borrowing():
    if request.method == 'POST':
        book_id = request.form['book_id']
        student_id = request.form['student_id']
        borrow_date = request.form['borrow_date']
        return_date = request.form['return_date']
        conn = get_db_connection()
        conn.execute('INSERT INTO borrowings (book_id, student_id, borrow_date, return_date) VALUES (?, ?, ?, ?)', (book_id, student_id, borrow_date, return_date))
        conn.commit()
        conn.close()
        return redirect(url_for('borrowings'))
    conn = get_db_connection()
    books = conn.execute('SELECT * FROM books').fetchall()
    students = conn.execute('SELECT * FROM students').fetchall()
    conn.close()
    return render_template('add_borrowing.html', books=books, students=students)

@app.route('/update_borrowing/<int:id>', methods=['GET', 'POST'])
def update_borrowing(id):
    if request.method == 'POST':
        book_id = request.form['book_id']
        student_id = request.form['student_id']
        borrow_date = request.form['borrow_date']
        return_date = request.form['return_date']
        conn = get_db_connection()
        conn.execute('UPDATE borrowings SET book_id = ?, student_id = ?, borrow_date = ?, return_date = ? WHERE id = ?', (book_id, student_id, borrow_date, return_date, id))
        conn.commit()
        conn.close()
        return redirect(url_for('borrowings'))
    conn = get_db_connection()
    borrowing = conn.execute('SELECT * FROM borrowings WHERE id = ?', (id,)).fetchone()
    books = conn.execute('SELECT * FROM books').fetchall()
    students = conn.execute('SELECT * FROM students').fetchall()
    conn.close()
    return render_template('update_borrowing.html', borrowing=borrowing, books=books, students=students)

@app.route('/delete_borrowing/<int:id>')
def delete_borrowing(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM borrowings WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('borrowings'))

if __name__ == '__main__':
    app.run(debug=True)
