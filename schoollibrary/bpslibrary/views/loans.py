"""
Loans
=====

A view to handle loans and returns of books."""

from datetime import datetime
from flask import Blueprint, flash, render_template, request
from flask_login import login_required, current_user
from sqlalchemy import and_
from werkzeug.utils import secure_filename
from bpslibrary.database import db_session
from bpslibrary.models import Book, Classroom, Pupil, User, Loan
from bpslibrary.utils.nav import redirect_to_previous
from bpslibrary.utils.barcode import scan_for_isbn
from bpslibrary.forms import NewLoanForm, LoanReturnForm
from bpslibrary.utils.enums import BookLocation

mod = Blueprint('loans', __name__, url_prefix='/loans')


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
    
    return redirect_to_previous(True)
