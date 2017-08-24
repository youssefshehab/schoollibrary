"""A view top handle all user related functionalities.

It includes user and access management function which are
performed by an admin.
"""

import csv
import os
from flask import (Blueprint, flash, redirect,
                   render_template, request, url_for)
from flask_login import login_user, logout_user
from werkzeug.utils import secure_filename
from bpslibrary import db_session
from bpslibrary.models import Classroom, Pupil, User
from bpslibrary.forms import LoginForm, NewAccessForm


UPLOAD_DIR = '/tmp/'
ALLOWED_EXTENSIONS = set(['csv'])

mod = Blueprint('users', __name__, url_prefix='/users')


def allowed_file(filename):
    """Check if file is suitable for upload."""
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@mod.route('/update', methods=['GET', 'POST'])
def update_classroom():
    """Update classroom list of students."""
    session = db_session()
    if request.method == 'GET':
        classrooms = session.query(Classroom).order_by(Classroom.name)
        return render_template('update_classroom.html', classrooms=classrooms)

    if request.method == 'POST':
        try:
            if 'classroom_file' not in request.files:
                raise FileNotFoundError("Could not find the file!")

            classroom_file = request.files['classroom_file']

            if classroom_file.filename == '':
                raise ValueError("No files have been selected.")

            if not allowed_file(classroom_file.filename):
                raise ValueError("This file type is not permitted.")

            if classroom_file:
                filename = secure_filename(classroom_file.filename)
                file_path = os.path.join(UPLOAD_DIR, filename)
                classroom_file.save(file_path)

                if update_db(file_path):
                    flash("Classroom details have been updated successfully!")

        except (FileNotFoundError, ValueError) as error:
            flash("<strong>Error! </strong> %s" % str(error), 'error')
            # pass

        return redirect('users/update')


def update_db(classroom_file):
    try:
        session = db_session()
        with open(classroom_file) as csv_file:
            reader = csv.reader(csv_file, delimiter=',', quotechar='"')

            classrooms = []
            current_classroom = None

            for row in reader:
                if not current_classroom or \
                   not row[0] == current_classroom.name:
                    current_classroom = Classroom(row[0])
                    current_classroom.year = row[1]
                    session.add(current_classroom)
                current_classroom.pupils.append(Pupil(row[2]))

            session.commit()
            return True
    except Exception as err:
        flash("Something has gone wrong!<br>" + str(err), 'error')

    return False


@mod.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm()
    
    if request.method == 'POST':
        if login_form.validate_on_submit():
            user = User.query.filter_by(username=login_form.username.data).first()
            login_user(user)
            flash("Logged in successfully!")
            return redirect('')
        else:
            flash("Please provide login details!")

    return render_template('access.html', login_form=login_form)

    
@mod.route('/logout', methods=['GET', 'POST'])
def logout():
    logout_user()
    flash("Logged out successfully!")
    return redirect('')


@mod.route('/add', methods=['GET', 'POST'])
def add_user():
    new_access_form = NewAccessForm()
    return render_template('access.html', new_access_form=new_access_form)
