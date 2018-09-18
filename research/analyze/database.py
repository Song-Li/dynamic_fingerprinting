import ConfigParser
from extractinfo import *
import pandas as pd
import MySQLdb
import hashlib
from django.utils.encoding import smart_str, smart_unicode
from sqlalchemy import create_engine
from tqdm import *
from feature_lists import *

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

        self.fingerprint_feature_list = get_fingerprint_feature_list()

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

    def combine_tables(self, feature_list, dfs, aim_table):
        """
        we will use the first df as the base df
        we'd better put the biggest df at the begining
        """
        print ("start to combine tables")
        for idx in range(len(dfs)):
            dfs[idx] = dfs[idx][feature_list]
        big_df = pd.concat(dfs)
        print ("Finished calculation, start to put back to csv")
        big_df.to_sql(aim_table, self.get_db_engine(), if_exists='replace', chunksize = 1000)
        print ("Finished push to csv")

    def generate_browserid(self, df, get_browserid = null_generator, aim_table = 'pandas_features', browserid_name = 'browserid'):
        """
        generate the browserid of a df
        """
        df[browserid_name] = 'browserid'
        drop_list = []
        for idx in tqdm(df.index):
            if pd.isna(df.at[idx, 'agent']):
                drop_list.append(idx)
                continue
            browser_str = get_browserid(df.iloc[idx])
            df.at[idx, browserid_name] = browser_str

        df.drop(drop_list, inplace = True)

        print ("Finished calculation, start to put back to csv")
        df.to_sql(aim_table, self.get_db_engine(), index = False, if_exists='replace', chunksize = 1000)
        print ("Finished push to csv")

    def generate_new_column(self, column_names, df, generators, generator_feature = 'agent', aim_table = None):
        """
        input the generators of the column_names, add new columns to the table
        if different column names need different generator, the code need to be updated
        """
        for column_name in column_names:
            df[column_name] = column_name
        if generator_feature == 'all_features':
            for idx in tqdm(df.index):
                for index in range(len(column_names)):
                    column_name = column_names[index]
                    generator = generators[index]
                    df.at[idx, column_name] = generator(df.iloc[idx])
        else:
            for idx in tqdm(df.index):
                for index in range(len(column_names)):
                    column_name = column_names[index]
                    generator = generators[index]
                    df.at[idx, column_name] = generator(df.at[idx, generator_feature])
        print ("Finished calculation, start to put back to sql")
        if aim_table == None:
            aim_table = 'tmptable' 
        df.to_sql(aim_table, self.get_db_engine(), index = False, if_exists='replace', chunksize = 1000)
        print ("Finished push to sql")

    def clean_sql(self, feature_list, df, generator = null_generator, get_device = null_generator, get_browserid =  null_generator, get_dybrowserid = null_generator, aim_table = 'pandas_features'):
        """
        input the methods to generate browserid, deviceid and dybrowserid
        generate all needed info of each row
        including: ipcity, ipregion, ipcountry, latitude, longitude, os, os version, 
        browser, browser version,
        """
        print ("fingerprint feature list: {}".format('\n'.join(feature_list)))
        # remove the null rows
        df = df[pd.notnull(df['jsFonts'])]
        #df = df[pd.notnull(df['gpuimgs'])]
        df = df[df.jsFonts != '']
        df = df[df.langsdetected != '']
        df = df[df.clientid != 'Not Set']
        # add columns
        df['ipcity'] = 'ipcity'
        df['ipregion'] = 'ipregion'
        df['ipcountry'] = 'ipcountry'
        df['latitude'] = 'latitude'
        df['longitude'] = 'longitude'
        df['deviceid'] = 'deviceid'
        df['browserid'] = 'browserid'
        df['dybrowserid'] = 'dybrowserid'
        df['browser'] = 'browser'
        df['os'] = 'os'
        df['device'] = 'device'
        df['osversion'] = 'osversion'
        df['browserversion'] = 'browserversion'
        df['fulldevice'] = 'fulldevice'
        df['partgpu'] = 'partgpu'
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

            row = df.iloc[idx]
            df.at[idx, 'partgpu'] = row['gpu'].split('Direct')[0]
            df.at[idx, 'fulldevice'] = get_full_device(row) 

            try:
                device_str = get_device(df.iloc[idx])
                df.at[idx, 'deviceid'] = device_str 
            except:
                print (df.iloc[idx])
            # hashlib.sha256(device_str).hexdigest()
            df.at[idx, 'browser'] = get_browser_from_agent(df.at[idx, 'agent'])
            browser_str = get_browserid(df.iloc[idx]) + df.at[idx, 'browser']
            df.at[idx, 'browserid'] = browser_str

            # here we need to generate the dybrowserid
            # for safari user,we use browserid as dybrowserid
            # for other users, we use label(cookie)
            if 'Safari' in df.at[idx, 'browser']:
                df.at[idx, 'dybrowserid'] = df.at[idx, 'browserid']
            else:
                df.at[idx, 'dybrowserid'] = df.at[idx, 'label']

            # add other value to pandas table
            df.at[idx, 'os'], df.at[idx, 'osversion'], df.at[idx, 'browser'], df.at[idx, 'browserversion'], df.at[idx, 'device'] = get_all_info(df.at[idx, 'agent'])

            res_str = ""
            noipfingerprint_str = ''
            for feature in feature_list:
                # update the false to False
                if df.at[idx, feature] == 'true':
                    df.at[idx, feature] = 'True'
                elif df.at[idx, feature] == 'false':
                    df.at[idx, feature] = 'False'

                res_str += str(df.at[idx, feature] )
                if 'ip' not in feature:
                    noipfingerprint_str += str(df.at[idx, feature] )

            hash_str = hashlib.sha256(res_str).hexdigest()
            df.at[idx, 'browserfingerprint'] = hash_str
            hash_str = hashlib.sha256(noipfingerprint_str).hexdigest()
            df.at[idx, 'noipfingerprint'] = hash_str

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

    def load_data(self, feature_list = ['*'], table_name = 'features', limit = -1, where = None):
        """
        this function will take a feature list, a table name and a limit
        if the feature list do not include browserid, the browserid will be loaded also
        """
        if feature_list[0] != '*' and 'browserid' not in feature_list:
            feature_list.append('browserid')
        column_names = self.get_column_names(table_name)
        for feature in feature_list:
            if feature not in column_names:
                print 'feature name {} do not exsit in table {}'.format(feature, table_name)
        if (feature_list[0] != '*'):
            feature_list = [item for item in feature_list if item in column_names]
        feature_str = ""
        for feature in feature_list:
            feature_str += feature + ','
        feature_str = feature_str[:-1]
        limit_str = {}
        if limit == -1:
            limit_str = ""
        else:
            limit_str = ' limit {}'.format(limit)

        if where == None:
            where_str = ""
        else:
            where_str = ' where {}'.format(where)
        df = pd.read_sql('select {} from {} {} {};'.format(feature_str, table_name, where_str, limit_str), con=self.get_db())
        print ('finished loading {}'.format(table_name))
        return df

    def get_column_names(self, table_name):
        query = 'select * from ' + table_name + ' limit 1'
        self.__cursor.execute(query)
        self.__field_names = [i[0] for i in self.__cursor.description]
        return self.__field_names

    def accept_httpheaders_patch(self, df):
        """
        some of the accept and httpheader is not collected in the beginning
        we just assume it haven't change from the beginning
        """
        grouped = df.groupby('browserid')
        print ('doing accept patch')
        for key, cur_group in tqdm(grouped):
            if cur_group['accept'].nunique() == 1:
                continue
            val = ''
            for idx, row in cur_group.iterrows():
                print row['accept']
                if row['accept'] != '':
                    val = row['accept']
                    print val
                    break

            for idx, row in cur_group.iterrows():
                if row['accept'] == '':
                    df.at[idx, 'accept'] = val

        print ('doing httpheaders patch')
        for key, cur_group in tqdm(grouped):
            if cur_group['httpheaders'].nunique() == 1:
                continue
            val = ''
            for idx, row in cur_group.iterrows():
                if row['httpheaders'] == None:
                    continue
                if row['httpheaders'].find('_') != -1:
                    val = row['httpheaders']
                    break

            for idx, row in cur_group.iterrows():
                if row['httpheaders'] == None or row['httpheaders'].find('_') == -1:
                    print val
                    df.at[idx, 'httpheaders'] = val
                else:
                    break
        return df

    def audio_patch(self, df):
        """
        if audio is not supported, maybe because of the bug.
        we will change not supported to a value if belongs to a browserid and same IP and 
        not supported in the middle of values
        """
        patched_num = 0
        grouped = df.groupby('browserid')
        for key, cur_group in tqdm(grouped):
            pre_value = 'pre_value'
            pre_row = []
            for idx, row in cur_group.iterrows():
                if pre_value == 'pre_value':
                    pre_value = df.at[idx, 'audio']
                    pre_row = df.iloc[idx]
                    continue
                cur_value = df.at[idx, 'audio']
                if cur_value == 'not supported' and cur_value != pre_value:
                    df.at[idx, 'audio'] = pre_value
                    patched_num += 1

            pre_value = df.at[idx, 'audio']
            pre_row = df.iloc[idx]
            
        print '{} number of audio records patched'.format(patched_num)
        return df

    def partgpu_patch(self, df):
        """
        Edge v17 added ANGLE on top of gpu string
        """
        patched_num = 0
        for idx in tqdm(df.index):
            if df.at[idx, 'browser'] == 'Edge':
                if 'ANGLE (' in df.at[idx, 'browserid']:
                    df.at[idx, 'browserid'] = df.at[idx, 'browserid'].replace('ANGLE (', '')
                    df.at[idx, 'partgpu'] = df.at[idx, 'partgpu'].replace('ANGLE (', '')
            patched_num += 1

        print '{} number of partgpu records patched'.format(patched_num)
        return df

    def generate_fingerprint(self, df, feature_list):
        """
        generate the browserfingerprint of the df
        """
        for idx in tqdm(df.index):
            for feature in feature_list:
                res_str += str(df.at[idx, feature])
                if 'ip' not in feature:
                    noipfingerprint_str += str(df.at[idx, feature] )

            hash_str = hashlib.sha256(res_str).hexdigest()
            df.at[idx, 'browserfingerprint'] = hash_str
            hash_str = hashlib.sha256(noipfingerprint_str).hexdigest()
            df.at[idx, 'noipfingerprint'] = hash_str

        return df

    def pandas_patches(self, df, export_table = None):
        """
        after generated pandas features, we sometimes need to rebuild the table
        """
        df = self.audio_patch(df)
        #partgpu_patch(df)
        #df = self.accept_httpheaders_patch(df)
        df = generate_fingerprint(df, self.fingerprint_feature_list)

        if export_table != None:
            self.export_sql(df, export_table)

        return df
