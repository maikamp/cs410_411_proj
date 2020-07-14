import mysql.connector
import datetime
import requests
import math
import json
import os
#from werkzeug.security import check_password_hash
#from flask import Flask, flash, request, redirect, url_for
#from werkzeug.utils import secure_filename
#from wtforms import validators

DATABASE_NAME = 'Acubed'

class Database():
    # Initialize the MySQL-connector connection at the begining of of the script to ensure 
    # we are working from the correct database. Defines self.
    def __init__(self):
        self.connector = mysql.connector.connect(
            user = 'root',
            password = 'rT1@4PlgTd',
            database = DATABASE_NAME,
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
                database = DATABASE_NAME,
                #database = os.environ['DATABASE_NAME'],
                host = 'acubed_db',
                port = '3306'
            )
            self.cursor = self.connector.cursor()
    
    def login(self, content):
        self.ensureConnected()
        sql = "SELECT user_id, permission_level FROM user WHERE username = %s && password = %s"
        usr = (str(content["username"]), str(content["password"]))
        self.cursor.execute(sql, usr)
        result = self.cursor.fetchall()

        if len(result) == 0:
            payload = {
                "err_message" : "Failure: Invalid username or password."
            }
            return (json.dumps(payload), 401)
        else:
            if len(result) == 1:
                payload = {
                    "err_message" : "Successful login.",
                    "user_id" : result[0],
                    "permission_level": result[1]
                }
                return (json.dumps(payload), 200)
            else:
                payload = {
                    "err_message" : "Failure: Multiple users exist please contact admin."
                }
                return (json.dumps(payload), 401)

    def register(self, content):
        self.ensureConnected()
        sql_unique_user = "SELECT * FROM user WHERE username = %s OR user_email = %s"
        self.cursor.execute(sql_unique_user, (content.username, content.user_email))

        result = self.cursor.fetchall()
        #checking to see if account/email exists within the database, if it does, throw an error, if not, create account.
        if len(result) == 0:
            sqlUserInsert = "INSERT INTO user (access_level, username, password, user_email) VALUES (%s, %s, %s, %s, %s, %s)"
                
            val = (content['access_level'], content['username'], content['password'], content['user_email'])
            self.cursor.execute(sqlUserInsert, val)
            payload = {
                'data' : 'Account created.'
            }
            return (json.dumps(payload), 201)
        else:
            payload = {
                'data' : 'Username or email already in use.'
            }
            return(json.dumps(payload), 401)

    #Update a user's password
    def changePw(self, content):
        self.ensureConnected()

        sqlpw = "SELECT password FROM user WHERE username = %s && password = %s"
        val = (str(content["username"]),str(content["password"])) 
        self.cursor.execute(sqlpw, val)

        result = self.cursor.fetchall()
        if len(result) == 0:
            payload = {
                "err_message": "Failure: Username or password does not exist."
            }
            return (json.dumps(payload), 404)
        else:
            sql = "Update user SET password = %s WHERE username = %s"
            val = (str(content["new_password"]), str(content["username"]))
            self.cursor.execute(sql, val)
            self.connector.commit()
            payload = {
                "err_message": "Success: Password changed."
            }
            return (json.dumps(payload), 200)

    def allowed_file(self, filename):
        return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    #Uploads original file
    def artifactUpload(self, content):
        self.ensureConnected()

        if str(content["user_id"]) == "":
            sql = "SELECT user_id FROM user WHERE username = %s && password = %s"
            data = (str(content["username"]), str(content["password"]))
            self.cursor.execute(sql, data)
            results = self.cursor.fetchall()
            if len(results) == 0:
                payload = {
                    "err_message": "Failure: You do not have permission to create a repository."
                }
                return (json.dumps(payload), 401)
        else:
            results = (content["user_id"], )   

        fileUpload = request.files['inputFile']
        sqlUp = "INSERT INTO artifact (owner_id, artifact_repo, artifact_access_level, artifact_name, artifact_orginal_source, artifact_creation_date) VALUES (%s, %s, %s, %s, %s, %s)" 
        sqlTwo = "INSERT INTO artifact_change_record (change_datetime, changer_id, artifact_size, artifact_blob) VALUES (%s, %s, %s, %s)" 
        dataUp = (int(content["owner_id"]), int(content["artifact_repo"]), int(content["artifact_access_level"]), str(content["artifact_name"]), str(content["artifact_original_source"]), content["artifact_creation_date"]) 
        dataTwo = (content["change_datetime"], int(content["changer_id"]), int(content["artifact_size"]), content["artifact_blob"]) 

        self.cursor.execute(sqlUp, dataUp)
        self.cursor.commit()
        self.cursor.execute(sqlTwo, dataTwo)
        self.cursor.commit()

        return fileUpload.filename 
        
        #check if artifact exists in db, by artifact_name
        #if exisSts, prompt "would you like to update?"
        #if not exists, original upload

        #if request.method == 'POST':
            #check if the post request has the file part
            #if 'file' not in request.files:
                #flash('No file part')
                #return redirect(request.url)
            #file = request.files[request.url]
            # if user does not select file, browser also
            # submit an empty part without filename
            #if file.filename == '':
                #flash('No selected file')
                #return redirect(request.url)
            #if file and self.allowed_file(file.filename):
                #filename = secure_filename(file.filename)
                #file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                #return redirect(url_for('uploaded_file',
                                        #filename=filename))
    
    def addUser(self,content):
        self.ensureConnected()
        if  (str(content["accessLevel"]) == ""):
            sql = "INSERT INTO user (access_level, username, password, user_email) VALUES (3, %s, %s, %s)"
            data = (str(content["username"]), str(content["password"]), str(content["email"]))
            self.cursor.execute(sql, data)
            self.connector.commit()
            payload = {
                "err_message": "Success: User added."
            }
            return (json.dumps(payload), 200)
        else:    
            sql = "INSERT INTO user (access_level, username, password, user_email) VALUES (%s, %s, %s, %s)"
            data = (content["accessLevel"],str(content["username"]), str(content["password"]), str(content["email"]))
            self.cursor.execute(sql, data)
            self.connector.commit()
            payload = {
                "err_message": "Success: User added."
            }
            return (json.dumps(payload), 200)

    def createRepo(self,content):
        self.ensureConnected()
        #authenticate
        if str(content["user_id"]) == "":
            sql = "SELECT user_id FROM user WHERE username = %s && password = %s"
            data = (str(content["username"]), str(content["password"]))
            self.cursor.execute(sql, data)
            results = self.cursor.fetchall()
            if len(results) == 0:
                payload = {
                    "err_message": "Failure: You do not have permission to create a repository."
                }
                return (json.dumps(payload), 401)
        else:
            results = (content["user_id"], )
        
        sql = "INSERT INTO repository (repo_creator, permission_req, repo_name) VALUES (%s, %s, %s)"
        data = (int(results[0]), int(content["permission_req"]), str(content["repo_name"]))
        #repo_creator pulled from user_id from current user, the user creating the repo
        self.cursor.execute(sql, data)
        self.connector.commit()

        sql = "SELECT * FROM repository WHERE repo_name = %s"
        val = (str(content["repo_name"]))
        self.cursor.execute(sql, val)
        results = self.cursor.fetchall()
        payload = {
            "repo_name": results[3],
            "owner_name": results[1],
            "err_message": "Success: Repository created. " 
        }

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
