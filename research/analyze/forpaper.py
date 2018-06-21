import pandas as pd
import re
import hashlib
import os
from pd_analyze import *
from database import Database
from extractinfo import *
from feature_lists import *
import collections
import user_agents

long_feature_list = get_long_feature_list()
feature_list = get_feature_list()
ori_long_feature_list = get_ori_long_feature_list()
ori_feature_list = get_ori_feature_list()
global ip2location

def generate_changes_database(db, feature_list = feature_list):
    """
    this function will generate the changes database
    the database should be generated before the call of this function
    """
    browserid = 'dybrowserid'
    df = db.load_data(feature_list = ["*"], 
            table_name = "pandas_features_split")
    df = filter_less_than_n(df, 5)

    # add label changes to database
    if 'label' not in feature_list:
        feature_list.append('label')

    maps = {} 
    for feature in feature_list:
        maps[feature] = {'browserid':[], "IP":[], "from":[], "to":[], "fromtime":[], "totime":[], "browser":[], "os":[]}

    grouped = df.groupby(browserid)
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
            for feature in feature_list:
                if feature not in row:
                    continue
                if pre_row[feature] != row[feature]:
                    maps[feature]['browserid'].append(row[browserid])
                    maps[feature]['IP'].append(row['IP'])
                    maps[feature]["from"].append(pre_row[feature])
                    maps[feature]['to'].append(row[feature])
                    maps[feature]['fromtime'].append(pre_row['time'])
                    maps[feature]['totime'].append(row['time'])
                    maps[feature]['browser'].append(row['browser'])
                    maps[feature]['os'].append(get_os_from_agent(row['agent']))
            pre_row = row

    db = Database('filteredchanges{}_split'.format(browserid))
    for feature in feature_list:
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

    """
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
    """

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

def get_key_from_agent(agent, key_type = 'browser'):
    ret = ""
    if key_type == 'browser':
        # RETURN big number of version number
        ret = get_browser_version(agent).split('.')[0]
    return ret

# NOTE this function is not tested
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

def draw_feature_number_by_date(feature_name, percentage = False):
    """
    draw total number of a feature by date
    this function will return a stacked dat file
    """
    show_number = 5
    db = Database('forpaper')
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


    f = safeopen('./featureNumberByDate/{}'.format(feature_name), 'w')
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

def draw_feature_number_by_browser_date_paper(feature, df):
    """
    draw number of feature by browser and date
    currently this function will output a stacked picture data
    """
    # here we put the keys of each features
    browserid = 'browserid'
    maps = {}
    browser_options = ['chrome', 'firefox', 'safari']
    print "round time to days"
    df = round_time_to_day(df)
    df = df.drop_duplicates(subset = [feature, 'time', browserid])
    
    min_date = min(df['time'])
    min_date = min_date.replace(microsecond = 0, second = 0, minute = 0, hour = 0)
    max_date = max(df['time'])
    lendate = (max_date - min_date).days
    datelist = [min_date + datetime.timedelta(days = i) for i in range(lendate + 3)]
    for date in datelist:
        maps[date] = {}

    grouped = df.groupby(browserid)
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
    for feature in feature_list:
        print 'generating {}'.format(feature)
        df = db.load_data(feature_list = ["*"], 
                table_name = "{}changes".format(feature))
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
    """
    this function should be used as 
    remove the users who have less than n records
    """
    grouped = df.groupby('browserid')
    filtered = set()
    print 'filtering'
    for key, cur_group in tqdm(grouped):
        length = len(cur_group['browserid'])
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
                if row[feature] == pre_row[feature]:
                    continue
                if change_feature_name == "": 
                    sep = get_sep(feature)
                else:
                    if row[change_feature_name] == pre_row[change_feature_name]:
                        continue

                    cur_str = '{} {}\n'.format(feature, get_change_strs(pre_row[feature], row[feature], sep=sep))
                    if cur_str not in changes:
                        changes[cur_str] = 0
                    changes[cur_str] += 1
        pre_row = row

    return changes

