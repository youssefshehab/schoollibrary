"""Handle the main page functions."""

from flask import Blueprint, render_template, jsonify, url_for

mod = Blueprint('index', __name__)


@mod.route('/')
def index():
    """Render the root page."""
    return render_template('home.html')
