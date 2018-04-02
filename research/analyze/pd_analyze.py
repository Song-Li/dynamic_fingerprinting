import pandas as pd
from datetime_truncate import truncate
import operator
import collections
from tqdm import *
from math import sin, cos, sqrt, atan2, radians
import re
from extractinfo import *
import json
from urllib2 import urlopen
import datetime
from database import Database
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import os
import bisect

global df

def featureDiff(f1, f2):
    return f1 != f2 and 'None' not in str(f1) and 'None' not in str(f2) and pd.notnull(f1) and pd.notnull(f2) 

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
    num_users_changed = 0 
    for key, items in cookies:
        if items['browserfingerprint'].nunique() > 1:
            num_users_changed += 1
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
    res.append("We have {} users changed their fingerprint({}%)".format(num_users_changed, 
        float(num_users_changed) / float(num_users) * 100))

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

# input a list of data
# output the latexified list
def get_latex_table(table, title):
    head = r"\begin{table}[h!]"
    head += r"\centering\captionof{table}"
    body = r"{" + title + r"}{\begin{tabular}{"
    for i in range(len(table[0])):
        body += "c "
    body += r"}\hline"
    head_line = True
    for line in table:
        body += '&'.join(line) 
        body += r'\\'
        if head_line:
            body += r'\hline'
            head_line = False
    tail = r'\hline\end{tabular}}\end{table}'
    return head + body + tail


def get_basic_numbers(client):
    # get the basic numbers of a group
    basic = basic_numbers(client)
    basic = get_latex_items(basic)
    basic_sub = get_latex_subsection(basic, 'Basic Numbers')
    print ('basic numbers generated')
    return basic_sub

def get_num_cookies_distribution(client, title):
    # generate the number of cookies distribution
    distribution = num_feature_distribution(client, 'label')
    pic_name = '{}cookiedis'.format(title.replace(' ',''))
    draw_bar(distribution, pic_name = pic_name) 
    #draw_line(distribution, pic_name = pic_name)
    pic_latex = get_latex_pic(pic_name)
    distribution_sub = get_latex_subsection(pic_latex, "The distribution of cookie")
    distribution_sub += str(distribution)
    print ("cookie distribution generated")
    return distribution_sub


def get_fingerprint_change(client, title):
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
    return change_by_time_sub


def get_feature_change(client, title):
    # generate the feature change
    pic_name = '{}featurechange'.format(title.replace(' ',''))
    get_every_change(client, pic_name) 
    pic_latex = get_latex_pic(pic_name)
    feature_change_sub = get_latex_subsection(pic_latex, "How many changes for every feature")
    print ('feature changes generated')
    return feature_change_sub


def get_num_of_users_per_fingerprint(client, title, sql_key):
    global df
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
    num_of_users = get_latex_subsection(pic_latex, "How many fingerprints have multiple users")
    print ("how many fingerprints have multiple users generated")
    return num_of_users, less_than_n


def get_tolerance(client, title, less_than_n):
    # generate the accuracy if we can tolerant
    # a number of users share the same fingerprint
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
    print ("tolerance table generated")
    print 'tolerance:', tolerance
    return tolerance_sub

def get_num_device_distribution(title):
    pic_name = '{}numdevice'.format(title.replace(' ',''))
    distribution = num_device_distribution(pic_name) 
    draw_bar(distribution, pic_name = pic_name) 
    pic_latex = get_latex_pic(pic_name)
    device_distribution = get_latex_subsection(pic_latex, "Number of device distribution")
    device_distribution += str(distribution)
    print ('number of device generated')
    return device_distribution 
    

def get_agent_change_distribution(client, title):
    print ("start generating agent change")
    cnts = [0 for i in range(6)]
    for key, items in tqdm(client):
        if items['agent'].nunique() > 1:
            client_group = items.groupby('agent')
            pre = ""
            for agent, data in client_group:
                if pre == "":
                    pre = agent
                    continue
                browser_change, os_change = get_agent_change(pre, agent) 
                pre = agent

                if browser_change == 0 and os_change == 3:
                # nothing changed
                    cnts[0] += 1
                elif browser_change != 0 and os_change != 3:
                # both changed
                    cnts[3] += 1
                else:
                    cnts[browser_change] += 1
                    cnts[os_change] += 1 

    res = cnts 
    draw_labels = [
            "nothing\n changed",
            "browser",
            "browser\n version",
            "both\n changed",
            "os",
            "os version"
            ]
    pic_name = '{}agentdis'.format(title.replace(' ', ""))
    draw_bar(res, keys = draw_labels, pic_name = pic_name)
    pic_latex = get_latex_pic(pic_name)
    agent_change = get_latex_subsection(pic_latex, "Agent change")
    agent_change += str(res)
    print ('agent change generated')
    return agent_change



def get_group_section(client, title, sql_key):
    agent_change_sub = get_agent_change_distribution(client, title)
    num_device_dis_sub = get_num_device_distribution(title) 
    location_change_sub = get_location_change(client, title)
    basic_sub = get_basic_numbers(client)
    num_of_users, less_than_n = get_num_of_users_per_fingerprint(client, title, sql_key)
    distribution_sub = get_num_cookies_distribution(client, title)
    change_by_time_sub = get_fingerprint_change(client, title)
    feature_change_sub = get_feature_change(client, title)
    tolerance_sub = get_tolerance(client, title, less_than_n)
    # generate the moving distance distributaion of people
    #location_change = get_location_change(client, title)

    section = get_latex_section(
            basic_sub + 
            change_by_time_sub + 
            feature_change_sub + 
            num_of_users +
            tolerance_sub + 
            location_change_sub + 
            num_device_dis_sub + 
            agent_change_sub +
            distribution_sub, 
            'Based On {}'.format(title))

    return section

# take in the grouped database
def get_all(clientid):
    clientid_section = get_group_section(clientid, "Based on Client ID", 'clientid')
    # cookies_section = get_group_section(cookies, "Based on Cookie", 'label')
    get_latex_doc(clientid_section) # + cookies_section)



