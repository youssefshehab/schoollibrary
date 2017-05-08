from sqlalchemy import Column, String, Integer, Sequence, ForeignKey, Binary
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from . import Model


class ClassRoom(Model):
    '''A school class'''
    __tablename__ = 'class_rooms'
    id = Column(Integer, Sequence('class_rooms_seq', start=0, increment=1), primary_key=True)
    name = Column(String, unique=True)
    year = Column(Integer, nullable=False)
    username = Column(String, unique=True)
    password = Column(String, nullable=False)
    pupils = relationship("Pupil", back_populates='class_room')

    def __repr__(self):
        return '<Class %r>' % self.name


class Pupil(Model):
    '''A pupil in the school'''
    __tablename__ = 'pupils'
    id = Column(Integer, Sequence('pupils_seq', start=0, increment=1), primary_key=True)
    name = Column(String, nullable=False)
    class_room_id = Column(Integer, ForeignKey('class_rooms.id'))
    class_room = relationship("ClassRoom", back_populates="pupils")

    def __repr__(self):
        return '<Pupil %r>' % self.name


class Author(Model):
    """A book author"""
    __tablename__ = 'authors'
    id = Column(Integer, Sequence('authors_seq', start=0, increment=1), primary_key=True)
    name = Column(String, nullable=False)
    bio = Column(String)

    books = relationship("Book", back_populates='author')

    def __init__(self, name):
        self.name = name
    
    def __repr__(self):
        return '<Author %r>' % self.name


class Category(Model):
    """Category of a book"""
    __tablename__ = 'categories'
    id = Column(Integer, Sequence('categories_seq', start=0, increment=1), primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String)
    books = relationship('Book', back_populates='category')

    def __init__(self, name):
        self.name = name
    
    def __repr__(self):
        return '<Category %r>' % self.name

class ReadingLevel(Model):
    '''Book reading level'''
    __tablename__ = 'reading_levels'
    id = Column(Integer, Sequence('reading_level_seq', start=0, increment=1), primary_key=True)
    level = Column(String, unique=True)
    age_min = Column(Integer)
    age_max = Column(Integer)
    books = relationship('Book', back_populates='reading_level')

    def __repr__(self):
        return '<ReadingLevel %r age(%r-%r)>' % self.level, self.age_min, self.age_max


class Book(Model):
    """A book in the library"""
    __tablename__ = 'books'
    id = Column(Integer, Sequence('books_seq', start=0, increment=1), primary_key=True)
    isbn10 = Column(String, unique=True, nullable=True)
    isbn13 = Column(String, unique=True, nullable=True)
    title = Column(String)
    preview = Column(String)
    category_id = Column(Integer, ForeignKey('categories.id'))
    category = relationship("Category", back_populates="books")
    author_id = Column(Integer, ForeignKey('authors.id'))
    author = relationship("Author", back_populates="books")
    reading_level_id = Column(Integer, ForeignKey('reading_levels.id'))
    reading_level = relationship("ReadingLevel", back_populates="books")
    image = Column(Binary)

    def __repr__(self):
        return '<Book %r>' % self.title

