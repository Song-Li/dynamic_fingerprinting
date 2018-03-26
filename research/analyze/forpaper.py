import pandas as pd
import hashlib
import os
from pd_analyze import *
from database import Database
from extractinfo import *
from feature_lists import *
import collections

long_feature_list = get_long_feature_list()
feature_list = get_feature_list()
ori_long_feature_list = get_ori_long_feature_list()
ori_feature_list = get_ori_feature_list()

def feature_delta_paper(db):
    df = load_data(load = True, feature_list = ["*"], 
            table_name = "pandas_longfeatures", db = db)
    df = filter_less_than_n(df, 7)
    maps = {} 
    for feature in long_feature_list:
        maps[feature] = {"browserid":[], "IP":[], "from":[], "to":[], "fromtime":[], "totime":[], "browser":[], "os":[]}

    grouped = df.groupby('browserid')
    pre_fingerprint = ""
    pre_row = []
    for cur_key, cur_group in tqdm(grouped):
        if cur_group['browserfingerprint'].nunique() == 1:
            continue
        pre_fingerprint = ""
        for idx, row in cur_group.iterrows():
            if pre_fingerprint == "":
                pre_fingerprint = row['browserfingerprint']
                pre_row = row
                continue
            for feature in long_feature_list:
                if feature not in row:
                    continue
                if pre_row[feature] != row[feature]:
                    maps[feature]['browserid'].append(row['browserid'])
                    maps[feature]['IP'].append(row['IP'])
                    maps[feature]["from"].append(pre_row[feature])
                    maps[feature]['to'].append(row[feature])
                    maps[feature]['fromtime'].append(pre_row['time'])
                    maps[feature]['totime'].append(row['time'])
                    maps[feature]['browser'].append(row['browser'])
                    maps[feature]['os'].append(get_os_from_agent(row['agent']))
            pre_row = row

    db = Database('filteredchanges')
    for feature in long_feature_list:
        print feature
        try:
            df = pd.DataFrame.from_dict(maps[feature])
            db.export_sql(df, '{}changes'.format(feature))
            print 'success'
        except:
            print len(maps[feature]['from']), len(maps[feature]['to']), len(maps[feature]['fromtime']), len(maps[feature]['totime'])
    return maps

def check_flip_changes(group):
    appeared = set()
    for idx, row in group.iterrows():
        # if to value is used to be from
        # its fliped
        if row['to'] in appeared:
            return True
        appeared.add(row['from'])
    return False

def check_flip_browserid(group, feature):
    appeared = set()
    pre_feature = ""
    for idx, row in group.iterrows():
        if pre_feature != row[feature]:
            # appeared before
            if row[feature] in appeared:
                return True 
            pre_feature = row[feature]
            appeared.add(row[feature])
    return False 


def remove_flip_users(df):
    flip_list = []
    grouped = df.groupby('browserid')
    print('remove flip users')
    for key, cur_group in tqdm(grouped):
        if check_flip_changes(cur_group):
            flip_list.append(key)

    return df[~df['browserid'].isin(flip_list)] 

def get_feature_percentage(group, key):
    users = {} 
    num_users = group['browserid'].nunique()
    for idx, row in group.iterrows():
        if row[key] not in users:
            users[row[key]] = set() 
        users[row[key]].add(row['browserid'])
    sorted_dict = sorted(users.iteritems(), key=lambda (k,v): (-len(v),k))
    res = []
    for cur in sorted_dict:
        res.append((cur[0], float(len(cur[1])) / float(num_users)))
    return res 


