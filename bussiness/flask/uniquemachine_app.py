from flask import Flask, request,make_response, current_app
import os
import md5
from flask_failsafe import failsafe
import flask
from flask_cors import CORS, cross_origin
import json
import hashlib
from flaskext.mysql import MySQL
import ConfigParser
import re
import numpy as np
from PIL import Image
import base64
import cStringIO
from datetime import datetime
from urllib2 import urlopen
from django.utils.encoding import smart_str, smart_unicode

root = "/home/sol315/server/uniquemachine/"
pictures_path = "/home/sol315/pictures/"
config = ConfigParser.ConfigParser()
config.read(root + 'password.ignore')

mysql = MySQL()
app = Flask(__name__)
app.config['MYSQL_DATABASE_USER'] = config.get('mysql', 'username')
app.config['MYSQL_DATABASE_PASSWORD'] = config.get('mysql', 'password')
app.config['MYSQL_DATABASE_DB'] = 'uniquemachine'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)
CORS(app)
base64_header = "data:image/png;base64,"

mask = []
mac_mask = []
feature_list = [
        "agent",
        "accept",
        "encoding",
        "language",
        "langsDetected",
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
        "adBlock", 
        "cpucores", 
        "canvastest", 
        "audio",
        "ccaudio",
        "hybridaudio",
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
        "fp2_webglvendoe"
        ]

def run_sql(sql_str):
    db = mysql.get_db()
    cursor = db.cursor()
    cursor.execute(sql_str)
    db.commit()
    res = cursor.fetchall() 
    return res

def get_os_from_agent(agent):
    start_pos = 0
    if agent.find('(') != -1:
        start_pos = agent.find('(')
    end_pos = agent.find(')', start_pos)

    return agent[start_pos:end_pos]

def get_browser_from_agent(agent):
    start_pos = 0
    if agent.find('Firefox') != -1:
        start_pos = agent.find("Firefox")
    elif agent.find('Edge') != -1:
        start_pos = agent.find('Edge')
    elif agent.find('Chrome') != -1:
        start_pos = agent.find('Chrome')
    elif agent.find('Safari') != -1:
        start_pos = agent.find('Safari')

    if start_pos == 0:
        return 'unknown'
    else:
        # here use space as the end char
        end_pos = agent.find(' ', start_pos)
        if end_pos == -1:
            end_pos = len(agent)
        return agent[start_pos:end_pos]

def genFingerprint(recordID):
    feature_str = ",".join(feature_list)
    sql_str = 'select {} from features where uniquelabel="{}"'.format(feature_str, recordID)
    res = run_sql(sql_str)
    fingerprint = hashlib.sha1(str(res[0])).hexdigest()
    sql_str = 'UPDATE features SET {}="{}" WHERE uniquelabel = "{}"'.format('browserfingerprint', fingerprint, recordID)
    run_sql(sql_str)
    return fingerprint



@app.route("/finishPage", methods=['POST'])
def finishPage():
    recordID = request.values['recordID']
    return genFingerprint(recordID)

@app.route("/distance", methods=['POST'])
def distance():
    feature_list = [
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
            "cpu_cores", 
            "canvas_test", 
            "audio",
            "cc_audio",
            "hybrid_audio",
            "clientId"
            ]


    sql_str = "DESCRIBE features"
    res = run_sql(sql_str)
    attrs = []
    for attr in res:
        attrs.append(attr[0])

    ID = request.values['id']
    sql_str = "SELECT * FROM features"
    all_records = run_sql(sql_str)
    sql_str = "SELECT * FROM features WHERE id=" + ID
    aim_record = run_sql(sql_str)[0]
    num_attr = len(aim_record)
    cur_max = -1 
    max_record = ""
    cur_same = 0
    for record in all_records:
        cur_same = 0
        if str(ID) == str(record[24]):
            continue
        for feature in feature_list: 
            i = attrs.index(feature)
            if record[i] == aim_record[i]:
                cur_same += 1
        if cur_same > cur_max:
            cur_max = cur_same
            max_record = str(record[21])
    return str(float(cur_max) / float(len(feature_list))) + ", " + max_record 


