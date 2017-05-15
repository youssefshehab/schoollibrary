
from bpslibrary.models import Book
from wtforms import TextField
from wtforms.validators import Optional
from wtforms_alchemy import ModelForm


class BookForm(ModelForm):
    class Meta:
        modle = Book
        include = ['authors']

    thumbnail_url = TextField()
    preview_url = TextField()