def ip2int(ip):
    o = map(int, ip.split('.'))
    res = (16777216 * o[0]) + (65536 * o[1]) + (256 * o[2]) + o[3]
    return res


def get_device(row):
    id_str = ""
    # platform is between the first ( and the first ;
    platform = ""
    try:
        platform = row['agent'].split(')')[0].split('(')[1].split(';')[0]
    except:
        pass

    #print ("error getting platform: ", row['agent'])
    keys = ['clientid', 'cpucores', 'fp2_platform']
    for key in keys:
        # we assume that all of the keys are not null
        try:
            id_str += str(row[key])
        except:
            pass

    #id_str += platform
    #gpu_type = row['gpu'].split('Direct')[0]
    #id_str += gpu_type
    return id_str

def get_browserid(row):
    id_str = ""
    # platform is between the first ( and the first ;
    platform = ""
    platform = get_os_from_agent(row['agent'])

    #print ("error getting platform: ", row['agent'])
    keys = ['clientid', 'cpucores', 'fp2_platform']
    for key in keys:
        # we assume that all of the keys are not null
        try:
            id_str += str(row[key])
        except:
            pass

    id_str += platform
    gpu_type = row['gpu'].split('Direct')[0]
    id_str += row['inc']
    id_str += gpu_type
    return id_str
    


def load_data(load = True, db = None, file_path = None, table_name = "features", 
        feature_list = ['*'], limit = -1, other = ""):
# clean the sql regenerate the fingerprint
# without the gpuimgs, ccaudio and hybridaudio
    small_features = [ 
        "fp2_colordepth",
        "fp2_addbehavior",
        "fp2_opendatabase",
        "fp2_cpuclass",
        "fp2_liedlanguages",
        "fp2_liedresolution",
        "fp2_liedos",
        "fp2_pixelratio",
        "fp2_liedbrowser"
        "agent",
        "accept",
        "encoding",
        "language",
        "langsdetected",
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
        "ipcity",
        "ipregion",
        "ipcountry"
        ]

    global ip2location
    df = None
    if load == True:
        #df = pd.read_sql('select * from pandas_longfeatures;', con=db.get_db())    
        #used for combine databases
        feature_str = ""
        for feature in feature_list:
            feature_str += feature + ','
        # remove the last ,
        feature_str = feature_str[:-1]
        if limit == -1:
            limit_str = ""
        else:
            limit_str = ' limit {}'.format(limit)
        #df = pd.read_sql('select {} from {} where jsFonts is not NULL and clientid <> "Not Set" {};'.format(feature_str, table_name, limit_str), con=db.get_db())    
        df = pd.read_sql('select {} from {} {} {};'.format(feature_str, table_name, other ,limit_str), con=db.get_db())    
        print ("data loaded")
    else:
        ip2location = pd.read_sql('select * from ip2location_db5;', con=db.get_db())    
        print ("ip2location data loaded")
        df = pd.read_sql('select * from {} where jsFonts is not NULL and clientid is not "Not Set" {};'.format(table_name, other),
                con=db.get_db())    
        print ("data loaded")
        # delete the null clientid rows
        df = df[pd.notnull(df['clientid'])]
        print ("start clean")
        db.clean_sql(small_features, df, generator = get_location_dy_ip, 
                get_device = get_device, get_browserid = get_browserid,
                aim_table = 'pandas_longfeatures')
        #db.generate_browserid(small_features, df, get_device = get_device, get_browserid = get_browserid)
        print ("clean finished")
    return df

# output the detiled difference of a feature
def output_diff(client, feature_name, output_number):
    #if feature_name not in counted_features:
    #    print ("Wrong feature name {}".format(feature_name))
    #    return

    cnt = 1 
    for key, items in client:
        if items[feature_name].nunique() > 1:
            print ("Client ID: {}".format(key))
            client_group = items.groupby(feature_name)
            if cnt > output_number:
                 return 
            cnt += 1
            for fn, data in client_group:
                print (fn, get_os_version(fn), get_browser_version(fn))

# return the distribution of number of cookies
def num_cookie_distribution_paper(df):
    client = df.groupby('browserid')
    MAXLEN = 35
    distribution = {}
    length = 0
    for key, group in client:
        browser = group['browser'].iloc[0]
        if browser not in distribution:
            distribution[browser] = [0 for i in range(MAXLEN)]
        number = group['label'].nunique()
        if number <= 30:
            distribution[browser][number] += 1
        length = max(length, number)

    f = open('cookie.dat', 'w')
    for browser in distribution:
        f.write('{} '.format(browser))
    for i in range(len(distribution['chrome'])):
        f.write('{} '.format(i))
        for browser in distribution:
            f.write('{} '.format(distribution[browser][i]))
        f.write('\n')
    f.close()
    return distribution


def num_device_distribution(client):
    MAXLEN = int(1e5)
    distribution = [0 for i in range(MAXLEN)]
    length = 0
    print 'we have ', len(client), ' users'
    for key, group in client:
        number = group['deviceid'].nunique()
        distribution[number] += 1
        length = max(length, number)
        if number > 10:
            print key
    return distribution[:length + 1]


def draw_line(values, keys = "T^T", pic_name = "default"):
    plt.clf()
    ind = [i for i in range(len(values))]
    if keys != "T^T":
        ind = keys
    plt.plot(ind, values)
    plt.savefig('./report/' + pic_name + '.png')
    plt.clf()


# draw a bar figure
def draw_bar(values, keys = "T^T", pic_name = "default"):
    plt.clf()
    ind = [i for i in range(len(values))]
    if keys == "T^T":
        keys = [i for i in range(len(values))]

    plt.bar(ind, values, 0.5)
    plt.gcf().subplots_adjust(bottom=0.5)
    plt.xticks(ind, keys, rotation=90, ha='center')
    plt.savefig('./report/' + pic_name + '.png')
    plt.clf()

# get distance by ip change
def ip_distance(lat1, lon1, lat2, lon2):
    # approximate radius of earth in km
    R = 6373.0

    lat1 = radians(lat1)
    lon1 = radians(lon1)
    lat2 = radians(lat2)
    lon2 = radians(lon2)

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = R * c
    return distance

