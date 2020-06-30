import mysql.connector

config = {
    'user': 'root',
    'password': 'rT1@4PlgTd',
    'host': 'acubed_db:3306'
}

db = mysql.connector.connect(**config)
cursor = db.cursor