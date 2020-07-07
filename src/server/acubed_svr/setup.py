from __future__ import print_function
import mysql.connector
from mysql.connector import errorcode

config = {
    'user': 'root',
    'password': 'rT1@4PlgTd',
    'host': 'acubed_db',
    'port': '3306'
}

connection = mysql.connector.connect(**config)
cursor = connection.cursor()

DATABASE_NAME = 'Acubed'

TABLES = {}

TABLES['permission_level'] = """
    CREATE TABLE `permission_level` (
    `level` INT NOT NULL,

    PRIMARY KEY (`level`)
    ) ENGINE=InnoDB
    """

TABLES['user'] = """
    CREATE TABLE `user` (
    `user_id` INT NOT NULL AUTO_INCREMENT,
    `access_level` INT NOT NULL,
    `username` varchar(20) NOT NULL,
    `password` varchar(20) NOT NULL,
    `user_email` varchar(20),
    `last_login` datetime,

    PRIMARY KEY (`user_id`),
    INDEX `permission_level_fk` (`access_level`),
    FOREIGN KEY (`access_level`) REFERENCES `permission_level` (`level`)
        
    ) ENGINE=InnoDB 
    """

TABLES['repository'] = """
    CREATE TABLE `repository` (
    `repository_id` INT NOT NULL AUTO_INCREMENT,
    `repo_creator` INT NOT NULL,
    `permission_req` INT NOT NULL,
    `repo_name` varchar(20) NOT NULL,

    PRIMARY KEY (`repository_id`),
    INDEX `permission_level_fk` (`permission_req`),
    FOREIGN KEY (`permission_req`) REFERENCES `permission_level` (`level`),
    INDEX `user_id_fk` (`repo_creator`),
    FOREIGN KEY (`repo_creator`) REFERENCES `user` (`user_id`)
    ) ENGINE=InnoDB 
    """

TABLES['artifact_change_record'] = """
    CREATE TABLE `artifact_change_record` (
    `change_datetime` datetime NOT NULL,
    `changer_id` INT NOT NULL,
    `artifact_id` INT NOT NULL,
    `artifact_blob` blob NOT NULL,
    `version` INT NOT NULL,

    PRIMARY KEY (`change_datetime`),
    INDEX `user_id_fk` (`changer_id`),
    FOREIGN KEY (`changer_id`) REFERENCES `user` (`user_id`)
    ) ENGINE=InnoDB
    """
#this is the I removed from artifact change record to get it to work
#, INDEX `artifact_id_fk` (`artifact_id`),
#FOREIGN KEY (`artifact_id`) REFERENCES `artifact` (`artifact_id`)

TABLES['artifact'] = """
    CREATE TABLE `artifact` (
    `artifact_id` INT NOT NULL AUTO_INCREMENT, 
    `owner_id` INT NOT NULL,
    `artifact_repo` INT NOT NULL,
    `artifact_last_changed` datetime,
    `artifact_access_level` INT NOT NULL,
    `artifact_name` varchar(40) NOT NULL,
    `artifact_original_source` text,
    `artifact_size` INT,
    `artifact_creation_date` datetime NOT NULL,
    `artifact_last_accessed` datetime,
    `artifact_access_count` INT,

    PRIMARY KEY (`artifact_id`),
    INDEX `permission_level_fk` (`artifact_access_level`),
    FOREIGN KEY (`artifact_access_level`) REFERENCES `permission_level` (`level`),
    INDEX `user_id_fk` (`owner_id`),
    FOREIGN KEY (`owner_id`) REFERENCES `user` (`user_id`),
    INDEX `repository_id_fk` (`artifact_repo`),
    FOREIGN KEY (`artifact_repo`) REFERENCES `repository` (`repository_id`),
    INDEX `artifact_change_fk` (`artifact_last_changed`),
    FOREIGN KEY (`artifact_last_changed`) REFERENCES `artifact_change_record` (`change_datetime`)
    ) ENGINE=InnoDB
    """

