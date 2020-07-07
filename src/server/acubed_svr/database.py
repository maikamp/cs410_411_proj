import mysql.connector
import datetime
import requests
import math
import json
import os

DATABASE_NAME = 'Acubed'

class Database():
    # Initialize the MySQL-connector connection at the begining of of the script to ensure 
    # we are working from the correct database. Defines self.
    def __init__(self):
        self.connector = mysql.connector.connect(
            user = 'root',
            password = 'rT1@4PlgTd',
            database = 'Acubed',
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
                database = 'Acubed',
                #database = os.environ['DATABASE_NAME'],
                host = 'acubed_db',
                port = '3306'
            )
            self.cursor = self.connector.cursor()
    
    def login(self, content):
        self.ensureConnected()
        sql = "SELECT user_id FROM user WHERE username = %s && password = %s"
        usr = (str(content["username"]), str(content["password"]))
        self.cursor.execute(sql, usr)
        result = self.cursor.fetchall()

        if len(result) == 0:
            payload = {
                'data' : 'Invalid username or password.'
            }
            return (json.dumps(payload), 401)
        else:
            if len(result) == 1:
                payload = {
                    'data' : 'Successful login.',
                    'user_id' : result,
                }
                return (json.dumps(payload), 200)
            else:
                payload = {
                    'data' : 'Incorrect password.'
                }
                return (json.dumps(payload), 401)

    def register(self, content):
        self.ensureConnected()
        sql_unique_user = "SELECT * FROM user WHERE username = %s OR user_email = %s"
        self.cursor.execute(sql_unique_user, (content.username, content.user_email))

        result = self.cursor.fetchall()

        if len(result) == 0:
            payload = {
                'data' : 'Account created.'
            }
            return (json.dumps(payload), 200)
        else:
            payload = {
                'data' : 'Username or email already in use.'
            }
            return(json.dumps(payload), 401)


    def testmysql(self):
        self.ensureConnected()
        sql = "SHOW TABLES"
        self.cursor.execute(sql)
        answer = self.cursor.fetchall()
        temp = {
            'tables': answer
        }
        return (temp, 200)
    
    def testmysqlArtifact(self):
        self.ensureConnected()
        sql = "DESCRIBE artifact"
        self.cursor.execute(sql)
        answer = self.cursor.fetchall()
        temp = {
            'artifact': answer
        }
        return (temp, 200)
    
    def testmysqlArtfactChangeRecord(self):
        self.ensureConnected()
        sql = "DESCRIBE artifact_change_record"
        self.cursor.execute(sql)
        answer = self.cursor.fetchall()
        temp = {
            'artifact_change_record': answer
        }
        return (temp, 200)

    def testmysqlPermissionLevel(self):
        self.ensureConnected()
        sql = "DESCRIBE permission_level"
        self.cursor.execute(sql)
        answer = self.cursor.fetchall()
        temp = {
            'permission_level': answer
        }
        return (temp, 200)
    
    def testmysqlRepository(self):
        self.ensureConnected()
        sql = "DESCRIBE repository"
        self.cursor.execute(sql)
        answer = self.cursor.fetchall()
        temp = {
            'repository': answer
        }
        return (temp, 200)
    
    def testmysqlTag(self):
        self.ensureConnected()
        sql = "DESCRIBE tag"
        self.cursor.execute(sql)
        answer = self.cursor.fetchall()
        temp = {
            'tag': answer
        }
        return (temp, 200)

    def testmysqlUser(self):
        self.ensureConnected()
        sql = "DESCRIBE user"
        self.cursor.execute(sql)
        answer = self.cursor.fetchall()
        temp = {
            'user': answer
        }
        return (temp, 200)
    
    def testmysqlUserBookmarks(self):
        self.ensureConnected()
        sql = "DESCRIBE user_bookmarks"
        self.cursor.execute(sql)
        answer = self.cursor.fetchall()
        temp = {
            'user_bookmarks': answer
        }
        return (temp, 200)

    def testlevels(self):
        self.ensureConnected()
        sql = "SELECT level FROM permission_level"
        self.cursor.execute(sql)
        answer = self.cursor.fetchall()
        temp = {
            'levels': answer
        }
        return (temp, 200)