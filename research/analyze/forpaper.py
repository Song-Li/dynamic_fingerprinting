import pandas as pd
from pd_analyze import *
from database import Database
from extractinfo import *
import collections
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
            table_name = "pandas_features", db = db)
    df = filter_less_than_n(df, 7)
    maps = {} 
    for feature in feature_list:
        maps[feature] = {"from":[], "to":[], "fromtime":[], "totime":[]}

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
            for feature in feature_list:
                if feature not in row:
                    continue
                if pre_row[feature] != row[feature]:
                    maps[feature]["from"].append(pre_row[feature])
                    maps[feature]['to'].append(row[feature])
                    maps[feature]['fromtime'].append(pre_row['time'])
                    maps[feature]['totime'].append(row['time'])

    db = Database('changes')
    for feature in feature_list:
        df = pd.DataFrame.from_dict(maps[feature])
        db.export_sql(df, '{}changes'.format(feature))
    return maps

def feature_change_by_date_paper(feature_name, df):
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
        ret = get_browser_version(agent)
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

def feature_by_date_paper(feature, df):
    maps = {}
    browser_options = ['chrome', 'firefox', 'safari']
    print "round time to days"
    for idx in tqdm(df.index):
        df.at[idx, 'time'] = df.at[idx, 'time'].replace(microsecond = 0, second = 0, minute = 0, hour = 0)
    df = df.drop_duplicates(subset = ['agent', 'time', 'browserid'])
    
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
            for browser in browser_options:
                if browser_version.lower().find(browser) != -1:
                    if browser_version not in browser_version_all[browser]:
                        browser_version_all[browser][browser_version] =0
                    browser_version_all[browser][browser_version] += 1

            date = row['time']
            if browser_version not in maps[date]:
                maps[date][browser_version] = 0
            maps[date][browser_version] += 1

    #sort browser versions
    for browser in browser_version_all:
        browser_version_all[browser] = sorted(browser_version_all[browser].iteritems(), key=lambda (k,v): (-v,k))
        for date in maps:
            for browser_version, value in browser_version_all[browser]:
                if browser_version not in maps[date]:
                    maps[date][browser_version] = 0

    f = {}
    f['chrome'] = open('./dat/chrome.dat','w')
    f['firefox'] = open('./dat/firefox.dat','w')
    f['safari'] = open('./dat/safari.dat','w')

    # write titles
    for browser in f:
        for browser_version, value in browser_version_all[browser]:
            f[browser].write('{} '.format(browser_version.replace(' ', '_')))
        f[browser].write('\n')

    for date in datelist:
        for browser in browser_options:
            f[browser].write('{}-{}-{} '.format(date.year, date.month, date.day))
            for browser_version, cnt in browser_version_all[browser]:
                f[browser].write('{} '.format(maps[date][browser_version]))
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

def check_browser_become_unique(db):
    df = load_data(load = True, feature_list = ["*"], 
            table_name = "pandas_features", db = db, limit = 10000)
    unique_list = get_unique_fingerprint_list(df)
    ret = {}
    change_feature = {feature: 0 for feature in feature_list}
    grouped = df.groupby('browserid')
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
                            change_feature[feature] += 1
                pre_row = row
    print change_feature
    for uniquefp in ret:
        print uniquefp, ret[uniquefp]
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


def main():
    db = Database('changes')
    #maps = feature_delta_paper(db)
    #change_to_unique, change_feature = check_browser_become_unique(db)
    get_all_feature_change_by_date_paper(db)
    #df = load_data(load = True, feature_list = ["*"], table_name = "pandas_longfeatures", db = db)
    #feature_by_date_paper('agent', df)
    #db = Database('changes')



if __name__ == "__main__":
    main()
