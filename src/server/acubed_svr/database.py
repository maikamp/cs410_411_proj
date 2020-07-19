import mysql.connector
import datetime
import requests
import math
import json
import os
import sys
import pypandoc
from flask import send_file, redirect, url_for

#Global Variables
DATABASE_NAME = 'Acubed'
UPLOAD_FOLDER = '/path/to/the/uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'docx', 'doc', 'ppt', 'pptx', 'odt', 'htm', 'html', 'md', 'py', 'java', 'cpp'}
CONVERTIBLE_EXTENSIONS = {'pdf', 'doc', 'docx', 'ppt', 'pptx', 'odt', 'htm', 'html'}

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

    #get user id when you have a username and password
    def getUserId(self, username, password):
        sql = "SELECT user_id FROM user WHERE username = %s && password = %s"
        data = (username, password)
        self.cursor.execute(sql, data)
        temp = self.cursor.fetchall()
        result = temp[0]
        if len(temp) == 0:
            #set to an empty string for no users
            userId = ""
        else:
            userId = result[0]
        return userId

    #get repo id when you only have the repo name
    def getRepoId(self, reponame, permissionLevel):
        sql = "SELECT repository_id FROM repository WHERE repo_name = %s && permission_req = %s"
        data = (reponame, permissionLevel)
        self.cursor.execute(sql, data)
        temp = self.cursor.fetchall()
        if len(temp) == 0:
            #set an empty string for no repository
            repoId = ""
        else:
            repoId = temp[0][0]
        return repoId

    def getPermissionLevel(self, userId):
        sql = "SELECT access_level FROM user WHERE user_id = %s"
        data = (userId, )
        self.cursor.execute(sql, data)
        temp = self.cursor.fetchall()
        return temp[0][0]
    
    #get the user id and access level for a user 
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
                    "user_id" : str(results[0]),
                    "permission_level": str(results[1])
                }
                return (json.dumps(payload), 200)
            else:
                payload = {
                    "err_message" : "Failure: Multiple users exist please contact admin."
                }
                return (json.dumps(payload), 401)
    
    #register a new user
    def register(self, content):
        self.ensureConnected()
        sql_unique_user = "SELECT * FROM user WHERE username = %s OR user_email = %s"
        self.cursor.execute(sql_unique_user, (content["username"], content["email"]))

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
        temp = self.cursor.fetchall()
        if len(temp == 0):
            payload = {
                "err_message": "Failure: Username or password does not exist."
            }
            return (json.dumps(payload), 404)
        else:
            sql = "UPDATE user SET password = %s WHERE username = %s"
            val = (str(content["new_password"]), str(content["username"]))
            self.cursor.execute(sql, val)
            self.connector.commit()
            payload = {
                "err_message": "Success: Password changed."
            }
            return (json.dumps(payload), 200)

    #check file type for defined set of allowed extensions AND check for convertible extensions
    #returns tuple = ('extension', 0 OR 1 OR 2) where 0 = not allowed, 1 = allowed, 2 = convertible
    def allowed_file(self, filename):
        extension = filename.rsplit('.', 1)[1].lower()
        check = 0
        if extension in ALLOWED_EXTENSIONS:
            check = 1
        if extension in CONVERTIBLE_EXTENSIONS:
            check = 2
        return (extension, check)

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

        sqlUp = "INSERT INTO artifact (owner_id, artifact_repo, artifact_access_level, artifact_name, artifact_creation_date, artifact_original_filetype) VALUES (%s, %s, %s, %s, %s, %s)"
        #can UI send us repository_id or do we need to query for it?
        #creation date, we need to pull current datetime
        datecreated = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        dataUp = (int(results[0]), int(content["artifact_repo"]), int(content["artifact_access_level"]), str(content["artifact_name"]), datecreated, "filetype goes here")
        
        self.cursor.execute(sqlUp, dataUp)
        self.connector.commit()
        
        #artifact_file = open("simplemd.md", "r")
        #fileupload steps
        
        if request.method == 'POST':
            #check if the post request has the file part
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
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename)
                #TODO return json dump here
                return redirect(url_for('uploaded_file', filename=filename))
        

        #TODO check extension, then convert to MD step for appropriate file types
        #extTuple = self.allowed_file("simplemd.md")
        sqlId = "SELECT artifact_id FROM artifact WHERE artifact_name = %s"
        val = (str(content["artifact_name"]))
        self.cursor.execute(sqlId, (val, ))
        temp = self.cursor.fetchone()
        while (self.cursor.fetchone() != None):
            tempTrash = self.cursor.fetchone()
        
        #split into new function, artifact upload?
        sqlTwo = "INSERT INTO artifact_change_record (change_datetime, changer_id, artifact_id, artifact_blob, version) VALUES (%s, %s, %s, %s, %s)"
        #datetime from artifact_creation_date, changer_id from owner_id, artifact_size get file size, convert to blob
        #(variable for version) = (query for previous version, if updating; 1 if no previous version)
        #TODO replace with proper file upload
        dataTwo = (datecreated, int(results[0]), temp[0], artifact_file.read(), 1)
        
        self.cursor.execute(sqlTwo, dataTwo)
        self.connector.commit()
        
        payload = {
                "err_message": "Success: Artifact uploaded."
            }
        return (json.dumps(payload), 200)
        
        #return fileUpload.filename 
        #check if artifact exists in db, by artifact_name
        #if exists, prompt "would you like to update?"
        #if not exists, original upload

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
            temp = self.getUserId(str(content["username"]), str(content["password"]))        
            if temp == "":
                payload = {
                    "err_message": "Failure: That username or password does not exist."
                }
                return (json.dumps(payload), 401)   
            userId = int(temp)
        else:
            userId = int(content["user_id"])
        
        #create the repository
        val2 = content["repo_name"]
        sql = "INSERT INTO repository (repo_creator, permission_req, repo_name) VALUES (%s, %s, %s)"
        data = (userId, int(content["permission_req"]), str(val2))
        #repo_creator pulled from user_id from current user, the user creating the repo
        self.cursor.execute(sql, data)
        self.connector.commit()

        #get ther repository information to return the info to the user
        sql2 = "SELECT * FROM repository WHERE repo_name = %s"
        self.ensureConnected()
        print (val2, file = sys.stderr)
        self.cursor.execute(sql2, (val2, ))
        temp = self.cursor.fetchall()
        results = temp[0]
        payload = {
            "repo_name": str(results[3]),
            "owner_name": str(results[1]),
            "err_message": "Success: Repository created. " 
        }
        return (json.dumps(payload), 200)

    def changeUsername(self,content):
        self.ensureConnected()

        sqlpw = "SELECT username FROM user WHERE username = %s && password = %s"
        val = (str(content["username"]),str(content["password"])) 
        self.cursor.execute(sqlpw, val)

        result = self.cursor.fetchall()
        if len(result) == 0:
            payload = {
                "err_message": "Failure: Username or password does not exist."
            }
            return (json.dumps(payload), 404)
        
        sql = "UPDATE user SET username = %s WHERE username = %s"
        val = (str(content["new_username"]), str(content["username"]))
        self.cursor.execute(sql, val)
        self.connector.commit()
        payload = {
            "err_message": "Success: Username changed."
        }
        return (json.dumps(payload), 200)
    '''
    this needs work
    '''
    def updateRepoAttrib(self,content):
        self.ensureConnected()

        if str(content["user_id"]) == "":
            sql = "SELECT user_id FROM user WHERE username = %s && password = %s"
            data = (str(content["username"]), str(content["password"]))
            self.cursor.execute(sql, data)
            temp = self.cursor.fetchall()
            if len(temp) == 0:
                payload = {
                    "err_message": "Failure: You do not have permission to change this repository."
                }
                return (json.dumps(payload), 401)
            
            results = (temp[0])
        else:
            results = (int(content["user_id"]), )

        sql = "UPDATE repository WHERE repo_name = %s SET repo_creator = %s && permission_req = %s && repo_name = %s"
        val = (str(content["repo_name"]), str(content["attribute": "repo_creator"]), str(content["attribute": "permission_req"]), str(content["attribute": "repo_name"]))
        self.cursor.execute(sql, val)
        self.connector.commit()
        payload = {
            "err_message": "Success: Repo attributes changes."
        }
        return (json.dumps(payload), 200)
    '''
    this needs work  
    '''
    
    def updateArtifactAttrib(self,content):
        self.ensureConnected()

        if str(content["user_id"]) == "":
            temp = self.getUserId(str(content["username"]), str(content["password"]))        
            if temp == "":
                payload = {
                    "err_message": "Failure: That username or password does not exist."
                }
                return (json.dumps(payload), 401)   
            userId = int(temp)
        else:
            userId = int(content["user_id"])
        
        permissionLevel = self.getPermissionLevel(userId)

        sql = "UPDATE artifact WHERE artifact_name = %s && repo_name = %s SET owner_id = %s && artifact_access_level = %s && artifact_name = %s && artifact_original_source = %s"
        val = (str(content["artifact_name"]), str(content["repo_name"]), str(content["attribute": ["owner_id"]]), 
                str(content["attribute": ["artifact_access_level"]]), str(content["attribute": ["artifact_name"]]), 
                str(content["artifact_original_source"]))
        self.cursor.execute(sql, val)
        self.connector.commit()
        payload = {
            "err_message": "Success: Artifact attributes changes."
        }
        return (json.dumps(payload), 200)
    
    '''
    def updateArtifact(self,content): ?
    '''
     
    def artifactInfo(self, content):
        self.ensureConnected()

        if str(content["user_id"]) == "":
            temp = self.getUserId(str(content["username"]), str(content["password"]))        
            if temp == "":
                payload = {
                    "err_message": "Failure: That username or password does not exist."
                }
                return (json.dumps(payload), 401)   
            userId = int(temp)
        else:
            userId = int(content["user_id"])
        
        permissionLevel = self.getPermissionLevel(userId)

        if str(content["repository_id"]) == "":
            temp = self.getRepoId(str(content["repo_name"]), permissionLevel)
            if temp == "":
                payload = {
                    "err_message": "Failure: That repository does not exist."
                }
                return (json.dumps(payload), 401)
            repoId = int(temp)
        else:
            repoId = int(content["repository_id"])
        
        if str(content["artifact_id"]) == "":
            sql = "SELECT artifact_id FROM artifact WHERE artifact_repo = %s && artifact_name = %s"
            data = (repoId, str(content["artifact_name"]))
            self.cursor.execute(sql, data)
            temp = self.cursor.fetchall()
            if len(temp) == 0:
                payload = {
                    "err_message": "Failure: That artifact does not exist."
                }
                return (json.dumps(payload), 401)
            artifactId = int(temp[0][0])
        else:
            artifactId = int(content["artifact_id"])

        sql = "SELECT * FROM artifact WHERE artifact_repo = %s && artifact_id = %s"
        data = (repoId, artifactId)
        self.cursor.execute(sql, data)
        temp = self.cursor.fetchall()
        artifactData = temp[0]

        if str(content["version"]) == "":
            sql = "SELECT MAX(version) FROM artifact_change_record WHERE artifact_id = %s"
            data = (artifactId, )
            self.cursor.execute(sql, data)
            temp = self.cursor.fetchall()
            version = int(temp[0][0])
        else:
            version = (int(content["version"]))
        
        sql = "SELECT * FROM artifact_change_record WHERE artifact_id = %s && version = %s"
        data = (artifactId, version)
        self.cursor.execute(sql, data)
        temp = self.cursor.fetchall()
        artifactChange = temp[0]
    
        payload = {
            "artifact_id": str(artifactData[0]),
            "owner_id": str(artifactData[1]),
            "artifact_repo": str(artifactData[2]),
            "artifact_access_level": str(artifactData[3]),
            "artifact_name": str(artifactData[4]),
            "artifact_original_source": str(artifactData[5]),
            "artifact_original_filetype": str(artifactData[6]),
            "artifact_creation_date": str(artifactData[7]),
            "artifact_last_accessed": str(artifactData[8]),
            "artifact_access_count": str(artifactData[9]),
            "change_datetime": str(artifactChange[0]),
            "artifact_size": str(artifactChange[3]),
            "version": str(artifactChange[5])
        }
        return (json.dumps(payload), 200)
    
    def repoInfo(self,content):
        self.ensureConnected()
        
        if str(content["user_id"]) == "":
            temp = self.getUserId(str(content["username"]), str(content["password"]))        
            if temp == "":
                payload = {
                    "err_message": "Failure: That username or password does not exist."
                }
                return (json.dumps(payload), 401)   
            userId = int(temp)
        else:
            userId = int(content["user_id"])
        
        permissionLevel = self.getPermissionLevel(userId)

        if str(content["repository_id"]) == "":
            temp = self.getRepoId(str(content["repo_name"]), permissionLevel)
            if temp == "":
                payload = {
                    "err_message": "Failure: That repository does not exist."
                }
                return (json.dumps(payload), 401)
            repoId = int(temp)
        else:
            repoId = int(content["repository_id"])

        sql = "SELECT * FROM repository WHERE repository_id = %s"
        data = (repoId, )
        self.cursor.execute(sql, data)
        temp = self.cursor.fetchall()
        repoData = temp[0]

        payload = {
            "repository_id": str(repoData[0]),
            "repo_name": str(repoData[3]),
            "repo_creator": str(repoData[1]),
            "permission_req": str(repoData[2])
        }
        return (json.dumps(payload), 200)

    '''
    def authenticate(self, content):
        #receive username and pw or user_id
        #check against db
        #return tuple (user_id, )

    def diff(self, content):
        #check file type, can be diff'd, full diff
        #can't be diff'd, simple compare

    def simpleCompare (self, content):

    def removeRepo(self,content):

    def removeArtifact(self, content):

    def removeUser(self, content): 
    '''

    #receives string filename, returns converted file in MD
    def convertToMD(self, filename):
        #file = open(str(content("filename")), "r")
        '''
        sql = "SELECT artifact_id FROM artifact WHERE artifact_name = %s"
        data = (str(content("artifact_name")),)

        self.cursor.execute(sql, data)
        temp = self.cursor.fetchone()
        while (self.cursor.fetchone() != None):
            tempTrash = self.cursor.fetchone()
        '''
        fileMD = pypandoc.convert_file(filename, 'md')
        
        return fileMD

    def convertFromMD(self, content):
        #if version not selected, select highest version, else select specified version
        if str(content["version"]) == "":
            sql = "SELECT artifact_blob FROM artifact_change_record WHERE artifact_id = %s && version = (SELECT MAX(version) FROM artifact_change_record WHERE artifact_id = %s)"
            data = (str(content("artifact_id")), str(content("artifact_id")))
        else:
            sql = "SELECT artifact_blob FROM artifact_change_record WHERE artifact_id = %s && version = %s"
            data = (str(content("artifact_id")), str(content("version")))

        self.cursor.execute(sql, data)
        temp = self.cursor.fetchone()
        while (self.cursor.fetchone() != None):
            tempTrash = self.cursor.fetchone()
        
        #write blob to file
        file = temp[0].write()
        
        #convert file to md
        og_file = pypandoc.convert_file(file, 'md')

        return og_file
    
    def exportArtifact(self, content):
        self.ensureConnected()

        if str(content["user_id"]) == "":
            temp = self.getUserId(str(content["username"]), str(content["password"]))        
            if temp == "":
                payload = {
                    "err_message": "Failure: That username or password does not exist."
                }
                return (json.dumps(payload), 401)   
            userId = int(temp)
        else:
            userId = int(content["user_id"])
        
        permissionLevel = self.getPermissionLevel(userId)

        if str(content["repository_id"]) == "":
            temp = self.getRepoId(str(content["repo_name"]), permissionLevel)
            if temp == "":
                payload = {
                    "err_message": "Failure: That repository does not exist."
                }
                return (json.dumps(payload), 401)
            repoId = int(temp)
        else:
            repoId = int(content["repository_id"])
        
        if str(content["artifact_id"]) == "":
            sql = "SELECT artifact_id FROM artifact WHERE artifact_repo = %s && artifact_name = %s"
            data = (repoId, str(content["artifact_name"]))
            self.cursor.execute(sql, data)
            temp = self.cursor.fetchall()
            if len(temp) == 0:
                payload = {
                    "err_message": "Failure: That artifact does not exist."
                }
                return (json.dumps(payload), 401)
            artifactId = int(temp[0][0])
        else:
            artifactId = int(content["artifact_id"])

        sql = "SELECT * FROM artifact WHERE artifact_repo = %s && artifact_id = %s"
        data = (repoId, artifactId)
        self.cursor.execute(sql, data)
        temp = self.cursor.fetchall()
        artifactData = temp[0]

        if str(content["version"]) == "":
            sql = "SELECT MAX(version) FROM artifact_change_record WHERE artifact_id = %s"
            data = (artifactId, )
            self.cursor.execute(sql, data)
            temp = self.cursor.fetchall()
            version = int(temp[0][0])
        else:
            version = (int(content["version"]))

        sql = "SELECT * FROM artifact_change_record WHERE artifact_id = %s && version = %s"
        data = (artifactId, version)
        self.cursor.execute(sql, data)
        temp = self.cursor.fetchall()
        artifactChange = temp[0]

        fileextension = '.' + str(artifactData[6])
        filename = str(artifactData[1]) + fileextension
        blobfile = artifactChange[4]
        with open(filename, 'wb') as file:
            file.write(blobfile)
    
        payload = {
            "artifact_id": str(artifactData[0]),
            "owner_id": str(artifactData[1]),
            "artifact_name": str(artifactData[4]),
            "artifact_original_filetype": str(artifactData[6]),
            "artifact_size": str(artifactChange[3]),
            "version": str(artifactChange[5])
        }

        return (send_file(filename, attachment_filename=filename))
    
    
    '''
    def addTag(self, content):

    def addBookmark(self,content):

    def changeTag(self, content):

    def removeBookmark(self, content):

    def makeBlob?

    def addArtifactChangeRecord(self, content):

    def returnArtifactChangeRecord(self, content):
    '''

    