import mysql.connector
import datetime
import requests
import math
import json
import os
import sys
import pypandoc
import difflib
import urllib.request
from bs4 import BeautifulSoup
from flask import send_file, redirect, url_for, request, flash
from werkzeug.utils import secure_filename

#Global Variables
DATABASE_NAME = 'Acubed'
UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = {'txt', 'docx', 'doc', 'odt', 'htm', 'html', 'md', 'py', 'java', 'cpp'}
CONVERTIBLE_EXTENSIONS = {'doc', 'docx', 'odt', 'htm', 'html'}
#create the default payload for no username/password combination
AUTHENTICATE_FAIL = {
                "err_message": "Failure: That username or password does not exist."
            }
NO_REPO = {
        "err_message": "Failure: That repository does not exist."
}
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
    def get_user_id(self, username, password):
        sql = "SELECT user_id FROM user WHERE username = %s && password = %s"
        data = (username, password)
        self.cursor.execute(sql, data)
        temp = self.cursor.fetchall()
        if len(temp) == 0:
            #set to an empty string for no users
            user_id = ""
        else:
            user_id = int(temp[0][0])
        return user_id

    #get repo id when you only have the repo name
    def get_repo_id(self, reponame, permission_level):
        sql = "SELECT repository_id FROM repository WHERE repo_name = %s && permission_req = %s"
        data = (reponame, permission_level)
        self.cursor.execute(sql, data)
        temp = self.cursor.fetchall()
        if len(temp) == 0:
            #set an empty string for no repository
            repo_id = ""
        else:
            repo_id = int(temp[0][0])
        return repo_id

    #get permission level of the user
    def get_permission_level(self, user_id):
        sql = "SELECT access_level FROM user WHERE user_id = %s"
        data = (user_id, )
        self.cursor.execute(sql, data)
        temp = self.cursor.fetchall()
        return temp[0][0]

    #get artifact id when you only have the repo name
    def get_artifact_id(self, user_id, repo_id, artifact_name):
        sql = "SELECT artifact_id FROM artifact WHERE owner_id = %s && artifact_repo = %s && artifact_name = %s"
        val = (user_id, repo_id, artifact_name)
        self.cursor.execute(sql, val)
        temp = self.cursor.fetchall()
        if len(temp) == 0:
            #set an empty string for no repository
            artifact_id = ""
        else:
            artifact_id = int(temp[0][0])
        return artifact_id
    
    #check file type for defined set of allowed extensions 
    def allowed_file(self, filename):
        return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    
    #check file type for defined set of convertible extensions
    def convertible_file(self, filename):
        return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in CONVERTIBLE_EXTENSIONS
    
    #receives string filename and original extension, returns converted filename in MD
    def convertToMD(self, filename, ext):
        #create the output path + filename with the .md extension         
        md_filename = './uploads/' + filename + '.md'
        #create the input path + filename witht the original extension
        temp_filename = './uploads/' + filename + '.' + ext
        #run pandoc and as far as I can tell it must have a variable which will be empty 
        file_MD = pypandoc.convert_file(temp_filename, 'md', outputfile = md_filename)
        #assert the variable is empty
        assert file_MD == ""
        #return the created filename without the path
        return filename + '.md'

    #recieves string filename.md, returns converted filename in new extension
    def convertFromMD(self, filename, ext):
        #create a temporary file with the correct extension
        tempname = "./uploads/temp." + ext
        #run pandoc, the variable will be empty but the file will be saved in the uploads folder
        converted_file = pypandoc.convert_file(filename, ext, outputfile=tempname)
        #assert the variable is empty
        assert converted_file == ""
        #return the temp.extension filepath so we can send the file to the user
        return tempname
    
    #get the user id and access level for a user 
    def login(self, content):
        self.ensureConnected()
        sql = "SELECT user_id, access_level FROM user WHERE username = %s && password = %s"
        usr = (str(content["username"]), str(content["password"]))
        self.cursor.execute(sql, usr)
        temp = self.cursor.fetchall()
        results = temp[0]
        if len(temp) == 0:
            return (json.dumps(AUTHENTICATE_FAIL), 401)
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
                return (json.dumps(payload), 400)
    
    #register a new user
    def register(self, content):
        self.ensureConnected()
        sql_unique_user = "SELECT * FROM user WHERE username = %s OR user_email = %s"
        self.cursor.execute(sql_unique_user, (content["username"], content["email"]))
        result = self.cursor.fetchall()

        if content.get("access_level", "") == "":
            access_level = "3"
        else: 
            access_level = content["access_level"]

        #checking to see if account/email exists within the database, if it does, throw an error, if not, create account.
        if len(result) == 0:
            sql_user_insert = "INSERT INTO user (access_level, username, password, user_email) VALUES (%s, %s, %s, %s)"
            val = (access_level, content["username"], content["password"], content["email"])
            self.cursor.execute(sql_user_insert, val)
            self.connector.commit()
            payload = {
                "err_message" : "Success: Account created."
            }
            return (json.dumps(payload), 201)
        else:
            payload = {
                "err_message" : "Failure: Username or email already in use."
            }
            return(json.dumps(payload), 400)

    #Update a user's password
    def change_pw(self, content):
        self.ensureConnected()

        if content.get("user_id", "") == "":
            user_id = self.get_user_id(str(content["username"]), str(content["password"]))        
            if user_id == "":
                return (json.dumps(AUTHENTICATE_FAIL), 401)
        else:
            user_id = int(content["user_id"])
        
        sql = "UPDATE user SET password = %s WHERE user_id = %s"
        val = (str(content["new_password"]), user_id)
        self.cursor.execute(sql, val)
        self.connector.commit()
        payload = {
            "err_message": "Success: Password changed."
        }
        return (json.dumps(payload), 202)
    
    #Uploads original file  content = request.files['file']
    def artifact_upload(self, file, content):
        self.ensureConnected()
        
        content = json.loads(content.read().decode('utf-8'))
        if content.get("user_id", "") == "":
            user_id = self.get_user_id(str(content["username"]), str(content["password"]))        
            if user_id == "":
                return (json.dumps(AUTHENTICATE_FAIL), 401)
        else:
            user_id = int(content["user_id"])

        if content.get("repository_id", "") == "":
            repo_id = self.get_repo_id(str(content["repo_name"]), user_id)
            if repo_id == "":
                return (json.dumps(NO_REPO), 400)
        else:
            repo_id = int(content["repository_id"])
         
        artifact_id = self.get_artifact_id(user_id, repo_id, str(content["artifact_name"]))
        datecreated = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        #check for the first time an artifact has been uploaded
        if artifact_id == "":
            #version control for initial version
            if str(content["version"]) == "":
                version = 1
            else:
                version = int(content["version"])
            #get the extension from the filename
            extension = file.filename.rsplit('.', 1)[1].lower()
            #create an entry for the artifact in the artifact table
            sqlUp = "INSERT INTO artifact (owner_id, artifact_repo, artifact_access_level, artifact_name, artifact_original_filetype, artifact_creation_date) VALUES (%s, %s, %s, %s, %s, %s)"
            dataUp = (user_id, repo_id, int(content["artifact_access_level"]), str(content["artifact_name"]), extension, datecreated)
            self.cursor.execute(sqlUp, dataUp)
            self.connector.commit()
        #artifact has been uploaded before so its an update get the max version and increment by 1
        else:
            sql = "SELECT MAX(version) FROM artifact_change_record WHERE artifact_id = %s"
            val = (artifact_id, )
            self.cursor.execute(sql, val)
            results = self.cursor.fetchall()
            version = results[0][0] + 1
        
        #check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            payload = {
                "err_message": "No file part."
            }
            return (json.dumps(payload), 404)
        #if user does not select file, browser also
        #submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            payload = {
                "err_message": "No selected file."
            }
            return (json.dumps(payload), 404)
        #make the fileneame secure and save it   
        filename = secure_filename(file.filename)
        file.save(os.path.join(UPLOAD_FOLDER, filename))
        artifact_id = self.get_artifact_id(user_id, repo_id, str(content["artifact_name"]))

        if file and self.allowed_file(file.filename):
            if self.convertible_file(file.filename):
                tempname = str(content["artifact_name"])
                extension = file.filename.rsplit('.', 1)[1].lower()
                filename = self.convertToMD(tempname, extension)

            sqlTwo = "INSERT INTO artifact_change_record (change_datetime, changer_id, artifact_id, artifact_blob, version) VALUES (%s, %s, %s, %s, %s)"
            #datetime from artifact_creation_date, changer_id from owner_id, artifact_size get file size, convert to blob
            #(variable for version) = (query for previous version, if updating; 1 if no previous version)
            artifact_blob = open(os.path.join(UPLOAD_FOLDER, filename), "rb").read()
            dataTwo = (datecreated, user_id, artifact_id, artifact_blob, version)
            self.cursor.execute(sqlTwo, dataTwo)
            self.connector.commit()
            payload = {
                    "err_message": "Success: Artifact uploaded."
                }
            return (json.dumps(payload), 201)
        else:
            #needs a location for the file we stored
            temp = UPLOAD_FOLDER + file.filename
            sqlTwo = "INSERT INTO artifact_change_record (change_datetime, changer_id, artifact_id, version) VALUES (%s, %s, %s, %s)"
            #datetime from artifact_creation_date, changer_id from owner_id, artifact_size get file size, convert to blob
            #(variable for version) = (query for previous version, if updating; 1 if no previous version)
            dataTwo = (datecreated, user_id, artifact_id, version)    
            self.cursor.execute(sqlTwo, dataTwo)
            self.connector.commit()
            payload = {
                    "err_message": "Success: Artifact uploaded."
                }
            return (json.dumps(payload), 201)

    def artifact_scrape(self, content):
        self.ensureConnected()

        if content.get("user_id", "") == "":
            user_id = self.get_user_id(str(content["username"]), str(content["password"]))        
            if user_id == "":
                return (json.dumps(AUTHENTICATE_FAIL), 401)
        else:
            user_id = int(content["user_id"])

        if content.get("repository_id", "") == "":
            repo_id = self.get_repo_id(str(content["repo_name"]), user_id)
            if repo_id == "":
                return (json.dumps(NO_REPO), 400)
        else:
            repo_id = int(content["repository_id"])

        #collects file from url
        retrieved_file = requests.get(content["desired_url"])
        
        #https://www.w3.org/TR/PNG/iso_8859-1.txt
        only_filename = content["desired_url"].split("/")[-1]
        retrieved_filename = os.path.join(UPLOAD_FOLDER, only_filename)
        with open(retrieved_filename, "wb") as file_on_disk:
            file_on_disk.write(retrieved_file.content)

        #gets extension of file and gets the time of creation
        #tempname = str(content["artifact_name"])
        extension = retrieved_filename.rsplit('.', 1)[1].lower()
        #conversion = self.convertToMD(tempname, extension)
        datecreated = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
        artifact_id = self.get_artifact_id(user_id, repo_id, str(content["artifact_name"]))
        print(artifact_id, file=sys.stderr)
        if artifact_id == "":
            if str(content["version"]) == "":
                version = 1
            else:
                version = int(content["version"])
            #extension = retrieved_filename.rsplit('.', 1)[1].lower()
            sqlUp = "INSERT INTO artifact (owner_id, artifact_repo, artifact_access_level, artifact_name, artifact_original_filetype, artifact_creation_date) VALUES (%s, %s, %s, %s, %s, %s)"
            dataUp = (user_id, repo_id, int(content["artifact_access_level"]), str(content["artifact_name"]), extension, datecreated)
            self.cursor.execute(sqlUp, dataUp)
            self.connector.commit()

            artifact_id = self.get_artifact_id(user_id, repo_id, str(content["artifact_name"]))
        else:
            sql = "SELECT MAX(version) FROM artifact_change_record WHERE artifact_id = %s"
            val = (artifact_id, )
            self.cursor.execute(sql, val)
            results = self.cursor.fetchall()
            version = results[0][0] + 1
        
        if self.allowed_file(only_filename):
            if self.convertible_file(only_filename):
                tempname = only_filename.rsplit('.', )[0].lower()
                print(tempname, file=sys.stderr)
                print(extension, file=sys.stderr)
                retrieved_filename = self.convertToMD(tempname, extension)
        
            sqlTwo = "INSERT INTO artifact_change_record (change_datetime, changer_id, artifact_id, artifact_blob, version) VALUES (%s, %s, %s, %s, %s)"
            artifact_blob = open(retrieved_filename, "rb").read()
            dataTwo = (datecreated, user_id, artifact_id, artifact_blob, version)
            self.cursor.execute(sqlTwo, dataTwo)
            self.connector.commit()
            payload = {
                "err_message": "Success: Artifact uploaded."
            }
            return (json.dumps(payload), 201)
        else:
            #needs a location for the file we stored
            sqlTwo = "INSERT INTO artifact_change_record (change_datetime, changer_id, artifact_id, version) VALUES (%s, %s, %s, %s)"
            #datetime from artifact_creation_date, changer_id from owner_id, artifact_size get file size, convert to blob
            #(variable for version) = (query for previous version, if updating; 1 if no previous version)
            dataTwo = (datecreated, user_id, artifact_id, version)    
            self.cursor.execute(sqlTwo, dataTwo)
            self.connector.commit()
            payload = {
                    "err_message": "Success: Artifact uploaded."
                }
            return (json.dumps(payload), 201)
        
    #create a repository as long as the user has permission and no repository they own has the same name
    def create_repo(self,content):
        self.ensureConnected()
        #authenticate
        if content.get("user_id", "") == "":
            user_id = self.get_user_id(str(content["username"]), str(content["password"]))        
            if user_id == "":
                return (json.dumps(AUTHENTICATE_FAIL), 401) 
        else:
            user_id = int(content["user_id"])  
        
        if self.get_permission_level(user_id) >= 3:
            sql = "SELECT * FROM repository WHERE repo_creator = %s && repo_name = %s"
            val = (user_id, str(content["repo_name"]))
            self.cursor.execute(sql, val)
            temp = self.cursor.fetchall()
            #make sure no other repositories you own have the same name
            if len(temp) == 0:
                #create the repository
                sql = "INSERT INTO repository (repo_creator, permission_req, repo_name) VALUES (%s, %s, %s)"
                data = (user_id, int(content["permission_req"]), str(content["repo_name"]))
                #repo_creator pulled from user_id from current user, the user creating the repo
                self.cursor.execute(sql, data)
                self.connector.commit()

                #get the repository information to return the info to the user
                sql2 = "SELECT * FROM repository WHERE repo_name = %s"
                self.ensureConnected()
                self.cursor.execute(sql2, (str(content["repo_name"]), ))
                temp = self.cursor.fetchall()
                payload = {
                    "repo_name": str(temp[0][3]),
                    "owner_id": str(temp[0][1]),
                    "err_message": "Success: Repository created. " 
                }
                return (json.dumps(payload), 201)
            else:
                payload = {
                    "err_message": "Failure: You already own a repository with this name."
                }
                return (json.dumps(payload), 400)
        else:
            payload = {
                "err_message: Failure you do not have permission to create a repository."
            }
        return (json.dumps(payload), 401)

    #change a users username (not implemented in the ui)
    def change_username(self,content):
        self.ensureConnected()

        if content.get("user_id", "") == "":
            user_id = self.get_user_id(str(content["username"]), str(content["password"]))        
            if user_id == "":
                return (json.dumps(AUTHENTICATE_FAIL), 401)   
        else:
            user_id = int(content["user_id"])
       
        sql = "UPDATE user SET username = %s WHERE user_id = %s"
        val = (str(content["new_username"]), user_id)
        self.cursor.execute(sql, val)
        self.connector.commit()
        payload = {
            "err_message": "Success: Username changed."
        }
        return (json.dumps(payload), 202)
    
    #update the repositories attributes (still in progress)
    def update_repo_attrib(self,content):
        self.ensureConnected()

        if content.get("user_id", "") == "":
            user_id = self.get_user_id(str(content["username"]), str(content["password"]))        
            if user_id == "":
                return (json.dumps(AUTHENTICATE_FAIL), 401)   
        else:
            user_id = int(content["user_id"])
        
        if content.get("repository_id", "") == "":
            repo_id = self.get_repo_id(str(content["repo_name"]), user_id)
            if repo_id == "":
                return (json.dumps(NO_REPO), 400)
        else:
            repo_id = int(content["repository_id"])

        if self.get_permission_level(user_id) >= 3:
            sql = "SELECT repo_creator FROM repository WHERE repository_id = %s"
            self.cursor.execute(sql, (repo_id, ))
            temp = self.cursor.fetchall()
            if int(temp[0][0]) == user_id or (int(self.get_permission_level(user_id)) == 5):
                if content.get("new_repo_creator", "") != "":
                    sql = "UPDATE repository WHERE repository_id = %s SET repo_creator = %s"
                    val = (repo_id, str(content["new_repo_creator"]))
                    self.cursor.execute(sql, val)
                    self.cursor.commit()
                if content.get("new_permission_req", "") != "":
                    sql = "UPDATE repository WHERE repository_id = %s SET permission_req = %s"
                    val = (repo_id, str(content["new_permission_req"]))
                    self.cursor.execute(sql, val)
                    self.cursor.commit()
                if content.get("new_repo_name", "") != "":
                    sql = "UPDATE repository WHERE repository_id = %s SET repo_name = %s"
                    val = (repo_id, str(content["new_repo_name"]))
                    self.cursor.execute(sql, val)
                    self.cursor.commit()
                if content.get("tag", "" != ""):
                    #tagging info will go here i think
                    sql = "UPDATE"
                payload = {
                    "err_message": "Success: Repo attributes changes."
                }
                return (json.dumps(payload), 202)
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
    
    #This on needs a lot of attention
    def update_artifact_attrib(self,content):
        self.ensureConnected()

        if content.get("user_id", "") == "":
            user_id = self.get_user_id(str(content["username"]), str(content["password"]))        
            if user_id == "":
                return (json.dumps(AUTHENTICATE_FAIL), 401)   
        else:
            user_id = int(content["user_id"])
        
        if content.get("repository_id", "") == "":
            repo_id = self.get_repo_id(str(content["repo_name"]), user_id)
            if repo_id == "":
                return (json.dumps(NO_REPO), 400)
        else:
            repo_id = int(content["repository_id"])

        if content.get("artifact_id", "") == "":
            sql = "SELECT artifact_id FROM artifact WHERE artifact_repo = %s && artifact_name = %s"
            data = (repo_id, str(content["artifact_name"]))
            self.cursor.execute(sql, data)
            temp = self.cursor.fetchall()
            if len(temp) == 0:
                payload = {
                    "err_message": "Failure: That artifact does not exist."
                }
                return (json.dumps(payload), 400)
            artifact_id = int(temp[0][0])
        else:
            artifact_id = int(content["artifact_id"])
        
        if self.get_permission_level(user_id) >= 3:
            sql = "SELECT owner_id FROM artifact WHERE artifact_id = %s"
            self.cursor.execute(sql, (artifact_id, ))
            temp = self.cursor.fetchall()
            if int(temp[0][0]) == user_id or (int(self.get_permission_level(user_id)) == 5):
                if content.get("new_owner_id", "") != "":
                    sql = "UPDATE artifact WHERE artifact_id = %s SET owner_id = %s"
                    val = (artifact_id, str(content["new_owner_id"]))
                    self.cursor.execute(sql, val)
                    self.cursor.commit()
                if content.get("new_access_level", "") != "":
                    sql = "UPDATE artifact WHERE artifact_id = %s SET access_level = %s"
                    val = (artifact_id, str(content["new_access_level"]))
                    self.cursor.execute(sql, val)
                    self.cursor.commit()
                if content.get("new_artifact_original_source", "") != "":
                    sql = "UPDATE artifact WHERE artifact_id = %s SET artifact_original_source = %s"
                    val = (artifact_id, str(content["new_artifact_original_source"]))
                    self.cursor.execute(sql, val)
                    self.cursor.commit()
                if content.get("new_artifact_name", "") != "":
                    sql = "UPDATE artifact WHERE artifact_id = %s SET artifact_name = %s"
                    val = (artifact_id, str(content["new_artifact_name"]))
                    self.cursor.execute(sql, val)
                    self.cursor.commit()       
                payload = {
                    "err_message": "Success: Artifact attributes changes."
                }
                return (json.dumps(payload), 202)
            else:
                payload = {
                    "err_message": "Failure: You do not have permission to change attributes on this artifact."
                }
                return (json.dumps(payload), 401)
        else:
            payload = {
                "err_message": "Failure: You do not have permission to change attributes on this artifact."
            }
            return (json.dumps(payload), 401)
    
    #Get information on an artifact 
    def artifact_info(self, content):
        self.ensureConnected()

        if content.get("user_id", "") == "":
            user_id = self.get_user_id(str(content["username"]), str(content["password"]))        
            if user_id == "":
                return (json.dumps(AUTHENTICATE_FAIL), 401)   
        else:
            user_id = int(content["user_id"])
        
        permission_level = self.get_permission_level(user_id)

        if content.get("repository_id", "") == "":
            repo_id = self.get_repo_id(str(content["repo_name"]), permission_level)
            if repo_id == "":
                return (json.dumps(NO_REPO), 400)
        else:
            repo_id = int(content["repository_id"])
        
        if content.get("artifact_id", "") == "":
            sql = "SELECT artifact_id FROM artifact WHERE artifact_repo = %s && artifact_name = %s"
            data = (repo_id, str(content["artifact_name"]))
            self.cursor.execute(sql, data)
            temp = self.cursor.fetchall()
            if len(temp) == 0:
                payload = {
                    "err_message": "Failure: That artifact does not exist."
                }
                return (json.dumps(payload), 400)
            artifact_id = int(temp[0][0])
        else:
            artifact_id = int(content["artifact_id"])

        sql = "SELECT * FROM artifact WHERE artifact_repo = %s && artifact_id = %s"
        data = (repo_id, artifact_id)
        self.cursor.execute(sql, data)
        artifact_data = self.cursor.fetchall()

        if content.get("version", "") == "":
            sql = "SELECT MAX(version) FROM artifact_change_record WHERE artifact_id = %s"
            data = (artifact_id, )
            self.cursor.execute(sql, data)
            temp = self.cursor.fetchall()
            version = int(temp[0][0])
        else:
            version = (int(content["version"]))
        
        sql = "SELECT * FROM artifact_change_record WHERE artifact_id = %s && version = %s"
        data = (artifact_id, version)
        self.cursor.execute(sql, data)
        artifact_change = self.cursor.fetchall()
    
        payload = {
            "artifact_id": str(artifact_data[0][0]),
            "owner_id": str(artifact_data[0][1]),
            "repository_id": str(artifact_data[0][2]),
            "artifact_access_level": str(artifact_data[0][3]),
            "artifact_name": str(artifact_data[0][4]),
            "artifact_original_source": str(artifact_data[0][5]),
            "artifact_original_filetype": str(artifact_data[0][6]),
            "artifact_creation_date": str(artifact_data[0][7]),
            "artifact_last_accessed": str(artifact_data[0][8]),
            "artifact_access_count": str(artifact_data[0][9]),
            "change_datetime": str(artifact_change[0][0]),
            "artifact_size": str(artifact_change[0][3]),
            "version": str(artifact_change[0][5])
        }
        return (json.dumps(payload), 200)
    
    #Get information on a repo
    def repo_info(self,content):
        self.ensureConnected()
        
        if content.get("user_id", "") == "":
            user_id = self.get_user_id(str(content["username"]), str(content["password"]))        
            if user_id == "":
                return (json.dumps(AUTHENTICATE_FAIL), 401)   
        else:
            user_id = int(content["user_id"])
        
        permission_level = self.get_permission_level(user_id)

        if content.get("repository_id", "") == "":
            repo_id = self.get_repo_id(str(content["repo_name"]), permission_level)
            if repo_id == "":
                return (json.dumps(NO_REPO), 400)
        else:
            repo_id = int(content["repository_id"])

        sql = "SELECT * FROM repository WHERE repository_id = %s"
        data = (repo_id, )
        self.cursor.execute(sql, data)
        repo_data = self.cursor.fetchall()

        payload = {
            "repository_id": str(repo_data[0][0]),
            "repo_name": str(repo_data[0][3]),
            "repo_creator": str(repo_data[0][1]),
            "permission_req": str(repo_data[0][2])
        }
        return (json.dumps(payload), 200)

    '''
    def diff(self, content):
        #check file type, can be diff'd, full diff
        #can't be diff'd, simple compare
    
    '''
    #html file which shows a side by side difference of the attributes of an artifact
    def simple_compare (self, content):
        self.ensureConnected()

        if content.get("user_id", "") == "":
            user_id = self.get_user_id(str(content["username"]), str(content["password"]))        
            if user_id == "":
                return (json.dumps(AUTHENTICATE_FAIL), 401)   
        else:
            user_id = int(content["user_id"])
        
        permission_level = self.get_permission_level(user_id)

        if content.get("repository_id", "") == "":
            repo_id = self.get_repo_id(str(content["repo_name"]), permission_level)
            if repo_id == "":
                return (json.dumps(NO_REPO), 400)
        else:
            repo_id = int(content["repository_id"])
        
        if content.get("artifact_id", "") == "":
            sql = "SELECT artifact_id FROM artifact WHERE artifact_repo = %s && artifact_name = %s"
            data = (repo_id, str(content["artifact_name"]))
            self.cursor.execute(sql, data)
            temp = self.cursor.fetchall()
            if len(temp) == 0:
                payload = {
                    "err_message": "Failure: That artifact does not exist."
                }
                return (json.dumps(payload), 400)
            artifact_id = int(temp[0][0])
        else:
            artifact_id = int(content["artifact_id"])

        if content.get("version", "") == "":
            sql = "SELECT MAX(version) FROM artifact_change_record WHERE artifact_id = %s"
            data = (artifact_id, )
            self.cursor.execute(sql, data)
            temp = self.cursor.fetchall()
            version = int(temp[0][0])
        else:
            version = (int(content["version"]))
        
        sql = "SELECT change_datetime, changer_id, artifact_id, artifact_size, version FROM artifact_change_record WHERE artifact_id = %s && version = %s"
        data = (artifact_id, version)
        self.cursor.execute(sql, data)
        temp = self.cursor.fetchall()
        artifact_change = "change datettime: " + str(temp[0][0]) + ",\nchanger id: " + str(temp[0][1]) + ",\nartifact_id: " + str(temp[0][2]) + ",\nartifact size: " + str(temp[0][3]) + ",\nversion: " + str(temp[0][4]) + '\n'


        if content.get("previous_version", "") == "":
            sql = "SELECT MAX(version) FROM artifact_change_record WHERE artifact_id = %s"
            data = (artifact_id, )
            self.cursor.execute(sql, data)
            temp = self.cursor.fetchall()
            version = int(temp[0][0])
        else:
            version = (int(content["previous_version"]))

        sql = "SELECT change_datetime, changer_id, artifact_id, artifact_size, version FROM artifact_change_record WHERE artifact_id = %s && version = %s"
        data = (artifact_id, version)
        self.cursor.execute(sql, data)
        temp = self.cursor.fetchall()
        artifact_change_previous = "change datettime: " + str(temp[0][0]) + ",\nchanger id: " + str(temp[0][1]) + ",\nartifact_id: " + str(temp[0][2]) + ",\nartifact size: " + str(temp[0][3]) + ",\nversion: " + str(temp[0][4]) + '\n'

        d = difflib.HtmlDiff()
        return  (d.make_file(artifact_change.split('\n'), artifact_change_previous.split('\n')), 200)
        #to only return a HTML table for ui to use if they need it
        #return (d.make_table(artifact_change.split('\n'), artifact_change_previous.split('\n')), 200)
    '''
    def remove_repo(self,content):

    def remove_artifact(self, content):

    def remove_user(self, content): 

    def remove_tag(self, content)
    '''
    #returns an artifact from the database
    def export_artifact(self, content):
        self.ensureConnected()

        if content.get("user_id", "") == "":
            user_id = self.get_user_id(str(content["username"]), str(content["password"]))        
            if user_id == "":
                return (json.dumps(AUTHENTICATE_FAIL), 401)   
        else:
            user_id = int(content["user_id"])
        
        permission_level = self.get_permission_level(user_id)

        if content.get("repository_id", "") == "":
            repo_id = self.get_repo_id(str(content["repo_name"]), permission_level)
            if repo_id == "":
                return (json.dumps(NO_REPO), 400)
        else:
            repo_id = int(content["repository_id"])
        
        if content.get("artifact_id", "") == "":
            sql = "SELECT artifact_id FROM artifact WHERE artifact_repo = %s && artifact_name = %s"
            data = (repo_id, str(content["artifact_name"]))
            self.cursor.execute(sql, data)
            temp = self.cursor.fetchall()
            if len(temp) == 0:
                payload = {
                    "err_message": "Failure: That artifact does not exist."
                }
                return (json.dumps(payload), 400)
            artifact_id = int(temp[0][0])
        else:
            artifact_id = int(content["artifact_id"])

        #get the information on the artifact we want to send
        sql = "SELECT * FROM artifact WHERE artifact_repo = %s && artifact_id = %s"
        data = (repo_id, artifact_id)
        self.cursor.execute(sql, data)
        artifact_data = self.cursor.fetchall()
        
        #check to see if the user specified a version if not then use the highest version
        if content.get("version", "") == "":
            sql = "SELECT MAX(version) FROM artifact_change_record WHERE artifact_id = %s"
            data = (artifact_id, )
            self.cursor.execute(sql, data)
            temp = self.cursor.fetchall()
            version = int(temp[0][0])
        else:
            version = (int(content["version"]))

        #get the artifact change record of the artifact with the version which has the blob in it
        sql = "SELECT * FROM artifact_change_record WHERE artifact_id = %s && version = %s"
        data = (artifact_id, version)
        self.cursor.execute(sql, data)
        artifact_change = self.cursor.fetchall()
        
        #create the names which will be used for the conversion if needed
        filename = str(artifact_data[0][4]) + '.'
        fullfilename = filename + str(artifact_data[0][6])

        blobfile = artifact_change[0][4]
        
        if str(artifact_data[0][6]) in CONVERTIBLE_EXTENSIONS:
            filenameMD = filename + 'md'
            with open(filenameMD, 'wb') as file:
                file.write(blobfile)

            if content.get("new_file_type", "") == "":
                convertedfile = self.convertFromMD(filenameMD, str(artifact_data[0][6]))
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

            return (send_file(fullfilename, attachment_filename=fullfilename))

    #add one or more tags to a repository or an artifact
    def add_tag(self, content):
        #if the tag field is missing or no tags are in the json
        if content.get("tag", "") == "":
            payload = {
                "err_message": "No tags specified."
            }
            return (json.dumps(payload), 400)
        #option 0 is intitial value (empty), 1 is repo, 2 is artifact
        option = 0
        if content.get("repo_name", "") != "":
            option = 1
        elif content.get("artifact_name", "") != "" or content.get("artifact_id", "") != "":
            option = 2
        #if the json passed in has neither artifact nor repo stuff, return error
        else:
            payload = {
                "err_message": "No artifact or repository specified."
            }
            return (json.dumps(payload), 400)
        
        tempRepoID = 0
        tempArtifactID = 0
        
        #if tagging a repo
        if option == 1:
            #query for repo id
            sql = "SELECT repository_id FROM repository WHERE repo_name = %s"
            val = (str(content["repo_name"]), )
            self.cursor.execute(sql, val)
            result = self.cursor.fetchall()
            tempRepoID = int(result[0][0])
        #if tagging an artifact
        if option == 2:
            if content.get("artifact_id", "") == "":
                #query for artifact id
                sql = "SELECT artifact_id FROM artifact WHERE artifact_name = %s"
                val = (str(content["artifact_name"]), )
                self.cursor.execute(sql, val)
                result = self.cursor.fetchall()
                tempArtifactID = int(result[0][0])
            else:
                tempArtifactID = int(content["artifact_id"])

        #process tag input(s)
        for x in content["tag"]:
            #check for duplicate in tag table
            sql = "SELECT * FROM tag WHERE tag_name = %s and (repo_id = %s or artifact_id = %s)"
            val = (x, tempRepoID, tempArtifactID)
            self.cursor.execute(sql, val)
            result = self.cursor.fetchall()
            #if tag input isnt a duplicate
            if len(result) == 0:
                #if user is tagging a repo
                if tempArtifactID == 0:
                    #add new row to tag table with repo id and specified tag
                    sql = "INSERT INTO tag (tag_name, repo_id) VALUES(%s, %s)"
                    val = (x, tempRepoID)
                    self.cursor.execute(sql, val)
                    self.connector.commit()
                    payload = {
                        "err_message": "Repository successfully tagged."
                    }
                #if user is tagging an artifact
                elif tempRepoID == 0:    
                    #add new row to tag table with artifact id and specified tag
                    sql = "INSERT INTO tag (tag_name, artifact_id) VALUES(%s, %s)"
                    val = (x, tempArtifactID)
                    self.cursor.execute(sql, val)
                    self.connector.commit()
                    payload = {
                        "err_message": "Artifact successfully tagged."
                    }
            #if the tag already exists
            else:  
                payload = {
                    "err_message": "Tag already exists."
                }
                return (json.dumps(payload), 400)
        return (json.dumps(payload), 202)
            
    '''
    def add_bookmark(self,content):

    def change_tag(self, content):

    def remove_bookmark(self, content):
    '''
    
    def return_artifact_list(self, content):
        self.ensureConnected()

        if content.get("user_id", "") == "":
            user_id = self.get_user_id(str(content["username"]), str(content["password"]))        
            if user_id == "":
                return (json.dumps(AUTHENTICATE_FAIL), 401)   
        else:
            user_id = int(content["user_id"])
        
        sql = "SELECT artifact_name FROM artifact WHERE permission_level <= %s"
        val = (self.get_permission_level(user_id), )
        self.cursor.execute(sql, val)
        result = self.cursor.fetchall()
        payload = {
            "err_message": "List of artifacts you have access to.",
            "repository_id": result
        }
        return (json.dumps(payload), 202)

    def return_repo_list(self, content):
        self.ensureConnected()

        if content.get("user_id", "") == "":
            user_id = self.get_user_id(str(content["username"]), str(content["password"]))        
            if user_id == "":
                return (json.dumps(AUTHENTICATE_FAIL), 401)   
        else:
            user_id = int(content["user_id"])
        
        sql = "SELECT repo_name FROM repository WHERE permission_level <= %s"
        val = (self.get_permission_level(user_id), )
        self.cursor.execute(sql, val)
        result = self.cursor.fetchall()
        payload = {
            "err_message": "List of repositories you have access to.",
            "repository_id": result
        }
        return (json.dumps(payload), 202)

    