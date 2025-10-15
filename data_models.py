from flask_sqlalchemy import SQLAlchemy

# Create the SQLAlchemy database instance
db = SQLAlchemy()

# Author model
class Author(db.Model):
    __tablename__ = 'authors'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    birth_date = db.Column(db.Date, nullable=False)
    date_of_death = db.Column(db.Date, nullable=True)

    # Relationship to books
    books = db.relationship('Book', backref='author', lazy=True, cascade="all, delete")

    def __repr__(self):
        return f"<Author {self.id}: {self.name}>"

    def __str__(self):
        return f"Author: {self.name} (born {self.birth_date}, died {self.date_of_death})"


# Book model
class Book(db.Model):
    __tablename__ = 'books'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    isbn = db.Column(db.String(50), unique=True ,nullable=False)
    title = db.Column(db.String(100), nullable=False)
    publication_year = db.Column(db.Integer, nullable=True)

    # Foreign Key
    author_id = db.Column(db.Integer, db.ForeignKey('authors.id'), nullable=False)

    def __repr__(self):
        return f"<Book {self.id}: {self.title}>"

    def __str__(self):
        return f"Book: {self.title} (published {self.publication_year}), ISBN: {self.isbn}"
