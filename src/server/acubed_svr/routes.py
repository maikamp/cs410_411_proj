# this allows for the rest api to be built for the database
from acubed_svr import app
from .database import Database
from .testDatabase import TestDatabase
from flask import request

import json

db = Database()
testdb = TestDatabase()

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
    return testdb.testmysql()

@app.route('/testmysql/artifact', methods = ['GET'])
def testmysqlartifact():
    return testdb.testmysqlArtifact()

@app.route('/testmysql/changerecord', methods = ['GET'])
def testmysqlArtifactChangeRecord():
    return testdb.testmysqlArtifactChangeRecord()

@app.route('/testmysql/permissionlevel', methods = ['GET'])
def testmysqlPermissionLevel():
    return testdb.testmysqlPermissionLevel()

@app.route('/testmysql/repository', methods = ['GET'])
def testmysqlRepository():
    return testdb.testmysqlRepository()

@app.route('/testmysql/tag', methods = ['GET'])
def testmysqlTag():
    return testdb.testmysqlTag()

@app.route('/testmysql/user', methods = ['GET'])
def testmysqlUser():
    return testdb.testmysqlUser()

@app.route('/testmysql/bookmarks', methods = ['GET'])
def testmysqlUserBookmarks():
    return testdb.testmysqlUserBookmarks()

@app.route('/testlevels', methods = ['GET'])
def testlevels():
    return testdb.testlevels()

@app.route('/adduser', methods = ['POST'])
@app.route('/register', methods = ['POST'])
def register():
    return db.register(request.get_json(force=True))

@app.route('/artifactupload', methods = ['GET', 'POST'])
def artifactupload():
    return db.artifact_upload(request.files['file'], request.files['meta-data'])
    #return db.artifactUpload(request.files['meta-data', 'file'])

@app.route('/artifactscrape', methods = ['GET', 'POST'])
def artifactscrape():
    return db.artifact_scrape(request.get_json(force=True))

#@app.route('/adduser', methods = ['GET', 'POST'])
#def adduser():
#    return db.addUser(request.get_json(force=True))

@app.route('/createrepo', methods = ['GET', 'POST'])
def createrepo():
    return db.create_repo(request.get_json(force=True))

@app.route('/changepw', methods = ['GET', 'POST'])
def changepw():
    return db.change_pw(request.get_json(force=True))

@app.route('/changeusername' ,methods = ['GET', 'POST'])
def changeusername():
    return db.change_username(request.get_json(force=True))

@app.route('/updaterepoattrib' ,methods = ['GET', 'POST'])
def updaterepoattrib():
    return db.update_repo_attrib(request.get_json(force=True))

@app.route('/updateartifactattrib' ,methods = ['GET', 'POST'])
def updateartifactattrib():
    return db.update_artifact_attrib(request.get_json(force=True))

#@app.route('/updateartifact' ,methods = ['GET', 'POST'])
#def updateartifact():

@app.route('/returnartifactinfo' ,methods = ['GET', 'POST'])
def returnartifactinfo():
    return db.artifact_info(request.get_json(force=True))

@app.route('/returnrepoinfo' ,methods = ['GET', 'POST'])
def returnrepoinfo():
    return db.repo_info(request.get_json(force=True))

@app.route('/simplecompare' ,methods = ['GET', 'POST'])
def simplecompare():
    return db.simple_compare(request.get_json(force=True))

@app.route('/diff' ,methods = ['GET', 'POST'])
def diff():
    return db.diff(request.get_json(force=True))
'''
@app.route('/removerepo' ,methods = ['GET', 'POST'])
def removerepo():

@app.route('/removeartifact' ,methods = ['GET', 'POST'])
def removeartifact():

@app.route('/removeuser' ,methods = ['GET', 'POST'])
def removeuser()):

@app.route('/removeartifact' ,methods = ['GET', 'POST'])
def removeartifact():
'''
@app.route('/exportartifact' ,methods = ['GET', 'POST'])
def exportartifact():
    return db.export_artifact(request.get_json(force=True))

@app.route('/addtag' ,methods = ['GET', 'POST'])
def addtag():
    return db.add_tag(request.get_json(force=True))

@app.route('/returnlistrepos' ,methods = ['GET', 'POST'])
def returnlistrepos():
    return db.return_repo_list(request.get_json(force=True))
    
@app.route('/returnlistartifacts' ,methods = ['GET', 'POST'])
def returnlistartifacts():
    return db.return_artifact_list(request.get_json(force=True))