TABLES['tag'] = """
    CREATE TABLE `tag` (
    `tag_name` varchar(20) NOT NULL,
    `repo_id` INT,
    `artifact_id` INT,

    PRIMARY KEY (`tag_name`),
    INDEX `repository_id_fk` (`repo_id`),
    FOREIGN KEY (`repo_id`) REFERENCES `repository` (`repository_id`),
    INDEX `artifact_id_fk` (`artifact_id`),
    FOREIGN KEY (`artifact_id`) REFERENCES `artifact` (`artifact_id`)                                                                                         
    ) ENGINE=InnoDB 
    """

TABLES['user_bookmarks'] = """
    CREATE TABLE `user_bookmarks` (
    `user_id` INT NOT NULL,
    `artifact_id` INT,
    `repo_id` INT,

    INDEX `user_id_fk` (`user_id`),
    FOREIGN KEY (`user_id`) REFERENCES `user` (`user_id`),
    INDEX `repository_id_fk` (`repo_id`),
    FOREIGN KEY (`repo_id`) REFERENCES `repository` (`repository_id`),
    INDEX `artifact_id_fk` (`artifact_id`),
    FOREIGN KEY (`artifact_id`) REFERENCES `artifact` (`artifact_id`) 
    ) ENGINE=InnoDB 
    """

def create_database(cursor):
    try:
        cursor.execute("CREATE DATABASE IF NOT EXISTS {} DEFAULT CHARACTER SET `utf8`".format(DATABASE_NAME))
    except mysql.connector.Error as err:
        print("Failed to create database: {}".format(err))
        exit(1)

if __name__ == '__main__':
    try:
        cursor.execute("USE {}".format(DATABASE_NAME))
    except mysql.connector.Error as err:
        print("Database {} does not exist.".format(DATABASE_NAME))
        if err.errno == errorcode.ER_BAD_DB_ERROR:
            create_database(cursor)
            print("Database {} created successfully.".format(DATABASE_NAME))
            connection.database = DATABASE_NAME
        else:
            print(err)
            exit(1)   
    #convert to python f string or prepared query
    #docker volumes persistant 
    for table_name in TABLES:
        table_description = TABLES[table_name]
        try:
            print("Creating table {}: ".format(table_name), end='')
            cursor.execute(table_description)
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                print("already exists.")
            else:
                print(err.msg)
        else:
            print("OK")

    cursor.close()
    connection.close()
    config2 = {
        'user': 'root',
        'password': 'rT1@4PlgTd',
        'host': 'acubed_db',
        'port': '3306',
        'database': 'Acubed'
    }

    connection2 = mysql.connector.connect(**config2)
    cursor2 = connection2.cursor()
    try:        
        #cursor.execute("USE {}".format(DATABASE_NAME))
        #print("Using Acubed.")
        sqlinsert = ("INSERT INTO permission_level (level) VALUES (%s)")
        val = (1,)
        cursor2.execute(sqlinsert, val)
        print("Setting permission_level {}: ".format(str(val)), end='')
        connection2.commit()
        sqlinsert = ("INSERT INTO permission_level (level) VALUES (%s)")
        val = (3,)
        cursor2.execute(sqlinsert, val)
        print("Setting permission_level {}: ".format(str(val)), end='')
        connection2.commit()
        sqlinsert = ("INSERT INTO permission_level (level) VALUES (%s)")
        val = (5,)
        cursor2.execute(sqlinsert, val)
        print("Setting permission_level {}: ".format(str(val)), end='')
        connection2.commit()
        sqlinsert = ("INSERT INTO user (access_level, username, password, user_email) VALUES (%s, %s, %s, %s)")
        val = (5, "njenn001", "password", "testemail")
        cursor2.execute(sqlinsert, val)
        print("Setting test user {}: ".format(str(val)), end='')
        connection2.commit()
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_NON_INSERTABLE_TABLE:
            print("I messed up.")
        else:
            print("OK")
   
    cursor2.close()
    connection2.close()
        

