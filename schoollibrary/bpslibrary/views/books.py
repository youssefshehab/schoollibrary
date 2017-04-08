
from flask import Blueprint, render_template, jsonify, request
from bpslibrary.database import db_session
from bpslibrary.models import Author, Book, Category, ReadingLevel


mod = Blueprint('books', __name__, url_prefix='/books')

@mod.route('/')
def index():
    return render_template('books.html')

@mod.route('/add', methods=['GET', 'POST'])
def add_book():
    error = None
    if request.method == 'GET':
        return render_template('add_book.html')       