def check_diff_feature_value(db, feature, from_val, to_val):
    """
    input the feature name, two different feature value
    return the basic info of these features
    """
    df = load_data(load = True, feature_list = ["browserid"], table_name = "{}changes".format(feature), db = db, other = ' where `from` = "{}" and `to` = "{}"'.format(from_val, to_val))
    browserid_list = list(df['browserid'])
    return browserid_list

def draw_feature_change_by_date(db):
    df = load_data(load = True, feature_list = ["*"], table_name = "pandas_features", db = db)

def round_time_to_day(df):
    print ('Rounding time to days')
    # round time to days
    for idx in tqdm(df.index):
        df.at[idx, 'time'] = df.at[idx, 'time'].replace(microsecond = 0, second = 0, minute = 0, hour = 0)
    return df

def get_change_details(change_feature_name, change_from, change_to, df):
    db = Database('filteredchanges')
    browserid_list = check_diff_feature_value(db, change_feature_name, change_from, change_to)
    f = safeopen('./tmpout', 'w')
    for browserid in browserid_list:
        print browserid
        f.write(browserid + '\n')
    f.close()
    get_browserid_change(df,'./tmpout', change_from, change_to, '{}_{} -> {}'.format(change_feature_name,change_from,change_to), change_feature_name = change_feature_name)

def get_all_change_details(file_name):
    db = Database('forpaper')
    df = load_data(load = True, feature_list = ["*"], table_name = "pandas_features", db = db)

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
            get_change_details(feature_name, change_from, change_to, df)

def round_time_to_hour(df):
    print ('Rounding time to hours')
    # round time to days
    for idx in tqdm(df.index):
        df.at[idx, 'time'] = df.at[idx, 'time'].replace(microsecond = 0, second = 0, minute = 0)
    return df

def tdhours(td):
    """
    return the timedelta hours
    """
    return td.days * 24 + td.seconds//3600

#NOTE not tested
def life_time_distribution(db, feature_name = 'IP'):
    """
    get the life time distribution of a feature in hours
    input the df and feature name
    output a list with number of related life time
    """
    # for research, filter less than 5
    df = db.load_data(feature_list = ['os', 'label', 'IP', 'time', 'browserid'], table_name = 'pandas_features')
    # CONSIDER NON mac only
    df = filter_df(df, 'os', filtered_list = ['iOS', 'Mac OS X'])

    min_date = min(df['time'])
    max_date = max(df['time'])
    df = filter_less_than_n(df, 4)
    
    # we use the browserid as current ground truth
    # try to use label as ground truth
    grouped = df.groupby('browserid')
    round_time_to_hour(df)
    min_date = min(df['time'])
    max_date = max(df['time'])
    length = tdhours(max_date - min_date) + 3
    life_time = [0 for i in range(length + 10)]

    #this part is userd for change together with label
    together_life_time = [0 for i in range(length + 10)]
    all_visit = [0 for i in range(length + 10)]

    
    for browserid, cur_group in tqdm(grouped):
        pre_feature = ""
        pre_label = ""
        pre_time = -1
        for idx, row in cur_group.iterrows():
            if pre_feature == "":
                pre_feature = row[feature_name]
                pre_time = row['time']
                pre_label = row['label']
                continue

            cur_delt = tdhours(row['time'] - pre_time)
            if pre_feature != row[feature_name]:
                life_time[cur_delt] += 1
                if row['label'] != pre_label:
                    together_life_time[cur_delt] += 1

            pre_feature = row[feature_name]
            pre_time = row['time']
            pre_label = row['label']
            all_visit[cur_delt] += 1

    return all_visit, life_time, together_life_time

def life_time_median_paper(db):
    df = load_data(load = True, feature_list = ["*"], table_name = "pandas_features", db = db)
    df = filter_less_than_n(df, 7)

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

