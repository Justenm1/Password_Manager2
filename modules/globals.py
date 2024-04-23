""" For:
    Configuring the database and flask as globals allows them to be accessed
    by various functions across the project without concern for scope. """

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from modules.secrets import flask_secret


# SQL database connection
db = SQLAlchemy()
print("administrative: (1) database initialized")

# Flask configuration
app = Flask(__name__, template_folder='../templates', static_folder="../static")
app.config["DEBUG"] = True
app.secret_key = flask_secret

# query completeness configuration
app.config['patients'] = 0
app.config['fake_rate'] = 5  # 1 in every n patients will be fake

# database configuration
SQLALCHEMY_DATABASE_URI = "sqlite:///secure_database.sqlite3"

# flask connecting to database
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 280}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.logger.info("administrative: (2) flask configured")

db.init_app(app)
app.logger.info("administrative: (3) flask connected to database")