from database import Database
from tqdm import *
from forpaper import *
import collections

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

    def life_time_median(self, db = None, filter_less_than = 3, output_file = './res/life_time_median.dat'):
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
            # cur_group is the df of this group
            pre_feature = {}
            pre_time = {}
            changed = {}
            for idx, row in cur_group.iterrows():
                for feature in feature_list:
                    if feature in pre_feature:
                        if pre_feature[feature] != row[feature]:
                            cur_delt = (row['time'] - pre_time[feature]).days
                            life_time[feature][cur_delt] += 1
                            pre_feature[feature] = row[feature]
                            pre_time[feature] = row['time']
                            changed[feature] = True
                    else:
                        pre_feature[feature] = row[feature]
                        pre_time[feature] = row['time']
                        changed[feature] = False 

            # if not changed, we assume the life time is maxmium till the 
            # end date of our database
            for feature in feature_list:
                if not changed[feature]:
                    life_time[feature][(max_date - pre_time[feature]).days] += 1

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
            f.write('\n')
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
                # get ride of gpuimgs
                if feature == 'gpuimgs':
                    continue
                group_key = group_map[i]
                cur_feature = row[feature]
                # some times ture and True is different
                # unknown reason, just put a patch here
                # the reason is known, because of the update of 
                # adding value of lied value, fixed in clean_sql, patch not needed
                """
                if cur_feature == 'true':
                    cur_feature = 'True'
                elif cur_feature == 'false':
                    cur_feature = 'False'
                """

                if group_key not in group_vals:
                    group_vals[group_key] = ""
                group_vals[group_key] += str(cur_feature)
                
                if feature not in value_set:
                    value_set[feature] = {}
                if cur_feature not in value_set[feature]:
                    value_set[feature][cur_feature] = set()
                value_set[feature][cur_feature].add(row['browserid'])

                if feature not in browser_instance[row['browserid']]:
                    browser_instance[row['browserid']][feature] = set()
                browser_instance[row['browserid']][feature].add(cur_feature)

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

    def get_all_feature_change_by_date(self):
        """
        get the part of the big table
        """
        change_db = Database('filteredchangesbrowserid')
        get_all_feature_change_by_date_paper(change_db)

    def verify_browserid_by_cookie(self):
        """
        this function will return the lower, upper bound of browserid accuracy and the total number
        the upper bound is the percentage of browserids with more than one cookies
        the lower bound is the percentage of browserids with fliped cookies
        """
        browserid = 'browserid'
        db = self.db
        df = db.load_data(feature_list = [browserid, 'label', 'os'], table_name = 'pandas_features')

        #we can add filter here
        df = filter_less_than_n(df, 3)

        #here we can filter the unrelated os
        df = filter_df(df, 'os', filtered_list = ['iOS', 'Mac OS X'])
        """
        filtered_list = [
                'safari'
                ]
        df = df[~df['browser'].isin(filtered_list)]
        """

        grouped = df.groupby(browserid)
        lower_wrong_browserid = []
        upper_wrong_browserid = []
        total_number = df[browserid].nunique()

        for key, cur_group in tqdm(grouped):
            appeared = set()
            pre_cookie = ""
            if cur_group['label'].nunique() > 1:
                upper_wrong_browserid.append(key)
            for idx, row in cur_group.iterrows():
                if pre_cookie != row['label']:
                    pre_cookie = row['label']
                    if row['label'] in appeared:
                        lower_wrong_browserid.append(row[browserid])
                        break
                    appeared.add(row['label'])
        return lower_wrong_browserid, upper_wrong_browserid, total_number

    def new_return_user_by_date(self, percentage = False):
        """
        return the number of returned users and new users in each day
        the result will be written into newVsReturn
        if the percentage key is set to True
        the function will return the percentage instead of the real number
        """
        df = self.db.load_data(feature_list = ['browserid', 'time'], table_name = 'pandas_features')
        df = round_time_to_day(df)
        df = df.drop_duplicates(subset = ['time', 'browserid'])
        grouped = df.groupby('browserid')
        min_date = min(df['time'])
        max_date = max(df['time'])
        lendate = (max_date - min_date).days
        datelist = [min_date + datetime.timedelta(days = i) for i in range(lendate + 3)]
        # round time to day
        return_user = {}
        new_user = {} 
        for date in datelist:
            return_user[date] = 0
            new_user[date] = 0

        #here we already removed the multiple visites for same user in same day
        for key, group in tqdm(grouped):
            first = True
            for idx, row in group.iterrows():
                if first:
                    first = False
                    new_user[row['time']] += 1
                else:
                    return_user[row['time']] += 1

        if percentage:
            for date in datelist:
                cur_total = new_user[date] + return_user[date]
                # avoid divide by zero
                if cur_total == 0:
                    cur_total = 1
                new_user[date] = float(new_user[date]) / float(cur_total)
                return_user[date] = float(return_user[date]) / float(cur_total)

        f = safeopen('./res/newVsReturn.dat', 'w')
        f.write('{} {}\n'.format('new-user', 'return-user'))
        for date in datelist:
            f.write('{}-{}-{} {} {}\n'.format(date.year, date.month, date.day, new_user[date], return_user[date]))
        f.close()

    def feature_distribution_by_date(self, feature_name, percentage = False, show_number = 7):
        """
        draw total number of a feature by date
        this function will return a stacked dat file
        """
        db = self.db
        df = db.load_data(feature_list = ['time', 'browserid', feature_name], table_name = 'pandas_features')
        min_date = min(df['time'])
        min_date = min_date.replace(microsecond = 0, second = 0, minute = 0, hour = 0)
        max_date = max(df['time'])
        lendate = (max_date - min_date).days
        datelist = [min_date + datetime.timedelta(days = i) for i in range(lendate + 3)]
        # round time to day
        df = round_time_to_day(df)
        df = df.drop_duplicates(subset = [feature_name, 'time', 'browserid'])
        grouped = df.groupby([feature_name, 'time'])
        res = {}
        total_numbers = {}
        daily_all_numbers = {}
        for date in datelist:
            res[date] = {}
            daily_all_numbers[date] = 0

        for key, group in tqdm(grouped):
            cur_number = group['browserid'].nunique()

            daily_all_numbers[key[1]] += cur_number
            if key[0] not in res[key[1]]:
                res[key[1]][key[0]] = 0
            res[key[1]][key[0]] += cur_number

            if key[0] not in total_numbers:
                total_numbers[key[0]] = 0
            total_numbers[key[0]] += cur_number


        f = safeopen('./res/featureNumberByDate/{}.dat'.format(feature_name), 'w')
        total_numbers = sorted(total_numbers.iteritems(), key=lambda (k,v): (-v,k))
        total_numbers = total_numbers[:show_number]
        # print feature names
        for val in total_numbers:
            f.write('{} '.format(val[0]))
        f.write('others\n')

        if percentage:
            for date in datelist:
                for feature in res[date]:
                    # avoid divide by zero
                    if daily_all_numbers[date] == 0:
                        daily_all_numbers[date] = 1
                    res[date][feature] = float(res[date][feature]) / float(daily_all_numbers[date])


        for date in datelist:
            cur_sum = 0
            f.write('{}-{}-{}'.format(date.year, date.month, date.day))
            for feature in total_numbers:
                if feature[0] not in res[date]:
                    f.write(' 0')
                    continue
                cur_sum += res[date][feature[0]]
                f.write(' {}'.format(res[date][feature[0]]))
            if percentage:
                f.write(' {}\n'.format(1.0 - cur_sum))
            else:
                f.write(' {}\n'.format(daily_all_numbers[date] - cur_sum))
        f.close()

    def feature_change_by_browser_date_paper(self, feature, method = 'window'):
        """
        return the number of changed browserid of the feature in each day
        method options: window, accu, day 
        """
        #TODO discuss number of browserid or number of changes
        print ("generating each day's number")
        db = Database('forpaper345')
        df = db.load_data(feature_list = ['time', 'browser', 'browserid'], table_name = 'pandas_features')
        df = round_time_to_day(df)

        # keep the same df as changes database
        df = filter_less_than_n(df, 3)
        grouped = df.groupby(['time', 'browser'])
        total_number = {}
        max_size = 0

        if method == 'window':
            max_size = 5
        elif method == 'accu':
            max_size = 10000000
        elif method == 'day':
            max_size = 1

        cur_total = {}
        for cur_group in tqdm(grouped):
            # here we assume time is sorted
            cur_time = cur_group[0][0]
            cur_browser = cur_group[0][1]
            cur_number = cur_group[1]['browserid'].nunique()

            if cur_time not in total_number:
                total_number[cur_time] = {}
            if cur_browser not in cur_total:
                cur_total[cur_browser] = collections.deque() 

            # assume every day we have data for this browser
            cur_total[cur_browser].append(cur_number)
            while len(cur_total[cur_browser]) > max_size:
                cur_total[cur_browser].popleft()

            total_number[cur_time][cur_browser] = sum(cur_total[cur_browser])

        print ("generating real data")
        db = Database('filteredchangesbrowserid')
        df = db.load_data(table_name = '{}changes'.format(feature))
        df = round_time_to_day(df, timekey = 'totime')
        min_date = min(df['fromtime'])
        min_date = min_date.replace(microsecond = 0, second = 0, minute = 0, hour = 0)
        max_date = max(df['totime'])

        lendate = (max_date - min_date).days
        datelist = [min_date + datetime.timedelta(days = i) for i in range(lendate + 3)]

        # to time is the day that this feature changes
        grouped = df.groupby(['totime', 'browser'])

        res = {}

        for cur_group in tqdm(grouped):
            cur_time = cur_group[0][0]
            cur_browser = cur_group[0][1]
            cur_number = cur_group[1]['browserid'].nunique()

            if cur_browser not in res:
                res[cur_browser] = {}

            if total_number[cur_time][cur_browser] == 0:
                res[cur_browser][cur_time] = 0
            else:
                res[cur_browser][cur_time] = float(cur_number) / float(total_number[cur_time][cur_browser]) * 100

        f = safeopen('./change_dats/{}_{}.dat'.format(feature, max_size), 'w')
        f.write('Browser ')
        cnt = 1
        browser_list = []
        for browser in res:
            cnt += 1
            browser_list.append(browser)
            f.write('{}_{} '.format(cnt, browser.replace(' ', '_')))
        f.write('\n')

        for date in datelist:
            # here we replace the space of browsers with _
            f.write('{}-{}-{} '.format(date.year, date.month, date.day))
            for browser in browser_list:
                if date in res[browser]:
                    cur_num = res[browser][date]
                else:
                    cur_num = 0
                f.write('{} '.format(cur_num))
            f.write('\n')
        f.close()

    def feature_change_by_date_paper(self, feature_name):
        """
        take the name of the feature and the changes df
        """
        db = Database('filteredchangesbrowserid')
        df = db.load_data(table_name = '{}changes'.format(feature_name))
        df = remove_flip_users(df)
        print ("{} users remain".format(df['browserid'].nunique()))
        try:
            min_date = min(df['fromtime'])
        except:
            return 
        min_date = min_date.replace(microsecond = 0, second = 0, minute = 0, hour = 0)
        max_date = max(df['totime'])
        lendate = (max_date - min_date).days
        grouped = df.groupby(['from', 'to'])
        # how many browserids 
        sorted_group = collections.OrderedDict(grouped['browserid'].nunique().sort_values(ascending=False))
        sorted_keys = sorted_group.keys()
        total_len = len(grouped)
        output_length = 5
        cur = 0
        dates_data = {}
        datelist = [min_date + datetime.timedelta(days = i) for i in range(lendate + 3)]

        cnt = 0
        sep = ' '

        f = safeopen('./res/topchanges.dat', 'a')
        for group in sorted_group:
            if feature_name == 'langsdetected' or feature_name == 'jsFonts':
                sep = '_'
            elif feature_name == 'plugins':
                sep = '~'
            counts = get_feature_percentage(grouped.get_group(group), 'browser')
            os_counts = get_feature_percentage(grouped.get_group(group), 'os')
            
            try:
                f.write('{} {} {} {} {} {} {} {}\n'.format('$$'.join(group), 
                    '$$', get_change_strs(group[0], group[1], sep=sep), 
                    sorted_group[group], counts[0][0], counts[0][1], os_counts[0][0], os_counts[0][1]))
            except:
                print '$$'.join(str(e) for e in group)
            cnt += 1
            if cnt > 10:
                break
        f.close()

        print ('all changes finished')

        for date in datelist:
            dates_data[date] = {}
            for t in sorted_keys:
                dates_data[date][t] = 0

        for i in tqdm(range(11)):
            try:
                cur_key = sorted_keys[i]
            except:
                break
            cur_group = grouped.get_group(cur_key)
            for idx, row in cur_group.iterrows():
                # round to day
                cur_time = row['totime'].replace(microsecond = 0, second = 0, minute = 0, hour = 0)
                dates_data[cur_time][cur_key] += 1
        first = True
        f = safeopen('./dat/{}changebydate.dat'.format(feature_name),'w')
        for date in datelist:
            if first:
                first = False
                for idx in range(10):
                    try:
                        key = sorted_keys[idx]
                    except:
                        break
                    f.write('{} '.format(str(get_change_strs(key[0], key[1], sep = ' ')).replace(' ','_')))
                f.write('\n')
            f.write('{}-{}-{} '.format(date.year, date.month, date.day))
            sumup = 0
            for idx in range(10):
                try:
                    key = sorted_keys[idx]
                except:
                    break
                f.write('{} '.format(dates_data[date][key]))
                sumup += dates_data[date][key]
                f.write('{} '.format(sum(dates_data[date].values()) - sumup))
            f.write('\n')
        f.close()