def get_device(row):
    id_str = ""
    # platform is between the first ( and the first ;
    platform = ""
    parsed = user_agents.parse(row['agent'])
    os = ignore_non_ascii(parsed.os.family)
    device = ignore_non_ascii(parsed.device.family)
    browser = ignore_non_ascii(parsed.browser.family)
    full_os = '{} {}'.format(ignore_non_ascii(parsed.os.family), ignore_non_ascii(parsed.os.version_string))
    full_device = '{} {}'.format(ignore_non_ascii(parsed.device.family), ignore_non_ascii(parsed.device.brand))
    full_browser = '{} {}'.format(ignore_non_ascii(parsed.browser.family), ignore_non_ascii(parsed.browser.version_string))
    keys = ['clientid', 'cpucores']
    for key in keys:
        # we assume that all of the keys are not null
        try:
            id_str += str(row[key])
        except:
            pass

    id_str += os 
    id_str += full_device
    return id_str

def get_location_dy_ip(ip):
    # try to use the ip location
    global ip2location
    int_ip = ip2int(ip)
    ip_from = ip2location['ip_from']
    idx = bisect.bisect_left(ip_from, int_ip) - 1
    city = ip2location.iloc[idx]['city_name']
    region = ip2location.iloc[idx]['region_name']
    country = ip2location.iloc[idx]['country_name']
    latitude = ip2location.iloc[idx]['latitude']
    longitude = ip2location.iloc[idx]['longitude']
    return [city, region, country, latitude, longitude]

def get_action(feature_name, value_from, value_to):
    if feature_name not in feature_list:
        print ("feature_name not in feature list")
        return 
    action = ""
    if feature_name == 'agent':
        browser_type = get_browser_from_agent(value_from)
        from_browser_version = get_browser_version(value_from)
        to_browser_version = get_browser_version(value_to)
        if from_browser_version != to_browser_version:
            action = '{}_{}->{}'.format(browser_type, from_browser_version, to_browser_version)
            return action
        from_os_version = get_os_from_agent(value_from)
        to_os_version = get_os_from_agent(value_to)
        if from_os_version != to_os_version:
            action = '{}-{}->{}'.format(browser_type, from_os_version, to_os_version)
            return action
    elif feature_name == 'jsFonts':
        changes = get_change_strs(value_from, value_to, sep = '_')
        action = '{}->{}'.format(changes[0], changes[1])
    else:
        action = '{}->{}'.format(value_from, value_to)
    return action

def filter_df(df, feature_name, filtered_list = ['iphone', 'ipad', 'mac']):
    df = df[~df[feature_name].isin(filtered_list)] 
    return df

def verify_browserid_by_cookie():
    """
    this function will return the lower bound and upper bound of browserid accuracy
    the upper bound is the percentage of browserids with more than one cookies
    the lower bound is the percentage of browserids with fliped cookies
    """
    browserid = 'dybrowserid'
    db = Database('forpaper')
    df = db.load_data(feature_list = [browserid, 'label', 'os', 'browser'], table_name = 'pandas_features_split')

    #we can add filter here
    df = filter_less_than_n(df, 5)

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

def generate_databases():
    #db = Database('round1')
    #df1 = load_data(load = True, feature_list = long_feature_list, table_name = "features", db = db)
    '''
    db = Database('round2')
    df2 = db.load_data(feature_list = ['*'], table_name = "features")
    db = Database('round3')
    df3 = db.load_data(feature_list = ['*'], table_name = "features")
    '''
    db = Database('round4')
    df4 = db.load_data(feature_list = ['*'], table_name = "features")
    db = Database('round5')
    df5 = db.load_data(feature_list = ['*'], table_name = "features")
    #aim_db.combine_tables(ori_long_feature_list, [df2, df3, df4], 'longfeatures')
    aim_db = Database('forpaper')
    aim_db.combine_tables(ori_feature_list, [df4, df5, df6], 'features')
    return 
    #df2 = aim_db.load_data(feature_list = ori_long_feature_list, table_name = "longfeatures")
    db = Database('uniquemachine')
    aim_db = Database('forpaper')
    global ip2location   
    ip2location = pd.read_sql('select * from ip2location_db5;', con=db.get_db())    
    print ("ip2location data loaded")
    df3 = aim_db.load_data(feature_list = ori_feature_list, table_name = "features")
    aim_db.clean_sql(feature_list, df3, generator = get_location_dy_ip, 
            get_device = get_device, get_browserid = get_browserid,
            aim_table = 'pandas_features')

    return 
    df3 = aim_db.load_data(feature_list = ori_long_feature_list, table_name = "longfeatures")
    aim_db.clean_sql(long_feature_list, df3, generator = get_location_dy_ip, 
            get_device = get_device, get_browserid = get_browserid,
            aim_table = 'pandas_longfeatures')

