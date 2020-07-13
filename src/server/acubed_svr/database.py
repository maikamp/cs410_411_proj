import mysql.connector
import datetime
import requests
import math
import json
import os
from werkzeug.security import check_password_hash
from flask import Flask, flash, request, redirect, url_for
from werkzeug.utils import secure_filename
from wtforms import validators

DATABASE_NAME = 'Acubed'

UPLOAD_FOLDER = '/path/to/the/uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

class Database():
    # Initialize the MySQL-connector connection at the begining of of the script to ensure 
    # we are working from the correct database. Defines self.
    def __init__(self):
        self.connector = mysql.connector.connect(
            user = 'root',
            password = 'rT1@4PlgTd',
            database = 'Acubed',
            host = 'acubed_db',
            port = '3306'
        )
        self.cursor = self.connector.cursor()

    # Make sure the connection to the database was established and reconnect if needed.
    # Rediefines self if needed.
    def ensureConnected(self):
        if not self.connector.is_connected():
            self.connector = mysql.connector.connect(
                user = 'root',
                password = 'rT1@4PlgTd',
                database = 'Acubed',
                #database = os.environ['DATABASE_NAME'],
                host = 'acubed_db',
                port = '3306'
            )
            self.cursor = self.connector.cursor()
    
    def login(self, content):
        self.ensureConnected()
        sql = "SELECT user_id FROM user WHERE username = %s && password = %s"
        usr = (str(content["username"]), str(content["password"]))
        self.cursor.execute(sql, usr)
        result = self.cursor.fetchall()

        if len(result) == 0:
            payload = {
                "data" : "Invalid username or password."
            }
            return (json.dumps(payload), 401)
        else:
            if len(result) == 1:
                payload = {
                    "data" : "Successful login.",
                    "user_id" : result,
                }
                return (json.dumps(payload), 200)
            else:
                payload = {
                    "data" : "Incorrect password."
                }
                return (json.dumps(payload), 401)

    def register(self, content):
        self.ensureConnected()
        sql_unique_user = "SELECT * FROM user WHERE username = %s OR user_email = %s"
        self.cursor.execute(sql_unique_user, (content.username, content.user_email))

        result = self.cursor.fetchall()
        #checking to see if account/email exists within the database, if it does, throw an error, if not, create account.
        if len(result) == 0:
            sqlUserInsert = "INSERT INTO user (user_id, access_level, username, password, user_email, last_login) VALUES (%s, %s, %s, %s, %s, %s)"
                
            val = (content['user_id'], content['access_level'], content['username'], content['password'], content['user_email'], content['last_login'])
            self.cursor.execute(sqlUserInsert, val)
            payload = {
                'data' : 'Account created.'
            }
            return (json.dumps(payload), 200)
        else:
            payload = {
                'data' : 'Username or email already in use.'
            }
            return(json.dumps(payload), 401)

    #Update a user's password
    def changePw(self, content):
        self.ensureConnected()

        sqlpw = "SELECT password FROM user WHERE username = %s && password = %s"
        val = "Update user SET password = %s WHERE username = %s"
        self.cursor.execute(sqlpw, val)

        #sqlpw = "INSERT INTO user (password) VALUES (%s)"
        #data = (str(content["password"]))
        #self.cursor.execute(sqlpw, data)
        #self.connector.commit()

    def allowed_file(self, filename):
        return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    #Uploads original file
    def artifactUpload(self, content):
        self.ensureConnected()

        #check if artifact exists in db, by artifact_name
        #if exists, prompt "would you like to update?"
        #if not exists, original upload

        if request.method == 'POST':
            #check if the post request has the file part
            if 'file' not in request.files:
                flash('No file part')
                return redirect(request.url)
            file = request.files[request.url]
            # if user does not select file, browser also
            # submit an empty part without filename
            if file.filename == '':
                flash('No selected file')
                return redirect(request.url)
            if file and self.allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                return redirect(url_for('uploaded_file',
                                        filename=filename))
    
    def addUser(self,content):
        self.ensureConnected()
        sql = "INSERT INTO user (access_level, username, password) VALUES (%s, %s, %s)"
        data = (str(content["access_level"]),str(content["username"]), str(content["password"]))
        self.cursor.execute(sql, data)
        self.connector.commit()

    def createRepo(self,content):
        self.ensureConnected()
        #authenticate
        userID = "SELECT user_id FROM user WHERE username = %s"
        data2 = (str(content["username"]))
        self.cursor.execute(userID, data2)

        sql = "INSERT INTO repository (repo_creator, permission_req, repo_name) VALUES (%s, %s, %s)"
        
        data = (userID, str(content["permission_req"]), str(content["repo_name"]))
        #repo_creator pulled from user_id from current user, the user creating the repo
        self.cursor.execute(sql, data)
        self.connector.commit()

    #def changePw(self,content):

    #def changeUsername(self,content):

    #def updateRepoAttrib(self,content):
    
    #def updateArtifactAttrib(self,content):

    #def updateArtifact(self,content): ?

    #def returnArtifactInfo(self,content):

    #def returnRepoInfo(self,content):

    #def authenticate(self, content):

    #def diff(self, content):
        #check file type, can be diff'd, full diff
        #can't be diff'd, simple compare

    #def simpleCompare (self, content):

    #def removeRepo(self,content):

    #def removeArtifact(self, content):

    #def removeUser(self, content): 

    #def convertToMD(self, content):

    #def convertFromMD(self, content):

    #def exportArtifact(self, content):

    #def addTag(self, content):

    #def addBookmark(self,content):

    #def changeTag(self, content):

    #def removeBookmark(self, content):

    #def makeBlob?

    #def addArtifactChangeRecord(self, content):

    #def returnArtifactChangeRecord(self, content):
