import pandas as pd
import os
from pd_analyze import *
from database import Database
from extractinfo import *
import collections
long_feature_list = [
        "agent",
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
        "fp2_liedbrowser",

        "browserfingerprint"
        ]

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
        "fp2_liedbrowser",

        "browserfingerprint"
        ]

def feature_delta_paper(db):
    df = load_data(load = True, feature_list = ["*"], 
            table_name = "pandas_longfeatures", db = db)
    df = filter_less_than_n(df, 2)
    maps = {} 
    for feature in long_feature_list:
        maps[feature] = {"browserid":[], "from":[], "to":[], "fromtime":[], "totime":[]}

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
                    maps[feature]["from"].append(pre_row[feature])
                    maps[feature]['to'].append(row[feature])
                    maps[feature]['fromtime'].append(pre_row['time'])
                    maps[feature]['totime'].append(row['time'])
            pre_row = row

    db = Database('changes')
    for feature in long_feature_list:
        print feature
        try:
            df = pd.DataFrame.from_dict(maps[feature])
            db.export_sql(df, '{}changes'.format(feature))
            print 'success'
        except:
            print len(maps[feature]['from']), len(maps[feature]['to']), len(maps[feature]['fromtime']), len(maps[feature]['totime'])
    return maps

def feature_change_by_date_paper(feature_name, df):
    #df = load_data(load = True, feature_list = ["*"], table_name = "pandas_features", db = db)
    try:
        min_date = min(df['fromtime'])
    except:
        return 
    min_date = min_date.replace(microsecond = 0, second = 0, minute = 0, hour = 0)
    max_date = max(df['totime'])
    lendate = (max_date - min_date).days
    grouped = df.groupby(['from', 'to'])
    sorted_group = collections.OrderedDict(grouped.size().sort_values(ascending=False))
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
        try:
            print group, get_change_strs(group[0], group[1], sep=sep), sorted_group[group]
        except:
            pass
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
def check_flipping(df, feature, key_words, sep = ' '):
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
    for feature in feature_list:
        print 'generating {}'.format(feature)
        df = load_data(load = True, feature_list = ["*"], 
                table_name = "{}changes".format(feature), db = db)
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

def get_browserid_change(df, file_name):
    f = open(file_name, 'r')
    content = f.readlines()
    users = [x.strip() for x in content] 
    for user in users:
        get_browserid_change_id(df, user)

def get_browserid_change_id(df, browserid):
    print browserid
    try:
        f = open('./specialusers/{}'.format(browserid), 'w')
    except:
        return
    aim_df = df[df['browserid'] == browserid]
    aim_df = aim_df.reset_index(drop = True)
    pre_row = {}
    sep = ' '
    for idx in tqdm(aim_df.index):
        sep = ' '
        row = aim_df.iloc[idx]
        if len(pre_row) == 0:
            pre_row = row
            continue
        if row['browserfingerprint'] != pre_row['browserfingerprint']:
            for feature in feature_list:
                if row[feature] != pre_row[feature]:
                    sep = get_sep(feature)
                    if feature == 'agent':
                        print ('{} {}\n'.format(pre_row[feature], row[feature]))
                    f.write('{} {}\n'.format(feature, get_change_strs(pre_row[feature], row[feature], sep = sep)))
            f.write('====================================\n')
        pre_row = row
    f.close()

# input the feature name, two different feature value
# return the basic info of these features
def check_diff_feature_value(db, feature, from_val, to_val):
    df = load_data(load = True, feature_list = ["*"], table_name = "pandas_features", db = db)
    grouped = df.groupby('browserid')
    browserid_list = []
    for key, cur_group in tqdm(grouped):
        if from_val in cur_group[feature] and to_val in cur_group[feature]:
            browserid_list.append(key)
    return browserid_list


def draw_feature_change_by_date(db):
    df = load_data(load = True, feature_list = ["*"], table_name = "pandas_features", db = db)

def round_time_to_day(df):
    # round time to days
    for idx in tqdm(df.index):
        df.at[idx, 'time'] = df.at[idx, 'time'].replace(microsecond = 0, second = 0, minute = 0, hour = 0)
    return df


def main():
    #db = Database('uniquemachine')
    db = Database('changes')
    get_all_feature_change_by_date_paper(db)
    #maps = feature_delta_paper(db)
    #df = load_data(load = True, feature_list = ["*"], table_name = "pandas_features", db = db)
    #get_browserid_change_id(df, "f4ce016af1e96e71ddcd0bde3f78869f2iPhoneImagination TechnologiesPowerVR SGX 543safari")
    #db = Database('changes')
    #browserid_list = check_diff_feature_value(db, 'canvastest', '0b8855214c07f309dcdab1540352acab9fe6212a', '5bf70d8119b0953b10bef0fa2fdd62c33f92a971')
    #for browserid in browserid_list:
    #    print browserid
    #df = load_data(load = True, feature_list = ["*"], table_name = "pandas_features", db = db, other = ' where jsFonts is not NULL and gpuimgs is not NULL')
    #df = round_time_to_day(df)
    #for feature in feature_list:
    #    feature_by_date_paper(feature, df)
    #check_browser_become_unique(db)
    #num_fingerprints_distribution(db)
    #df = load_data(load = True, feature_list = ["*"], table_name = "pandas_features", db = db)
    #get_browserid_change(df,'./res/num_bf_distribution')
    #check_browser_become_unique(db)
    #change_to_unique, change_feature = check_browser_become_unique(db)
    #df = load_data(load = True, feature_list = ["*"], table_name = "pandas_longfeatures", db = db)
    #db = Database('changes')



if __name__ == "__main__":
    main()
