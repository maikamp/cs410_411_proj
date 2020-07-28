import mysql.connector
import datetime
import requests
import math
import json
import os
import sys
import pypandoc
import difflib
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
    def artifactUpload(self, file, content):
        self.ensureConnected()
        
        content = json.loads(content.read().decode('utf-8'))

  
        if str(content["user_id"]) == "":
            temp = self.get_user_id(str(content["username"]), str(content["password"]))        
            if temp == "":
                payload = {
                    "err_message": "Failure: That username or password does not exist."
                }
                return (json.dumps(payload), 401)   
            user_id = int(temp)
        else:
            user_id = int(content["user_id"])

        repo_id = int(content["repository_id"])
         
        sql = "SELECT artifact_id FROM artifact WHERE owner_id = %s && artifact_repo = %s && artifact_name = %s"
        val = (user_id, repo_id, str(content["artifact_name"]))
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
            dataUp = (user_id, int(content["artifact_repo"]), int(content["artifact_access_level"]), str(content["artifact_name"]), extension, datecreated)
        
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
        filename = secure_filename(file.filename)
        file.save(os.path.join(UPLOAD_FOLDER, filename))
        if file and self.allowed_file(file.filename):
            if self.convertible_file(file.filename):
                tempname = str(content["artifact_name"])
                extension = file.filename.rsplit('.', 1)[1].lower()
                print(filename, file = sys.stderr, end='')
                filename = self.convertToMD(tempname, extension)

            sql = "SELECT artifact_id FROM artifact WHERE owner_id = %s && artifact_repo = %s && artifact_name = %s"
            val = (user_id, repo_id, str(content["artifact_name"]))
            self.cursor.execute(sql, val)
            temp = self.cursor.fetchall()
            sqlTwo = "INSERT INTO artifact_change_record (change_datetime, changer_id, artifact_id, artifact_blob, version) VALUES (%s, %s, %s, %s, %s)"
            #datetime from artifact_creation_date, changer_id from owner_id, artifact_size get file size, convert to blob
            #(variable for version) = (query for previous version, if updating; 1 if no previous version)
            artifact_blob = open(os.path.join(UPLOAD_FOLDER, filename), "rb").read()
            #temp_filename = UPLOAD_FOLDER + '/'
            #temp_blob = temp_filename + file.filename
            dataTwo = (datecreated, user_id, temp[0][0], artifact_blob, version)
            
            self.cursor.execute(sqlTwo, dataTwo)
            self.connector.commit()
            
            payload = {
                    "err_message": "Success: Artifact uploaded."
                }
            return (json.dumps(payload), 201)
        else:
            sql = "SELECT artifact_id FROM artifact WHERE owner_id = %s && artifact_repo = %s && artifact_name = %s"
            val = (user_id, repo_id, str(content["artifact_name"]))
            self.cursor.execute(sql, val)
            temp = self.cursor.fetchall()
            temp = UPLOAD_FOLDER + file.filename
            sqlTwo = "INSERT INTO artifact_change_record (change_datetime, changer_id, artifact_id, version) VALUES (%s, %s, %s, %s)"
            #datetime from artifact_creation_date, changer_id from owner_id, artifact_size get file size, convert to blob
            #(variable for version) = (query for previous version, if updating; 1 if no previous version)

            #temp_filename = UPLOAD_FOLDER + '/'
            #temp_blob = temp_filename + file.filename
            dataTwo = (datecreated, user_id, temp[0][0], version)
            
            self.cursor.execute(sqlTwo, dataTwo)
            self.connector.commit()
            
            payload = {
                    "err_message": "Success: Artifact uploaded."
                }
            return (json.dumps(payload), 201)

    def artifact_scrape(self, content):
        self.ensureConnected()


        if str(content["user_id"]) == "":
            temp = self.get_user_id(str(content["username"]), str(content["password"]))        
            if temp == "":
                payload = {
                    "err_message": "Failure: That username or password does not exist."
                }
                return (json.dumps(payload), 401)   
            user_id = int(temp)
        else:
            user_id = int(content["user_id"])

        repo_id = int(content["repository_id"])

        #retrieved_file = urlopen(content["desired_url"]).read().decode('utf-8')
        #retrieved_file.save(os.path.join(UPLOAD_FOLDER, retrieved_file))

        retrieved_file = requests.get("desired_url")
        soup = BeautifulSoup(retrieved_file.content, 'html_parser')

        soup.save(os.path.join(UPLOAD_FOLDER, retrieved_file))
        datecreated = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sqlUp = "INSERT INTO artifact (owner_id, artifact_repo, artifact_access_level, artifact_name, artifact_original_filetype, artifact_creation_date) VALUES (%s, %s, %s, %s, %s, %s)"
        dataUp = (user_id, int(content["artifact_repo"]), int(content["artifact_access_level"]), str(content["artifact_name"]), ".txt", datecreated)

        self.cursor.execute(sqlUp, dataUp)
        self.connector.commit()

        sql = "SELECT artifact_id FROM artifact WHERE owner_id = %s && artifact_repo = %s && artifact_name = %s"
        val = (user_id, repo_id, str(content["artifact_name"]))
        self.cursor.execute(sql, val)
        temp = self.cursor.fetchall()
        

        sqlTwo = "INSERT INTO artifact_change_record (change_datetime, changer_id, artifact_id, artifact_blob, version) VALUES (%s, %s, %s, %s, %s)"

        artifact_blob = open(os.path.join(UPLOAD_FOLDER, retrieved_file), "rb").read()

        dataTwo = (datecreated, user_id, temp[0][0], artifact_blob, 1)
        
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

        permission_level = self.get_permission_level(user_id)

        sql = "UPDATE artifact WHERE artifact_name = %s && repo_name = %s SET owner_id = %s && artifact_access_level = %s && artifact_name = %s && artifact_original_source = %s"
        val = (str(content["artifact_name"]), str(content["repo_name"]), str(content["attribute": ["owner_id"]]), 
                str(content["attribute": ["artifact_access_level"]]), str(content["attribute": ["artifact_name"]]), 
                str(content["artifact_original_source"]))
        self.cursor.execute(sql, val)
        self.connector.commit()
        payload = {
            "err_message": "Success: Artifact attributes changes."
        }
        return (json.dumps(payload), 202)
    
    '''
    def updateArtifact(self,content): ?
    '''
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
            "artifact_repo": str(artifact_data[0][2]),
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
    def authenticate(self, content):
        #receive username and pw or user_id
        #check against db
        #return tuple (user_id, )

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
        #return  (d.make_table(artifact_change.split('\n'), artifact_change_previous.split('\n')), 200)
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

    #add atag to a repository or a artifact
    def add_tag(self, content):
        #receive user id ?
        #permission check from user id?

        tempRepoID = 0
        tempArtifactID = 0
        #if the json passed in has repo name or id, hold repository_id in tempRepoID
        if str(content["repository_id"]) != "":
            tempRepoID = int(content["repository_id"])
        elif str(content["repository_id"] == "" and str(content["repo_name"]) != ""):
            #query for repo id
            sql = "SELECT repository_id FROM repository WHERE repo_name = %s"
            val = (str(content["repo_name"]), )
            self.cursor.execute(sql, val)
            result = self.cursor.fetchall()
            tempRepoID = result[0][0]
        #if the json passed in has artifact name or id, hold artifact_id in tempArtifactID
        elif str(content["artifact_id"]) != "":
            tempArtifactID = int(content["artifact_id"])
        elif str(content["artifact_id"] == "") and str(content["artifact_name"]) != "":
            #query for artifact id
            sql = "SELECT artifact_id FROM artifact WHERE artifact_name = %s"
            val = (str(content["artifact_name"]), )
            self.cursor.execute(sql, val)
            result = self.cursor.fetchall()
            tempArtifactID = result[0][0]
        #if the json passed in has neither artifact nor repo stuff, return error
        else:
            payload = {
                "err_message": "No artifact or repository specified."
            }
            return (json.dumps(payload), 400)

        #process tag input(s)
        for x in content["tag"]:
            #check to tag table to find match for input tag(s)
            sql = "SELECT tag_name FROM tag WHERE tag_name = %s"
            val = (x, )
            self.cursor.execute(sql, val)
            result = self.cursor.fetchall()
            #if tag doesnt yet exist
            if len(result) == 0:
                #if user is tagging a repo
                if tempArtifactID == 0:
                    #add new row to tag table with repo id and specified tag
                    sql = "INSERT INTO tag (tag_name, repository_id) VALUES(%s, %s)"
                    val = (x, tempRepoID)
                    self.cursor.execute(sql, val)
                    self.connector.commit()
                    payload = {
                        "err_message": "Repository successfully tagged."
                    }
                    return (json.dumps(payload), 202)

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
                    return (json.dumps(payload), 202)

            #if the tag already exists
            else:
                #if user is tagging a repo
                if tempArtifactID == 0:
                    #add new row to tag table with repo id and specified tag
                    sql = "INSERT INTO tag (tag_name, repository_id) VALUES(%s, %s)"
                    val = (x, tempRepoID)
                    self.cursor.execute(sql, val)
                    self.connector.commit()
                    payload = {
                        "err_message": "Repository successfully tagged."
                    }
                    return (json.dumps(payload), 202)

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
                    return (json.dumps(payload), 202)
            
    '''
    def add_bookmark(self,content):

    def change_tag(self, content):

    def remove_bookmark(self, content):
    
    def return_artifact_list(self, content):

    def return_repo_list(self, content):
    '''

    