import mysql.connector
import datetime
import requests
import math
import json
import os
import sys
import pypandoc
import difflib
from flask import send_file, redirect, url_for, request, flash
from werkzeug.utils import secure_filename

#Global Variables
DATABASE_NAME = 'Acubed'
UPLOAD_FOLDER = './uploads'
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
        if content["access_level"] == "":
            access_level = "3"
        else: 
            access_level = content["access_level"]

        #checking to see if account/email exists within the database, if it does, throw an error, if not, create account.
        if len(result) == 0:
            sqlUserInsert = "INSERT INTO user (access_level, username, password, user_email) VALUES (%s, %s, %s, %s)"
            val = (access_level, content["username"], content["password"], content["email"])
            self.cursor.execute(sqlUserInsert, val)
            self.connector.commit()
            payload = {
                "err_message" : "Success: Account created."
            }
            return (json.dumps(payload), 201)
        else:
            payload = {
                "err_message" : "Failure: Username or email already in use."
            }
            return(json.dumps(payload), 401)

    #Update a user's password
    def changePw(self, content):
        self.ensureConnected()

        temp = self.getUserId(str(content["username"]), str(content["password"]))        
        if temp == "":
            payload = {
                "err_message": "Failure: That username or password does not exist."
            }
            return (json.dumps(payload), 401)

        userId = int(temp)
        sql = "UPDATE user SET password = %s WHERE user_id = %s"
        val = (str(content["new_password"]), userId)
        self.cursor.execute(sql, val)
        self.connector.commit()
        payload = {
            "err_message": "Success: Password changed."
        }
        return (json.dumps(payload), 200)

    #check file type for defined set of allowed extensions AND check for convertible extensions
    #returns tuple = ('extension', 0 OR 1 OR 2) where 0 = not allowed, 1 = allowed, 2 = convertible
    def allowed_file(self, filename):
        return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    def convertible_file(self, filename):
        return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in CONVERTIBLE_EXTENSIONS
    
    #Uploads original file  content = request.files['file']
    def artifactUpload(self, file, content):
        self.ensureConnected()
        
        content = json.loads(content.read().decode('utf-8'))

  
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

        repoId = int(content["artifact_repo"])
         
        sql = "SELECT artifact_id FROM artifact WHERE owner_id = %s && artifact_repo = %s && artifact_name = %s"
        val = (userId, repoId, str(content["artifact_name"]))
        self.cursor.execute(sql, val)
        temp = self.cursor.fetchall()
        datecreated = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if len(temp) == 0:
            if str(content["version"]) == "":
                version = 1
            else:
                version = int(content["version"])
            extension = file.filename.rsplit('.', 1)[1].lower()
            sqlUp = "INSERT INTO artifact (owner_id, artifact_repo, artifact_access_level, artifact_name, artifact_original_filetype, artifact_creation_date) VALUES (%s, %s, %s, %s, %s, %s)"
            #can UI send us repository_id or do we need to query for it?
            #creation date, we need to pull current datetime
            #pull extension from filename
            #exten = self.allowed_file(filename)
            dataUp = (userId, int(content["artifact_repo"]), int(content["artifact_access_level"]), str(content["artifact_name"]), extension, datecreated)
        
            self.cursor.execute(sqlUp, dataUp)
            self.connector.commit()
        else:
            sql = "SELECT MAX(version) FROM artifact_change_record WHERE artifact_id = %s"
            val = (temp[0][0], )
            self.cursor.execute(sql, val)
            results = self.cursor.fetchall()
            version = results[0][0] + 1
        
        #artifact_file = open("simplemd.md", "r")
        #fileupload steps
        
        #if request.method == 'POST':
        #check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            payload = {
                "err_message": "No file part."
            }
            return (json.dumps(payload), 404)
        #file = request.files[request.url]
        #if user does not select file, browser also
        #submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            payload = {
                "err_message": "No selected file."
            }
            return (json.dumps(payload), 404)
        if file and self.allowed_file(file.filename):

            filename = secure_filename(file.filename)
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            if self.convertible_file(file.filename):
                tempname = str(content["artifact_name"])
                extension = file.filename.rsplit('.', 1)[1].lower()
                print(filename, file = sys.stderr, end='')
                filename = self.convertToMD(tempname, extension)

            #split into new function, artifact upload?
            sqlTwo = "INSERT INTO artifact_change_record (change_datetime, changer_id, artifact_id, artifact_blob, version) VALUES (%s, %s, %s, %s, %s)"
            #datetime from artifact_creation_date, changer_id from owner_id, artifact_size get file size, convert to blob
            #(variable for version) = (query for previous version, if updating; 1 if no previous version)
            #TODO replace with proper file upload
            artifact_blob = open(os.path.join(UPLOAD_FOLDER, filename), "rb").read()
            #temp_filename = UPLOAD_FOLDER + '/'
            #temp_blob = temp_filename + file.filename
            dataTwo = (datecreated, userId, temp[0][0], artifact_blob, version)
            
            self.cursor.execute(sqlTwo, dataTwo)
            self.connector.commit()
            
            payload = {
                    "err_message": "Success: Artifact uploaded."
                }
            return (json.dumps(payload), 200)
        else:
            #TODO store along side database
            temp = UPLOAD_FOLDER + file.filename
            sqlTwo = "INSERT INTO artifact_change_record (change_datetime, changer_id, artifact_id, version) VALUES (%s, %s, %s, %s)"
            #datetime from artifact_creation_date, changer_id from owner_id, artifact_size get file size, convert to blob
            #(variable for version) = (query for previous version, if updating; 1 if no previous version)

            #temp_filename = UPLOAD_FOLDER + '/'
            #temp_blob = temp_filename + file.filename
            dataTwo = (datecreated, userId, temp[0][0], version)
            
            self.cursor.execute(sqlTwo, dataTwo)
            self.connector.commit()
            
            payload = {
                    "err_message": "Success: Artifact uploaded."
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
        
        if self.getPermissionLevel(userId) >= 3:
            sql = "SELECT * FROM repository WHERE repo_creator = %s && repo_name = %s"
            val = (userId, str(content["repo_name"]))
            self.cursor.execute(sql, val)
            temp = self.cursor.fetchall()
            if len(temp) == 0:
                #create the repository
                sql = "INSERT INTO repository (repo_creator, permission_req, repo_name) VALUES (%s, %s, %s)"
                data = (userId, int(content["permission_req"]), str(content["repo_name"]))
                #repo_creator pulled from user_id from current user, the user creating the repo
                self.cursor.execute(sql, data)
                self.connector.commit()

                #get the repository information to return the info to the user
                sql2 = "SELECT * FROM repository WHERE repo_name = %s"
                self.ensureConnected()
                print (str(content["repo_name"]), file = sys.stderr)
                self.cursor.execute(sql2, (str(content["repo_name"]), ))
                temp = self.cursor.fetchall()
                payload = {
                    "repo_name": str(temp[0][3]),
                    "owner_id": str(temp[0][1]),
                    "err_message": "Success: Repository created. " 
                }
                return (json.dumps(payload), 200)
            else:
                payload = {
                    "err_message": "Failure: You already own a repository with this name."
                }
        else:
            payload = {
                "err_message: Failure you do not have permission to create a repository."
            }

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
        
        sql = "UPDATE user SET username = %s WHERE username = %s && password = %s "
        val = (str(content["new_username"]), str(content["username"]), str(content["password"]))
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
        
        repo_id = self.getRepoId(str(content["repo_name"]), userId)

        if int(permissionLevel) >= 3:
            sql = "SELECT repo_creator FROM repository WHERE repository_id = %s"
            self.cursor.execute(sql, (repo_id, ))
            temp = self.cursor.fetchall()
            if int(temp[0][0]) == userId or int(permissionLevel)==5:
                if not str(content["new_repo_creator"]):
                    sql = "UPDATE repository WHERE repository_id = %s SET repo_creator = %s"
                    val = (repo_id, str(content["new_repo_creator"]))
                    self.cursor.execute(sql, val)
                    self.cursor.commit()
                if not str(content["new_permission_req"]):
                    sql = "UPDATE repository WHERE repository_id = %s SET permission_req = %s"
                    val = (repo_id, str(content["new_permission_req"]))
                    self.cursor.execute(sql, val)
                    self.cursor.commit()
                if not str(content["new_repo_name"]):
                    sql = "UPDATE repository WHERE repository_id = %s SET repo_name = %s"
                    val = (repo_id, str(content["new_repo_name"]))
                    self.cursor.execute(sql, val)
                    self.cursor.commit()
                payload = {
                    "err_message": "Success: Repo attributes changes."
                }
                return (json.dumps(payload), 200)
            else:
                payload = {
                    "err_message": "Failure: You do not have permission to change attributes on this repository."
                }
                return (json.dumps(payload), 401)
        else:
            payload = {
                "err_message": "Failure: You do not have permission to change attributes on this repository."
            }
            return (json.dumps(payload), 401)
    
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
    
    '''
    def simpleCompare (self, content):
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

        if str(content["version"]) == "":
            sql = "SELECT MAX(version) FROM artifact_change_record WHERE artifact_id = %s"
            data = (artifactId, )
            self.cursor.execute(sql, data)
            temp = self.cursor.fetchall()
            version = int(temp[0][0])
        else:
            version = (int(content["version"]))
        
        sql = "SELECT change_datetime, changer_id, artifact_id, artifact_size, version FROM artifact_change_record WHERE artifact_id = %s && version = %s"
        data = (artifactId, version)
        self.cursor.execute(sql, data)
        temp = self.cursor.fetchall()
        artifactChange = "change datettime: " + str(temp[0][0]) + ",\nchanger id: " + str(temp[0][1]) + ",\nartifact_id: " + str(temp[0][2]) + ",\nartifact size: " + str(temp[0][3]) + ",\nversion: " + str(temp[0][4]) + '\n'


        if str(content["previous_version"]) == "":
            sql = "SELECT MAX(version) FROM artifact_change_record WHERE artifact_id = %s"
            data = (artifactId, )
            self.cursor.execute(sql, data)
            temp = self.cursor.fetchall()
            version = int(temp[0][0])
        else:
            version = (int(content["previous_version"]))

        sql = "SELECT change_datetime, changer_id, artifact_id, artifact_size, version FROM artifact_change_record WHERE artifact_id = %s && version = %s"
        data = (artifactId, version)
        self.cursor.execute(sql, data)
        temp = self.cursor.fetchall()
        artifactChangePrevious = "change datettime: " + str(temp[0][0]) + ",\nchanger id: " + str(temp[0][1]) + ",\nartifact_id: " + str(temp[0][2]) + ",\nartifact size: " + str(temp[0][3]) + ",\nversion: " + str(temp[0][4]) + '\n'

        d = difflib.HtmlDiff()
        return  (d.make_file(artifactChange.split('\n'), artifactChangePrevious.split('\n')), 200)
        #to only return a HTML table for ui to use if they need it
        #return  (d.make_table(artifactChange.split('\n'), artifactChangePrevious.split('\n')), 200)
    '''
    def removeRepo(self,content):

    def removeArtifact(self, content):

    def removeUser(self, content): 
    '''

    #receives string filename, returns converted file in MD
    def convertToMD(self, filename, ext):
        #file = open(str(content("filename")), "r")
        '''
        sql = "SELECT artifact_id FROM artifact WHERE artifact_name = %s"
        data = (str(content("artifact_name")),)

        self.cursor.execute(sql, data)
        temp = self.cursor.fetchone()
        while (self.cursor.fetchone() != None):
            tempTrash = self.cursor.fetchone()
        '''
        
        mdfilename = './uploads/' + filename + '.md'
        mdfilename = './uploads/' + filename + ext
        fileMD = pypandoc.convert_file(filename, 'md', outputfile=mdfilename)
        
        return fileMD

    def convertFromMD(self, filename, ext):
        '''
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
        '''
        
        
        #convert file to md
        tempname = "./uploads/temp." + ext
        converted_file = pypandoc.convert_file(filename, ext, outputfile=tempname)

        return converted_file
    
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
        if len(temp) == 0:
            payload = {
                "err_message": "Failure there is no artifact here."
            }
            return (json.dumps(payload), 401)
        else:
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
            
            filename = str(artifactData[4]) + '.'
            fullfilename = filename + str(artifactData[6])
            filenameMD = filename + 'md'

            blobfile = artifactChange[4]
            
            if str(artifactData[6]) in CONVERTIBLE_EXTENSIONS:
                with open(filenameMD, 'wb') as file:
                    file.write(blobfile)

                if str(content["new_file_type"]) == "":
                    convertedfile = self.convertFromMD(filenameMD, str(artifactData[6]))
                else:
                    if (str(content["new_file_type"]) in CONVERTIBLE_EXTENSIONS):
                        fullfilename = filename + str(content["new_file_type"])
                        convertedfile = self.convertFromMD(filenameMD, str(content["new_file_type"]))
                    else:
                        payload = {
                            "err_message": "Failure: We cannot convert to that type."
                        }
                return (send_file(convertedfile, attachment_filename=fullfilename))

            else:
                with open(fullfilename, 'wb') as file:
                    file.write(blobfile)

                #payload = {
                #    "artifact_id": str(artifactData[0]),
                #    "owner_id": str(artifactData[1]),
                #    "artifact_name": str(artifactData[4]),
                #    "artifact_original_filetype": str(artifactData[6]),
                #    "artifact_size": str(artifactChange[3]),
                #    "version": str(artifactChange[5])
                #}
                return (send_file(fullfilename, attachment_filename=fullfilename))
    
    '''
    def addTag(self, content):

    def addBookmark(self,content):

    def changeTag(self, content):

    def removeBookmark(self, content):

    def makeBlob?

    def addArtifactChangeRecord(self, content):

    def returnArtifactChangeRecord(self, content):
    '''

    