"""
    BPS library system
    ==================

    A primary school library system aimed at aiding the administration
    of the library and enhancing its effectiveness.
    
    :copyright:
    
    Copyright (C) 2017 Youssef Shehab

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program. If not, see <http://www.gnu.org/licenses/>.
"""

from flask import Flask
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base


def init_database():
    """Call for init_db to initialise the database."""
    from bpslibrary.database import init_db
    init_db()


def register_views():
    """Register the flask blueprint views."""
    from bpslibrary.views import books, index, users, loans
    app.register_blueprint(books.mod)
    app.register_blueprint(index.mod)
    app.register_blueprint(users.mod)
    app.register_blueprint(loans.mod)


# create app and import config
app = Flask(__name__, instance_relative_config=True)
app.config.from_object('bpslibrary_config')

# create password hasher
bcrypt = Bcrypt(app)

# create login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'users.login'

# initialise database
init_database()

# register the views
register_views()


@login_manager.user_loader
def load_user(userid):
    """The callback for reloading a user from the session."""
    from bpslibrary.models import User
    return User.query.filter(User.id == int(userid)).first()


@app.teardown_appcontext
def shutdown_session(exception=None):
    """Removes the db session when application is terminated."""
    from bpslibrary.database import db_session
    db_session.remove()


if __name__ == '__main__':
    app.run()
