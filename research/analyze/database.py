import ConfigParser
from extractinfo import *
import pandas as pd
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
                            db=database_name)

        self.__db_engine = create_engine("mysql+mysqldb://{}:{}@localhost/{}".format(username, password, database_name))
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

    # we will use the first df as the base df
    # we'd better put the biggest df at the begining
    def combine_tables(self, feature_list, dfs, aim_table):
        for idx in range(len(dfs)):
            dfs[idx] = dfs[idx][feature_list]
        big_df = pd.concat(dfs)
        print ("Finished calculation, start to put back to csv")
        big_df.to_sql(aim_table, self.get_db_engine(), if_exists='replace', chunksize = 1000)
        print ("Finished push to csv")

    def generate_browserid(self, feature_list, df, get_device = null_generator, get_browserid = null_generator):
        df['deviceid'] = 'deviceid'
        df['browserid'] = 'browserid'
        df['browser'] = 'browser'
        # remove the null rows
        df = df[pd.notnull(df['jsFonts'])]
        #df = df[pd.notnull(df['gpuimgs'])]
        df = df[df.jsFonts != '']
        df = df[df.langsdetected != '']
        df = df.reset_index()
        for idx in tqdm(df.index):
            try:
                device_str = get_device(df.iloc[idx])
                df.at[idx, 'deviceid'] = device_str 
            except:
                print (idx)
                print (df.at[idx, 'id'])
                print (df.iloc[idx])
            # hashlib.sha256(device_str).hexdigest()
            df.at[idx, 'browser'] = get_browser_from_agent(df.at[idx, 'agent'])
            browser_str = get_browserid(df.iloc[idx]) + df.at[idx, 'browser']
            df.at[idx, 'browserid'] = browser_str

            res_str = ""
            for feature in feature_list:
                res_str += str(df.at[idx, feature] )

            hash_str = hashlib.sha256(res_str).hexdigest()
            df.at[idx, 'browserfingerprint'] = hash_str

        print ("Finished calculation, start to put back to csv")
        df.to_sql('pandas_longfeatures', self.get_db_engine(), index = False, if_exists='replace', chunksize = 1000)
        print ("Finished push to csv")


    def clean_sql(self, feature_list, df, generator = null_generator, get_device = null_generator, get_browserid =  null_generator, aim_table = 'pandas_features'):
        # remove the null rows
        df = df[pd.notnull(df['jsFonts'])]
        #df = df[pd.notnull(df['gpuimgs'])]
        df = df[df.jsFonts != '']
        df = df[df.langsdetected != '']
        # add columns
        df['ipcity'] = 'ipcity'
        df['ipregion'] = 'ipregion'
        df['ipcountry'] = 'ipcountry'
        df['latitude'] = 'latitude'
        df['longitude'] = 'longitude'
        df['deviceid'] = 'deviceid'
        df['browserid'] = 'browserid'
        df['browser'] = 'browser'
        # regenerate ip realted features
        # and generate the browser finergrpint
        df = df.reset_index()
        for idx in tqdm(df.index):
            ip_related = generator(df.at[idx, 'IP'])
            # the first 5 return values realted to IP location
            df.at[idx, 'ipcity'] = ip_related[0]
            df.at[idx, 'ipregion'] = ip_related[1]
            df.at[idx, 'ipcountry'] = ip_related[2]
            df.at[idx, 'latitude'] = ip_related[3] 
            df.at[idx, 'longitude'] = ip_related[4] 

            try:
                device_str = get_device(df.iloc[idx])
                df.at[idx, 'deviceid'] = device_str 
            except:
                print (idx)
                print (df.at[idx, 'id'])
                print (df.iloc[idx])
            # hashlib.sha256(device_str).hexdigest()
            df.at[idx, 'browser'] = get_browser_from_agent(df.at[idx, 'agent'])
            browser_str = get_browserid(df.iloc[idx]) + df.at[idx, 'browser']
            df.at[idx, 'browserid'] = browser_str

            res_str = ""
            for feature in feature_list:
                res_str += str(df.at[idx, feature] )

            hash_str = hashlib.sha256(res_str).hexdigest()
            df.at[idx, 'browserfingerprint'] = hash_str

        print ("Finished calculation, start to put back to csv")
        self.export_sql(df, aim_table)
        print ("Finished push to csv")

    def build_map(self, df):
        map_res = {}
        map_pre = {}
        print ("generating map round 1")
        for idx in tqdm(df.index):
            agent = df.at[idx, 'agent']
            browserid = df.at[idx, 'browserid']
            if browserid not in map_pre:
                map_pre[browserid] = {}
            cur_browser_version = get_browser_version(agent)
            if cur_browser_version not in map_pre[browserid]:
                map_pre[browserid][cur_browser_version] = df.at[idx, 'canvastest'] 

        print ("generating map round 2")
        for browserid in map_pre:
            for cur_browser_version in map_pre[browserid]:
                cur_hash = map_pre[browserid][cur_browser_version]
                for bv in map_pre[browserid]:
                    cur_key = cur_hash + bv
                    if cur_key not in map_res:
                        map_res[cur_key] = []
                    if map_pre[browserid][bv] not in map_res[cur_key]:
                        map_res[cur_key].append(map_pre[browserid][bv])

        print ("generating unique rate")
        unique = 0
        for cur_key in map_pre:
            if len(map_pre[cur_key]) == 1:
                unique += 1
        print ("Unique rate is: {}".format(str(float(unique) / float(len(map_pre)))))
        
        return map_res

    def export_sql(self, df, table_name):
        df.to_sql(table_name, self.get_db_engine(), if_exists='replace', chunksize = 1000, index = False)
