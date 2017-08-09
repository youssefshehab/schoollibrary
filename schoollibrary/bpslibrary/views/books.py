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
from bpslibrary.utils.fileuploader import upload_to_tmp
from bpslibrary.utils.barcodereader import scan_image
from bpslibrary.utils.enums import FileType
from bpslibrary.utils.apihandler import APIClient

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
        found_books = []
        barcode_isbn = []
        isbn_list = []
        isbn = request.form['isbn'].strip()
        book_title = request.form['book_title'].strip()
        try:
            if 'barcode' in request.files and \
               not request.files['barcode'].filename == '':
                image_path = upload_to_tmp(request, 'barcode', FileType.IMAGE)
                barcode_isbn = scan_image(image_path)

            if barcode_isbn or isbn or book_title:
                isbn_list.append(isbn)
                isbn_list = set(isbn_list + barcode_isbn)
                api_client = APIClient(isbn_list, book_title)
                found_books = api_client.find_books()

        except ValueError as e:
            flash("Something has gone wrong! <br>" + str(e), 'error')

        return render_template('add_book.html',
                               found_books=found_books,
                               search_title=book_title,
                               search_isbn=isbn,
                               username="Youssef")


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
