
from wtforms import StringField, PasswordField, SelectField
from wtforms.validators import Optional, DataRequired
# from wtforms_alchemy import ModelForm
from flask_wtf import FlaskForm
from bpslibrary.models import Classroom
from bpslibrary import db_session

'''
class BookForm(ModelForm):
    class Meta:
        modle = Book
        include = ['authors']

    thumbnail_url = StringField()
    preview_url = StringField()
'''


class LoginForm(FlaskForm):
    username = StringField(label='Username',
                           validators=[DataRequired()],
                           description="Provided by administration.")
    password = PasswordField(label='Password', validators=[DataRequired()])


class NewAccessForm(FlaskForm):
        
    def get_usernames():
        session = db_session()
        return [(cn[0], cn[0]) for cn
                in session.query(Classroom.name).distinct()]

    username = SelectField(label='Username',
                           validators=[DataRequired()], 
                           choices=get_usernames())
    password = StringField(label='Password', validators=[DataRequired()])