def one_change2other_change(from_feature, to_feature, file_name):
    """
    this function will take a file which contains a list of browserids
    and two features
    return if from feature changes, the percentage of to_feature changes
    """
    db = Database('forpaper')
    df = db.load_data(feature_list = ['browserid', from_feature, to_feature], table_name = "pandas_features")
    grouped = df.groupby('browserid')
    f = open(file_name, 'r')
    content = f.readlines()
    users = [x.strip() for x in content] 
    changed_browserid = []
    for user in tqdm(users):
        cur_group = grouped.get_group(user)
        pre_from = ''
        pre_to = ''
        for idx, row in cur_group.iterrows():
            if pre_from == '':
                pre_from = row[from_feature]
                pre_to = row[to_feature]
                continue
            if row[from_feature] != pre_from and row[to_feature] != pre_to:
                changed_browserid.append(user)
                break
            pre_from = row[from_feature]
            pre_to = row[to_feature]
    return float(len(changed_browserid)) / float(len(users))

def load_list_from_file(file_name, line_type = 'normal', sep = '!@#'):
    """
    this function will load a list from a file
    the format of the file is separated by lines
    which is userd by most of my code
    """
    f = ""
    try:
        f = open(file_name, 'r')
    except:
        print ('open {} failed'.format(file_name))
        return 

    content = f.readlines()
    users = []
    if line_type == 'list':
        for cont in content:
            users.append(cont.split(sep))
    else:
        users = [x.strip() for x in content] 
    return users

def find_common(df, file_name = None, feature_list = feature_list, user_list = None):
    """
    this function will take a file as file_name which has a list of browserids
    return the common values of feature in feature list
    this function will take a file name or a user list
    if user list is None, this function will use file name
    """
    if user_list is None:
        users = load_list_from_file(file_name)
    else:
        users = user_list

    #if 'browserid' not in feature_list:
    #    feature_list.append('browserid')
    # remove the browserid value
    #feature_list.remove('browserid')
    grouped = df.groupby('browserid')
    num_users = len(users)
    res = {}
    for user in tqdm(users):
        try:
            cur_group = grouped.get_group(user)
        except:
            continue
        for feature in feature_list:
            vals = []
            if feature == 'os':
                cur_res = set()
                vals = cur_group['agent'].unique()
                for val in vals:
                    cur_res.add(get_os_from_agent(str(val)))
                vals = cur_res
            else:
                vals = cur_group[feature].unique()
            for val in vals:
                val = str(val) + '-' + feature
                if val not in res:
                    res[val] = 0
                res[val] += 1

    sorted_dict = sorted(res.iteritems(), key=lambda (k,v): (-v,k))
    res = []
    for cur in sorted_dict:
        res.append([cur[0], float(cur[1]) / float(num_users)])
    return res

def feature_flip_checking(db, feature_name):
    """
    this function will output a list of users with flipping of 
    a specific feature
    the db is a changes db
    """
    df = db.load_data(table_name = 'labelchanges')
    flip_list = []
    grouped = df.groupby('browserid')
    print ('Checking {}.'.format(feature_name))
    for key, cur_group in tqdm(grouped):
        if check_flip_changes(cur_group):
            flip_list.append(key)

    f = open('./flipusers/flip_users{}.dat'.format(feature_name), 'w')
    for user in flip_list:
        f.write(user + '\n')
    f.close()

