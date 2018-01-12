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
def get_all(clientid, cookies):
    clientid_section = get_group_section(clientid, "Based on Client ID", 'clientid')
    # cookies_section = get_group_section(cookies, "Based on Cookie", 'label')
    get_latex_doc(clientid_section) # + cookies_section)



def ip2int(ip):
    o = map(int, ip.split('.'))
    res = (16777216 * o[0]) + (65536 * o[1]) + (256 * o[2]) + o[3]
    return res

global ip2location
# try to use the ip location
def get_location_dy_ip(ip):
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


def get_device(row):
    id_str = ""
    # platform is between the first ( and the first ;
    platform = ""
    try:
        platform = row['agent'].split(')')[0].split('(')[1].split(';')[0]
    except:
        pass

    #print ("error getting platform: ", row['agent'])
    keys = ['clientid', 'inc', 'fp2_platform']
    for key in keys:
        # we assume that all of the keys are not null
        try:
            id_str += str(row[key])
        except:
            pass

    id_str += platform
    gpu_type = row['gpu'].split('Direct')[0]
    id_str += gpu_type
    return id_str
    


def load_data(load = True, file_path = None):
# clean the sql regenerate the fingerprint
# without the gpuimgs, ccaudio and hybridaudio
    global ip2location
    df = None
    if load == True:
        df = pd.read_sql('select * from pandas_features;', con=db.get_db())    
        print ("data loaded")
    else:
        ip2location = pd.read_sql('select * from ip2location_db5;', con=db.get_db())    
        print ("ip2location data loaded")
        df = pd.read_sql('select * from features;', con=db.get_db())    
        # delete the null clientid rows
        df = df[pd.notnull(df['clientid'])]
        print ("start clean")
        db.clean_sql(counted_features, df, generator = get_location_dy_ip, 
                get_device = get_device)
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
def num_feature_distribution(client, feature_name):
    MAXLEN = int(1e5)
    distribution = [0 for i in range(MAXLEN)]
    length = 0
    for key, group in client:
        number = group['label'].nunique()
        distribution[number] += 1
        length = max(length, number)
    return distribution[:30]


def num_device_distribution(client):
    global df
    client = df.groupby('clientid')
    MAXLEN = int(1e5)
    distribution = [0 for i in range(MAXLEN)]
    length = 0
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


# the two strs put in this function is separated by _
# if it's separated by ' ', trans them before this function
# or use the sep param
# return the diff of str1 to str2 and str2 to str1 
def get_change_strs(str1, str2, sep = '_'):
    str1 = str(str1)
    str2 = str(str2)
    if str1 == None:
        str1 = ""
    if str2 == None:
        str2 = ""
    words_1 = set(str1.split(sep))
    words_2 = set(str2.split(sep))
    return words_1 - words_2, words_2 - words_1

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
def diff_record(row_1, row_2):
    res = {} 
    for key in counted_features:
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
                        if feature == 'agent' and row['time'].day == 20 and row['time'].month == 12:
                            print row['agent'], pre['agent']
                            print get_change_strs(row['agent'], pre['agent'], sep = ' ')
                            print '==============================='
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



def main():
    global df
    df = load_data(load = True)
    cookies = df.groupby('label')
    feature_names = list(df.columns.values)
    df = df[pd.notnull(df['clientid'])]
    df = df.reset_index(drop = True)
    clientid = df.groupby('browserid')
    #get_all(clientid, cookies)
    #changes, features = changes_of_date(clientid)
    #f = open('./pics/changebydate.dat', 'w')
    #for date in sorted(changes):
    #    f.write('{}-{}-{}'.format(date.year, date.month, date.day))
    #    for feature in features:
    #        f.write(' {}'.format(changes[date][feature]))
    #    f.write('\n')
    #f.close()
    fliped = font_flip_count(clientid)
    for os in fliped:
        print os, len(fliped[os])

    #clientid = df.groupby('clientid')
    #output_diff(clientid, 'inc', 100)
    #output_diff(clientid, 'gpu', 100)
    #print private_browser_test(df)
    #fonts, cnts = get_os_fonts(df)
    #output_to_file(fonts)

    '''
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
    '''

if __name__ == '__main__':
    main()
