import ConfigParser
import MySQLdb
import hashlib


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

    def get_entry_by_id(self, table, entry_id):
        """
        get an entry by the table name and id
        vars: table name, entry id
        return: the selected data
        """
        sql_str = "SELECT * from " + str(table) + " WHERE id='" + str(entry_id) + "'"
        # here we assume that the ID is identical
        # return only the first value
        return self.run_sql(sql_str)[0]


    def run_sql(self, sql_str):
        self.__cursor.execute(sql_str)
        self.__db.commit()
        res = self.__cursor.fetchall()
        return res

    def gen_fingerprint(self, recordID, feature_str):
        sql_str = 'select {} from features where uniquelabel="{}"'.format(feature_str, recordID)
        res = self.run_sql(sql_str)
        fingerprint = hashlib.sha1(str(res[0])).hexdigest()
        sql_str = 'UPDATE features SET {}="{}" WHERE uniquelabel = "{}"'.format('browserfingerprint', fingerprint, recordID)
        self.run_sql(sql_str)

    def clean_sql(self, feature_list):
        sql_str = "DELETE FROM features WHERE jsFonts is NULL"
        self.run_sql(sql_str)
        sql_str = 'select uniquelabel from features'
        unique_labels = self.run_sql(sql_str)
        cur = 0
        leng = len(unique_labels)
        pro = 0
        feature_str = ",".join(feature_list)
        for label in unique_labels:
            cur += 1
            if int(float(cur) / float(leng) * 100) != pro:
                pro += 1
                print pro
            self.gen_fingerprint(label[0], feature_str)
