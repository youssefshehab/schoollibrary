"""A view to handle all user related functionalities.

It includes user and access management functions.
"""

# for some reason, pylint is giving error on wtforms StringField
# pylint: disable=E1101


import csv
import os
from flask import Blueprint, flash, redirect, render_template, request
from flask_login import login_user, logout_user, current_user
from werkzeug.utils import secure_filename
from bpslibrary.database import db_session
from bpslibrary.models import Classroom, Pupil, User
from bpslibrary.forms import LoginForm, NewAccessForm
from bpslibrary.utils.nav import redirect_to_previous
from bpslibrary.utils.permission import admin_access_required


UPLOAD_DIR = '/tmp/'
ALLOWED_EXTENSIONS = set(['csv'])

# pylint: disable=C0103
mod = Blueprint('users', __name__, url_prefix='/users')


@mod.route('/access', methods=['GET'])
@admin_access_required
def access():
    """Render the homepage of user access."""
    return render_template('access.html')


def allowed_file(filename):
    """Check if file is suitable for upload."""
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@mod.route('/update', methods=['GET', 'POST'])
@admin_access_required
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
    """Persist the the details in the file into the database."""
    try:
        session = db_session()
        with open(classroom_file) as csv_file:
            reader = csv.reader(csv_file, delimiter=',', quotechar='"')

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
    except Exception as err:  # pylint: disable=W0703
        flash("Something has gone wrong!<br>" + str(err), 'error')
    return False


@mod.route('/login', methods=['GET', 'POST'])
def login():
    """Login users into the system."""
    if current_user.is_authenticated:
        flash("You are already logged on!")
        return redirect_to_previous()

    login_form = LoginForm()

    if request.method == 'POST':
        if login_form.validate_on_submit():
            user = User.query.filter(User.username.ilike(
                login_form.username.data.lower())).first()

            if user and user.is_correct_password(login_form.password.data):
                login_user(user)
                flash("Logged in successfully!")
                return redirect_to_previous()

        flash("Invalid login details.", 'error')

    return render_template('access.html', login_form=login_form)


@mod.route('/logout', methods=['GET', 'POST'])
def logout():
    """Logout users from the system."""
    if current_user.is_authenticated:
        logout_user()
        flash("Logged out successfully!")
    else:
        flash("You are not logged in!")

    return redirect('')


@mod.route('/add', methods=['GET', 'POST'])
@admin_access_required
def add_user():
    """Give access to a classroom, pupil or admin."""
    session = db_session()
    new_access_form = NewAccessForm()
    new_access_form.classroom.choices = [(0, 'None')] + \
        [(cr[0], '{} ({})'.format(cr[1], cr[2]))
         for cr in session.query(Classroom.id,
                                 Classroom.name,
                                 Classroom.year).distinct()]

    if request.method == 'POST':
        if new_access_form.validate_on_submit():
            # check if it's an existing user
            user = User.query.filter(
                User.username.ilike(new_access_form.username.data)).first()
            # check if a classroom id has been passed
            classroom = Classroom.query.filter(
                Classroom.id == new_access_form.classroom.data).first()

            # for individual user; should be unique
            if user and not classroom:
                flash("This username is already in use, " +
                      "please chose a different username.", 'error')

            # for classroom username/password change, update db
            if user and classroom:
                user.username = new_access_form.username.data
                user.password = new_access_form.password.data
                user.is_admin = new_access_form.is_admin.data
                session.commit()
                flash("Login details have been updated!")

            # for new users, create
            elif not user:
                user = User()
                user.username = new_access_form.username.data
                user.password = new_access_form.password.data
                user.is_admin = new_access_form.is_admin.data

                # link to classroom if provided
                if classroom:
                    classroom.user = user

                session.add(user)
                session.commit()
                flash("Access has been created successfully!")
        else:
            flash("Invalid entries!", 'error')

    return render_template('access.html', new_access_form=new_access_form)
