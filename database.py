import mysql.connector
from mysql.connector import Error as MySQLError

database = mysql.connector.connect(
    host ='localhost',
    user = 'root',
    password = '',
    database = 'bd_Bar'
)

def delete(id, table, conditionField):
    sql = f"DELETE FROM {table} WHERE {conditionField} = {id}"
    cursor = database.cursor()
    try:
        cursor.execute(sql)
        database.commit()
        return "Registro eliminado"
    except MySQLError as error:
        return f"Error: {error}"
    
def select(sql):
    cursor = database.cursor()
    try:
        cursor.execute(sql)
        data = cursor.fetchall()
        return data
    except MySQLError as error:
        return f"Error: {error}"
    
def executeSQL(sql):
    cursor = database.cursor()
    try:
        cursor.execute(sql)
        database.commit()
        return "Completo"
    except MySQLError as error:
        return f"Error: {error}"

def error():
    return MySQLError
