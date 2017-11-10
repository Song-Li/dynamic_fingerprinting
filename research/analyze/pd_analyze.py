import pandas as pd
import datetime
from database import Database


def featureDiff(f1, f2):
    return f1 != f2 and 'None' not in str(f1) and 'None' not in str(f2) 

db = Database('uniquemachine')
df = pd.read_sql('select * from features;', con=db.get_db())    
print ("data loaded")

cookies = df.groupby('label')
feature_names = list(df.columns.values)

# print a 2D table
def printTable(table):
    head = [' '] + feature_names
    print ' '.join(['{:<5.5}'.format(name) for name in head])
    for k in feature_names:
        if k not in table:
            continue
        print '{:<5.5} '.format(k) + ' '.join(['{:<5.5}'.format(str(table[k][k2])) for k2 in feature_names])

# get the both-change number of features
def relation(cookies):
    numbers = {}
    total = 0
    more_than_2 = 0
    stop = False 
    res_table = {}
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
                more_than_2 += 1
                for k in feature_names:
                    if not featureDiff(min_row[k], max_row[k]):
                        continue
                    if k not in numbers:
                        numbers[k] = {} 
                    for k2 in feature_names:
                        if k2 not in numbers[k]:
                            numbers[k][k2] = 0
                        if featureDiff(min_row[k2], max_row[k2]):
                            numbers[k][k2] += 1
    return numbers

# get how many users have unique fingerprints
def diff_diff(cookies):
    total = 0
    num_users = len(cookies)
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
        for fingerprint in fingerprints:
            if big_fingerprint_set[fingerprint] == 1:
                total += 1
                break

    print ("We have {} fingerprintable users in total".format(total))
    return total


# numbers = relation(cookies)
numbers = diff_diff(cookies)
# printTable(numbers)
