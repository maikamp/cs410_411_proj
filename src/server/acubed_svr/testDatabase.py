import mysql.connector
import datetime
import requests
import math
import json
import os
#from werkzeug.security import check_password_hash
#from flask import Flask, flash, request, redirect, url_for
#from werkzeug.utils import secure_filename

DATABASE_NAME = 'Acubed'

class TestDatabase():
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
    
    def testmysql(self):
        self.ensureConnected()
        sql = "SHOW TABLES"
        self.cursor.execute(sql)
        answer = self.cursor.fetchall()
        temp = {
            "tables": answer
        }
        return (temp, 200)
    
    def testmysqlartifact(self):
        self.ensureConnected()
        sql = "DESCRIBE artifact"
        self.cursor.execute(sql)
        answer = self.cursor.fetchall()
        temp = {
            "artifact": answer
        }
        return (temp, 200)
    
    def testmysqlartifactchangerecord(self):
        self.ensureConnected()
        sql = "DESCRIBE artifact_change_record"
        self.cursor.execute(sql)
        answer = self.cursor.fetchall()
        temp = {
            "artifact_change_record": answer
        }
        return (temp, 200)

    def testmysqlpermissionlevel(self):
        self.ensureConnected()
        sql = "DESCRIBE permission_level"
        self.cursor.execute(sql)
        answer = self.cursor.fetchall()
        temp = {
            "permission_level": answer
        }
        return (temp, 200)
    
    def testmysqlrepository(self):
        self.ensureConnected()
        sql = "DESCRIBE repository"
        self.cursor.execute(sql)
        answer = self.cursor.fetchall()
        temp = {
            "repository": answer
        }
        return (temp, 200)
    
    def testmysqltag(self):
        self.ensureConnected()
        sql = "DESCRIBE tag"
        self.cursor.execute(sql)
        answer = self.cursor.fetchall()
        temp = {
            "tag": answer
        }
        return (temp, 200)

    def testmysqluser(self):
        self.ensureConnected()
        sql = "DESCRIBE user"
        self.cursor.execute(sql)
        answer = self.cursor.fetchall()
        temp = {
            "user": answer
        }
        return (temp, 200)
    
    def testmysqluserBookmarks(self):
        self.ensureConnected()
        sql = "DESCRIBE user_bookmarks"
        self.cursor.execute(sql)
        answer = self.cursor.fetchall()
        temp = {
            "user_bookmarks": answer
        }
        return (temp, 200)

    def testlevels(self):
        self.ensureConnected()
        sql = "SELECT level FROM permission_level"
        self.cursor.execute(sql)
        answer = self.cursor.fetchall()
        temp = {
            "levels": answer
        }
        return (temp, 200)

    
   
