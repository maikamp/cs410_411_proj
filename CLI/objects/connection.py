import mysql.connector
from mysql.connector import MySQLConnection, Error

class Connection (): 
    def __init__(self):
        self.connection = None
        self.database = "test0"
        self.user = "pynative"
        self.password = "pynative@#29"

    def connect(self):
        print("connect")

        try:
            connection = mysql.connector.connect(host = self.connection,
                                                database = self.database,
                                                user = self.user,
                                                password = self.password)
            if connection.is_connected():
                db_Info = connection.get_server_info()
                print("Connected to MySQL Server version ", db_Info)
                cursor = connection.cursor()
                cursor.execute("select database();")
                record = cursor.fetchone()
                print("You're connected to database: ", record)

        except Error as e:
            print("Error while connecting to MySQL", e)
        finally:
            if (connection.is_connected()):
                cursor.close()
                connection.close()
                print("MySQL connection is closed")