def get_location_change(client, title):
    pre_row = ""
    cnt = [0 for i in range(2000)] 
    for key, items in client:
        if items['IP'].nunique() > 1:
            pre_row = ""
            for name, row in items.iterrows():
                if type(pre_row) == type("") or pre_row['IP'] == row['IP']:
                    pre_row = row
                    continue
                seconds_change = float((row['time'] - pre_row['time']).seconds)
                distance_change = ip_distance(pre_row['latitude'], pre_row['longitude'],
                        row['latitude'],
                        row['longitude']) 
                if distance_change == 0:
                    continue

                if seconds_change == 0:
                    seconds_change = 0.1

                km_per_hour = distance_change / (seconds_change / 60) * 60
                pre_row = row
                if km_per_hour > 1999:
                    km_per_hour = 1999 
                cnt[int(km_per_hour)] += 1
    pic_name = '{}locationchange'.format(title.replace(' ',''))
    draw_line(cnt, pic_name = pic_name)
    pic_latex = get_latex_pic(pic_name)
    location_change = get_latex_subsection(pic_latex, "location change speed per hour")
    return location_change

def get_change_agent(agent):
    os_changed = get_os_changed(agent)
    browser = get_browser_agent(agent)
    browser_changed = get_browser_changed(agent)



def get_item_change(client, title, key, sep = '_', N = 10):
    print ("start generating {} change".format(key))
    cnts = {}
    for cur_id, items in tqdm(client):
        if items[key].nunique() > 1:
            pre = ""
            pre_row = ""
            for name, row in items.iterrows():
                cur_key = row[key]
                if pre == "":
                    pre = cur_key 
                    pre_row = row
                    continue
                if pre == cur_key:
                    continue
                str1_str2, str2_str1 = get_change_strs(pre, cur_key, sep = sep) 
                # assume no downgrading
                part1 = '~'.join(str1_str2)
                part2 = '~'.join(str2_str1)
                pre = cur_key 
                
                if max(part1, part2) == "Tifinagh":
                    diff = diff_record(pre_row, row)
                    print cur_id
                    print pre_row['agent']
                    print row['agent']
                    print pre_row['time'], row['time'], diff
                    print '=============================='

                res = min(part1, part2) + '\n' + max(part1, part2)
                if res not in cnts:
                    cnts[res] = [] 
                cnts[res].append(cur_id) 
                pre_row = row
    for cnt in cnts:
        cnts[cnt] = len(set(cnts[cnt]))
    cnts = sorted(cnts.items(), key = operator.itemgetter(1), reverse = True)[:N]
    print ("finished generating {} change".format(key))
    values = [c[1] for c in cnts] 
    keys = [c[0] for c in cnts]
    print (keys, values)
    draw_bar(values, 
            keys = keys,
            pic_name = '{}{}change'.format(title, key))
    return cnts

# input two lists of fonts
# return the intersection of these two sets
def get_fonts_intersection(fonts_1, fonts_2):
    font_list1 = fonts_1.split('_')
    font_list2 = fonts_2.split('_')
    return set(font_list1) & set(font_list2) 

# input two df rows
# return the diff of these two rows
# the return is a dict of changes
def diff_record(row_1, row_2, feature_list):
    res = {} 
    for key in feature_list:
        if row_1[key] != row_2[key]:
            if key == 'jsFonts' or key == 'langsdetected':
                res[key] = get_change_strs(row_1[key], row_2[key], sep = '_')
            else:
                res[key] = get_change_strs(row_1[key], row_2[key], sep = ' ')
    return res

#return the update of browsers fonts
def get_browser_update_influence(browserid, method = "all"):
    res = {}
    for browser, group in browserid:
        if group['agent'].nunique() > 1:
            first = True
            for name, row in group.iterrows():
                if first:
                    first = False
                    pre_row = row
                    continue
                # only keep the int number
                browser_v1 = get_browser_version(pre_row['agent']).split('.')[0]
                browser_v2 = get_browser_version(row['agent']).split('.')[0]
                if browser_v1 == 'other' or browser_v2 == 'other':
                    continue
                try:
                    browser_v1_int = int(browser_v1.split('/')[1])
                    browser_v2_int = int(browser_v2.split('/')[1])
                except:
                    pass
                if browser_v1_int < browser_v2_int:
                    diff = diff_record(pre_row, row)
                    change_key = browser_v1 + '~' + browser_v2
                    for key in diff:
                        if change_key not in res:
                            res[change_key] = {} 
                            res[change_key]['cnt'] = set() 
                        if key not in res[change_key]:
                            res[change_key][key] = {} 
                        res[change_key]['cnt'].add(browser) 
                        if method == "all":
                            if str(diff[key]) not in res[change_key][key]:
                                res[change_key][key][str(diff[key])] = 0
                            res[change_key][key][str(diff[key])] += 1
                        else:
                            if len(res[change_key][key]) == 0:
                                res[change_key][key] = diff[key]
                            else:
                                after_0 = res[change_key][key][0] & diff[key][0]
                                after_1 = res[change_key][key][1] & diff[key][1]
                                res[change_key][key] = (after_0, after_1)
                pre_row = row

    for key in res:
        print ('============================')
        print (key)
        print ('browser count: {}'.format(len(res[key]['cnt'])))
        for k in res[key]:
            if k == 'cnt':
                continue
            print (k, res[key][k])
    return res

# input the agent string 
# return whether this is a private agent or not
def is_private(agent):
    agent = agent.lower()
    if get_os_from_agent(agent) == 'other':
        return True 
    return False 


# Private browser test
def private_browser_test(df, fonts):
    private_count = 0
    possible_os = {}
    fail = set()
    for idx in tqdm(df.index):
        row = df.iloc[idx]
        agent = row['agent']
        if is_private(agent):
            for os in fonts:
                if len(fonts[os] - set(row['jsFonts'].split('_'))) == 0:
                    if row['browserid'] not in possible_os:
                        possible_os[row['browserid']] = [row['agent']] 
                    possible_os[row['browserid']].append(os)
            if row['browserid'] not in possible_os:
                fail.add(row['browserid'])
    return possible_os, fail

