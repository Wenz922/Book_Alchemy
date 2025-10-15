from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
import os

from data_models import db, Author, Book

# Create the app
app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(basedir, 'data/library.sqlite')}"
db.init_app(app)


@app.route('/add_author', methods=['GET', 'POST'])
def add_author():
    message = ""

    if request.method == 'POST':
        author_name = request.form.get('name')
        birth_date = request.form.get('birthdate')
        date_of_death = request.form.get('date_of_death')

        if not author_name:
            message = "Please enter a author name."
        else:
            try:
                new_author = Author(name=author_name, birth_date=birth_date, date_of_death=date_of_death or None)
                db.session.add(new_author)
                db.session.commit()
                message = f"Author {author_name} added successfully!"
            except Exception as e:
                db.session.rollback()
                message = f"An error occurred while adding author {author_name} : {e}"

    return render_template('add_author.html', message=message)


# Create the tables, only run once!
#with app.app_context():
#    db.create_all()
