"""Handle book repository functionalities."""

# pylint: disable=C0103

from urllib import request as urllib_request
import urllib.parse
import re
import requests
from flask import Blueprint, flash, redirect, render_template, request
from sqlalchemy import exc, or_, update
from bpslibrary import db_session
from bpslibrary.models import Author, Book, Category


mod = Blueprint('books', __name__, url_prefix='/books')
IMG_DIR = 'bpslibrary/static/img/'


@mod.route('/')
def index():
    """Render the default landing page for books."""
    return view_books()


@mod.route('/lookup', methods=['GET', 'POST'])
def lookup_book():
    """Look up book details online."""
    if request.method == 'GET':
        return render_template('add_book.html')

    if request.method == 'POST':
        lookup_results = render_template('add_book.html')
        try:
            isbn = request.form['isbn'].strip()
            book_title = request.form['book_title'].strip()

            if isbn or book_title:
                found_books = query_google_books(isbn, book_title)

                lookup_results = render_template('add_book.html',
                                                 found_books=found_books,
                                                 search_title=book_title,
                                                 search_isbn=isbn,
                                                 username="Youssef")
        except Exception as e:
            flash("Something has gone wrong! <br>" + str(e), 'error')
        return lookup_results


def query_google_books(isbn: str, title: str):
    """Look up a book on google books api.

    This method uses the `Volumes: list` method. It is designed for v1
    of the API.
    (https://developers.google.com/books/docs/v1/reference/volumes/list)
    """
    search_query = ''
    api_url = \
        'https://www.googleapis.com/books/v1/volumes?q={}&printType=books'

    if title and title.strip():
        search_query = '+intitle:' + urllib.parse.quote_plus(title)
    if isbn and isbn.strip():
        search_query = search_query + '+isbn:' + isbn

    if not search_query:
        return

    search_result = requests.get(api_url.format(search_query))

    # parse results into Book objects
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
    try:
        book = Book()
        book.is_available = 1
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
            category = Category.query.\
                filter(Category.name == category_name).first()
            if not category:
                category = Category(category_name)
            book.categories.append(category)

        thumbnail_url = request.form['thumbnail_url'].strip()
        if thumbnail_url:
            title = [c for c in book.title.replace(' ', '_')
                     if re.match(r'\w', c)]
            image_name = ''.join(title) + book.isbn13 + '.jpg'

            img = open(IMG_DIR + image_name, 'wb')
            img.write(urllib_request.urlopen(thumbnail_url).read())
            book.thumbnail_url = image_name

        dbsession = db_session()
        dbsession.add(book)
        dbsession.commit()
        flash("The book has been added to the library successfully!")
    except Exception as e:
        error_message = "Something has gone wrong!"
        if isinstance(e, exc.IntegrityError):
            error_message += "<br>It seems that the book '%s' "\
                "already exists in the library." % book.title

        flash(error_message, 'error')

    return render_template('add_book.html')


def validate_add_book():
    """Validate books on addition or modification."""
    return None


@mod.route('/edit', methods=['GET', 'POST'])
def edit_book():
    """Update a book in the library."""
    session = db_session()

    if request.method == 'GET':
        lookup_isbns = []
        lookup_titles = []
        books = session.query(Book).distinct().\
            values(Book.isbn10,
                   Book.isbn13,
                   Book.title)

        for book in books:
            lookup_isbns.append(book[0])
            lookup_isbns.append(book[1])
            lookup_titles.append(book[2])

        lookup_isbns.sort()
        lookup_titles.sort()
        return render_template('edit_book.html',
                               lookup_isbns=lookup_isbns,
                               lookup_titles=lookup_titles)

    found_books = []

    if request.method == 'POST':
        search_isbn = request.form['search_isbn']
        search_title = request.form['search_title']

        if search_title and search_title.strip():
            search_term = '%' + search_title.strip() + '%'
            found_books = session.query(Book).\
                filter(Book.title.ilike(search_term))

        if search_isbn and search_isbn.strip():
            search_term = '%' + search_isbn.strip() + '%'
            found_books = found_books + session.query(Book).\
                filter(or_(Book.isbn10.ilike(search_term),
                           Book.isbn13.ilike(search_term)))

    result = render_template('edit_book.html',
                             search_isbn=search_isbn,
                             search_title=search_title,
                             found_books=sorted(found_books,
                                                key=lambda b: b.title),
                             username="Youssef")
    return result


@mod.route('/update', methods=['POST'])
def update_book():
    """Update a book with provided details."""
    try:
        session = db_session()

        book_id = request.form['book_id']
        book_status = int(request.form['book_status'])

        session.query(Book).filter(Book.id == book_id).update(
            {Book.is_available: book_status},
            synchronize_session=False)
        session.commit()

        flash("The book has been updated successfully!")
    except Exception as e:
        flash("Something has gone wrong! <br>%s" % str(e), 'error')

    return redirect('books/edit')


@mod.route('/view', methods=['GET'])
def view_books():
    """Display books in the library.

    Defaults to displaying available books only.
    If `include_unavailable` parameter is set in the `request`,
    it display all books; this is used in the admin view all.
    """
    session = db_session()
    include_unavailable = request.args.get('include-unavailable')
    if include_unavailable:
        books = session.query(Book).order_by(Book.title)
    else:
        books = session.query(Book).filter(Book.is_available == 1).\
            order_by(Book.title)
    return render_template('view_book.html', books=books, username="Youssef")


@mod.route('/find', methods=['POST'])
def find_books():
    """Find books in the library based on the search term.

    Search term can be a full or partial book title, author name or
    category name.
    """
    search_term = request.form["search_term"]

    if search_term and search_term.strip():
        search_term = '%' + search_term.strip() + '%'
        session = db_session()

        books = session.query(Book).\
            join(Author.books).\
            filter(or_(Book.title.ilike(search_term),
                       Author.name.ilike(search_term))).\
            union(
                session.query(Book).
                join(Category.books).
                filter(or_(Book.title.ilike(search_term),
                           Category.name.ilike(search_term)))
            ).\
            order_by(Book.title)

    if not search_term or not books:
        return view_books()

    return render_template('view_book.html', books=books)
