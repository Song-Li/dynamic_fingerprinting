import ConfigParser
import MySQLdb


class Database():

    def __init__(self, database_name):
        config = ConfigParser.ConfigParser()
        config.read('password.ignore')
        username = config.get('mysql', 'username')
        password = config.get('mysql', 'password')

        self.__db = MySQLdb.connect(host='localhost',
                             user=username,
                             passwd = password,
                            db='uniquemachine')

        self.__cursor = self.__db.cursor()

    def get_db(self):
        return self.__db

    def run_sql(self, sql_str):
        self.__cursor.execute(sql_str)
        self.__db.commit()
        res = self.__cursor.fetchall()
        return res