# output fonts to file
def output_to_file(fonts):
    f = open('osversion2fonts', 'w')
    start = True
    for os in fonts:
        if start:
            start = False
        else:
            f.write("~~~")
        f.write("{}___{}".format(os, '---'.join(fonts[os])))
    f.close()

# load fonts into memory
def load_from_file(filename):
    fonts = {}
    f = open(filename, 'r')
    data = f.readline().split('~~~')
    for tmp in data:
        fonts[tmp.split('___')[0]] = set(tmp.split('___')[1].split('---'))
        tmp = f.readline()
    return fonts


# the percentage of changes on that day
def number_of_change_of_days(client):
    print 'the percentage of changes on that day'
    total = 0.0
    changes = [0.0 for i in range(100)]
    for browserid, cur_group in client:
        total += 1.0
        if cur_group['browserfingerprint'].nunique() > 1:
            min_time = datetime.datetime.now()
            counted_days = -1
            for index, row in cur_group.iterrows():
                if min_time > row['time']:
                    min_time = row['time']
                    min_row = row
                if row['browserfingerprint'] != min_row['browserfingerprint']:
                    if counted_days == (row['time'] - min_time).days:
                        continue
                    counted_days = (row['time'] - min_time).days
                    changes[counted_days] += 1.0
    while changes.pop() == 0:
        pass
    for idx in range(len(changes)):
        changes[idx] /= total
    print 'finished the percentage of changes on that day'
    return changes

# the percentage of changes on the date
# here the change is based on the change of previous 
def changes_of_date(client):
    print 'the percentage of changes on that date'
    features = [
            'browserfingerprint',
            'agent',
            'jsFonts',
            'canvastest'
            ]
    total = 0.0
    changes = {}
    min_date = min(df['time'])
    max_date = max(df['time'])
    # truncate the mindate to days
    min_date = truncate(min_date, 'day')
    length = (max_date - min_date).days
    length += 3
    for feature in features:
        changes[feature] = [0.0 for i in range(length + 1)] 

    for browserid, cur_group in client:
        pre = {} 
        if cur_group['browserfingerprint'].nunique() > 1:
            start = True
            for index, row in cur_group.iterrows():
                total += 1.0
                if start:
                    pre = row
                    start = False
                    continue
                for feature in features:
                    if row[feature] != pre[feature]:
                        delt = (row['time'] - min_date).days
                        changes[feature][delt] += 1.0
                pre = row
    res = {}
    print changes
    for date in range(length + 1):
        cur_date = min_date + datetime.timedelta(days = date)
        res[cur_date] = {}
        for feature in features:
            res[cur_date][feature] = changes[feature][date] / total
    print 'finished the percentage of changes on that date'
    return res, features 

# the percentage of changes on the date
# here the change is based on the change of previous 
def agent_changes_of_date(count_feature, client, df):
    print 'the percentage of changes on that date'
    features = [
            'chrome',
            'opera',
            'firefox',
            'opr/',
            'safari',
            'trident',
            'samsungbrowser',
            'other'
            ]
    total = 0.0
    changes = {}
    min_date = min(df['time'])
    max_date = max(df['time'])
    # truncate the mindate to days
    min_date = truncate(min_date, 'day')
    length = (max_date - min_date).days
    length += 3
    num_browserids_that_day = {}
    for feature in features:
        changes[feature] = [0.0 for i in range(length + 1)] 
        num_browserids_that_day[feature] = [set() for i in range(length + 1)]

    print 'generating number of changed browser in each day'
    total_num_ids_that_day = [set() for i in range(length + 1)]
    for idx in tqdm(df.index):
        delt = (df.at[idx, 'time'] - min_date).days
        num_browserids_that_day[df.at[idx, 'browser']][delt].add(df.at[idx, 'browserid'])
        total_num_ids_that_day[delt].add(df.at[idx, 'browserid'])

    for feature in features:
        for idx in range(length + 1):
            num_browserids_that_day[feature][idx] = float(len(num_browserids_that_day[feature][idx]))
    #print num_browserids_that_day
    '''
#=================================================
    res = {}
    for feature in features:
        for idx in range(length + 1):
            cur_date = min_date + datetime.timedelta(days = idx)
            if cur_date not in res:
                res[cur_date] = {}
            res[cur_date][feature] = num_browserids_that_day[feature][idx]
    return res, features 
#=================================================
    '''
    print 'finished generating number of changed browser in each day'
    cur_cnt = {}
    total_cnt = {}
    total_change = {}
    small_features = [ 
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
        "audio"
        ]
    for browserid, cur_group in client:
        pre = {} 
        if cur_group['browserfingerprint'].nunique() > 1:
            start = True
            for index, row in cur_group.iterrows():
                total += 1.0
                agent = row['agent']
                if start:
                    pre = row
                    start = False
                    continue
                #if get_browser_version(agent) != get_browser_version(pre['agent']):
                #if row['agent'] != pre['agent']:
                if row[count_feature] != pre[count_feature]:
                    delt = (row['time'] - min_date).days
                    changes[row['browser']][delt] += 1.0
                    '''
                    if row['time'].date() >= datetime.datetime(2018, 1, 28).date() and row['time'].date() <= datetime.datetime(2018, 2, 5).date() and row['browser'] == 'trident':
                        browser = row['browser']
                        if browser not in total_change:
                            total_change[browser] = 0
                            total_cnt[browser] = 0
                            cur_cnt[browser] = 0
                        total_change[browser] += 1
                        if get_os_from_agent(agent) == 'win' :
                            total_cnt[browser] += 1
                        #if get_change_strs(row['jsFonts'], pre['jsFonts'])[1] >= smallset:
                        if row[count_feature] != pre[count_feature]:
                            if get_os_from_agent(agent) == 'win' :
                                cur_cnt[browser] += 1
                        print '=========================='
                        print row['agent']
                        print pre['agent'] 
                        print diff_record(pre, row, small_features)
                        print '=========================='
                    '''
                    break
                pre = row
    res = {}
    #print changes
    '''
    print '============================'
    for browser in total_change:
        print browser, cur_cnt[browser], total_cnt[browser], total_change[browser], total
    print '============================'
    '''
    for date in range(length + 1):
        cur_date = min_date + datetime.timedelta(days = date)
        res[cur_date] = {}
        for feature in features:
            if num_browserids_that_day[feature][date] == 0.0:
                res[cur_date][feature] = 0.0
            else:
                res[cur_date][feature] = 100 * changes[feature][date] / num_browserids_that_day[feature][date]
    #        print feature, cur_date, num_browserids_that_day[feature][date], changes[feature][date], res[cur_date][feature]
