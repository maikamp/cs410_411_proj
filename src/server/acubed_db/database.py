import mysql.connector

config = {
    'user': 'root',
    'password': 'rT1@4PlgTd',
    'host': 'localhost'
}

db = mysql.connector.connect(**config)
cursor = db.cursor