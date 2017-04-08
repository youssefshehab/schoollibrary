from flask import Blueprint, render_template, jsonify, url_for

mod = Blueprint('index', __name__)

@mod.route('/')
def index():
    return render_template('base.html')