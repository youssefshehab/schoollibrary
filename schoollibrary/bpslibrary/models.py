"""The library system entities."""


from sqlalchemy import (Column, String, Integer, Sequence,
                        ForeignKey, Table, Boolean, Date)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property
from flask_login import UserMixin
from bpslibrary import bcrypt
from bpslibrary.database import Model
from bpslibrary.utils.enums import BookLocation

# Associations
book_author_association = \
    Table('book_author_association',
          Model.metadata,
          Column('book_id', Integer, ForeignKey('books.id')),
          Column('author_id', Integer, ForeignKey('authors.id')),
          extend_existing=True)

book_category_association = \
    Table('book_category_association',
          Model.metadata,
          Column('book_id', Integer, ForeignKey('books.id')),
          Column('category_id', Integer, ForeignKey('categories.id')),
          extend_existing=True)


class Classroom(Model):
    """A school class."""

    # orm required fields
    __tablename__ = 'classrooms'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer,
                Sequence('classrooms_seq', start=0, increment=1),
                primary_key=True)

    # columns
    name = Column(String, unique=True)
    year = Column(Integer, nullable=False)

    # relationships
    pupils = relationship('Pupil', back_populates='classroom')
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship('User', back_populates='classroom')

    @property
    def open_loans(self):
        """Open loans for pupils of this classroom."""
        loans = []
        for pupil in self.pupils:
            loans += [loan for loan in pupil.loans if not loan.end_date]
        return loans

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "<Class %r>" % self.name


class Pupil(Model):
    """A pupil in the school."""

    # orm required fields
    __tablename__ = 'pupils'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer,
                Sequence('pupils_seq', start=0, increment=1),
                primary_key=True)

    # columns
    name = Column(String, nullable=False)

    # relationships
    classroom_id = Column(Integer, ForeignKey('classrooms.id'))
    classroom = relationship(
        'Classroom', back_populates='pupils', uselist=False)

    loans = relationship('Loan', back_populates='pupil')

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "<Pupil %r>" % self.name


class Category(Model):
    """Category of a book."""

    # orm required fields
    __tablename__ = 'categories'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer,
                Sequence('categories_seq', start=0, increment=1),
                primary_key=True)

    # columns
    name = Column(String, nullable=False)
    description = Column(String)

    # relationships
    books = relationship('Book',
                         secondary=book_category_association,
                         back_populates='categories')

    def __init__(self, name):
        """Initialise a new Category object."""
        self.name = name

    def __repr__(self):
        return "<Category %r>" % self.name


class Author(Model):
    """A book author."""

    # orm required fields
    __tablename__ = 'authors'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer,
                Sequence('authors_seq', start=0, increment=1),
                primary_key=True)

    # columns
    name = Column(String, nullable=False)
    bio = Column(String)

    # relationships
    books = relationship('Book',
                         secondary=book_author_association,
                         back_populates='authors')

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "<Author %r>" % self.name


class Book(Model):
    """A book in the library."""

    # orm required fields
    __tablename__ = 'books'
    __table_args__ = {'extend_existing': True}

    # columns
    id = Column(Integer,
                Sequence('books_seq', start=0, increment=1),
                primary_key=True)
    isbn10 = Column(String, unique=True, nullable=True)
    isbn13 = Column(String, unique=True, nullable=True)
    title = Column(String)
    description = Column(String)
    thumbnail_url = Column(String)
    preview_url = Column(String)
    availability = Column(String)
    is_available = Column(Boolean)
    current_location = Column(String)

    # relationships
    categories = relationship('Category',
                              secondary=book_category_association,
                              back_populates='books')

    authors = relationship('Author',
                           secondary=book_author_association,
                           back_populates='books')
    loans = relationship('Loan', back_populates='book')

    @property
    def authors_names(self):
        """Names of the author(s) separated by comma."""
        if len(self.authors) > 1:
            return ", ".join([a.name for a in self.authors])
        elif len(self.authors) == 1:
            return str(self.authors[0].name)

    @property
    def categories_names(self):
        """Names of the categories separated by comma."""
        if len(self.categories) > 1:
            return ", ".join([c.name for c in self.categories])
        elif len(self.categories) == 1:
            return str(self.categories[0].name)

    @property
    def short_description(self):
        """First 150 characters from the description."""
        if self.description and self.description.strip():
            return self.description[:150] + "..."
        else:
            return "..."

    @property
    def current_loan(self):
        """Current open loan."""
        current_loan = [loan for loan in
                        sorted(self.loans, key=lambda l: l.id, reverse=True)
                        if not loan.end_date]

        return current_loan[0] if current_loan else None

    def __repr__(self):
        return "<Book %r>" % self.title


class User(Model, UserMixin):
    """Users of the system.

    This class specifies the access details of users.
    """

    # orm fields
    __tablename__ = 'users'
    __table_args__ = {'extend_existing': True}

    # columns
    id = Column(Integer,
                Sequence('users_seq', start=0, increment=1),
                primary_key=True)
    username = Column(String(64), unique=True, nullable=False)
    _password = Column(String(128), nullable=False)
    is_admin = Column(Boolean)

    # relationships
    classroom = relationship('Classroom', back_populates='user', uselist=False)

    @hybrid_property
    def password(self):
        return self._password

    @password.setter
    def _set_password(self, password_text):
        """
        Sets the password property after hashing it.
        
        :param1: password_text (str)
        The password to be hashed.
        """
        self._password = bcrypt.generate_password_hash(password_text)

    def is_correct_password(self, password_text):
        """
        Check the hash of password_text against the saved hash.
        
        """
        return bcrypt.check_password_hash(self._password, password_text)

    def get_id(self):
        """Retrieves the user by id."""
        return str(self.id)


class Loan(Model):
    """Book loan to a pupil."""

    # orm fields
    __tablename__ = 'loans'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer,
                Sequence('loans_seq', start=0, increment=1),
                primary_key=True)

    pupil_id = Column(Integer, ForeignKey('pupils.id'))
    pupil = relationship('Pupil', back_populates='loans', uselist=False)
    book_id = Column(Integer, ForeignKey('books.id'))
    book = relationship('Book', back_populates='loans', uselist=False)

    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)

    def __repr__(self):
        return "<Loan %d (book %d) %s-%s" %\
            (self.id, self.book_id, self.start_date, self.end_date)