def feature_change_by_date_paper(feature_name, df):
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
    for group in sorted_group:
        if feature_name == 'langsdetected' or feature_name == 'jsFonts':
            sep = '_'
        elif feature_name == 'plugins':
            sep = '~'
        counts = get_feature_percentage(grouped.get_group(group), 'browser')
        os_counts = get_feature_percentage(grouped.get_group(group), 'os')
        
        try:
            print '$$'.join(group), '$$', get_change_strs(group[0], group[1], sep=sep), sorted_group[group], counts[0][0], counts[0][1], os_counts[0][0], os_counts[0][1]
        except:
            print '$$'.join(str(e) for e in group)
        cnt += 1
        if cnt > 10:
            break

    return 

    for date in datelist:
        dates_data[date] = {}
        for t in sorted_keys:
            dates_data[date][t] = 0

    for i in tqdm(range(11)):
        cur_key = sorted_keys[i]
        cur_group = grouped.get_group(cur_key)
        for idx, row in cur_group.iterrows():
            # round to day
            cur_time = row['totime'].replace(microsecond = 0, second = 0, minute = 0, hour = 0)
            dates_data[cur_time][cur_key] += 1
    first = True
    f = open('./dat/{}changebydate.dat'.format(feature_name),'w')
    for date in datelist:
        if first:
            first = False
            for idx in range(10):
                key = sorted_keys[idx]
                f.write('{} '.format(str(get_change_strs(key[0], key[1], sep = ' ')).replace(' ','_')))
            f.write('\n')
        f.write('{}-{}-{} '.format(date.year, date.month, date.day))
        sumup = 0
        for idx in range(10):
            key = sorted_keys[idx]
            f.write('{} '.format(dates_data[date][key]))
            sumup += dates_data[date][key]
            f.write('{} '.format(sum(dates_data[date].values()) - sumup))
        f.write('\n')
    f.close()

def get_key_from_agent(agent, key_type = 'browser'):
    ret = ""
    if key_type == 'browser':
        # RETURN big number of version number
        ret = get_browser_version(agent).split('.')[0]
    return ret

# TODO this function is not tested
def check_df_flipping(df, feature, key_words, sep = ' '):
    grouped = df.groupby('browserid')
    total_flipping = 0
    key_words_contained = 0
    for key, group in tqdm(grouped):
        if group['browserfingerprint'].nunique() == 1:
            continue
        appeared = set()
        pre_val = "fake"
        for idx, row in group.iterrows():
            cur_val = row[feature]
            if pre_val != cur_val:
                pre_val = cur_val
                if cur_val in appeared:
                    total_flipping += 1
                    diff_bag = get_change_strs(pre_val, cur_val, sep = sep)
                    if len(key_words - diff_bag[0]) == 0 or len(key_words - diff_bag[1]) == 0:
                        key_words_contained += 1
                else:
                    appeared.add(cur_val)

    print total_flipping,key_words_contained

def safeopen(file_name, way):
    if not os.path.exists(os.path.dirname(file_name)):
        try:
            os.makedirs(os.path.dirname(file_name))
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise
    f = open(file_name, way)
    return f

def get_key_from_feature(value, feature):
    if feature == 'agent':
        return get_key_from_agent(value)
    else:
        return value


def feature_by_date_paper(feature, df):
    # here we put the keys of each features
    maps = {}
    browser_options = ['chrome', 'firefox', 'safari']
    print "round time to days"
    df = df.drop_duplicates(subset = [feature, 'time', 'browserid'])
    
    min_date = min(df['time'])
    max_date = max(df['time'])
    lendate = (max_date - min_date).days
    datelist = [min_date + datetime.timedelta(days = i) for i in range(lendate + 3)]
    for date in datelist:
        maps[date] = {}

    grouped = df.groupby('browserid')
    browser_version_all = {browser: {} for browser in browser_options}

    for key, group in tqdm(grouped):
        for idx, row in group.iterrows():
            browser_version = get_key_from_agent(row['agent'])
            value_key = get_key_from_feature(row[feature], feature)
            for browser in browser_options:
                if browser_version.lower().find(browser) != -1:
                    if value_key not in browser_version_all[browser]:
                        browser_version_all[browser][value_key] =0
                    browser_version_all[browser][value_key] += 1

            date = row['time']
            if value_key not in maps[date]:
                maps[date][value_key] = 0
            maps[date][value_key] += 1

    #sort browser versions
    for browser in browser_version_all:
        browser_version_all[browser] = sorted(browser_version_all[browser].iteritems(), key=lambda (k,v): (-v,k))
        for date in maps:
            for browser_version, value in browser_version_all[browser]:
                if browser_version not in maps[date]:
                    maps[date][browser_version] = 0

    f = {}
    f['chrome'] = safeopen('./stackednumberbydate/{}/chrome.dat'.format(feature), 'w')
    f['firefox'] = safeopen('./stackednumberbydate/{}/firefox.dat'.format(feature), 'w')
    f['safari'] = safeopen('./stackednumberbydate/{}/safari.dat'.format(feature), 'w')

    # write titles
    for browser in f:
        cur_cnt = 0
        for browser_version, value in browser_version_all[browser]:
            cur_cnt += 1
            if cur_cnt >= 5:
                break
            f[browser].write('{} '.format(str(browser_version).replace(' ', '_')))
        f[browser].write('others\n')

    # chrome version 58 check
    for date in datelist:
        for browser in browser_options:
            f[browser].write('{}-{}-{} '.format(date.year, date.month, date.day))
            sum_all = 0
            other = 0
            cur_cnt = 0
            for browser_version, cnt in browser_version_all[browser]:
                sum_all += maps[date][browser_version]
                if sum_all == 0:
                    sum_all = 1
            for browser_version, cnt in browser_version_all[browser]:
                cur_cnt += 1
                if cur_cnt >= 5:
                    break
                else:   
                    cur_value = float(maps[date][browser_version]) / float(sum_all)
                    f[browser].write('{0:.3f} '.format(cur_value * 100))
                    other += cur_value

            f[browser].write('{0:.3f} '.format(100 * (1.0 - float(other))))
            f[browser].write('\n')

                
    for browser in f:
        f[browser].close()
    


