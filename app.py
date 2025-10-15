from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from datetime import datetime
import os

from data_models import db, Author, Book

# Create the app
app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(basedir, 'data/library.sqlite')}"
db.init_app(app)


@app.route('/')
def home():
    books = Book.query.all()

    for book in books:
        if book.isbn:
            # Use OpenLibrary cover API
            book.cover_url = f"https://covers.openlibrary.org/b/isbn/{book.isbn}-M.jpg"
        else:
            book.cover_url = None

    return render_template('home.html', books=books)


@app.route('/add_author', methods=['GET', 'POST'])
def add_author():
    message = ""

    if request.method == 'POST':
        author_name = request.form.get('name')
        birth_date_str = request.form.get('birthdate')
        date_of_death_str = request.form.get('date_of_death')

        if not author_name:
            message = "Please enter a author name and birthdate."
        else:
            try:
                birth_date = datetime.strptime(birth_date_str, "%Y-%m-%d").date() if birth_date_str else None
                date_of_death = datetime.strptime(date_of_death_str, "%Y-%m-%d").date() if date_of_death_str else None

                new_author = Author(name=author_name, birth_date=birth_date, date_of_death=date_of_death)
                db.session.add(new_author)
                db.session.commit()
                message = f"Author {author_name} added successfully!"
            except Exception as e:
                db.session.rollback()
                message = f"An error occurred while adding author {author_name} : {e}"

    return render_template('add_author.html', message=message)


@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    message = ""
    authors = Author.query.order_by(Author.name).all()

    if request.method == 'POST':
        book_title = request.form.get('title')
        isbn = request.form.get('isbn')
        publication_year = request.form.get('publication_year')
        author_id = request.form.get('author_id')

        if not book_title or not isbn or not author_id:
            message = "Please enter a book title, ISBN, (optional publication year) and author id."
        else:
            try:
                new_book = Book(title=book_title, isbn=isbn, publication_year=publication_year or None, author_id=int(author_id))
                db.session.add(new_book)
                db.session.commit()
                message = f"Book {book_title} added successfully!"
            except Exception as e:
                db.session.rollback()
                message = f"An error occurred while adding book {book_title} : {e}"

    return render_template('add_book.html', message=message, authors=authors)



# Create the tables, only run once!
#with app.app_context():
#    db.create_all()
