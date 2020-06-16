import mysql.connector
from database import cursor

DATABASE_NAME = 'A3database'

TABLES = {}

TABLES['artifact'] = (
    "CREATE TABLE 'Artifact' ("
    " 'artifact_id' int() NOT NULL AUTO_INCREMENT, "
    " 'owner_id' int() NOT NULL,"
    " 'artifact_repo' int() NOT NULL,"
    " 'artifact_last_changed' datetime,"
    " 'artifact_access_level' int() NOT NULL,"
    " 'artifact_name' varchar(40) NOT NULL,"
    " 'artifact_original_source' text,"
    " 'artifact_size' int(),"
    " 'artifact_creation_date' datetime,"
    " 'artifact_last_accessed' datetime,"
    " 'artifact_access_count' int(),"
    ") 
)

def create_database():
    cursor.execute("CREATE DATABASE IF NOT EXISTS {} DEFAULT CHARACTER SET 'utf8'".format(DATABASE_NAME))
    #convert to python f string or prepared query
    #docker volumes persistant 