#total_num_ids_that_day[date]
    print 'finished the percentage of changes on that date'
    return res, features 


# return a list of browser id that happens fliping
def font_flip_count(client):
    total = 0
    res = {} 
    pre = ""
    for browserid, cur_group in client:
        total += 1
        if cur_group['browserfingerprint'].nunique() > 1:
            history = set() 
            start = True
            cur_jsFonts = ""
            for idx, row in cur_group.iterrows():
                cur_jsFonts = row['jsFonts']
                if start:
                    start = False
                    pre = cur_jsFonts
                    continue
                if cur_jsFonts in history and cur_jsFonts != pre:
                    os = get_os_from_agent(row['agent'])
                    if os not in res:
                        res[os] = set()
                    res[os].add(row['browserid'])
                    break
                else:
                    history.add(cur_jsFonts)
                pre = cur_jsFonts
    return res


# get the mapping between os and canvastest
def get_canvas_agent_mapping(df, func):
    mapping = {}
    for idx in tqdm(df.index):
        row = df.iloc[idx]
        agent = row['agent']
        canvas = row['canvastest']
        aim = func(agent)
        if canvas not in mapping:
            mapping[canvas] = {'ids': set(), 'aim': set()}
        mapping[canvas]['aim'].add(os)
        mapping[canvas]['ids'].add(row['browserid'])
    return mapping

# get the mapping between os and canvastest
def get_attr_mapping(df, attr_from, attr):
    mapping = {}
    for idx in tqdm(df.index):
        row = df.iloc[idx]
        cur_attr = row[attr]
        attr_from_val = row[attr_from]
        if attr_from_val not in mapping:
            mapping[attr_from_val] = {'ids': set(), 'aim': set()}
        mapping[attr_from_val]['aim'].add(cur_attr)
        mapping[attr_from_val]['ids'].add(row['browserid'])
    return mapping

def get_mapping_back(df, canvas_mapping, gpuimgs_mapping, back_name, null_val = 'No Debug Info'):
    users = {}
    for idx in tqdm(df.index):
        row = df.iloc[idx]
        value = row[back_name]
        canvas_value = row['canvastest']
        gpu_value = row['gpuimgs']
        userid = row['browserid']
        if value.find(null_val) == -1:
            continue
        if userid not in users:
            users[userid] = canvas_mapping[canvas_value]['aim'] 
        #users[userid] &= gpuimgs_mapping[gpu_value]['aim']
    return users

def draw_browser_change_by_date_paper(df):
    feature_names = list(df.columns.values)
    df = df[pd.notnull(df['clientid'])]
    df = df.reset_index(drop = True)
    clientid = df.groupby('browserid')
    small_features = [ 
        "gpuimgs",
        "browserfingerprint",
        "agent",
        "jsFonts",
        "canvastest",
        "accept",
        "encoding",
        "language",
        "langsdetected",
        "resolution",
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
        "audio"
        ]
    for feature in small_features: 
        changes, features = agent_changes_of_date(feature, clientid, df)
        #f = open('./pics/{}changebydate.dat'.format(feature), 'w')
        f = open('./changebydate/{}changebydate.dat'.format(feature), 'w')
        for date in sorted(changes):
            f.write('{}-{}-{}'.format(date.year, date.month, date.day))
            for feature in features:
                f.write(' {:.2f}'.format(changes[date][feature]))
            f.write('\n')
        f.close()
        break;

def feature_latex_table_paper(df):
    value_set = {}
    browser_instance = {}
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

    group_features = {
            'headers_features' : [0, 1, 2, 3, 4],
            'browser_features' : [5, 6, 7, 8, 9, 10],
            'os_features' : [11, 12, 13],
            'hardware_feature' : [14, 15, 16, 17, 18, 19, 20, 21],
            'ip_features': [22, 23, 24],
            'consistency' : [25, 26, 27, 28]
            }

    group_map = ['' for i in range(29)]
    for key in group_features:
        for i in group_features[key]:
            group_map[i] = key

    print group_map
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
    f = open('feature_table.dat', 'w')
    for feature in value_set:
        distinct[feature] = len(value_set[feature])
        cnt = 0
        for val in value_set[feature]:
            if len(value_set[feature][val]) == 1:
                if feature == 'agent':
                    print val
                cnt += 1
        unique[feature] = cnt

        for bid in browser_instance:
            if feature not in per_browser_instance:
                per_browser_instance[feature] = 0
            if len(browser_instance[bid][feature]) == 1 and bid in back_users:
                per_browser_instance[feature] += 1
        per_browser_instance[feature] = float(per_browser_instance[feature]) / float(num_back)
        f.write(r'{} & {} & {} & {:.4f} \\'.format(feature, distinct[feature], unique[feature], per_browser_instance[feature]))
    f.close()

