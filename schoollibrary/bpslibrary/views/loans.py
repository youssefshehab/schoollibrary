"""
Loans
=====

A view to handle loans and returns of books."""

from datetime import datetime
from flask import Blueprint, flash, render_template, request
from flask_login import login_required, current_user
from flask_paginate import Pagination, get_page_parameter
from sqlalchemy import and_
from werkzeug.utils import secure_filename
from bpslibrary import app
from bpslibrary.database import db_session
from bpslibrary.models import Book, Classroom, Pupil, User, Loan
from bpslibrary.utils.nav import redirect_to_previous
from bpslibrary.utils.barcode import scan_for_isbn
from bpslibrary.forms import NewLoanForm, LoanReturnForm
from bpslibrary.utils.enums import BookLocation


mod = Blueprint('loans', __name__, url_prefix='/loans')
THUMBNAILS_DIR = app.config['THUMBNAILS_DIR']
PER_PAGE = app.config['PER_PAGE']


@mod.route('/record', methods=['POST'])
@login_required
def record_loan():
    """Records loan of a book to a pupil."""
    session = db_session()
    new_loan_form = NewLoanForm()

    class_id = current_user.classroom.id
    new_loan_form.pupil_id.choices = \
        [(p[0], p[1]) for p in session.query(Pupil.id, Pupil.name).
         filter(Pupil.classroom_id == class_id)]
    try:
        user = User.query.filter(
            User.id == int(new_loan_form.user_id.data)
            ).first()
        pupil = Pupil.query.filter(
            Pupil.id == int(new_loan_form.pupil_id.data)
            ).first()
        book = Book.query.filter(
            Book.id == int(new_loan_form.book_id.data)
            ).first()

        if not user or not pupil or not book:
            raise ValueError(
                "Invalid entries! Book: %s; Pupil: %s; User: %s" %
                (str(book), str(pupil), str(user))
            )

        if not new_loan_form.barcode_img.data:
            raise ValueError(
                "No barcode image provided. Please scan the barcode."
            )

        isbnlist = scan_for_isbn(request.files[new_loan_form.barcode_img.name])

        if len(isbnlist) < 1:
            raise ValueError(
                "No ISBN found in provided image."
            )

        if book.isbn13 not in isbnlist:
            raise ValueError(
                "Barcode does not match selected book."
            )

        loan = Loan()
        loan.pupil = pupil
        loan.book = book
        loan.start_date = datetime.date(datetime.now())

        book.current_location = BookLocation.LOAN.value

        session.add(loan)
        session.commit()
        flash("Loan has been recorded for '%s' to %s" %
              (book.title, pupil.name))

    except ValueError as val_err:
        flash(str(val_err), 'error')

    return redirect_to_previous(True)


@mod.route('/return', methods=['POST'])
@login_required
def record_return():
    """Records return of a book."""
    session = db_session()
    loan_return_form = LoanReturnForm()

    try:
        book = Book.query.filter(
            Book.id == int(loan_return_form.book_id.data)
            ).first()

        if not book:
            raise ValueError("Invalid entries!")

        if not loan_return_form.barcode_img.data:
            raise ValueError(
                "No barcode image provided. Please scan the barcode.")

        isbnlist = scan_for_isbn(
            request.files[loan_return_form.barcode_img.name])

        if len(isbnlist) < 1:
            raise ValueError("No ISBN found in provided image.")

        if book.isbn13 not in isbnlist:
            raise ValueError("Barcode does not match selected book.")

        loan = book.current_loan

        if not loan:
            raise ValueError("No loans found for this book.")

        loan.end_date = datetime.date(datetime.now())
        book.current_location = BookLocation.LIBRARY.value

        session.commit()
        flash("Book return has been recorded for '%s' by %s" %
              (book.title, loan.pupil.name))

    except ValueError as val_err:
        flash(str(val_err), 'error')
    return redirect_to_previous(True)


@mod.route('/view', methods=['GET'])
@login_required
def view_loans():
    """Displays loans of a book, or of all books."""
    session = db_session()
    if current_user.is_admin:
        found_books = session.query(Book).filter(
            Book.current_location == BookLocation.LOAN.value).all()
    else:
        found_books = session.query(Book).filter(
            Book.current_location == BookLocation.LOAN.value and
            Book.id in [l.book_id for l in Classroom.query(
                Classroom.user_id == current_user.id).open_loans]).all()

    # pagination
    total = len(found_books)
    page = request.args.get(get_page_parameter(), type=int, default=1)
    pagination = Pagination(page=page,
                            total=total,
                            per_page=PER_PAGE,
                            css_framework="bootstrap3")

    # initialise loan forms
    new_loan_form, loan_return_form = init_loan_forms()

    return render_template('loans.html',
                           books=found_books,
                           new_loan_form=new_loan_form,
                           loan_return_form=loan_return_form,
                           pagination=pagination,
                           thumbnails_dir=THUMBNAILS_DIR)


def init_loan_forms():
    """Initialise a new_loan and loan_return forms."""
    session = db_session()

    new_loan_form = None
    loan_return_form = None

    if current_user.is_authenticated:
        loan_return_form = LoanReturnForm()
        if current_user.classroom:
            new_loan_form = NewLoanForm()
            class_id = current_user.classroom.id
            new_loan_form.pupil_id.choices = \
                [(p[0], p[1]) for p in session.query(Pupil.id, Pupil.name).
                 filter(Pupil.classroom_id == class_id)]

    return new_loan_form, loan_return_form
