

from urllib.parse import urlparse, urljoin
from wtforms.fields import (StringField, PasswordField, SelectField,
                            IntegerField, BooleanField, FileField)
from wtforms.validators import Optional, DataRequired
from flask import request
from flask_wtf import FlaskForm
from bpslibrary.database import get_classroom_names

'''
class BookForm(ModelForm):
    class Meta:
        model = Book
        include = ['authors']

    thumbnail_url = StringField()
    preview_url = StringField()
'''


def is_url_safe(target_url: str):
    host_url = urlparse(request.host_url)
    check_url = urlparse(urljoin(request.host_url, target_url))
    return host_url.netloc == check_url.netloc and \
        check_url.scheme in ('http', 'https')


class LoginForm(FlaskForm):
    username = StringField(label='Username',
                           validators=[Optional()],
                           description="Provided by administration.")
    password = PasswordField(label='Password', validators=[DataRequired()])


class NewAccessForm(FlaskForm):
    """"""
    classroom = SelectField(label='Classroom', validators=[Optional()], coerce=int)
    username = StringField(label='Username', validators=[DataRequired()])
    password = StringField(label='Password', validators=[DataRequired()])
    is_admin = BooleanField(label='Admin', validators=[Optional()])

    def reset(self):
        """Clear the form."""
        self.username = ''
        self.password = ''
        self.is_admin = False


class NewLoanForm(FlaskForm):
    book_id = IntegerField(validators=[DataRequired()])
    book_isbn = StringField(label='ISBN', validators=[DataRequired()])
    user_id = IntegerField(validators=[DataRequired()])
    pupil_id = SelectField(label='Pupil',
                           validators=[DataRequired()],
                           coerce=int,
                           description="The pupil who will borrow this book.")
    barcode_img = FileField(label='Scan Barcode',
                            validators=[DataRequired()],
                            description="Take a picture using tablet/phone " +
                            "camera or upload and image of the barcode.")


class LoanReturnForm(FlaskForm):
    book_id = IntegerField(validators=[DataRequired()])
    barcode_img = FileField(label='Scan Barcode',
                            validators=[DataRequired()],
                            description="Take a picture using tablet/phone " +
                            "camera or upload and image of the barcode.")
