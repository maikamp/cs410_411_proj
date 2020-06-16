import mysql.connector
from database import cursor

DATABASE_NAME = 'A3database'

def create_database():
    cursor.execute("CREATE DATABASE IF NOT EXISTS {} DEFAULT CHARACTER SET 'utf8'".format(DATABASE_NAME))
    