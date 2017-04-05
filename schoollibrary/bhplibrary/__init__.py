from flask import Flask

INST_PATH = '/home/youssef/Workspace/py/schoollibrary/bhplibrary'
app = Flask(__name__, instance_path=INST_PATH, instance_relative_config=True)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['Debug']=True

from bhplibrary.database import init_db, db_session

init_db()

#import bhplibrary.views
#import bhplibrary.models

from bhplibrary.views import books, index
app.register_blueprint(books.mod)
app.register_blueprint(index.mod)

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

if __name__ == '__main__':
    app.run()
