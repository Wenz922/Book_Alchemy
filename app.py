from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
from datetime import datetime
import os

from data_models import db, Author, Book

# Create the app
app = Flask(__name__)
app.secret_key = "supersecretkey"  # For flash messages

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(basedir, 'data/library.sqlite')}"
db.init_app(app)


@app.route('/')
def home():
    # Default sort by title
    sort_by = request.args.get('sort', 'title')
    # Search key
    search_query = request.args.get('q', '').strip()
    query = Book.query.join(Author)

    # SQLAlchemy query and sorting
    if search_query:
        query = query.filter(or_(
            Book.title.ilike(f'%{search_query}%'),
            Book.isbn.ilike(f"%{search_query}%"),
            Author.name.ilike(f'%{search_query}%')))

    if sort_by == 'title':
        query = query.order_by(Book.title)
    elif sort_by == 'author':
        query = query.order_by(Author.name)
    elif sort_by == 'year':
        query = query.order_by(Book.publication_year)

    books = query.all()

    for book in books:
        # Use OpenLibrary cover API
        book.cover_url = f"https://covers.openlibrary.org/b/isbn/{book.isbn}-M.jpg" if book.isbn else None

    message = ""
    if search_query and not books:
        message = f"No books found for {search_query}."

    return render_template('home.html', books=books, sort_by=sort_by, message=message, search_query=search_query)


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


@app.route('/<int:book_id>/delete', methods=['POST'])
def delete_book(book_id):
    try:
        delete_book = Book.query.get(book_id)
        author = delete_book.author  # store reference before deleting book

        db.session.delete(delete_book)
        db.session.commit()

        # Check if author has any books left
        remaining_books = Book.query.filter_by(author_id=author.id).count()
        if remaining_books == 0:
            db.session.delete(author)
            db.session.commit()
            flash(f"Book {delete_book.title} and author {author.name} were deleted successfully!")
        else:
            flash(f"Book {delete_book.title} deleted successfully!")
    except Exception as e:
        db.session.rollback()
        flash(f"Error occurred while deleting book {delete_book.title}: {e}")

    return redirect(url_for('home'))



# Create the tables, only run once!
#with app.app_context():
#    db.create_all()
