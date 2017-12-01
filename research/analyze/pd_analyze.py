import pandas as pd
import re
import json
from urllib2 import urlopen

import datetime
from database import Database
import matplotlib.pyplot as plt
import numpy as np
from latex import build_pdf
import os
import bisect

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
        "gpuimgs", 
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
        "doNotTrack",
        "fp2_colordepth", 
        "fp2_sessionstorage",
        "fp2_indexdb",
        "fp2_addbehavior",
        "fp2_opendatabase",
        "fp2_cpuclass",
        "fp2_pixelratio",
        "fp2_platform",
        "fp2_liedlanguages",
        "fp2_liedresolution",
        "fp2_liedos",
        "fp2_liedbrowser",
        "fp2_webgl",
        "fp2_webglvendoe",
        "ipcity",
        "ipregion",
        "ipcountry"
        ]
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
def get_every_change(cookies, pic_name):
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
        if k!='ccaudio' and k!='hybridaudio':
            feature.append(k)
            num_change.append(cnt[k])
    ind = np.arange(len(feature))
    plt.bar(ind, num_change, 0.5)
    plt.xticks(ind, feature, rotation=90, ha='center')
    plt.savefig('./report/' + pic_name + '.png')
    plt.clf()
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
def basic_numbers(cookies):
    total = 0
    num_users = len(cookies)
    only_one = 0
    big_fingerprint_set = {}
    for key, items in cookies:
        num_exsit = 0
        # how many fingerprints we have
        fingerprints = set(items['browserfingerprint'])
        for fingerprint in fingerprints:
            if fingerprint not in big_fingerprint_set:
                big_fingerprint_set[fingerprint] = 0 
            big_fingerprint_set[fingerprint] += 1

    res = []
    res.append("We have {} fingerprints in total".format(len(big_fingerprint_set)))
    res.append("We have {} users in total".format(num_users))

    for key, items in cookies:
        fingerprints = set(items['browserfingerprint'])
        if len(fingerprints) == 1:
            only_one += 1
        for fingerprint in fingerprints:
            if big_fingerprint_set[fingerprint] == 1:
                total += 1
                break


    res.append("We have {} fingerprintable users in total ({:.2f}\\%)".format(total, 100 * float(total) / float(num_users)))
    res.append("We have {} users only have one fingerprint ".format(only_one))
    return res

# get how many clientid have just one cookie
def num_of_same_cookie(clientid):
    total = 0
    for key, items in clientid:
        if items['label'].nunique() == 1:
            total += 1
        else:
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


def num_of_users_per_fingerprint(cookies, base):
    num = []
    count = 20
    num_of_fingerprint = [0 for i in range(count + 1)]
    user_set = [set() for i in range(count + 1)]
    for key, items in cookies:
        fingerprints = items[base].nunique()
        if fingerprints <= count:
            num_of_fingerprint[fingerprints] += 1
            for i in range(fingerprints, count + 1):
                for item in items[base]:
                    # make sure have more than 1 items
                    user_set[i].add(item)

    return num_of_fingerprint, user_set


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
    return res

def get_latex_items(items):
    head = r"\begin{itemize}"
    body = ""
    for item in items:
        body += r'\item {}'.format(item)

    tail = r'\end{itemize}'
    return head + body + tail 

def get_latex_section(body, title):
    head = '\\section{' + title + '}\n'
    return head + body


def get_latex_subsection(body, title):
    head = '\\subsection{' + title + '}\n'
    return head + body


def get_latex_doc(body):
    with open('./report/base.tex', 'r') as base:
        out_lines = []
        for line in base.readlines():
            out_lines.append(line.replace('qwerbodyqwer', body))

    with open('./report/report.tex', 'w') as output:
        for line in out_lines:
            output.write(line)

    os.system("cd ./report && pdflatex -synctex=1 -interaction=nonstopmode \"report\".tex")
    
def get_latex_pic(path):
    head = r"\begin{figure}[H]"
    head += r'\centering'
    body = r'\includegraphics[width=75mm,scale=0.5]{' + path + '}'
    #body += r'\caption{How many users changed in days}'
    tail = r'\end{figure}'
    return head + body + tail

