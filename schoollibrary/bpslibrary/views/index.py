"""Handle the main page functions."""

from flask import Blueprint, render_template
from bpslibrary.database import db_session
from bpslibrary.models import Author, Book, Category

mod = Blueprint('index', __name__)


@mod.route('/')
def index():
    """Render the home page.

    Initialising the search box with books titles, authors names,
    and categories names.
    """
    session = db_session()
    search_terms = []

    for book_title in session.query(Book.title).distinct():
        search_terms.append(book_title[0])

    for category_name in session.query(Category.name).distinct():
        search_terms.append(category_name[0])

    for author_name in session.query(Author.name).distinct():
        search_terms.append(author_name[0])

    search_terms.sort()

    return render_template('home.html', search_terms=search_terms)
