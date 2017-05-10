
from flask import Blueprint, render_template, jsonify, request
from bpslibrary import db_session
from bpslibrary.models import Author, Book, Category, ReadingLevel
import requests, json

mod = Blueprint('books', __name__, url_prefix='/books')

@mod.route('/')
def index():
    return render_template('books.html')

@mod.route('/add', methods=['GET', 'POST'])
def add_book():
    error = None
    if request.method == 'GET':
        return render_template('add_book.html')
    if request.method == 'POST':
        isbn = request.form['isbn'].strip()
        book_title = request.form['book_title'].strip()
        found_books = []
        if isbn != '' or book_title != '':
            found_books = find_on_google(isbn, book_title) #'9781509804757', 'The Gruffalo')
        return render_template('add_book.html', found_books=found_books\
                                                , searchTitle=book_title\
                                                , searchIsbn=isbn)

def find_on_google(isbn, title):
    '''Looks up a book on google books api'''
    end_point = 'https://www.googleapis.com/books/v1/volumes?'
    search_query = 'q={0}+isbn:{1}&printType=books'
    search_result = requests.get(end_point + search_query.format(title.replace(' ', '+'), isbn))
    #parse results into books
    found_books = []
    if search_result.status_code == requests.codes.ok:  #pylint: disable=E1101
        total_items = search_result.json()['totalItems']
        if total_items > 0:
            for item in search_result.json()['items']:
                book = Book()
                vol_info = None
                if 'volumeInfo' in item.keys():
                    vol_info = item['volumeInfo']
                    if 'title' in vol_info.keys():
                        book.title = vol_info['title']
                    if 'authors' in vol_info.keys():
                        book.author = Author(str(vol_info['authors']))
                    if 'description' in vol_info.keys():
                        book.preview = vol_info['description']
                    book.isbn13 = vol_info['industryIdentifiers'][0]['identifier']
                    book.isbn10 = vol_info['industryIdentifiers'][1]['identifier']
                    found_books.append(book)
    return found_books