def get_num_each_day_paper(df):
    min_date = min(df['time'])
    max_date = max(df['time'])
    min_date = min_date.replace(microsecond = 0, second = 0, minute = 0, hour = 0)
    length = (max_date - min_date).days + 3

    num_new_user =  [set() for i in range(length)]
    num_new_device = [set() for i in range(length)]
    num_new_browserid = [set() for i in range(length)]
    num_back_user = [set() for i in range(length)]
    num_back_device = [set() for i in range(length)]
    num_back_browserid = [set() for i in range(length)]

    for idx in tqdm(df.index):
        row = df.iloc[idx]
        clientid = row['clientid'] 
        deviceid = row['deviceid']
        browserid = row['browserid']
        cur_delt_days = (row['time'] - min_date).days
        # add to new first, remove it later
        num_new_user[cur_delt_days].add(clientid)
        num_new_device[cur_delt_days].add(deviceid)
        num_new_browserid[cur_delt_days].add(browserid)

    # remove the new and add to exsits
    cur_users = set()
    cur_device = set()
    cur_browserid = set()
    for i in tqdm(range(length)):
        for user in num_new_user[i]:
            if user in cur_users:
                num_back_user[i].add(user)
            else:
                cur_users.add(user)

        for device in num_new_device[i]:
            if device in cur_device:
                num_back_device[i].add(device)
            else:
                cur_device.add(device)
        for browserid in num_new_browserid[i]:
            if browserid in cur_browserid:
                num_back_browserid[i].add(browserid)
            else:
                cur_browserid.add(browserid)

    for i in range(length):
        num_new_user[i] -= num_back_user[i]
        num_new_device[i] -= num_back_device[i]
        num_new_browserid[i] -= num_back_browserid[i]

    f = open('./pics/numusersdate.dat', 'w')
    for cur_delt in range(length):
        date = min_date + datetime.timedelta(days = cur_delt)
        f.write('{}-{}-{} '.format(date.year, date.month, date.day))
        f.write('{} {}\n'.format(len(num_new_user[cur_delt]), len(num_back_user[cur_delt])))
    f.close()

    f = open('./pics/numdevicedate.dat', 'w')
    for cur_delt in range(length):
        date = min_date + datetime.timedelta(days = cur_delt)
        f.write('{}-{}-{} '.format(date.year, date.month, date.day))
        f.write('{} {} \n'.format(len(num_new_device[cur_delt]), len(num_back_device[cur_delt])))
    f.close()
    f = open('./pics/numbrowseriddate.dat', 'w')
    for cur_delt in range(length):
        date = min_date + datetime.timedelta(days = cur_delt)
        f.write('{}-{}-{} '.format(date.year, date.month, date.day))
        f.write('{} {} \n'.format(len(num_new_browserid[cur_delt]), len(num_back_browserid[cur_delt])))
    f.close()

def get_num_visits_paper(df):
    MAX = -1
    cnt = {}
    for idx in tqdm(df.index):
        browserid = df.at[idx, 'browserid']
        browser = df.at[idx, 'browser']
        if browser not in cnt:
            cnt[browser] = {}
        if browserid not in cnt[browser]:
            cnt[browser][browserid] = 0
        cnt[browser][browserid] += 1
        MAX = max(MAX, cnt[browser][browserid])

    res = [{} for i in range(MAX + 1)]
    for browser in cnt:
        for browserid in cnt[browser]:
            if browser not in res[cnt[browser][browserid]]:
                res[cnt[browser][browserid]][browser] = 0
            res[cnt[browser][browserid]][browser] += 1

    fp = open('./pics/numvisits.dat', 'w')
    for browser in res[1]:
        fp.write('{} '.format([browser]))
    for i in range(MAX + 1):
        fp.write('{} '.format(i))
        for browser in res[i]:
            fp.write('{} '.format(res[i][browser]))
        fp.write('\n')
    fp.close()



def for_paper_jsFonts_diff(db):
    df = pd.read_sql('select jsFonts, clientid from features where clientid like "[final_test%]";', 
            con=db.get_db())    

    for idx in df.index:
        row = df.iloc[idx]
        if row['clientid'] != "[final_test_original_windows7]":
            continue
        for idx2 in df.index:
            row2 = df.iloc[idx2]
            set1, set2 = get_change_strs(row['jsFonts'], row2['jsFonts'])
            print row['clientid'], row2['clientid'], set1, len(set1), set2, len(set2) 
        break

def map_back(clientid, feature_names, df):
    base_row = df.loc[df['clientid'] == "[final_test_original_windows7]"].iloc[0]
    aim_row = df.loc[df['clientid'] == clientid].iloc[0]
    aim_fonts = get_change_strs(base_row['jsFonts'], aim_row['jsFonts'])[1]
    user_list = []
    grouped = df.groupby('browserid')

    for browserid, cur_group in grouped:
        for idx, row in cur_group.iterrows():
            mapped = 1
            for feature in feature_names:
                if feature == 'jsFonts':
                    cur_fonts = set(row[feature].split('_'))
                    if cur_fonts < aim_fonts:
                        mapped = 0
                elif row[feature] != aim_row[feature]:
                    mapped = 0
                    break
            if mapped == 1:
                user_list.append(browserid)
                break
    return user_list

def life_time_distribution_paper(df):
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

def cookie_life_cdf_paper(df):
    grouped = df.groupby('browserid')
    min_date = min(df['time'])
    max_date = max(df['time'])
    length = (max_date - min_date).days
    life_time = {}
    cnt_all = {}

    for browserid, cur_group in grouped:
        pre_cookie = ""
        pre_time = ""
        browser = cur_group.iloc[0]['browser']
        if browser not in cnt_all:
            cnt_all[browser] = 0
        cnt_all[browser] += cur_group['label'].nunique()
        for idx, row in cur_group.iterrows():
            browser = row['browser']
            cookie = row['label']
            if pre_cookie == "":
                pre_time = row['time']
                pre_cookie = cookie
                continue
            if pre_cookie != "" and cookie != pre_cookie:
                period = (row['time'] - pre_time).days
                if browser not in life_time:
                    life_time[browser] = [0 for i in range(length + 3)]
                life_time[browser][period] += 1
                pre_time = row['time']

            pre_cookie = cookie

    for browser in life_time:
        for i in range(1, len(life_time[browser])):
            life_time[browser][i] += life_time[browser][i - 1]
    for browser in life_time:
        for i in range(0, len(life_time[browser])):
            life_time[browser][i] = float(life_time[browser][i]) / float(cnt_all[browser]) * 100.0
    return life_time


def see_agent(df):
    mapping = {}
    for idx in tqdm(df.index):
        agent = df.at[idx, 'agent']
        if agent not in mapping:
            mapping[agent] = set()
        mapping[agent].add(df.at[idx, 'browserid'])

    cnt = 0
    for agent in mapping:
        if len(mapping[agent]) == 1:
            cnt += 1
            print agent
    print cnt
        