# update one feature requested from client to the database asynchronously.
# before this function, we have to make sure
# every feature is included in the sql server
def doUpdateFeatures(unique_label, data):
    update_str = ""
    for key, value in data.iteritems():
        update_str += '{}="{}",'.format(key, value)

    update_str = update_str[:-1]
    sql_str = 'UPDATE features SET {} WHERE uniquelabel = "{}"'.format(update_str, unique_label)
    res = run_sql(sql_str)
    genFingerprint(unique_label)
    return res 


# try to use the ip location
def get_location_by_ip(ip):
    city = "failed"
    #try:
    #    url = 'http://ipinfo.io/{}/json'.format(ip)
    #    response = urlopen(url)
    #    data = json.load(response)
    #    city = smart_str(data['city'])
    #except:
    #    pass
    return city

def doInit(unique_label, cookie):

    result = {}
    agent = ""
    accept = ""
    encoding = ""
    language = ""
    IP = ""
    keys = ""
    try:
        agent = request.headers.get('User-Agent')
        accept = request.headers.get('Accept')
        encoding = request.headers.get('Accept-Encoding')
        language = request.headers.get('Accept-Language')
        keys = '_'.join(request.headers.keys())
        IP = request.remote_addr
    except:
        print keys
        pass

    # create a new record in features table
    sql_str = "INSERT INTO features (uniquelabel, IP) VALUES ('{}', '{}')".format(unique_label, IP)
    run_sql(sql_str)

    # update the statics
    result['agent'] = agent
    result['accept'] = accept
    result['encoding'] = encoding
    result['language'] = language
    result['label'] = cookie
    # remove iplocation
    result['httpheaders'] = keys 

    return doUpdateFeatures(unique_label, result)

@app.route("/getCookie", methods=['POST'])
def getCookie():
    IP = request.remote_addr
    id_str = IP + str(datetime.now()) 
    unique_label = hashlib.sha1(id_str).hexdigest()

    cookie = request.values['cookie']
    sql_str = 'SELECT count(id) FROM cookies WHERE cookie = "{}"'.format(cookie)
    res = run_sql(sql_str)

    if res[0][0] == 0:
        cookie = unique_label 
        sql_str = "INSERT INTO cookies (cookie) VALUES ('" + cookie + "')"
        run_sql(sql_str)

    doInit(unique_label, cookie)
    return unique_label + ',' + cookie

@app.route("/check_exsit_picture", methods=['POST'])
def check_exsit_picture():
    hash_value = request.values['hash_value']
    sql_str = "SELECT count(dataurl) FROM pictures WHERE dataurl='" + hash_value + "'"
    res = run_sql(sql_str)

    if res[0][0] > 0: 
        return '1'
    else:
        return '0'

@app.route("/pictures", methods=['POST'])
def store_pictures():
    # get ID for this picture
    image_b64 = request.values['imageBase64']
    hash_value = hashlib.sha1(image_b64).hexdigest()

    db = mysql.get_db()
    cursor = db.cursor()
    sql_str = "INSERT INTO pictures (dataurl) VALUES ('" + hash_value + "')"
    cursor.execute(sql_str)
    db.commit()

    # remove the define part of image_b64
    image_b64 = re.sub('^data:image/.+;base64,', '', image_b64)
    # decode image_b64
    image_data = image_b64.decode('base64')
    image_data = cStringIO.StringIO(image_data)
    image_PIL = Image.open(image_data)
    image_PIL.save("/home/sol315/pictures/" + str(hash_value) + ".png")
    return hash_value 

@app.route('/updateFeatures', methods=['POST'])
def updateFeatures():
    result = request.get_json()
    unique_label = result['uniquelabel']
    features = {}

    for feature in result.iterkeys():
        value = result[feature]

        #fix the bug for N/A for cpu_cores
        if feature == 'cpu_cores':
            value = int(value)

        features[feature] = value

    doUpdateFeatures(unique_label, features)
    return flask.jsonify({'finished': features.keys()})
