"""Configuration of the system."""


import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

DEBUG = True

# secret key
SECRET_KEY = 'dev'

# database
DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR,
                                           'bpslibrary/bpslibrary.db')
DATABASE_CONNECT_OPTIONS = {}
SQLALCHEMY_TRACK_MODIFICATIONS = False

# password hashing
BCRYPT_LOG_ROUNDS = 12

# pagination
PER_PAGE = 15

# thumbnails
THUMBNAILS_ABSOLUTE_DIR = os.path.join(BASE_DIR,
                                       'bpslibrary/static/img/thumbnails/')
THUMBNAILS_DIR = 'img/thumbnails/'

# api keys
AWS_ACCESS_KEY = 'dev'
AWS_SECRET_KEY = 'dev'
AWS_ASSOCIATE_TAG = 'dev'
GOOGLE_API_KEY = 'dev'
EBAY_APPNAME = 'dev'

del os