def get_tolerance_paper(df):
    less_than_n = [{}, {}]
    grouped = df.groupby('browserid')
    group_size = len(grouped)
    grouped = df.groupby('browserfingerprint')

    for browserid, cur_group in tqdm(grouped):
        n = cur_group['browserid'].nunique()
        if n > 1 and n < 50:
            n = 2
        elif n >= 50:
            n = 3
        browserids = set(cur_group['browserid'])
        browser = cur_group['browser'].iloc[0]
        mobile = mobile_or_not(cur_group['agent'].iloc[0])
        if browser not in less_than_n[mobile]:
            less_than_n[mobile][browser] = [set() for i in range(4)]
        less_than_n[mobile][browser][n] |= browserids
        less_then_n[mobile]['all']

    f = open('./pics/desktoptolerance.dat', 'w')
    for browser in less_than_n[0]:
        f.write('{} '.format(str(browser)))
        cur_sum = 0
        for i in range(1,4):
            cur_sum += len(less_than_n[0][browser][i])
        for i in range(1, 4):
            f.write('{} '.format(str(100.0 * float(len(less_than_n[0][browser][i])) / float(cur_sum))))
        f.write('\n')
    f.close()

    f = open('./pics/mobiletolerance.dat', 'w')
    for browser in less_than_n[1]:
        f.write('{} '.format(str(browser)))
        cur_sum = 0
        for i in range(1,4):
            cur_sum += len(less_than_n[1][browser][i])
        for i in range(1, 4):
            f.write('{} '.format(str(100.0 * float(len(less_than_n[1][browser][i])) / float(cur_sum))))
        f.write('\n')
    f.close()

def gpu_mapback_paper(df):
    gpu_map = [
            'apple',
            'intel',
            'nvidia',
            'amd',
            'ati',
            'radeon',
            'asus',
            'adreno'
            ]
    mapback_keys = ['gpuimgs']
    df_masked = df[df['inc'] == 'No Debug Info']
    df = df[df['inc'] != 'No Debug Info']
    df = df.reset_index(drop = True)
    grouped = df.groupby(mapback_keys)
    img_mapping = {}
    for idx in tqdm(df.index):
        cur_gpu = df.at[idx, 'gpu'].lower()
        for gpu_inc in gpu_map:
            if cur_gpu.find('isklultgt2') != -1:
                cur_gpu = 'intel'
            if cur_gpu.find(gpu_inc) != -1:
                df.at[idx, 'gpu'] = gpu_inc
                break

    all_keys = 0
    for imgs, cur_group in tqdm(grouped):
        cur_key = str(imgs)
        if cur_key not in img_mapping:
            img_mapping[cur_key] = {'cnt': 0, 'res': set()} 
        cur_len = len(set(cur_group['browserid']))
        img_mapping[cur_key]['cnt'] += cur_len 
        all_keys += cur_len
        img_mapping[cur_key]['res'] |= set(cur_group['gpu'])

    grouped = df_masked.groupby(mapback_keys)
    mapped_number = [{} for i in range(30)]
    all_pos = 0
    for imgs, cur_group in tqdm(grouped):
        cur_key = str(imgs)
        cur_len = len(set(cur_group['browserid']))
        all_pos += cur_len
        if cur_key not in img_mapping:
            continue
        num_pos = len(img_mapping[cur_key]['res'])
        cur_res_str = '_'.join(img_mapping[cur_key]['res'])
        if num_pos >= 10:
            continue
        if cur_key in img_mapping:
            if cur_res_str not in mapped_number[num_pos]:
                mapped_number[num_pos][cur_res_str] = 0
            mapped_number[num_pos][cur_res_str] += cur_len

    print all_pos
    for idx in range(len(mapped_number)):
        cur_sum = 0
        print idx
        for gpu in mapped_number[idx]:
            cur_sum += mapped_number[idx][gpu]
            print gpu, '====', float(mapped_number[idx][gpu]) / float(all_pos) * 100
        print float(cur_sum) / float(all_pos) * 100
        

'''

    success = 0
    res = {}
    for cur_key in img_mapping:
        cur_type = ','.join(cur_key[1]['res'])
        if cur_type not in res:
            res[cur_type] = 0
        res[cur_type] += cur_key[1]['cnt']
        if len(cur_key[1]['res']) == 1:
            success += 1
    res = sorted(res.iteritems(), key=lambda (k, v): (-v, k))
    for cur_type, val in res:
        print (cur_type), float(val) / float(all_keys) * 100
'''

def ip_location_paper(df):
    client = df.groupby('clientid')
    pre_row = ""
    cnt = [0 for i in range(2005)] 
    for key, items in tqdm(client):
        if items['IP'].nunique() > 1:
            pre_row = ""
            for name, row in items.iterrows():
                if type(pre_row) == type("") or pre_row['IP'] == row['IP']:
                    pre_row = row
                    continue
                seconds_change = float((row['time'] - pre_row['time']).seconds)
                distance_change = ip_distance(pre_row['latitude'], pre_row['longitude'],
                        row['latitude'],
                        row['longitude']) 
                if distance_change == 0:
                    continue

                if seconds_change == 0:
                    seconds_change = 0.1

                km_per_hour = distance_change / (seconds_change / 60) * 60
                pre_row = row
                if km_per_hour > 1999:
                    km_per_hour = 1999 
                cnt[int(km_per_hour)] += 1

    f = open('./pics/ipchange.dat','w')
    for i in range(2001):
        f.write('{} {}\n'.format(i, cnt[i]))
    f.close()

def get_change_agent(agent):
    os_changed = get_os_changed(agent)
    browser = get_browser_agent(agent)
    browser_changed = get_browser_changed(agent)


# the two strs put in this function is separated by _
# if it's separated by ' ', trans them before this function
# or use the sep param

