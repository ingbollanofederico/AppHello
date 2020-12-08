import os
import sqlite3
from sqlite3 import Error

def create_connection():
    """ create a database connection to the SQLite database
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(os.path.dirname(os.path.abspath(__file__))
                               + "/website.db")
        return conn
    except Error as e:
        print(e)

    return conn


def dropTables(conn, tables_db):

    for table in tables_db:
        sql_permissions = """DROP TABLE IF EXISTS %s;""" %table
        try:
            c = conn.cursor()
            c.execute(sql_permissions)
        except Error as e:
            print(e)