def get_all_feature_change_by_date_paper(db):
    for feature in long_feature_list:
        print 'generating {}'.format(feature)
        df = load_data(load = True, feature_list = ["*"], 
                table_name = "{}changes".format(feature), db = db)
        print ("{} users changed in total".format(df['browserid'].nunique()))
        feature_change_by_date_paper(feature, df)

def get_unique_fingerprint_list(df):
    grouped = df.groupby('browserfingerprint')
    print ('getting the unique browserfingerprint set')
    unique_fingerprint = set()
    for key, grouped in tqdm(grouped):
        if grouped['browserid'].nunique() == 1:
            unique_fingerprint.add(key)
    return unique_fingerprint

def get_sep(feature):
    sep = ' '
    if feature == 'langsdetected' or feature == 'jsFonts':
        sep = '_'
    elif feature == 'plugins':
        sep = '~'
    return sep


def check_browser_become_unique(db):
    df = load_data(load = True, feature_list = ["*"], 
            table_name = "pandas_features", db = db)
    unique_list = get_unique_fingerprint_list(df)
    ret = {}
    change_feature = {feature: 0 for feature in feature_list}
    grouped = df.groupby('browserid')
    change_val = {}
    for key, cur_group in tqdm(grouped):
        pre_row = {'browserfingerprint': 'fake'}
        for idx, row in cur_group.iterrows():
            if pre_row['browserfingerprint'] == 'fake':
                pre_row = row
                continue
            if pre_row['browserfingerprint'] != row['browserfingerprint']:
                if pre_row['browserfingerprint'] not in unique_list and row['browserfingerprint'] in unique_list:
                    ret[row['browserfingerprint']] = [pre_row['browserfingerprint'], row['browserid']]
                    for feature in feature_list:
                        if row[feature] != pre_row[feature]:
                            if feature != 'browserfingerprint':
                                sep = get_sep(feature)
                                change = str(get_change_strs(pre_row[feature], row[feature], sep = sep))
                                if change not in change_val:
                                    change_val[change] = {}
                                    change_val[change]['total'] = 0
                                for sub_feature in feature_list:
                                    if row[sub_feature] != pre_row[sub_feature]:
                                        sub_value = sub_feature 
#str(get_change_strs(pre_row[sub_feature],
#                                            row[sub_feature], sep = sep))
                                        if sub_value not in change_val[change]:
                                            change_val[change][sub_value] = 0
                                        change_val[change][sub_value] += 1
                                change_val[change]['total'] += 1
                            change_feature[feature] += 1
                pre_row = row
                
    '''
    # we need to calculate the users with same fingerprints
    fp_grouped = df.groupby('browserfingerprint')
    for uniquefp in ret:
        pre_fp = ret[0]
        cur_group = fp_grouped.get_group(pre_fp)
        for key, row in cur_group.iterrows():
            pass
    '''
    
    change_val = sorted(change_val.iteritems(), key=lambda (k,v): (-v['total'],k))
    for change in change_val:
        print '==================================='
        print change[0], change[1]['total']
        for value in change[1]:
            print value, change[1][value]
        print '==================================='
    print change_feature
    #for uniquefp in ret:
    #    print uniquefp, ret[uniquefp]
    return ret, change_feature


