from flask import Flask

from flask_migrate import Migrate
from config import config


from src.db_init import db

app = Flask(__name__)
app.config.from_object(config.Config)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # just to remove warning in terminal
app.debug = True  # for auto-restarting the app after edits


db.init_app(app)
migrate = Migrate(app, db, render_as_batch=True)  # enable batch mode to solve issue with ALTER when dropping a column


# import only here since routes needs `app` and models need `db`
from src import routes, models
