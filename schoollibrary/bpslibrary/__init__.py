# pylint: disable=C0413, C0103

"""BPS library system"""


from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
# from flask_zurb_foundation import Foundation


app = Flask(__name__, instance_relative_config=True)
app.config.from_object('bpslibrary_config')

engine = create_engine(app.config['DATABASE_URI'], echo=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))

Model = declarative_base(name='Model')
Model.query = db_session.query_property()

from bpslibrary.models import Model         # noqa
Model.metadata.create_all(bind=engine)

# now import the views and register them
from bpslibrary.views import books, index   # noqa
app.register_blueprint(books.mod)
app.register_blueprint(index.mod)


@app.teardown_appcontext
def shutdown_session(exception=None):
    """Removes the db session when application is terminated"""
    db_session.remove()

# Foundation(app)

if __name__ == '__main__':
    app.run()