def filter_less_than_n(df, n):
    grouped = df.groupby('browserid')
    filtered = set()
    print 'filtering'
    for key, cur_group in tqdm(grouped):
        length = len(cur_group['IP'])
        if length >= n:
            filtered.add(str(key))

    df = df[df['browserid'].isin(filtered)]
    return df

def num_fingerprints_distribution(db):
    df = load_data(load = True, feature_list = ["*"], 
            table_name = "pandas_features", db = db)
    df = filter_less_than_n(df, 7)
    grouped = df.groupby('browserid')
    change_time = [0 for i in range(500)]
    for key, cur_group in tqdm(grouped):
        change_time[cur_group['browserfingerprint'].nunique()] += 1
        if cur_group['browserfingerprint'].nunique() > 40:
            print key
    print change_time
    return change_time

def get_browserid_change(df, file_name, change_from, change_to, output_file_name, change_feature_name = ""):
    print ("doing {} -> {}".format(change_from, change_to))
    f = open(file_name, 'r')
    content = f.readlines()
    users = [x.strip() for x in content] 
    changes = {} 
    for user in tqdm(users):
        changes = get_browserid_change_id(df, user, changes, change_from, change_to, change_feature_name = change_feature_name)

    sorted_dict = sorted(changes.iteritems(), key=lambda (k,v): (-v,k))
    if len(changes) == 0:
        return 

    total = sorted_dict[0][1]

    output_file_name = output_file_name.replace('/', '_')
    output_file_name = output_file_name.replace(' ', '_')
    if len(output_file_name) > 100:
        output_file_name = hashlib.sha256(output_file_name).hexdigest()

    output_file = safeopen('./changeres/{}/{}'.format(change_feature_name, output_file_name), 'w')
    output_file.write("doing {} -> {}\n".format(change_from, change_to))
    for pair in sorted_dict:
        output_file.write('{} {}\n'.format(pair[0], float(pair[1]) / float(total)))
    output_file.close()

def get_browserid_change_id(df, browserid, changes, change_from, change_to , change_feature_name = ""):
    #try:
    #    f = open('./specialusers/{}'.format(browserid), 'w')
    #except:
    #    return changes
    aim_df = df[df['browserid'] == browserid]
    #aim_df = aim_df[(aim_df[change_feature_name] == change_from) | (aim_df[change_feature_name] == change_to)]
    aim_df = aim_df.reset_index(drop = True)
    pre_row = {}
    sep = ' '
    for idx in aim_df.index:
        sep = ' '
        row = aim_df.iloc[idx]
        if len(pre_row) == 0:
            pre_row = row
            continue
        if pre_row[change_feature_name] == change_from and row[change_feature_name] == change_to:
            for feature in long_feature_list:
                #if feature == 'browserfingerprint':
                #    continue
                if row[feature] == pre_row[feature]:
                    continue
                if change_feature_name == "": 
                    sep = get_sep(feature)
                    #f.write('{} {}\n'.format(feature, get_change_strs(pre_row[feature], row[feature], sep = sep)))
                else:
                    if row[change_feature_name] == pre_row[change_feature_name]:
                        continue

                    cur_str = '{} {}\n'.format(feature, get_change_strs(pre_row[feature], row[feature], sep=sep))
                    if cur_str not in changes:
                        changes[cur_str] = 0
                    changes[cur_str] += 1
                    #f.write('{} {}\n'.format(feature, cur_str))
            #f.write('====================================\n')
        pre_row = row

    #f.close()
    return changes

# input the feature name, two different feature value
# return the basic info of these features
def check_diff_feature_value(db, feature, from_val, to_val):
    df = load_data(load = True, feature_list = ["browserid"], table_name = "{}changes".format(feature), db = db, other = ' where `from` = "{}" and `to` = "{}"'.format(from_val, to_val))
    browserid_list = list(df['browserid'])
    return browserid_list


def draw_feature_change_by_date(db):
    df = load_data(load = True, feature_list = ["*"], table_name = "pandas_features", db = db)

def round_time_to_day(df):
    # round time to days
    for idx in tqdm(df.index):
        df.at[idx, 'time'] = df.at[idx, 'time'].replace(microsecond = 0, second = 0, minute = 0, hour = 0)
    return df

