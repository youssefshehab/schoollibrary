"""All forms used within the system."""


from wtforms.fields import (StringField, PasswordField, SelectField,
                            IntegerField, BooleanField, FileField)
from wtforms.validators import Optional, DataRequired
from flask_wtf import FlaskForm


class LoginForm(FlaskForm):
    """Logging on form."""

    username = StringField(label='Username',
                           validators=[Optional()],
                           description="Provided by administration.")
    password = PasswordField(label='Password', validators=[DataRequired()])


class NewAccessForm(FlaskForm):
    """Form to setup new access."""

    classroom = SelectField(label='Classroom',
                            validators=[Optional()],
                            coerce=int)
    username = StringField(label='Username', validators=[DataRequired()])
    password = StringField(label='Password', validators=[DataRequired()])
    is_admin = BooleanField(label='Admin', validators=[Optional()])

    def reset(self):
        """Clear the form."""
        self.username = ''
        self.password = ''
        self.is_admin = False


class NewLoanForm(FlaskForm):
    """Form for book loans."""

    book_id = IntegerField(validators=[DataRequired()])
    book_isbn = StringField(label='ISBN', validators=[DataRequired()])
    user_id = IntegerField(validators=[DataRequired()])
    pupil_id = SelectField(label='Pupil',
                           validators=[DataRequired()],
                           coerce=int,
                           description="The pupil who will borrow this book.")
    barcode_img = FileField(label='Scan Barcode',
                            validators=[DataRequired()],
                            description="Take a picture using tablet/smart-" +
                            "phone camera or upload an image of the barcode.")


class LoanReturnForm(FlaskForm):
    """Form for returning books."""

    book_id = IntegerField(validators=[DataRequired()])
    barcode_img = FileField(label='Scan Barcode',
                            validators=[DataRequired()],
                            description="Take a picture using tablet/phone " +
                            "camera or upload and image of the barcode.")


class UpdateLoanPeriod(FlaskForm):
    """A form for updating the default loan period."""

    loan_period = IntegerField(validators=[DataRequired()],
                               label="Loan period",
                               description="The default period of loans.")