def all_flip_checking(db, feature_list):
    """
    this function will loop the a list of feature
    generate a list of files with user
    """
    for feature in feature_list:
        df = load_data(load = True, feature_list = ["*"], 
                table_name = "{}changes".format(feature), db = db)
        feature_flip_checking(df, feature)

def find_all_common(feature_list): 
    """
    this function will take a list of features
    then output the result to the findcommon res folder
    """
    db = Database('forpaper')
    df = db.load_data(feature_list = ['*'], table_name = "pandas_features")
    for feature in feature_list:
        res = find_common(df, './flipusers/flip_users{}.dat'.format(feature), ['gpu', 'inc', 'agent', 'os', 'browser'])
        if not res:
            continue
        f = open('./findcommonres/{}.res'.format(feature), 'w')
        for val in res:
            f.write(str(val) + '\n')
        f.close()

def get_browserid(row):
    """
    this function will take a row of data
    and return the generated browserid
    this function will generate browserid based on the os
    """
    id_str = ""
    # platform is between the first ( and the first ;
    platform = ""
    parsed = user_agents.parse(row['agent'])
    os = ignore_non_ascii(parsed.os.family)
    device = ignore_non_ascii(parsed.device.family)
    browser = ignore_non_ascii(parsed.browser.family)
    full_os = '{} {}'.format(os, ignore_non_ascii(parsed.os.version_string))
    full_device = '{} {}'.format(device, ignore_non_ascii(parsed.device.brand))
    full_browser = '{} {}'.format(browser, ignore_non_ascii(parsed.browser.version_string))
    keys = ['clientid', 'cpucores']
    for key in keys:
        # we assume that all of the keys are not null
        try:
            id_str += str(row[key])
        except:
            pass

    id_str += full_os 
    id_str += full_device
    id_str += browser
    gpu_type = row['gpu'].split('Direct')[0]
    id_str += row['inc']
    id_str += gpu_type
    return id_str

def list2file(aim_list, aim_file, limit = -1, index = False, line_type = 'normal', sep = '!@#'):
    """
    this function will output a list to a file
    one item a line
    """
    f = open(aim_file, 'w')
    cnt = 0
    for item in aim_list:
        if cnt == limit:
            break
        if line_type == 'list':
            cur_line = sep.join([str(i) for i in item])
        else:
            cur_line = item
        if index:
            f.write('{} {}\n'.format(cnt, cur_line))
        else:
            f.write('{}\n'.format(cur_line))
        cnt += 1
    f.close()

def check_list_diff(list1, list2):
    """
    this function will take two lists
    the format is [[key1, val1], [key2, val2]...]
    compare the item in list1 with list2
    the item will keep the sequence of list1
    return the [item, index_diff, value_diff]
    """
    index1 = {}
    index2 = {}
    res = []
    cur_idx = 0
    # get the item index in list1
    for item in list1:
        index1[item[0]] = cur_idx 
        cur_idx += 1

    #get the item index in list2
    cur_idx = 0
    for item in list2:
        index2[item[0]] = cur_idx
        cur_idx += 1

    for item in list1:
        key = item[0]
        if key not in index2:
            res.append([key, None, None])
        else:
            index_1 = index1[key]
            index_2 = index2[key]
            index_diff = index_2 - index_1
            value_diff = list2[index_2][1] - list1[index_1][1]
            res.append([key, index_diff, value_diff])
    return res

def get_all_user_list(df):
    """
    this function will take a df
    return the user list based on this df
    """
    browserid = 'browserid'
    return df[browserid].unique()

