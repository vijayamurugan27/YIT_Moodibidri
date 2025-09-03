# app/routes/book_routes.py
from flask import Blueprint, request, render_template, redirect, url_for
from app.models.book import Book
from app import db

book_routes = Blueprint('book_routes', __name__)

@book_routes.route('/')
@book_routes.route('/books')
def index():
    books = Book.query.all()
    return render_template('index.html', books=books)

@book_routes.route('/add', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        new_book = Book(title=request.form['title'], author=request.form['author'])
        db.session.add(new_book)
        db.session.commit()
        return redirect(url_for('book_routes.index'))
    return render_template('add_book.html')

@book_routes.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_book(id):
    book = Book.query.get_or_404(id)
    if request.method == 'POST':
        book.title = request.form['title']
        book.author = request.form['author']
        db.session.commit()
        return redirect(url_for('book_routes.index'))
    return render_template('edit_book.html', book=book)

@book_routes.route('/delete_confirm/<int:id>')
def delete_confirm(id):
    book = Book.query.get_or_404(id)
    return render_template('delete_book.html', book=book)

@book_routes.route('/delete/<int:id>', methods=['POST'])
def delete_book(id):
    book = Book.query.get_or_404(id)
    db.session.delete(book)
    db.session.commit()
    return redirect(url_for('book_routes.index'))
