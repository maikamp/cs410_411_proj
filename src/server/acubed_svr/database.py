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
import base64
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
    def get_repo_id(self, reponame):
        sql = "SELECT repository_id FROM repository WHERE repo_name = %s "
        data = (reponame, )
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
        return int(temp[0][0])

    #get artifact id when you only have the repo name
    def get_artifact_id(self, artifact_name):
        sql = "SELECT artifact_id FROM artifact WHERE artifact_name = %s"
        val = (artifact_name, )
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
        if len(temp) == 0:
            return (json.dumps(AUTHENTICATE_FAIL), 401)
        else:
            if len(temp) == 1:
                payload = {
                    "err_message" : "Successful login.",
                    "user_id" : str(temp[0][0]),
                    "permission_level": str(temp[0][1])
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
            repo_id = self.get_repo_id(str(content["repo_name"]))
            if repo_id == "":
                return (json.dumps(NO_REPO), 400)
        else:
            repo_id = int(content["repository_id"])
         
        if content.get("artifact_id", "") == "":
            artifact_id = self.get_artifact_id(str(content["artifact_name"]))
        else:
            artifact_id = int(content["artifact_id"])
                
        datecreated = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        sql = "SELECT repo_creator FROM repository WHERE repository_id = %s"
        self.cursor.execute(sql, (repo_id, ))
        results = self.cursor.fetchall()

        if (user_id != int(results[0][0])):
            if (self.get_permission_level(user_id) != 5):
                payload = {
                    "err_message": "Failure: Permission Denied."
                }
                return (json.dumps(payload), 403)
        
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
            artifact_id = self.get_artifact_id(str(content["artifact_name"]))  
        #artifact has been uploaded before so its an update get the max version and increment by 1
        else:
                sql = "SELECT MAX(version) FROM artifact_change_record WHERE artifact_id = %s"
                val = (artifact_id, )
                self.cursor.execute(sql, val)
                results = self.cursor.fetchall()
                version = results[0][0] + 1

        #tag goes here 
        tag_return_tuple = self.add_tag(content)
        if tag_return_tuple[1] >= 400:          
            #remove artifact
            sqlRemove = "DELETE FROM artifact WHERE artifact_id = %s"
            valRemove = (artifact_id, )
            self.cursor.execute(sqlRemove, valRemove)
            self.connector.commit()
            #set auto_increment back to reuse index from removed artifact
            sqlDecrIndex = "ALTER TABLE artifact AUTO_INCREMENT = %s"
            valDecrIndex = (1, )
            self.cursor.execute(sqlDecrIndex, valDecrIndex)
            self.connector.commit()
            return tag_return_tuple                            
        
        if file and self.allowed_file(file.filename):
            if self.convertible_file(file.filename):
                tempname = file.filename.rsplit('.', 1)[0]
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
            repo_id = self.get_repo_id(str(content["repo_name"]))
            if repo_id == "":
                return (json.dumps(NO_REPO), 400)
        else:
            repo_id = int(content["repository_id"])

        sql = "SELECT repo_creator FROM repository WHERE repository_id = %s"
        self.cursor.execute(sql,(repo_id, ))
        results = self.cursor.fetchall()
        if (user_id != results[0][0]):
            if (self.get_permission_level(user_id) != 5):
                payload = {
                    "err_message": "Failure: Permission Denied."
                }
                return (json.dumps(payload), 403)

        #collects file from url
        retrieved_file = requests.get(content["desired_url"])
        
        #https://www.w3.org/TR/PNG/iso_8859-1.txt
        file_path = content["desired_url"]
        only_filename = content["desired_url"].split("/")[-1]
        retrieved_filename = os.path.join(UPLOAD_FOLDER, only_filename)
        with open(retrieved_filename, "wb") as file_on_disk:
            file_on_disk.write(retrieved_file.content)

        #gets extension of file and gets the time of creation
        #tempname = str(content["artifact_name"])
        extension = retrieved_filename.rsplit('.', 1)[1].lower()
        #conversion = self.convertToMD(tempname, extension)
        datecreated = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
        artifact_id = self.get_artifact_id(str(content["artifact_name"]))
        if artifact_id == "":
            if str(content["version"]) == "":
                version = 1
            else:
                version = int(content["version"])
            #extension = retrieved_filename.rsplit('.', 1)[1].lower()
            sqlUp = "INSERT INTO artifact (owner_id, artifact_repo, artifact_access_level, artifact_name, artifact_original_source, artifact_original_filetype, artifact_creation_date) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            dataUp = (user_id, repo_id, int(content["artifact_access_level"]), str(content["artifact_name"]), file_path, extension, datecreated)
            self.cursor.execute(sqlUp, dataUp)
            self.connector.commit()

            artifact_id = self.get_artifact_id(str(content["artifact_name"]))
        else:
            sql = "SELECT MAX(version) FROM artifact_change_record WHERE artifact_id = %s"
            val = (artifact_id, )
            self.cursor.execute(sql, val)
            results = self.cursor.fetchall()
            version = results[0][0] + 1
        
        #tag goes here 
        tag_return_tuple = self.add_tag(content)
        if tag_return_tuple[1] >= 400:          
            #remove artifact
            sqlRemove = "DELETE FROM artifact WHERE artifact_id = %s"
            valRemove = (artifact_id, )
            self.cursor.execute(sqlRemove, valRemove)
            self.connector.commit()
            #set auto_increment back to reuse index from removed artifact
            sqlDecrIndex = "ALTER TABLE artifact AUTO_INCREMENT = %s"
            valDecrIndex = (1, )
            self.cursor.execute(sqlDecrIndex, valDecrIndex)
            self.connector.commit()
            return tag_return_tuple
        
        if self.allowed_file(only_filename):
            if self.convertible_file(only_filename):
                tempname = only_filename.rsplit('.', )[0]
                ext = retrieved_filename.rsplit('.', 1)[1]
                retrieved_filename = os.path.join(UPLOAD_FOLDER, self.convertToMD(tempname, ext))
        
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

                #tag goes here 
                tag_return_tuple = self.add_tag(content)
                if tag_return_tuple[1] >= 400:          
                    #remove repo
                    sqlRemove = "DELETE FROM repository WHERE repository_id = %s"
                    valRemove = (self.get_repo_id(str(content["repo_name"])), )
                    self.cursor.execute(sqlRemove, valRemove)
                    self.connector.commit()
                    #set auto_increment back to reuse index from removed repo
                    sqlDecrIndex = "ALTER TABLE repository AUTO_INCREMENT = %s"
                    valDecrIndex = (self.get_repo_id(str(content["repo_name"])), )
                    self.cursor.execute(sqlDecrIndex, valDecrIndex)
                    self.connector.commit()
                    return tag_return_tuple  

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
            repo_id = self.get_repo_id(str(content["repo_name"]))
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
            repo_id = self.get_repo_id(str(content["repo_name"]))
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

        if content.get("repository_id", "") == "":
            repo_id = self.get_repo_id(str(content["repo_name"]))
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

        #get the information that was stored in the artifact table
        sql = "SELECT * FROM artifact WHERE artifact_repo = %s && artifact_id = %s"
        data = (repo_id, artifact_id)
        self.cursor.execute(sql, data)
        artifact_data = self.cursor.fetchall()
        #retrieve artifact owner username
        sql2 = "SELECT username FROM user WHERE user_id = %s"
        val2 = (user_id, )
        self.cursor.execute(sql2, val2)
        owner_name =  self.cursor.fetchall()
        #retrieve tags for this artifact
        sql3 = "SELECT tag_name FROM tag WHERE artifact_id = %s"
        val3 = (artifact_id, )
        self.cursor.execute(sql3, val3)
        repo_tags =  self.cursor.fetchall()

        #if no version was specified get the max version
        if content.get("version", "") == "":
            sql = "SELECT MAX(version) FROM artifact_change_record WHERE artifact_id = %s"
            data = (artifact_id, )
            self.cursor.execute(sql, data)
            temp = self.cursor.fetchall()
            version = int(temp[0][0])
        else:
            version = (int(content["version"]))
        
        #get the stored data from the change record for the version specified or the MAX version
        sql = "SELECT * FROM artifact_change_record WHERE artifact_id = %s && version = %s"
        data = (artifact_id, version)
        self.cursor.execute(sql, data)
        artifact_change = self.cursor.fetchall()
        if (self.get_permission_level(user_id) >= int(artifact_data[0][3])) or (user_id == int(artifact_data[0][1])): 
            payload = {
                "artifact_id": str(artifact_data[0][0]),
                "owner_name": owner_name[0][0],
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
                "version": str(artifact_change[0][5]),
                "tag": repo_tags
            }
            return (json.dumps(payload), 200)
        else:
            payload = {
                "err_message": "Failure: Permission Denied."
            }
            return (json.dumps(payload), 403)

    #Get information on a repo
    def repo_info(self,content):
        self.ensureConnected()
        #get the user_id or find it when a username and password are present
        if content.get("user_id", "") == "":
            user_id = self.get_user_id(str(content["username"]), str(content["password"]))        
            if user_id == "":
                return (json.dumps(AUTHENTICATE_FAIL), 401)   
        else:
            user_id = int(content["user_id"])
        #get the repo id or look it up when the name is present
        if content.get("repository_id", "") == "":
            repo_id = self.get_repo_id(str(content["repo_name"]))
            if repo_id == "":
                return (json.dumps(NO_REPO), 400)
        else:
            repo_id = int(content["repository_id"])
        #get the attributes for the repo_id
        sql = "SELECT * FROM repository WHERE repository_id = %s"
        data = (repo_id, )
        self.cursor.execute(sql, data)
        repo_data = self.cursor.fetchall()
        #retrieve repo owner username
        sql2 = "SELECT username FROM user WHERE user_id = %s"
        val2 = (user_id, )
        self.cursor.execute(sql2, val2)
        owner_name =  self.cursor.fetchall()
        #retrieve tags for this repo
        sql3 = "SELECT tag_name FROM tag WHERE repo_id = %s"
        val3 = (repo_id, )
        self.cursor.execute(sql3, val3)
        repo_tags =  self.cursor.fetchall()
        #get the permission level of the user
        if (self.get_permission_level(user_id) >= int(repo_data[0][2])) or (user_id == int(repo_data[0][1])): 
            payload = {
                "repository_id": str(repo_data[0][0]),
                "repo_name": str(repo_data[0][3]),
                "repo_creator": owner_name[0][0],
                "permission_req": str(repo_data[0][2]),
                "tag": repo_tags
            }
            return (json.dumps(payload), 200)
        else:
            payload = {
                "err_message": "Failure: Permission Denied."
            }
            return (json.dumps(payload), 403)

    #Create a line by line diference report between versions
    def diff(self, content):
        #check file type, can be diff'd, full diff
        #can't be diff'd, simple compare
        self.ensureConnected()
        if content.get("user_id", "") == "":
            user_id = self.get_user_id(str(content["username"]), str(content["password"]))        
            if user_id == "":
                return (json.dumps(AUTHENTICATE_FAIL), 401)   
        else:
            user_id = int(content["user_id"])

        if content.get("repository_id", "") == "":
            repo_id = self.get_repo_id(str(content["repo_name"]))
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

        
        sql = "SELECT artifact_original_filetype WHERE artifact_id =%s"
        data = (artifact_id, )
        self.cursor.execute(sql, data)
        ext = self.cursor.fetchall()
        

        if ext in CONVERTIBLE_EXTENSIONS or ext == 'md':
            if content.get("version", "") == "":
                sql = "SELECT MAX(version) FROM artifact_change_record WHERE artifact_id = %s"
                data = (artifact_id, )
                self.cursor.execute(sql, data)
                temp = self.cursor.fetchall()
                version = int(temp[0][0])
            else:
                version = (int(content["version"]))

            sql = "SELECT artifact_blob FROM artifact_change_record WHERE artifact_id = %s && version = %s"
            data = (artifact_id, version)
            self.cursor.execute(sql, data)
            temp = self.cursor.fetchall()
            artifact_change = temp[0][0]
            extracted_data = artifact_change.decode('utf-8')
            readable_data = list(extracted_data.split('  '))
            
            if content.get("previous_version", "") == "":
                sql = "SELECT MAX(version) FROM artifact_change_record WHERE artifact_id = %s"
                data = (artifact_id, )
                self.cursor.execute(sql, data)
                temp = self.cursor.fetchall()
                version = int(temp[0][0])
            else:
                version = (int(content["previous_version"]))

            sql = "SELECT artifact_blob FROM artifact_change_record WHERE artifact_id = %s && version = %s"
            data = (artifact_id, version)
            self.cursor.execute(sql, data)
            temp = self.cursor.fetchall()
            artifact_change_previous = temp[0][0]
            extracted_data_previous_version = artifact_change_previous.decode('utf-8')
            readable_data_previous_version = list(extracted_data_previous_version.split('  '))
            with open("diffcompare.txt", "w") as file_out:
                #for line in list(difflib.context_diff(extracted_data, extracted_data_previous_version)):
                for i in difflib.context_diff(readable_data, readable_data_previous_version):
                    file_out.write(i)

            #with open("diffcompare.txt", "w") as file_out:
            #file_out.writelines(difflib.context_diff(extracted_data, extracted_data_previous_version))  
                
            return(send_file("diffcompare.txt", attachment_filename="diffcompare.txt"), 200)
            #d = difflib.Differ()
            #return  (d.compare(extracted_data, extracted_data_previous_version), 200)
            # read file into string, return said string

        else:
            payload = {
                "err_message": "Wrong file type, must be a convertable file type (doc, docx, odt, htm, html)"
            }
            return (json.dumps(payload),400)
                     
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
            repo_id = self.get_repo_id(str(content["repo_name"]))
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
        artifact_change = ["change datettime: " + str(temp[0][0]) + "\n", "changer id: " + str(temp[0][1]) + "\n", "artifact_id: " + str(temp[0][2]) + "\n", "artifact size: " + str(temp[0][3]) + "\n", "version: " + str(temp[0][4]) + "\n"]


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
        artifact_change_previous = ["change datettime: " + str(temp[0][0]) + "\n", "changer id: " + str(temp[0][1]) + "\n", "artifact_id: " + str(temp[0][2]) + "\n", "artifact size: " + str(temp[0][3]) + "\n", "version: " + str(temp[0][4]) + "\n"]

        #d = difflib.HtmlDiff()
        #return  (d.make_file(artifact_change.split('\n'), artifact_change_previous.split('\n')), 200)
        '''
        with open("simplecompare.txt", "w") as file_out:
            #for line in list(difflib.context_diff(extracted_data, extracted_data_previous_version)):
            for i in difflib.context_diff(list(artifact_change), list(artifact_change_previous)):
                file_out.write('\n'.join(i))
        '''
        with open("simplecompare.txt", "w") as file_out:
            file_out.writelines(difflib.context_diff(artifact_change, artifact_change_previous))
        return(send_file("simplecompare.txt", attachment_filename="simplecompare.txt"), 200)
        # read file into string, return said string
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

        if content.get("repository_id", "") == "":
            repo_id = self.get_repo_id(str(content["repo_name"]))
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
                    return (json.dumps(payload), 400)
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
        tag_count = 0
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
                    tag_count = tag_count + 1
                #if user is tagging an artifact
                else:    
                    #add new row to tag table with artifact id and specified tag
                    sql = "INSERT INTO tag (tag_name, artifact_id) VALUES(%s, %s)"
                    val = (x, tempArtifactID)
                    self.cursor.execute(sql, val)
                    self.connector.commit()
                    tag_count = tag_count + 1
        return (0 ,tag_count)
            
    '''
    def add_bookmark(self,content):

    def change_tag(self, content):

    def remove_bookmark(self, content):
    '''
    
    def return_artifact_list(self, content):
        self.ensureConnected()
        #acquire user id
        if content.get("user_id", "") == "":
            user_id = self.get_user_id(str(content["username"]), str(content["password"]))        
            if user_id == "":
                user_id = 1    
        else:
            user_id = int(content["user_id"])

        #retrieve artifact names for all artifacts user has permission to view
        if content.get("return_type", "") == "all":
            sql = "SELECT artifact_name, artifact_original_filetype, owner_id FROM artifact WHERE artifact_access_level <= %s || owner_id = %s"
            val = (self.get_permission_level(user_id), user_id)
            self.cursor.execute(sql, val)
            result = self.cursor.fetchall()
            result_list = {}
            i = 0
            for x in result:
                sql = "SELECT username FROM user WHERE user_id = %s"
                val = (x[2], )
                self.cursor.execute(sql, val)
                owner_name =  self.cursor.fetchall()
                result_list[i] = {
                    "artifact_name": x[0],
                    "artifact_original_filetype": x[1],
                    "owner_name": owner_name[0][0]
                }
                i = i + 1
            payload = {
                "err_message": "List of artifacts you have access to.",
                "artifact_name": result_list
            }
            return (json.dumps(payload), 200)

        #retrieve owned artifacts
        elif content.get("return_type", "") == "owned":
            sql = "SELECT artifact_name, artifact_original_filetype FROM artifact WHERE owner_id = %s"
            val = (user_id, )
            self.cursor.execute(sql, val)
            result = self.cursor.fetchall()
            result_list = {}
            i = 0
            for x in result:
                result_list[i] = {
                    "artifact_name": x[0],
                    "artifact_original_filetype": x[1]
                }
                i = i + 1
            payload = {
                "err_message": "List of artifacts you have access to.",
                "artifact_name": result_list
            }
            return (json.dumps(payload), 200)
        else:
            payload = {
                "err_message": "No return type specified."
            }
            return (json.dumps(payload), 400)
        '''
        #retrieve artifacts from specified repo
        sql = "SELECT artifact_name FROM artifact WHERE artifact_repo = %s && (artifact_access_level <= %s || owner_id = %s)"
        if content.get("repository_id", "") != "":
            val = (int(content["repository_id"]), self.get_permission_level(user_id), user_id)
        elif content.get("repo_name", "") != "":
            val = (self.get_repo_id(str(content["repo_name"])), self.get_permission_level(user_id), user_id)
        else:
            payload = {
                "err_message": "No repository specified."
            }
            return (json.dumps(payload), 400)
        self.cursor.execute(sql, val)
        result = self.cursor.fetchall()
        payload = {
            "err_message": "List of artifacts in specified repository.",
            "repository_id": [result]
        }
        return (json.dumps(payload), 202)

        #retrieve artifacts by tag

        '''
#in the json add entry "return_owned": "True or False"
    def return_repo_list(self, content):
        self.ensureConnected()
        #acquire user id
        if content.get("user_id", "") == "":
            user_id = self.get_user_id(str(content["username"]), str(content["password"]))        
            if user_id == "":
                user_id = 1  
        else:
            user_id = int(content["user_id"])
        
        #retrieve all repositories user has permission to view
        if content.get("return_type", "") == "all":
            sql = "SELECT repo_name, repo_creator FROM repository WHERE permission_req <= %s || repo_creator = %s"
            val = (self.get_permission_level(user_id), user_id)
            self.cursor.execute(sql, val)
            result = self.cursor.fetchall()
            result_list = {}
            i = 0
            for x in result:
                sql = "SELECT username FROM user WHERE user_id = %s"
                val = (x[1], )
                self.cursor.execute(sql, val)
                creator_name =  self.cursor.fetchall()
                result_list[i] = {
                    "repo_name": x[0], 
                    "repo_creator": creator_name[0][0]
                    }
                i = i + 1
            payload = {
                "err_message": "List of repositories you have access to.",
                "results": result_list
            }
            return (json.dumps(payload), 200)
            
        #retrieve owned repositories
        elif content.get("return_type", "") == "owned":    
            sql = "SELECT repo_name FROM repository WHERE repo_creator = %s"
            val = (user_id, )
            self.cursor.execute(sql, val)
            result = self.cursor.fetchall()
            result_list = {}
            i = 0
            for x in result:
                result_list[i] = {
                    "repo_name": x[0]
                    }
                i = i + 1
            payload = {
                "err_message": "List of repositories you own.",
                "results": result_list
            }
            return (json.dumps(payload), 200)

        else:
            payload = {
                "err_message": "No return type specified."
            }
            return (json.dumps(payload), 400)

        #retrieve repos by tag

        

    