import mysql.connector

config = {
    'user': 'root',
    'password': 'rT1@4PlgTd',
    'host': 'a3database',
    'port': '3306',
    'database': 'Acubed'
}

connection = mysql.connector.connect(**config) 
cursor = connection.cursor()