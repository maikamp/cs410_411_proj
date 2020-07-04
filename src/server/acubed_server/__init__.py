from flask import Flask
from .config import Config
from databaseConfig import connection
from databaseConfig import cursor


app = Flask(__name__)
app.config.from_object(Config)

