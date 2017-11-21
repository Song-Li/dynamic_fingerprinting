import pandas as pd
import datetime
from database import Database
import matplotlib.pyplot as plt
import numpy as np

def featureDiff(f1, f2):
    return f1 != f2 and 'None' not in str(f1) and 'None' not in str(f2) and pd.notnull(f1) and pd.notnull(f2) 



def featureDiff(f1, f2):
    return f1 != f2 and 'None' not in str(f1) and 'None' not in str(f2) 

db = Database('uniquemachine')
counted_features = [ 
        "agent",
        "accept",
        "encoding",
        "language",
        "langsdetected",
        "resolution",
        "jsFonts",
        "WebGL", 
        "inc", 
        "gpu", 
#        "gpuimgs", 
        "timezone", 
        "plugins", 
        "cookie", 
        "localstorage", 
        "adblock", 
        "cpucores", 
        "canvastest", 
        "audio",
#        "ccaudio",
#        "hybridaudio",
        "touchSupport",
        "doNotTrack"
        ]
# clean the sql regenerate the fingerprint
# without the gpuimgs, ccaudio and hybridaudio
print ("start clean")
db.clean_sql(counted_features)
print ("clean finished")
df = pd.read_sql('select * from features;', con=db.get_db())    
print ("data loaded")

cookies = df.groupby('label')
feature_names = list(df.columns.values)
def printTable(table):
    head = [' '] + feature_names
    print ' '.join(['{:<5.5}'.format(name) for name in head])
    for k in feature_names:
        if k not in table:
            continue
        print '{:<5.5} '.format(k) + ' '.join(['{:<5.5}'.format(str(table[k][k2])) for k2 in feature_names])

def get_change(cookies):
    total = 0
    cnt = {}
    only_one = 0
    for key, items in cookies:
        if items['browserfingerprint'].nunique() > 1:
            total += 1
            min_time = datetime.datetime.now()
            max_time = datetime.datetime.now() - datetime.timedelta(days = 10000)
            for index, row in items.iterrows():
                if min_time > row['time']:
                    min_time = row['time']
                    min_row = row
                if max_time < row['time']:
                    max_time = row['time']
                    max_row = row
            if max_time - min_time > datetime.timedelta(days = 0):
                for k in counted_features:
                    if featureDiff(min_row[k], max_row[k]):
                        if k not in cnt:
                            cnt[k] = 0
                        cnt[k] += 1
                        for k2 in counted_features:
                            if k == k2:
                                continue
                            # here we want to get the single change of every feature
                            if featureDiff(min_row[k2], max_row[k2]):
                                cnt[k] -= 1
                                break

    for k in cnt:
        print (k, cnt[k])
    return cnt

# get total change of specific features
def get_every_change(cookies):
    total = 0
    cnt = {}
    only_one = 0
    for key, items in cookies:
        if items['browserfingerprint'].nunique() > 1:
            total += 1
            min_time = datetime.datetime.now()
            max_time = datetime.datetime.now() - datetime.timedelta(days = 10000)
            for index, row in items.iterrows():
                if min_time > row['time']:
                    min_time = row['time']
                    min_row = row
                if max_time < row['time']:
                    max_time = row['time']
                    max_row = row
            if max_time - min_time > datetime.timedelta(days = 0):
                for k in counted_features:
                    if featureDiff(min_row[k], max_row[k]):
                        if k not in cnt:
                            cnt[k] = 0
                        cnt[k] += 1
    feature = []
    num_change = []
    for k in cnt:
        print (k, cnt[k])
        if k!='ccaudio' and k!='hybridaudio' and k!='gpuimgs':
            feature.append(k)
            num_change.append(cnt[k])
    ind = np.arange(len(feature))
    plt.bar(ind, num_change, 0.5)
    plt.xticks(ind, feature, rotation=40, ha='center')
    plt.show()
    return cnt
 

# get the both-change number of features
def relation(cookies):
    numbers = {}
    # total = 0
    # more_than_2 = 0
    # stop = False 
    # res_table = {}
    for key, items in cookies:
        if items['browserfingerprint'].nunique() > 1:
            # total += 1
            min_time = datetime.datetime.now()
            max_time = datetime.datetime.now() - datetime.timedelta(days = 10000)
            for index, row in items.iterrows():
                if min_time > row['time']:
                    min_time = row['time']
                    min_row = row
                if max_time < row['time']:
                    max_time = row['time']
                    max_row = row
            if max_time - min_time > datetime.timedelta(days = 0):
                # more_than_2 += 1
                for k in counted_features:
                    if not featureDiff(min_row[k], max_row[k]):
                        continue
                    if k not in numbers:
                        numbers[k] = {} 
                    for k2 in counted_features:
                        if k2 not in numbers[k]:
                            numbers[k][k2] = 0
                        if featureDiff(min_row[k2], max_row[k2]):
                            numbers[k][k2] += 1
    for k in numbers:
        print(k, numbers[k])
    return numbers

