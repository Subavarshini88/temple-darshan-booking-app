import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="suba",
        database="temple_darshan",
        auth_plugin="mysql_native_password"
    )