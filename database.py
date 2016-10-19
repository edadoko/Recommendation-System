import MySQLdb
from _md5 import md5

class database:
    host = 'eatit.mysql.pythonanywhere-services.com'
    user = 'eatit'
    password = '**********'
    db = 'eatit$recommendation_sys'

    def __init__(self):
        self.connection = MySQLdb.connect(self.host, self.user, self.password, self.db)
        self.cursor = self.connection.cursor()

    def read_from_db(self, expression):
        try:
            cursor = self.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute(expression)
            return cursor.fetchall()
        except MySQLdb.OperationalError:
            self.connection = MySQLdb.connect(self.host, self.user, self.password, self.db)
            self.cursor = self.connection.cursor()
            self.read_from_db(expression)

    def write_to_db(self, expression):
        try:
            self.cursor.execute(expression)
            self.connection.commit()
        except MySQLdb.OperationalError:
            self.connection = MySQLdb.connect(self.host, self.user, self.password, self.db)
            self.cursor = self.connection.cursor()
            self.write_to_db(expression)
        except:
            self.connection.rollback()
            print("problem executing db query")

    def close_db(self):
        self.connection.close()

    def encrypt_pw(self, pw):
        return md5(pw.encode('utf-8')).hexdigest()

if __name__ == '__main__':
    db = database()
    user = 'testing'
    password = db.encrypt_pw("test")
    expression = """insert into users(`username`, `password`) values ("test", "test")"""
    db.write_to_db(expression)
    print("ok")
