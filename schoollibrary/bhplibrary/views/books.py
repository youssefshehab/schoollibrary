
from flask import Blueprint, render_template, jsonify
from bhplibrary.database import db_session
from bhplibrary.models import Author, Book, Category, ReadingLevel


mod = Blueprint('books', __name__, url_prefix='/books')

@mod.route('/')
def index():
    return render_template('books.html')