def change_together(db, from_feature, user_list = None, to_feature_list = feature_list):
    """
    userd for analyze change together
    this function will take a user_list, a from feature and a to feature list
    return when from feature changes, the percentage of to feature list 
    also changes at the same time
    """

    df = db.load_data(feature_list = ['*'], table_name = "pandas_features")
    if user_list == None:
        user_list = get_all_user_list(df)

    grouped = df.groupby('browserid')
    all_changed_users = 0
    res = {}
    for to_feature in to_feature_list:
        changed_browserid = []
        for user in tqdm(user_list):
            cur_group = grouped.get_group(user)
            pre_from = ''
            pre_to = ''
            for idx, row in cur_group.iterrows():
                if pre_from == '':
                    pre_from = row[from_feature]
                    pre_to = row[to_feature]
                    continue
                if row[from_feature] != pre_from and row[to_feature] != pre_to:
                    changed_browserid.append(user)
                    break
                pre_from = row[from_feature]
                pre_to = row[to_feature]
        res[to_feature] = float(len(changed_browserid)) / float(len(user_list))
    return res

def load_list_from_file(file_name, line_type = 'normal', sep = '!@#'):
    """
    this function will load a list from a file
    the format of the file is separated by lines
    which is userd by most of my code
    """
    f = ""
    try:
        f = open(file_name, 'r')
    except:
        print ('open {} failed'.format(file_name))
        return 

    content = f.readlines()
    users = []
    if line_type == 'list':
        for cont in content:
            users.append(cont.split(sep))
    else:
        users = [x.strip() for x in content] 
    return users

def find_common(df, file_name = None, feature_list = feature_list, user_list = None):
    """
    this function will take a file as file_name which has a list of browserids
    return the common values of feature in feature list
    this function will take a file name or a user list
    if user list is None, this function will use file name
    """
    if user_list is None:
        users = load_list_from_file(file_name)
    else:
        users = user_list

    #if 'browserid' not in feature_list:
    #    feature_list.append('browserid')
    # remove the browserid value
    #feature_list.remove('browserid')
    grouped = df.groupby('browserid')
    num_users = len(users)
    res = {}
    for user in tqdm(users):
        try:
            cur_group = grouped.get_group(user)
        except:
            continue
        for feature in feature_list:
            vals = []
            if feature == 'os':
                cur_res = set()
                vals = cur_group['agent'].unique()
                for val in vals:
                    cur_res.add(get_os_from_agent(str(val)))
                vals = cur_res
            else:
                vals = cur_group[feature].unique()
            for val in vals:
                val = str(val) + '-' + feature
                if val not in res:
                    res[val] = 0
                res[val] += 1

    sorted_dict = sorted(res.iteritems(), key=lambda (k,v): (-v,k))
    res = []
    for cur in sorted_dict:
        res.append([cur[0], float(cur[1]) / float(num_users)])
    return res

def feature_flip_checking(db, feature_name):
    """
    this function will output a list of users with flipping of 
    a specific feature
    the db is a changes db
    """
    df = db.load_data(table_name = 'labelchanges')
    flip_list = []
    grouped = df.groupby('browserid')
    print ('Checking {}.'.format(feature_name))
    for key, cur_group in tqdm(grouped):
        if check_flip_changes(cur_group):
            flip_list.append(key)

    f = open('./flipusers/flip_users{}.dat'.format(feature_name), 'w')
    for user in flip_list:
        f.write(user + '\n')
    f.close()

def all_flip_checking(db, feature_list):
    """
    this function will loop the a list of feature
    generate a list of files with user
    """
    for feature in feature_list:
        df = load_data(load = True, feature_list = ["*"], 
                table_name = "{}changes".format(feature), db = db)
        feature_flip_checking(df, feature)

def find_all_common(feature_list): 
    """
    this function will take a list of features
    then output the result to the findcommon res folder
    """
    db = Database('forpaper')
    df = db.load_data(feature_list = ['*'], table_name = "pandas_features")
    for feature in feature_list:
        res = find_common(df, './flipusers/flip_users{}.dat'.format(feature), ['gpu', 'inc', 'agent', 'os', 'browser'])
        if not res:
            continue
        f = open('./findcommonres/{}.res'.format(feature), 'w')
        for val in res:
            f.write(str(val) + '\n')
        f.close()

