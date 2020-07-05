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
        usr = (str(content['username']), str(content["password"]))
        self.cursor.execute(sql, usr)
        result = self.cursor.fetchall()

        if len(result) == 0:
            payload = {
                'data' : 'Invalid username.'
            }
            return (json.dumps(payload), 401)
        else:
            if content['password'] == result[0][2]:
                payload = {
                    'data' : 'Successful login.',
                    'user_id' : result[0][3],
                }
                return (json.dumps(payload), 200)
            else:
                payload = {
                    'data' : 'Incorrect password.'
                }
                return (json.dumps(payload), 401)

    def testmysql(self):
        self.ensureConnected()
        sql = "SHOW TABLES"
        self.cursor.execute(sql)
        return (self.cursor.fetchall(), )
        