'''Handles book repository functionalities'''

# pylint: disable=C0103

import urllib.parse
from flask import Blueprint, render_template, jsonify, request
from bpslibrary import db_session
from bpslibrary.models import Author, Book, ReadingLevel, Category
from bpslibrary.forms import BookForm
import requests

mod = Blueprint('books', __name__, url_prefix='/books')

found_books = []


@mod.route('/')
def index():
    '''Default landing page for books'''

    return render_template('books.html')


@mod.route('/lookup', methods=['GET', 'POST'])
def lookup_book():
    ''' Looks up book details online '''

    global found_books
    found_books = []

    error = None

    if request.method == 'GET':
        return render_template('add_book.html')
    elif request.method == 'POST':
        isbn = request.form['isbn'].strip()
        book_title = request.form['book_title'].strip()

        if isbn or book_title:
            found_books = query_google_books(isbn, book_title)
            # found_books_2 = query_google_books_2(isbn, book_title)
        lookup_results = render_template('add_book.html',
                                         found_books=found_books,
                                         search_title=book_title,
                                         search_isbn=isbn)
        return lookup_results


def query_google_books(isbn, title):
    '''Looks up a book on google books api'''

    # global found_books
    # found_books = []

    api_url = 'https://www.googleapis.com/books/v1/volumes?q={}&printType=books'

    search_query = ''
    if title and title.strip():
        search_query = '+intitle:' + urllib.parse.quote_plus(title)
    if isbn and isbn.strip():
        search_query = search_query + '+isbn:' + isbn

    if not search_query:
        return []

    search_result = requests.get(api_url.format(search_query))

    # parse results into objects
    if search_result.status_code == requests.codes.ok:  # pylint: disable=E1101
        total_items = search_result.json()['totalItems']
        if total_items > 0:
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
                    isbns = vol_info['industryIdentifiers']
                    if '13' in isbns[0]['type']:
                        book.isbn13 = isbns[0]['identifier']
                        book.isbn10 = isbns[1]['identifier']
                    else:
                        book.isbn10 = isbns[0]['identifier']
                        book.isbn13 = isbns[1]['identifier']

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

                    # reading level

                    found_books.append(book)
    return sorted(found_books, key=lambda b: b.title)


def query_google_books_2(isbn, title):
    '''Looks up a book on google books api'''

    api_url = 'https://www.googleapis.com/books/v1/volumes?q={}&printType=books'

    search_query = ''
    if title and title.strip():
        search_query = '+intitle:' + urllib.parse.quote_plus(title)
    if isbn and isbn.strip():
        search_query = search_query + '+isbn:' + isbn
    search_result = requests.get(api_url.format(search_query))

    if not search_query:
        return []

    # parse results into objects
    found_books_2 = []
    if search_result.status_code == requests.codes.ok:  # pylint: disable=E1101
        total_items = search_result.json()['totalItems']
        if total_items > 0:
            for item in search_result.json()['items']:
                book_form = BookForm()
                vol_info = None
                if 'volumeInfo' in item.keys():
                    vol_info = item['volumeInfo']

                    # book title
                    if 'title' in vol_info.keys():
                        book_form.title = vol_info['title']

                    # description
                    if 'description' in vol_info.keys():
                        book_form.description = vol_info['description']

                    # isbn(s)
                    isbns = vol_info['industryIdentifiers']
                    if '13' in isbns[0]['type']:
                        book_form.isbn13 = isbns[0]['identifier']
                        book_form.isbn10 = isbns[1]['identifier']
                    else:
                        book_form.isbn10 = isbns[0]['identifier']
                        book_form.isbn13 = isbns[1]['identifier']

                    # author(s)
                    # if 'authors' in vol_info.keys():
                    #    for author_name in vol_info['authors']:
                    #        book_form.authors.append(Author(author_name))

                    # category
                    if 'categories' in vol_info.keys():
                        book_form.category = vol_info['categories'][0]

                        # for category in vol_info['categories']:
                        #    book_form.categories.append(Category(category))

                    # thumbnail
                    if 'imageLinks' in vol_info.keys():
                        book_form.thumbnail_url = vol_info['imageLinks']['thumbnail']

                    # preview link
                    if 'previewLink' in vol_info.keys():
                        book_form.preview_url = vol_info['previewLink']

                    # reading level

                    found_books_2.append(book_form)
    return sorted(found_books_2, key=lambda b: b.title)


@mod.route('/add', methods=['GET', 'POST'])
def add_book():
    '''Validates entries and adds the book to the library.'''

    global found_books

    book_index = 0
    if request.form['book_id']:
        book_index = int(request.form['book_id'])

    book = found_books[book_index]

    dbsession = db_session()

    dbsession.add(book)
    dbsession.commit()

    return render_template('add_book.html')


def validate_add_book():
    return None


@mod.route('/view', methods=['GET'])
def view_book():
    dbsession = db_session()

    books = Book.query.all()

    return render_template('view_book.html', books=books)