# get how many users have unique fingerprints
def diff_diff(cookies):
    total = 0
    num_users = len(cookies)
    only_one = 0
    print ("We have {} users in total".format(num_users))
    big_fingerprint_set = {}
    for key, items in cookies:
        num_exsit = 0
        # how many fingerprints we have
        fingerprints = set(items['browserfingerprint'])
        for fingerprint in fingerprints:
            if fingerprint not in big_fingerprint_set:
                big_fingerprint_set[fingerprint] = 0 
            big_fingerprint_set[fingerprint] += 1

    print ("We have {} fingerprints in total".format(len(big_fingerprint_set)))

    for key, items in cookies:
        fingerprints = set(items['browserfingerprint'])
        if len(fingerprints) == 1:
            only_one += 1
        for fingerprint in fingerprints:
            if big_fingerprint_set[fingerprint] == 1:
                total += 1
                break

    print ("We have {} fingerprintable users in total".format(total))
    print ("We have {} users in only have one fingerprint ".format(only_one))
    return total

# get how many clientid have just one cookie
def num_of_same_cookie(clientid):
    total = 0
    for key, items in clientid:
        if items['label'].nunique() == 1:
            total += 1
        else:
            # print (items['id'])
            pass
    print ("We have {} clientids in total".format(len(clientid)))
    print ("{} of them is const. {:.2f}%".format(total, float(total) / float(len(clientid)) * 100))
    return total

# get the percentage of NULL of every feature
def num_of_null(df):
    total = 0
    res = {}
    for index, row in df.iterrows():
        for feature in feature_names:
            if pd.isnull(row[feature]) or (row[feature] == 'None'):
                if feature not in res:
                    res[feature] = 0
                res[feature] += 1
    for feature in res:
        print feature, res[feature] 



# get how many users have only one browser fingerprint
def num_of_same_fingerprint(cookies):
    total = 0
    for key, items in cookies:
        if items['browserfingerprint'].nunique() == 1:
            total += 1
    print ("{} users have only one fingerprints".format(total))
    return total


def max_num_of_fingerprint(cookies):
    num = []
    num_of_fingerprint = {}
    for key, items in cookies:
        fingerprints = items['label'].nunique()
        num.append(fingerprints)
        if fingerprints not in num_of_fingerprint:
            num_of_fingerprint[fingerprints] = 0
        num_of_fingerprint[fingerprints] += 1
    for k in num_of_fingerprint:
        print (k, num_of_fingerprint[k])
    for i in range(0,10):
        print max(num)
        num.remove(max(num))
    return num_of_fingerprint


def feature_null (finger):
    null_val = {}
    for key, items in finger:
        if items['label'].nunique() == 3:
            cookie = []
            for i, row in items.iterrows():
                cookie.append(row)
            for k in counted_features:
                if k not in null_val:
                    null_val[k] = 0
                if 'None' in str(cookie[0][k]) or pd.isnull(cookie[0][k]):
                    null_val[k] += 1
    for k in null_val:
        print (k, null_val[k])
    return 

def no_null_feature (finger):
    count = {}
    for key, items in finger:
        if items['label'].nunique() > 1:
            if items['label'].nunique() not in count:
                count[items['label'].nunique()] = 0
            count[items['label'].nunique()] += 1
            for i, r in items.iterrows():
                row = r
                break
            for k in counted_features:
                if 'None' in str(row[k]) or pd.isnull(row[k]):
                    count[items['label'].nunique()] -= 1
                    break
    # result = 0
    # for key, items in finger:
    #     if items['label'].nunique() == 110:
    #         result = 1
    #         for i, r in items.iterrows():
    #             row = r
    #             break
    #         for k in counted_features:
    #             if 'None' in str(row[k]) or pd.isnull(row[k]):
    #                 result = 0
    #                 break
    #         if result == 1:
    #             print key
    for k in count:
        print (k, count[k])
    return


def fingerprint_change_time (cookies):
    days = 10
    res = [0 for i in range(days)]
    for key, items in cookies:
        if items['browserfingerprint'].nunique() > 1:
            for d in range(days):
                min_time = datetime.datetime.now()
                max_time = datetime.datetime.now() - datetime.timedelta(days = 10000)
                for index, row in items.iterrows():
                    if min_time > row['time']:
                        min_time = row['time']
                        min_row = row
                    if max_time < row['time'] and max_time - min_time < datetime.timedelta(days = d):
                        max_time = row['time']
                        max_row = row
                    else:
                        break
                if featureDiff(max_row['browserfingerprint'], min_row['browserfingerprint']):
                    res[d] += 1
    print res
    return res




# numbers = relation(cookies)
# get all records with clientid
# bsed on clientid here
# num_of_null(df)
df = df[pd.notnull(df['clientid'])]
clientid = df.groupby('clientid')
finger = df.groupby('browserfingerprint')
numbers = fingerprint_change_time(cookies)
#numbers = diff_diff(cookies)
#numbers = get_change(cookies)
#numbers = get_every_change(cookies)
#numbers = get_change(clientid)
#numbers = num_of_same_cookie(clientid)
#num_of_same_fingerprint(cookies)
#numbers = relation(cookies)
#feature_null(finger)
#no_null_feature(finger)
# printTable(numbers)
