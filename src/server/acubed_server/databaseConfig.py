import mysql.connector

configOld = {
    'user': 'root',
    'password': 'rT1@4PlgTd',
    'host': '127.0.0.1'
}

config = {
    'user': 'test',
    'password': 'testpw',
    'host': 'A3database',
    'port': '3306',
    'database': 'Acubed'
}

db = mysql.connector.connect(**config) 
cursor = db.cursor