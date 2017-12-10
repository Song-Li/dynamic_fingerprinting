import ConfigParser
import MySQLdb
import hashlib
from django.utils.encoding import smart_str, smart_unicode
from sqlalchemy import create_engine
from tqdm import *


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

        self.__db_engine = create_engine("mysql+mysqldb://{}:{}@localhost/uniquemachine".format(username, password))
        self.__cursor = self.__db.cursor()

    def get_db(self):
        return self.__db

    def get_db_engine(self):
        return self.__db_engine

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

    def add_columns(self, column_names):
        for column_name in column_names:
            try:
                sql_str = 'ALTER TABLE features ADD {} text'.format(column_name)
                self.run_sql(sql_str)
            except:
                pass


    def null_generator(string):
        pass


    def clean_sql(self, feature_list, df, generator = null_generator):
        # add columns
        df['ipcity'] = 'ipcity'
        df['ipregion'] = 'ipregion'
        df['ipcountry'] = 'ipcountry'
        df.to_csv('~/data/dynamic_fingerprinting/feature_table.csv')
        # regenerate ip realted features
        # and generate the browser finergrpint
        for idx in tqdm(df.index):
            ip_related = generator(df.at[idx, 'IP'])
            df.at[idx, 'ipcity'] = ip_related[0]
            df.at[idx, 'ipregion'] = ip_related[1]
            df.at[idx, 'ipcountry'] = ip_related[2]
            res_str = ""
            for feature in feature_list:
                res_str += str(df.at[idx, feature] )

            hash_str = hashlib.sha256(res_str).hexdigest()
            df.at[idx, 'browserfingerprint'] = hash_str

        print ("Finished calculation, start to put back to csv")
        #df.to_sql('pandas_features', self.get_db_engine(), if_exists='replace', chunksize = 100000)

        df.to_csv('~/data/dynamic_fingerprinting/feature_table.csv')
        print ("Finished push to csv")
