import mysql.connector

config = {
    'user': 'root',
    'password': 'rT1@4PlgTd',
    'host': 'acubed_db',
    'port': '3306'
}
 
connection = mysql.connector.connect(**config) 
cursor = connection.cursor()