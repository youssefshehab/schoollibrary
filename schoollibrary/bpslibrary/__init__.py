from flask import Flask


INST_PATH = '/home/youssef/Workspace/projects/schoollibrary/schoollibrary/bpslibrary'
app = Flask(__name__, instance_path=INST_PATH, instance_relative_config=True)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['Debug'] = True

from bpslibrary.database import init_db, db_session

# Initialise the database
init_db()

# now import the views and register them
from bpslibrary.views import books, index
app.register_blueprint(books.mod)
app.register_blueprint(index.mod)

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

if __name__ == '__main__':
    app.run()