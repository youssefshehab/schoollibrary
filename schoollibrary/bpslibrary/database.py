
from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from bpslibrary import app

engine = create_engine(app.config['DATABASE_URI'], echo=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Model = declarative_base(name='Model')
Model.query = db_session.query_property()


def init_db():
    """Initialise the database."""
    from bpslibrary.models import Model as md
    md.metadata.create_all(bind=engine)


def get_classroom_names():
    """Return id and name of all classrooms in db."""
    from bpslibrary.models import Classroom
    default = [(-1, 'None')]

    session = db_session()
    return default + [(cr[0], '{} ({})'.format(cr[1], cr[2]))
                      for cr
                      in session.query(Classroom.id,
                                       Classroom.name,
                                       Classroom.year).distinct()]
