import mysql.connector
from database import cursor

DATABASE_NAME = 'A3database'

TABLES = {}

TABLES['permission_level'] = """
    CREATE TABLE 'permission_level' (
    'level' int() NOT NULL
    ) ENGINE=InnoDB
    """

TABLES['user'] = """
    CREATE TABLE 'user' (
    'user_id' int() NOT NULL AUTO_INCREMENT,
    'access_level' int() NOT NULL,
    'username' varchar(20) NOT NULL,
    'password' varchar(20) NOT NULL,
    'user_email' varchar(20),
    'last_login' datetime
    ) ENGINE=InnoDB 
    """

TABLES['repository'] = """
    CREATE TABLE 'repository' (
    'repository_id' int() NOT NULL AUTO_INCREMENT,
    'repo_creator' int() NOT NULL,
    'permission_req' int() NOT NULL,
    'repo_name' varchar(20) NOT NULL
    ) ENGINE=InnoDB 
    """

TABLES['artifact'] = """
    CREATE TABLE 'artifact' (
    'artifact_id' int() NOT NULL AUTO_INCREMENT, 
    'owner_id' int() NOT NULL,
    'artifact_repo' int() NOT NULL,
    'artifact_last_changed' datetime,
    'artifact_access_level' int() NOT NULL,
    'artifact_name' varchar(40) NOT NULL,
    'artifact_original_source' text,
    'artifact_size' int(),
    'artifact_creation_date' datetime,
    'artifact_last_accessed' datetime,
    'artifact_access_count' int()
    ) ENGINE=InnoDB
    """

TABLES['artifact_change_record'] = """                                                                                                
    CREATE TABLE 'artifact_change_record' (                                                                                                
    'change_datetime' datetime NOT NULL,                                                                            
    'changer_id' int() NOT NULL,                                                                                              
    'artifact_id' int() NOT NULL,                                                                                          
    'artifact_blob' blob NOT NULL,                                                                                        
    'version' int() NOT NULL                                                                                           
    ) ENGINE=InnoDB                                                                                                          
    """  

TABLES['tag'] = """
    CREATE TABLE 'tag' (
    'tag_name' varchar(20) NOT NULL,
    'repo_id' int(),
    'artifact_id' int()
    ) ENGINE=InnoDB 
    """

TABLES['user_bookmarks'] = """
    CREATE TABLE 'user_bookmarks' (
    'user_id' int() NOT NULL,
    'artifact_id' int(),
    'repo_id' int()
    ) ENGINE=InnoDB 
    """

def create_database():
    cursor.execute("CREATE DATABASE IF NOT EXISTS {} DEFAULT CHARACTER SET 'utf8'".format(DATABASE_NAME))
    #convert to python f string or prepared query
    #docker volumes persistant 