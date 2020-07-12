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

#@app.route('/logout', methods = ['POST'])
#def logout():
#    return redirect(url_for('index'))

@app.route('/testmysql', methods = ['GET'])
def testmysql():
    return db.testmysql()

@app.route('/testmysql/artifact', methods = ['GET'])
def testmysqlArtifact():
    return db.testmysqlArtifact()

@app.route('/testmysql/changerecord', methods = ['GET'])
def testmysqlArtifactChangeRecord():
    return db.testmysqlArtifactChangeRecord()

@app.route('/testmysql/permissionlevel', methods = ['GET'])
def testmysqlPermissionLevel():
    return db.testmysqlPermissionLevel()

@app.route('/testmysql/repository', methods = ['GET'])
def testmysqlRepository():
    return db.testmysqlRepository()

@app.route('/testmysql/tag', methods = ['GET'])
def testmysqlTag():
    return db.testmysqlTag()

@app.route('/testmysql/user', methods = ['GET'])
def testmysqlUser():
    return db.testmysqlUser()

@app.route('/testmysql/bookmarks', methods = ['GET'])
def testmysqlUserBookmarks():
    return db.testmysqlUserBookmarks()

@app.route('/testlevels', methods = ['GET'])
def testlevels():
    return db.testlevels()

@app.route('/register', methods = ['POST'])
def register():
    return db.register(request.get_json())

@app.route('/artifactUpload', methods = ['GET', 'POST'])
def artifactUpload(filename):
    return db.artifactUpload(request.get_json())

@app.route('/addUser', methods = ['GET', 'POST'])
def addUser():
    return db.addUser(request.get_json())

@app.route('/createRepo', methods = ['GET', 'POST'])
def createRepo():
    return db.createRepo(request.get_json())

@app.route('/changePw', methods = ['GET', 'POST'])
def changePw():
    return db.changePw(request.get_json())