from database import Database
from tqdm import *
from forpaper import *

class Paperlib():
    def __init__(self, db):
        self.db = db
        self.feature_list = [
            "agent",
            "accept",
            "encoding",
            "language",
            "timezone", 

            "plugins", 
            "cookie", 
            "WebGL", 
            "localstorage", 
            "fp2_addbehavior",
            "fp2_opendatabase",

            "langsdetected",
            "jsFonts",
            "canvastest", 

            "inc", 
            "gpu", 
            "gpuimgs", 
            "cpucores", 
            "audio",
            "fp2_cpuclass",
            "fp2_colordepth",
            "fp2_pixelratio",

            "ipcity",
            "ipregion",
            "ipcountry",

            "fp2_liedlanguages",
            "fp2_liedresolution",
            "fp2_liedos",
            "fp2_liedbrowser"
            ]

        self.group_features = {
                'headers_features' : [0, 1, 2, 3, 4],
                'browser_features' : [5, 6, 7, 8, 9, 10],
                'os_features' : [11, 12, 13],
                'hardware_feature' : [14, 15, 16, 17, 18, 19, 20, 21],
                'ip_features': [22, 23, 24],
                'consistency' : [25, 26, 27, 28]
                }

    def life_time_median(self, db = None, filter_less_than = 5, output_file = './res/life_time_median.dat'):
        """
        calculate the median life time of each feature
        output to output_file
        """
        if db == None:
            db = self.db
        feature_list = self.feature_list
        df = db.load_data(table_name = 'pandas_features')
        df = filter_less_than_n(df, filter_less_than)

        grouped = df.groupby('browserid')
        min_date = min(df['time'])
        max_date = max(df['time'])
        length = (max_date - min_date).days + 3
        life_time = {}
        for feature in feature_list:
            life_time[feature] = [0 for i in range(length + 10)]

        for browserid, cur_group in tqdm(grouped):
            pre_feature = {}
            pre_time = {}
            for idx, row in cur_group.iterrows():
                for feature in feature_list:
                    if feature in pre_feature:
                        if pre_feature[feature] != row[feature]:
                            cur_delt = (row['time'] - pre_time[feature]).days
                            life_time[feature][cur_delt] += 1
                    pre_feature[feature] = row[feature]
                    pre_time[feature] = row['time']

        medians = {}
        for feature in tqdm(feature_list):
            cur = 0
            total_change = sum(life_time[feature])
            half = total_change / 2
            for i in range(length + 1):
                cur += life_time[feature][i]
                if cur > half:
                    medians[feature] = i + 1
                    break

        
        f = safeopen(output_file, 'w')
        for feature in medians:
            f.write(feature + ' ' + str(medians[feature]))
            f.write('/n')
        f.close()

    def feature_latex_table_paper(self, output_file = './res/feature_table_1.dat'):
        """
        generate table 1, which is used for all feature description
        """
        df = self.db.load_data(table_name = 'pandas_features')
        # assign to the class at the same time
        #self.pdfeatures = df
        value_set = {}
        browser_instance = {}
        feature_list = self.feature_list
        group_features = self.group_features

        group_map = ['' for i in range(29)]
        for key in group_features:
            for i in group_features[key]:
                group_map[i] = key

        num_back = 0;
        browser_id_group = df.groupby('browserid').size()
        browser_id_group = browser_id_group.reset_index(name='counts')
        back_users = set()
        for idx in browser_id_group.index:
            if browser_id_group.at[idx, 'counts'] > 1:
                num_back += 1
                back_users.add(browser_id_group.at[idx, 'browserid'])
        print 'num_back:', num_back
        print 'num_size:', len(back_users)
        df = df.reset_index(drop = True)

        for idx in tqdm(df.index):
            row = df.iloc[idx]
            if row['browserid'] not in browser_instance:
                browser_instance[row['browserid']] = {} 
            group_vals = {}
            for i in range(len(feature_list)):
                feature = feature_list[i]

                group_key = group_map[i]
                if group_key not in group_vals:
                    group_vals[group_key] = ""
                group_vals[group_key] += str(row[feature])
                
                if feature not in value_set:
                    value_set[feature] = {}
                if row[feature] not in value_set[feature]:
                    value_set[feature][row[feature]] = set()
                value_set[feature][row[feature]].add(row['browserid'])

                if feature not in browser_instance[row['browserid']]:
                    browser_instance[row['browserid']][feature] = set()
                browser_instance[row['browserid']][feature].add(row[feature])

            for group_key in group_vals:
                if group_key not in value_set:
                    value_set[group_key] = {}
                if group_vals[group_key] not in value_set[group_key]:
                    value_set[group_key][group_vals[group_key]] = set()
                value_set[group_key][group_vals[group_key]].add(row['browserid'])
                
                if group_key not in browser_instance[row['browserid']]:
                    browser_instance[row['browserid']][group_key] = set()
                browser_instance[row['browserid']][group_key].add(group_vals[group_key])

        distinct = {}
        unique = {}
        per_browser_instance = {}
        f = open(output_file, 'w')
        for feature in value_set:
            distinct[feature] = len(value_set[feature])
            cnt = 0
            for val in value_set[feature]:
                if len(value_set[feature][val]) == 1:
                    cnt += 1
            unique[feature] = cnt

            for bid in browser_instance:
                if feature not in per_browser_instance:
                    per_browser_instance[feature] = 0
                if len(browser_instance[bid][feature]) == 1 and bid in back_users:
                    per_browser_instance[feature] += 1
            per_browser_instance[feature] = float(per_browser_instance[feature]) / float(num_back)
            f.write(r'{} & {} & {} & {:.4f} \\'.format(feature, distinct[feature], unique[feature], per_browser_instance[feature]))
            f.write('\n')
        f.close()

    def get_all_feature_change_by_date(self, change_db):
        """
        get the part of the big table
        """
        get_all_feature_change_by_date_paper(change_db)