def get_change_details(change_feature_name, change_from, change_to, df):
    db = Database('filteredchanges')
    browserid_list = check_diff_feature_value(db, change_feature_name, change_from, change_to)
    f = safeopen('./tmpout', 'w')
    for browserid in browserid_list:
        f.write(browserid + '\n')
    f.close()
    get_browserid_change(df,'./tmpout', change_from, change_to, '{}_{} -> {}'.format(change_feature_name,change_from,change_to), change_feature_name = change_feature_name)

def get_all_change_details(file_name):
    db = Database('uniquemachine')
    df = load_data(load = True, feature_list = ["*"], table_name = "pandas_longfeatures", db = db)

    f = open(file_name, 'r')
    content = f.readlines()
    feature_name = ""
    start = False
    for line in content:
        if line.find('generating') != -1:
            feature_name = line.split(' ')[1].strip()
        elif line.find('$$') != -1:
            change_from = line.split('$$')[0].strip()
            change_to = line.split('$$')[1].strip()
            if feature_name == 'browserfingerprint':
                get_change_details(feature_name, change_from, change_to, df)

def life_time_distribution_paper(db):
    df = load_data(load = True, feature_list = ["*"], table_name = "pandas_features", db = db)
    df = filter_less_than_n(df, 7)
    feature_list = [ 
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
        print feature, life_time[feature]
        total_change = sum(life_time[feature])
        half = total_change / 2
        for i in range(length + 1):
            cur += life_time[feature][i]
            if cur > half:
                medians[feature] = i + 1
                break

    for feature in medians:
        print feature + ' ' + str(medians[feature])

def generate_databases():
    #db = Database('round1')
    #df1 = load_data(load = True, feature_list = long_feature_list, table_name = "features", db = db)
    db = Database('round2')
    df2 = load_data(load = True, feature_list = ori_long_feature_list, table_name = "features", db = db)
    db = Database('round3')
    df3 = load_data(load = True, feature_list = ori_feature_list, table_name = "features", db = db)
    db = Database('round4')
    df4 = load_data(load = True, feature_list = ori_feature_list, table_name = "features", db = db)
    aim_db = Database('forpaper')
    aim_db.combine_tables(ori_long_feature_list, [df2, df3, df4], 'longfeatures')
    aim_db.combine_tables(ori_feature_list, [df3, df4], 'features')
    df3 = load_data(load = True, feature_list = long_feature_list, table_name = "longfeatures", db = aim_db)
    db.clean_sql(long_feature_list, df3, generator = get_location_dy_ip, 
            get_device = get_device, get_browserid = get_browserid,
            aim_table = 'pandas_longfeatures')
    df3 = load_data(load = True, feature_list = feature_list, table_name = "features", db = aim_db)
    db.clean_sql(feature_list, df3, generator = get_location_dy_ip, 
            get_device = get_device, get_browserid = get_browserid,
            aim_table = 'pandas_features')


def main():
    generate_databases()
    #life_time_distribution_paper(db)
    #df = load_data(load = True, feature_list = ["*"], table_name = "pandas_features", db = db)
    #df = filter_less_than_n(df, 7)
    #feature_latex_table_paper(df)
    #get_all_change_details('./res/all_changes_by_date_filtered')
    #db = Database('filteredchanges')
    #get_all_feature_change_by_date_paper(db)
    #maps = feature_delta_paper(db)
    #get_browserid_change_id(df, "f4ce016af1e96e71ddcd0bde3f78869f2iPhoneImagination TechnologiesPowerVR SGX 543safari")
   # db = Database('changes')
    #df = load_data(load = True, feature_list = ["*"], table_name = "pandas_features", db = db)
    #db = Database('changes')
    #df = load_data(load = True, feature_list = ["*"], table_name = "pandas_features", db = db, other = ' where jsFonts is not NULL and gpuimgs is not NULL')
    #df = round_time_to_day(df)
    #for feature in feature_list:
    #    feature_by_date_paper(feature, df)
    #check_browser_become_unique(db)
    #num_fingerprints_distribution(db)
    #df = load_data(load = True, feature_list = ["*"], table_name = "pandas_longfeatures", db = db)
    #check_browser_become_unique(db)
    #change_to_unique, change_feature = check_browser_become_unique(db)
    #df = load_data(load = True, feature_list = ["*"], table_name = "pandas_longfeatures", db = db)
    #db = Database('changes')



if __name__ == "__main__":
    main()
