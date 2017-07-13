"""Handle book repository functionalities."""

# pylint: disable=C0103

from urllib import request as urllib_request
import urllib.parse
import re
import requests
import logging
import sys
from flask import Blueprint, render_template, request
from bpslibrary import db_session
from bpslibrary.models import Author, Book, Category


mod = Blueprint('books', __name__, url_prefix='/books')


@mod.route('/')
def index():
    """Render the default landing page for books."""
    return render_template('books.html')


@mod.route('/lookup', methods=['GET', 'POST'])
def lookup_book():
    """Look up book details online."""
    error = None

    if request.method == 'GET':
        return render_template('add_book.html')

    if request.method == 'POST':
        try:
            isbn = request.form['isbn'].strip()
            book_title = request.form['book_title'].strip()

            if isbn or book_title:
                found_books = query_google_books(isbn, book_title)

                lookup_results = render_template('add_book.html',
                                                 found_books=found_books,
                                                 search_title=book_title,
                                                 search_isbn=isbn)
        except:
            error = sys.exc_info()[0]
            lookup_results = render_template('add_book.html')
        return lookup_results


def query_google_books(isbn, title):
    """Look up a book on google books api."""
    search_query = ''
    api_url = 'https://www.googleapis.com/books/v1/volumes?q={}&printType=books'

    if title and title.strip():
        search_query = '+intitle:' + urllib.parse.quote_plus(title)
    if isbn and isbn.strip():
        search_query = search_query + '+isbn:' + isbn

    if not search_query:
        return []

    search_result = requests.get(api_url.format(search_query))

    # parse results into objects
    if search_result.status_code != requests.codes.ok:  # pylint: disable=E1101
        return []

    total_items = search_result.json()['totalItems']
    if total_items < 0:
        return []

    found_books = []

    for item in search_result.json()['items']:
        book = Book()
        vol_info = None
        if 'volumeInfo' in item.keys():
            vol_info = item['volumeInfo']

            # book title
            if 'title' in vol_info.keys():
                book.title = vol_info['title']

            # description
            if 'description' in vol_info.keys():
                book.description = vol_info['description']

            # isbn(s)
            if 'industryIdentifiers' in vol_info.keys():
                for ident in vol_info['industryIdentifiers']:
                    if ident['type'] == 'ISBN_13':
                        book.isbn13 = ident['identifier']
                    elif ident['type'] == 'ISBN_10':
                        book.isbn10 = ident['identifier']

            # author(s)
            if 'authors' in vol_info.keys():
                for author_name in vol_info['authors']:
                    book.authors.append(Author(author_name))

            # categories
            if 'categories' in vol_info.keys():
                for category_name in vol_info['categories']:
                    book.categories.append(Category(category_name))

            # thumbnail
            if 'imageLinks' in vol_info.keys():
                book.thumbnail_url = vol_info['imageLinks']['thumbnail']

            # preview link
            if 'previewLink' in vol_info.keys():
                book.preview_url = vol_info['previewLink']

            found_books.append(book)

    return sorted(found_books, key=lambda b: b.title)


@mod.route('/add', methods=['POST'])
def add_book():
    """Add a book to the library."""
    book = Book()
    book.title = request.form['book_title'].strip()
    book.isbn10 = request.form['isbn10'].strip()
    book.isbn13 = request.form['isbn13'].strip()
    book.description = request.form['book_description'].strip()
    book.preview_url = request.form['preview_url'].strip()

    for author_name in request.form['book_authors'].split(','):
        author_name = author_name.strip()
        author = Author.query.filter(Author.name == author_name).first()
        if not author:
            author = Author(author_name)
        book.authors.append(author)

    for category_name in request.form['book_categories'].split(','):
        category_name = category_name.strip()
        category = Category.query.filter(Category.name == category_name).first()
        if not category:
            category = Category(category_name)
        book.categories.append(category)

    thumbnail_url = request.form['thumbnail_url'].strip()
    if thumbnail_url:
        image_name = ''.join([c for c in book.title.replace(' ', '_')
                              if re.match(r'\w', c)]) + book.isbn13 + '.jpg'

        img = open('bpslibrary/static/img/' + image_name, 'wb')
        img.write(urllib_request.urlopen(thumbnail_url).read())
        book.thumbnail_url = image_name

    dbsession = db_session()
    dbsession.add(book)
    dbsession.commit()

    return render_template('add_book.html')


def validate_add_book():
    """Validate books on addition or modification."""
    return None


@mod.route('/view', methods=['GET'])
def view_books():
    """Display all books in the library."""
    session = db_session()
    books = session.query(Book).order_by(Book.title)
    return render_template('view_book.html', books=books)


@mod.route('/find', methods=['GET', 'POST'])
def find_books():
    """Find books in the library based on the search term."""
    session = db_session()
    books = session.query(Book).order_by(Book.title)
    return render_template('view_book.html', books=books)