def new_vs_return_by_date(db, percentage = False):
    """
    return the number of returned users and new users in each day
    the result will be written into newVsReturn
    if the percentage key is set to True
    the function will return the percentage instead of the real number
    """
    df = db.load_data(feature_list = ['browserid', 'time'], table_name = 'pandas_features')
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

    f = safeopen('./newVsReturn.dat', 'w')
    f.write('{} {}\n'.format('new-user', 'return-user'))
    for date in datelist:
        f.write('{}-{}-{} {} {}\n'.format(date.year, date.month, date.day, new_user[date], return_user[date]))
    f.close()

def feature2feature_distribution(feature1, feature2, db, percentage = True):
    """
    return how many feature1 has 1 feature2, 2 feature2 etc..
    we assume the max number is 499
    """
    df = db.load_data(feature_list = [feature1, feature2, 'os'], table_name = 'pandas_features_split')
    # we filter sth
    df = filter_df(df, 'os', filtered_list = ['iOS', 'Mac OS X'])
    grouped = df.groupby(feature1)
    # we assume the max number is 499
    res = [0 for i in range(5000)]
    total_num = df[feature1].nunique()
    for key, group in tqdm(grouped):
        cur_cnt = group[feature2].nunique()
        res[cur_cnt] += 1
        if cur_cnt > 100:
            print key, cur_cnt
    # remove the upper 0
    max_idx = -1
    for i in range(5000):
        if percentage:
            res[i] = float(res[i]) / float(total_num)
        if res[i] != 0:
            max_idx = i
    res = res[:max_idx + 1]
    return res

def rebuild_browserid():
    """
    this function will rebuild the database based on IP
    if IP and label changes in a sort time 
    split a browserid into multiple browserids
    """
    db = Database('forpaper')
    df = db.load_data(table_name = 'pandas_features')
    # after_map will store the changed dybrowserid
    after_map = set()
    grouped = df.groupby('browserid')
    for key, group in tqdm(grouped):
        pre_time = ""
        pre_label = ""
        pre_IP = ""
        for idx, row in group.iterrows():
            if pre_time == "":
                pre_time = row['time']
                pre_label = row['label']
                pre_IP = row['IP']
                continue
            if row['label'] != pre_label and row['IP'] != pre_IP:
                timedelta = row['time'] - pre_time
                # here we use 1 hour 
                if timedelta.days == 0 and timedelta.seconds < 3600:
                    after_map.add(row['label'])
            pre_time = row['time']
            pre_label = row['label']
            pre_IP = row['IP']
    print("generating dybrowserid")
    print ("{} changed browserid".format(len(after_map)))

    for idx in tqdm(df.index):
        if df.at[idx, 'label'] in after_map:
            df.at[idx, 'dybrowserid'] = df.at[idx, 'label']
        else:
            df.at[idx, 'dybrowserid'] = df.at[idx, 'browserid']

    db.export_sql(df, 'pandas_features_split')