def main():
    small_feature_list = [ 
        "IP",
        "time",
        "label",
        "clientid",
        "agent",
        "jsFonts",
        "canvastest", 
        #"browser",
        #"browserfingerprint",
        #"browserid",
        "accept",
        "encoding",
        "language",
        "langsdetected",
        "resolution",
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
        "audio"
        ]
    db = Database('uniquemachine')
    df = load_data(load = False, feature_list = ['*'], table_name = "longfeatures", db = db)
    '''
    feature_names = list(df.columns.values)
    df = df[pd.notnull(df['clientid'])]
    df = df.reset_index(drop = True)
    clientid = df.groupby('browserid')

    canvas_mapping = get_attr_mapping(df, 'canvastest', 'gpu')
    gpuimgs_mapping = get_attr_mapping(df, 'gpuimgs', 'gpu')
    res = get_mapping_back(df, canvas_mapping, gpuimgs_mapping, 'gpu')
    cnt = 0
    f = open('canvasmapback.dat', 'w')
    for r in res:
        # all should have 'No Debug Info'
        # we need to drop them
        val = res[r]
        if len(val) > 1:
            f.write(str(val))
            f.write('\n')
            cnt += 1
    print cnt, 'out of ', len(res)


    '''
    '''
    db = Database('data2')
    df1 = load_data(load = True, feature_list = small_feature_list, table_name = 'features', db = db)
    db = Database('uniquemachine')
    df2 = load_data(load = True, feature_list = small_feature_list, table_name = 'features', db = db)
    db.combine_tables(small_feature_list, [df1, df2])
    mapped = map_back("[final_test_officeproplus2013]", ['jsFonts', 'canvastest'], df)
    print len(mapped)
    for_paper_jsFonts_diff(db)
    db = Database('uniquemachine')
    df = load_data(load = True, feature_list = ['*'], table_name = 'pandas_longfeatures', db = db)
    get_num_visits(df)
    feature_latex_table(df)
    see_agent(df)
    cookie_cdf = cookie_life_cdf(df)
    f = open('cookie_cdf.dat', 'w')
    for browser in cookie_cdf:
        f.write('{} '.format(browser))
    for i in range(len(cookie_cdf['chrome'])):
        f.write('{} '.format(i + 1))
        for browser in cookie_cdf:
            f.write('{} '.format(cookie_cdf[browser][i]))
        f.write('\n')
    f.close()
    print cookie_cdf
    df = df[pd.notnull(df['clientid'])]
    df = df.reset_index(drop = True)
    #clientid = df.groupby('clientid')
    clientid = df.groupby('browserid')
    res = basic_numbers(clientid)
    device = num_device_distribution(clientid)
    print "based on browser instances:"
    print res
    print (device)
    
    #db.combine_tables(small_feature_list, [df1, df2])
    
    cookies = df.groupby('label')
    feature_names = list(df.columns.values)
    df = df[pd.notnull(df['clientid'])]
    df = df.reset_index(drop = True)
    clientid = df.groupby('browserid')

    canvas_mapping = get_canvas_attr_mapping(df, 'gpu')
    for key, value in sorted(canvas_mapping.iteritems(), key = lambda (k, v): (-len(v['ids']), k)):
        print key, len(value['ids']), value['aim']

    canvas_mapping = os_canvas_mapping(df, get_os_version)
    for key, value in sorted(canvas_mapping.iteritems(), key = lambda (k, v): (-len(v['ids']), k)):
        print key, len(value['ids']), value['os']
    
    db = Database('uniquemachine')
    df = load_data(load = True, table_name = "pandas_longfeatures", feature_list = small_feature_list, db = db)
    map_res = db.build_map(df)

    '''
    '''
    #fliped = font_flip_count(clientid)
    #for os in fliped:
    #    print os, len(fliped[os])

    #clientid = df.groupby('clientid')
    #output_diff(clientid, 'inc', 100)
    #output_diff(clientid, 'gpu', 100)
    #print private_browser_test(df)
    #fonts, cnts = get_os_fonts(df)
    #output_to_file(fonts)

    fonts = load_from_file('osversion2fonts')
    possible_os, fail = private_browser_test(df, fonts)
    for browserid in possible_os:
        print browserid, possible_os[browserid] 

    #get_browser_update_influence(clientid, method = 'intersection')
    get_item_change(clientid, 'radom', 'langsdetected', sep = '_')
    get_item_change(clientid, 'radom', 'gpu', sep = ' ')
    get_item_change(clientid, 'radom', 'agent', sep = ' ')
    get_item_change(clientid, 'radom', 'audio', sep = ' ')
    get_item_change(clientid, 'radom', 'ipcity', sep = '~')
    get_item_change(clientid, 'radom', 'jsFonts', sep = '_')

    change_time = fingerprint_change_time(clientid)
    print 'change time: ', change_time
    feature_change = get_every_change(clientid, 'bucunzai') 
    print 'feature change:', feature_change
    tolerance = [float(len(t)) / float(len(clientid)) * 100 for t in less_than_n]
    print 'tolerance: ', tolerance
    df = load_data(load = True, feature_list = ['clientid','inc', 'gpu', 'canvastest', 'gpuimgs', 'browser', 'browserid', 'browserfingerprint'], table_name = 'pandas_features', db = db)
    gpu_mapback_paper(df)
    feature_delta_paper(df)
    '''
    '''
    db = Database('uniquemachine')
    df = load_data(load = True, feature_list = ['*'], table_name = "pandas_features", db = db, other = ' where gpuimgs is not NULL ')
    draw_browser_change_by_date_paper(df)
    life_time_distribution_paper(df)
    feature_latex_table_paper(df)
    db = Database('uniquemachine')
    df = load_data(load = True, feature_list = ['latitude', 'longitude','IP', 'clientid', 'time'], table_name = "pandas_features", db = db)
    ip_location_paper(df)
    df = load_data(load = True, feature_list = ['agent', 'browser', 'browserid', 'browserfingerprint'], table_name = 'pandas_features', db = db)
    get_tolerance_paper(df)
    num_cookie_distribution_paper(df)

    get_num_each_day(df)
    clientid = df.groupby('browserid')
    #fingerprints = df.groupby('browserfingerprint')
    #changes, less_than_n = num_of_users_per_fingerprint(fingerprints, 'browserid')
    #print changes
    distribution = num_feature_distribution(clientid, 'label')
    '''

if __name__ == '__main__':
    main()
