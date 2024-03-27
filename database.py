import mysql.connector
from mysql.connector import Error as MySQLError

database = mysql.connector.connect(
    host ='localhost',
    user = 'root',
    password = '',
    database = 'bd_Bar'
)

def delete(id):
    id = id
    id = id
    sql = f"DELETE FROM `user` WHERE id_user = {id}"
    cursor = database.cursor()
    try:
        cursor.execute(sql)
        database.commit()
        return "Registro eliminado"
    except MySQLError as error:
        return f"Error: {error}"

def error():
    return MySQLError
