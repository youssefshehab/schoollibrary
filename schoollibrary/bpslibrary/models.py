"""The entities in the library"""

# pylint: disable=C0103

from sqlalchemy import (Column, String, Integer, Sequence,
                        ForeignKey, Binary, Table)
from sqlalchemy.orm import relationship
# from sqlalchemy.ext.declarative import declarative_base
from bpslibrary import Model


# Associations
book_author_association = \
    Table('book_author_association',
          Model.metadata,
          Column('book_id', Integer, ForeignKey('books.id')),
          Column('author_id', Integer, ForeignKey('authors.id')))


book_category_association = \
    Table('book_category_association',
          Model.metadata,
          Column('book_id', Integer, ForeignKey('books.id')),
          Column('category_id', Integer, ForeignKey('categories.id')))


class ClassRoom(Model):
    '''A school class'''

    # orm required fields
    __tablename__ = 'class_rooms'
    id = Column(Integer,
                Sequence('class_rooms_seq', start=0, increment=1),
                primary_key=True)

    # columns
    name = Column(String, unique=True)
    year = Column(Integer, nullable=False)
    username = Column(String, unique=True)
    password = Column(String, nullable=False)

    # relationships
    pupils = relationship("Pupil", back_populates='class_room')

    def __repr__(self):
        return '<Class %r>' % self.name


class Pupil(Model):
    '''A pupil in the school'''

    # orm required fields
    __tablename__ = 'pupils'
    id = Column(Integer,
                Sequence('pupils_seq', start=0, increment=1),
                primary_key=True)

    # columns
    name = Column(String, nullable=False)

    # relationships
    class_room_id = Column(Integer, ForeignKey('class_rooms.id'))
    class_room = relationship("ClassRoom", back_populates="pupils")

    def __repr__(self):
        return '<Pupil %r>' % self.name


class Category(Model):
    """Category of a book"""

    # orm required fields
    __tablename__ = 'categories'
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
        self.name = name

    def __repr__(self):
        return '<Category %r>' % self.name


class ReadingLevel(Model):
    '''Book reading level'''

    # orm requried fields
    __tablename__ = 'reading_levels'
    id = Column(Integer,
                Sequence('reading_level_seq', start=0, increment=1),
                primary_key=True)

    # columns
    level = Column(String, unique=True)
    age_min = Column(Integer)
    age_max = Column(Integer)

    # relationships
    books = relationship('Book', back_populates='reading_level')

    def __repr__(self):
        return '<ReadingLevel %r age(%r-%r)>' % self.level, self.age_min, self.age_max


class Author(Model):
    """A book author"""

    # orm required fields
    __tablename__ = 'authors'
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

    # books = relationship('BookAuthorAssociation', back_populates='author')

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Author %r>' % self.name


class Book(Model):
    """A book in the library"""

    # orm required fields
    __tablename__ = 'books'
    id = Column(Integer,
                Sequence('books_seq', start=0, increment=1),
                primary_key=True)

    # columns
    isbn10 = Column(String, unique=True, nullable=True)
    isbn13 = Column(String, unique=True, nullable=True)
    title = Column(String)
    description = Column(String)
    image = Column(Binary)
    thumbnail_url = Column(String)
    preview_url = Column(String)

    # relaationships
    reading_level_id = Column(Integer, ForeignKey('reading_levels.id'))
    reading_level = relationship("ReadingLevel", back_populates="books")

    categories = relationship("Category",
                              secondary=book_category_association,
                              back_populates="books")

    authors = relationship('Author',
                           secondary=book_author_association,
                           back_populates='books')

    # author_id = Column(Integer, ForeignKey('authors.id'))
    # authors = relationship('BookAuthorAssociation', back_populates="book")

    def __repr__(self):
        return '<Book %r>' % self.title

    def get_author_name(self):
        '''Returns the names of the author(s)'''

        if len(self.authors) > 1:
            return ', '.join([a.name for a in self.authors])
        else:
            return self.authors[0].name

    def get_category_name(self):
        '''Returns the names of the categories'''

        if len(self.categories) > 1:
            return ', '.join([c.name for c in self.categories])
        elif len(self.categories) == 1:
            return self.categories[0].name
        else:
            return None

    def get_short_description(self):
        '''Returns the first 50 character from the description'''

        if self.description and self.description.strip():
            return self.description[:150] + ' ...'
        return '...'
