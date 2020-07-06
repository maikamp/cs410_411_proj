# this allows for the rest api to be built for the database
from acubed_svr import app
from .database import Database
from flask import request

import json

db = Database()

@app.route('/')
@app.route('/index')
def index():
    return 'This is not a valid api.'

@app.route('/test')
def test():
    return 'This is a test route.'

@app.route('/login', methods = ['POST'])
def login():
    return db.login(request.get_json(force=True))

@app.route('/testmysql', methods = ['GET'])
def testmysql():
    return db.testmysql()

@app.route('/testlevels', methods = ['GET'])
def testlevels():
    return db.testlevels()