def main():
    #rebuild_browserid()
    db = Database('forpaper')
    #all_visit, res, together_res = life_time_distribution(db, feature_name = 'label')
    res = feature2feature_distribution('dybrowserid', 'label', db)
    list2file(res, './distributions/1hr_dybrowserid_label.distribution', index = True)
    #list2file(together_res, './distributions/browserid_IPlifetimelabel.distribution', index = True)
    #list2file(all_visit, './distributions/browserid_all_visit_lifetime.distribution', index = True)
    """
    all_column_names = db.get_column_names('pandas_features')
    res = change_together(db, 'label', user_list = None, to_feature_list = all_column_names)
    for r in res:
        print '{}: {}'.format(r, res[r])
    """
    #db = Database('forpaper')
   # generate_changes_database(db)
    #df = db.load_data(feature_list = [])
    #draw_feature_number_by_date('browser', percentage = True)
    #new_vs_return_by_date(db, percentage = True)
    #find_all_common(feature_list)
    #db = Database('filteredchangesbrowserid')
    #all_flip_checking(db, feature_list)
    #lower_wrong_browserids,upper_wrong_browserid, total_number = verify_browserid_by_cookie()
    #list2file(upper_wrong_browserid, './cookiechanged.dat', line_type = 'item')
    #print ('lower: {}, upper: {}, total: {}'.format(len(lower_wrong_browserids), len(upper_wrong_browserid), total_number))
    #db = Database('forpaper')
    #generate_changes_database(db)
    #db = Database('filteredchangesbrowserid')
    #feature_flip_checking(db, 'label')
    #percentage = one_change2other_change('label', 'agent', './tmpout')
    #print percentage

    """
    db = Database('forpaper')
    df = db.load_data(feature_list = ['browserid', 'os'], table_name = "pandas_features")
    print ('filter users from {} users'.format(df['browserid'].nunique()))
    df = filter_df(df, 'os', filtered_list = ['iphone', 'ipad', 'mac'])
    print ('number of filtered users {}'.format(df['browserid'].nunique()))
    df = db.load_data(feature_list = feature_list, table_name = "pandas_features")

    #res_1 = find_common(df, file_name = './tmpout')
    #list2file(res_1, './no_apple_mul_cookie_common', limit = 1000, line_type = 'list')

    #this part is used for generate all no apple common
    users = df['browserid'].unique()
    print ('number of total users: {}'.format(len(users)))
    res_2 = find_common(df, user_list = users, file_name = None)
    list2file(res_2, './all_no_apple_common', limit = 1000, line_type = 'list')

    #this part is userd for generate flip common
    res_3 = find_common(df, file_name = './flipusers/flip_userslabel.dat')
    list2file(res_3, './flip_no_apple_common', line_type = 'list', limit = 1000)

    list_diff = check_list_diff(res_2, res_3)
    list2file(list_diff, './list_diff_allnoapple2flipnoapple', limit = 1000)

    db = Database('forpaper')
    res = change_together(db, 'label', user_list = None, to_feature_list = feature_list)
    for r in res:
        print '{}: {}'.format(r, res[r])
    """
    #for val in res:
    #    print val
    #db = Database('filteredchangesdybrowserid')
    #get_all_feature_change_by_date_paper(db)
    #feature = 'agent'
    #print 'generating {}'.format(feature)
    #df = load_data(load = True, feature_list = ["*"], 
    #        table_name = "{}changes".format(feature), db = db)
    #print ("{} users changed in total".format(df['browserid'].nunique()))
    #remove_flip_users(df)
    #db = Database('forpaper')
    #maps = generate_changes_database(db)
    #df = db.load_data(feature_list = long_feature_list, table_name = "pandas_longfeatures")
    #get_change_details('gpu', 'ANGLE (Intel(R) HD Graphics Direct3D11 vs_4_0 ps_4_0)', 'ANGLE (Intel(R) HD Graphics Direct3D9Ex vs_3_0 ps_3_0)', df)
    #generate_databases()
    #life_time_distribution_paper(db)
    #df = load_data(load = True, feature_list = ["*"], table_name = "pandas_features", db = db)
    #df = filter_less_than_n(df, 7)
    #feature_latex_table_paper(df)
    #get_all_change_details('./res/all_changes_by_date_filtered')
    #get_all_change_details('./agentflip')
    #get_browserid_change_id(df, "0093b88be8a7aadf431d8e26c85145464winGoogle Inc.ANGLE (Intel(R) HD Graphics firefox)")
    #db = Database('changes')
    #df = load_data(load = True, feature_list = ["*"], table_name = "pandas_features", db = db)
    #db = Database('changes')
    #df = load_data(load = True, feature_list = ["*"], table_name = "pandas_features", db = db, other = ' where jsFonts is not NULL and gpuimgs is not NULL')
    #df = round_time_to_day(df)
    #df = db.load_data(feature_list = feature_list, table_name = "pandas_features")
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
