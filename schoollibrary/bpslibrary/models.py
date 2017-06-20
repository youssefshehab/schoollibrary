"""The library system entities."""


from sqlalchemy import Column, String, Integer, Sequence, ForeignKey, Table
from sqlalchemy.orm import relationship
from bpslibrary import Model

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


class ClassRoom(Model):
    """A school class."""

    # orm required fields
    __tablename__ = 'class_rooms'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer,
                Sequence('class_rooms_seq', start=0, increment=1),
                primary_key=True)

    # columns
    name = Column(String, unique=True)
    year = Column(Integer, nullable=False)
    username = Column(String, unique=True)
    password = Column(String, nullable=False)

    # relationships
    pupils = relationship('Pupil', back_populates='class_room')

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
    class_room_id = Column(Integer, ForeignKey('class_rooms.id'))
    class_room = relationship('ClassRoom', back_populates='pupils')

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
    id = Column(Integer,
                Sequence('books_seq', start=0, increment=1),
                primary_key=True)

    # columns
    isbn10 = Column(String, unique=True, nullable=True)
    isbn13 = Column(String, unique=True, nullable=True)
    title = Column(String)
    description = Column(String)
    thumbnail_url = Column(String)
    preview_url = Column(String)
    availability = Column(String)

    # relationships
    categories = relationship('Category',
                              secondary=book_category_association,
                              back_populates='books')

    authors = relationship('Author',
                           secondary=book_author_association,
                           back_populates='books')

    @property
    def authors_names(self):
        """Names of the author(s) separated by comma."""
        if len(self.authors) > 1:
            return ", ".join([a.name for a in self.authors])
        elif len(self.authors) == 1:
            return self.authors[0].name

    @property
    def categories_names(self):
        """Names of the categories seperated by comma."""
        if len(self.categories) > 1:
            return ", ".join([c.name for c in self.categories])
        elif len(self.categories) == 1:
            return self.categories[0].name

    @property
    def short_description(self):
        """First 150 characters from the description."""
        if self.description and self.description.strip():
            return self.description[:150] + "..."
        else:
            return "..."

    def __repr__(self):
        return "<Book %r>" % self.title
