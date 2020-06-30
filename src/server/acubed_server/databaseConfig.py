import mysql.connector

config = {
    'user': 'root',
    'password': 'rT1@4PlgTd',
    'host': '127.0.0.1'
}

db = mysql.connector.connect( 
    user= 'root',
    password= 'rT1@4PlgTd',
    host= 'A3database',
    database= 'Acubed')
cursor = db.cursor