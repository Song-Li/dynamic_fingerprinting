import ConfigParser
import MySQLdb
import hashlib
from django.utils.encoding import smart_str, smart_unicode


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

    
    def add_columns(self, column_names):
        for column_name in column_names:
            try:
                sql_str = 'ALTER TABLE features ADD {} text'.format(column_name)
                self.run_sql(sql_str)
            except:
                pass


    def generate_column(self, source_column_name, aim_column_names, generator, recordID):
        sql_str = 'select {} from features where uniquelabel="{}"'.format(source_column_name, recordID)
        res = self.run_sql(sql_str)[0][0]
        aim = generator(res)
        update_str = ""
        for i in range(len(aim_column_names)):
            name = aim_column_names[i]
            update_str += '{}="{}",'.format(name, aim[i])

        update_str = update_str[:-1]
        sql_str = 'UPDATE features SET {} WHERE uniquelabel = "{}"'.format(update_str, recordID)
        self.run_sql(sql_str)
        

    def null_generator(string):
        pass

    def clean_sql(self, feature_list, generator = null_generator):
        sql_str = "DELETE FROM features WHERE jsFonts is NULL"
        self.run_sql(sql_str)
        sql_str = 'select uniquelabel from features'
        unique_labels = self.run_sql(sql_str)
        cur = 0
        leng = len(unique_labels)
        pro = 0
        feature_str = ",".join(feature_list)
        self.add_columns(['ipcity', 'ipregion', 'ipcountry'])
        for label in unique_labels:
            cur += 1
            if int(float(cur) / float(leng) * 100) != pro:
                pro += 1
                print pro
            self.generate_column('ip', ['ipcity', 'ipregion', 'ipcountry'], generator, label[0])
            self.gen_fingerprint(label[0], feature_str)
