import mysql.connector
import datetime
import requests
import math
import json
import os
import sys
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
        sql = "SELECT user_id, access_level FROM user WHERE username = %s && password = %s"
        usr = (str(content["username"]), str(content["password"]))
        self.cursor.execute(sql, usr)
        temp = self.cursor.fetchall()
        results = temp[0]
        if len(temp) == 0:
            payload = {
                "err_message" : "Failure: Invalid username or password."
            }
            return (json.dumps(payload), 401)
        else:
            if len(temp) == 1:
                payload = {
                    "err_message" : "Successful login.",
                    "user_id" : results[0],
                    "permission_level": results[1]
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
            temp = self.cursor.fetchall()
            if len(temp) == 0:
                payload = {
                    "err_message": "Failure: You do not have permission for that."
                }
                return (json.dumps(payload), 401)
            results = (temp[0])
        else:
            results = (content["user_id"], )   

        #fileUpload = request.files['inputFile']
        #file location in json, either "local file": "file location" OR "web file": url
        #if local file, use fileupload
        #if web file, use webscraper

        sqlUp = "INSERT INTO artifact (owner_id, artifact_repo, artifact_access_level, artifact_name, artifact_creation_date) VALUES (%s, %s, %s, %s, %s)"
        #can UI send us repository_id or do we need to query for it?
        #creation date, we need to pull current datetime
        datecreated = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        dataUp = (int(results[0]), int(content["artifact_repo"]), int(content["artifact_access_level"]), str(content["artifact_name"]), datecreated)
        
        self.cursor.execute(sqlUp, dataUp)
        self.connector.commit()
        
        #TODO check extension, then convert to MD step for appropriate file types

        sqlId = "SELECT artifact_id FROM artifact WHERE artifact_name = %s"
        val = (str(content["artifact_name"]))
        self.cursor.execute(sqlId, (val, ))
        temp = self.cursor.fetchone()
        
        #split into new function, artifact upload?
        sqlTwo = "INSERT INTO artifact_change_record (change_datetime, changer_id, artifact_id, artifact_blob) VALUES (%s, %s, %s, %s)"
        #datetime from artifact_creation_date, changer_id from owner_id, artifact_size get file size, convert to blob
        artifact_file = open("simplemd.md", "r")

        #TODO replace with proper file upload
        dataTwo = (datecreated, (int(results[0])), temp[0], artifact_file.read())
        
        self.cursor.execute(sqlTwo, dataTwo)
        self.connector.commit()
        
        payload = {
                "err_message": "Success: Artifact uploaded."
            }
        return (json.dumps(payload), 200)
        
        #return fileUpload.filename 
        
        #check if artifact exists in db, by artifact_name
        #if exisSts, prompt "would you like to update?"
        #if not exists, original upload

        """
        if request.method == 'POST':
            check if the post request has the file part
            if 'file' not in request.files:
                flash('No file part')
                return redirect(request.url)
            file = request.files[request.url]
            #if user does not select file, browser also
            #submit an empty part without filename
            if file.filename == '':
                flash('No selected file')
                return redirect(request.url)
            if file and self.allowed_file(file.filename):
                #filename = secure_filename(file.filename)
                #file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                #TODO return json dump here
                #return redirect(url_for('uploaded_file',
                                        #filename=filename))
        """

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
            temp = self.cursor.fetchall()
            if len(temp) == 0:
                payload = {
                    "err_message": "Failure: You do not have permission to create a repository."
                }
                return (json.dumps(payload), 401)
            
            results = (temp[0])
        else:
            results = (int(content["user_id"]), )
        
        val2 = content["repo_name"]
        sql = "INSERT INTO repository (repo_creator, permission_req, repo_name) VALUES (%s, %s, %s)"
        data = (int(results[0]), int(content["permission_req"]), str(val2))
        #repo_creator pulled from user_id from current user, the user creating the repo
        self.cursor.execute(sql, data)
        self.connector.commit()

        sql2 = "SELECT * FROM repository WHERE repo_name = %s"
        #val2 = str(data[2])
        #val2 = (str(content["repo_name"]))
        self.ensureConnected()
        print (val2, file = sys.stderr)
        self.cursor.execute(sql2, (val2, ))
        temp = self.cursor.fetchall()
        results = temp[0]
        payload = {
            "repo_name": results[3],
            "owner_name": results[1],
            "err_message": "Success: Repository created. " 
        }
        return (json.dumps(payload), 200)

    #def changeUsername(self,content):

    #def updateRepoAttrib(self,content):
    
    #def updateArtifactAttrib(self,content):

    #def updateArtifact(self,content): ?

    #def returnArtifactInfo(self,content):

    #def returnRepoInfo(self,content):

    #def authenticate(self, content):
        #receive username and pw or user_id
        #check against db
        #return tuple (user_id, )

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
