import mysql.connector

class Database():
    def __init__(self, dbconfig):
        self.dbconfig = dbconfig

    def __enter__(self):
        self.connect = mysql.connector.MySQLConnection(**self.dbconfig)
        self.cursor = self.connect.cursor(prepared=True)
        return self

    def __exit__(self, extype, exvalue, traceback):
        self.cursor.close()
        self.connect.close()

