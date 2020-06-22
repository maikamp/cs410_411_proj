# this allows for the rest api to be built for the database
from acubed_server import app
from .database import Database

from flask import request

import json

db = Database()

@app.route('/')
@app.route('/index')
def index():
    return "This is not a valid api."

@app.route('/login', methods = ['POST'])
def login():
    return db.login(request.get_json)

