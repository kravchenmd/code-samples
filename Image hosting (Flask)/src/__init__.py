from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import config

app = Flask(__name__)
app.config.from_object(config.Config)  # get parameters, including secret key
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # just to remove warning in terminal
app.debug = True  # for auto-restarting the app after edits

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# import only here since routes needs `app` and models need `db`
from src import routes, models