def get_group_section(client, title, sql_key):
    # get the basic numbers of a group
    basic = basic_numbers(client)
    basic = get_latex_items(basic)
    basic_sub = get_latex_subsection(basic, 'Basic Numbers')
    print ('basic numbers generated')

    # fingerprint change in days subsection
    # change_time = fingerprint_change_time(client)
    change_time = [1163, 25580, 25858, 26040, 26085, 26120, 26120, 26120, 26120, 26120]
    plt.plot(change_time)
    pic_name = '{}changebytime'.format(title.replace(' ', ''))
    plt.savefig('./report/' + pic_name + '.png')
    plt.clf()
    pic_latex = get_latex_pic(pic_name)
    change_by_time_sub = get_latex_subsection(pic_latex, "How many users changed in days")
    print ('number of users changed generated')


    # generate the feature change
    pic_name = '{}featurechange'.format(title.replace(' ',''))
    get_every_change(client, pic_name) 
    pic_latex = get_latex_pic(pic_name)
    feature_change_sub = get_latex_subsection(pic_latex, "How many changes for every feature")
    print ('feature changes generated')

    # generate how many fingerprints have multiple users
    fingerprints = df.groupby('browserfingerprint')
    changes, less_than_n = num_of_users_per_fingerprint(fingerprints, sql_key)
    pic_name = '{}numberofusersfingerprint'.format(title.replace(' ',''))
    ind = np.arange(len(changes))
    plt.bar(ind, changes, 0.5)
    plt.xticks(ind, [i for i in range(len(changes))], ha='center')
    plt.savefig('./report/' + pic_name + '.png')
    plt.clf()
    pic_latex = get_latex_pic(pic_name)
    number_of_users_fingerprint = get_latex_subsection(pic_latex, "How many fingerprints have multiple users")

    tolerance = [float(len(t)) / float(len(client)) * 100 for t in less_than_n]
    pic_name = '{}tolerance'.format(title.replace(' ',''))
    ind = np.arange(len(tolerance))
    plt.bar(ind, tolerance, 0.5)
    plt.xticks(ind, [i for i in range(len(tolerance))], ha='center')
    plt.savefig('./report/' + pic_name + '.png')
    plt.clf()
    pic_latex = get_latex_pic(pic_name)
    tolerance_sub = get_latex_subsection(pic_latex, "The percentage of tolerance")
    tolerance_sub += str(tolerance)


    section = get_latex_section(
            basic_sub + 
            change_by_time_sub + 
            feature_change_sub + 
            number_of_users_fingerprint + 
            tolerance_sub, 
            'Based On {}'.format(title))

    return section

# take in the grouped database
def get_all(clientid, cookies):
    clientid_section = get_group_section(clientid, "Based on Client ID", 'clientid')
    cookies_section = get_group_section(cookies, "Based on Cookie", 'label')
    get_latex_doc(clientid_section + cookies_section)


ip2location = pd.read_sql('select * from ip2location_db5;', con=db.get_db())    
print ("ip2location data loaded")
def ip2int(ip):
    o = map(int, ip.split('.'))
    res = (16777216 * o[0]) + (65536 * o[1]) + (256 * o[2]) + o[3]
    return res

# try to use the ip location
def get_location_dy_ip(ip):
    int_ip = ip2int(ip)
    ip_from = ip2location['ip_from']
    idx = bisect.bisect_left(ip_from, int_ip) - 1
    city = ip2location.iloc[idx]['city_name']
    region = ip2location.iloc[idx]['region_name']
    country = ip2location.iloc[idx]['country_name']
    return [city, region, country]

# clean the sql regenerate the fingerprint
# without the gpuimgs, ccaudio and hybridaudio
print ("start clean")
db.clean_sql(counted_features, generator = get_location_dy_ip)
print ("clean finished")
df = pd.read_sql('select * from features;', con=db.get_db())    
print ("data loaded")

cookies = df.groupby('label')
feature_names = list(df.columns.values)

df = df[pd.notnull(df['clientid'])]
clientid = df.groupby('clientid')
get_all(clientid, cookies)
