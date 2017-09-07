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

with open(root + "mask.txt", 'r') as f:
    mask = json.loads(f.read())
with open(root + "mac_mask.txt", 'r') as fm:
    mac_mask = json.loads(fm.read())


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
            "flashFonts",
            "cc_audio",
            "hybrid_audio"
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


@app.route("/flashFonts", methods=['POST'])
def flashFonts():
    flashFonts = request.values['flashFonts']
    ID = request.values['id']
    sql_str = 'UPDATE features SET flashFonts="' + flashFonts + '" WHERE id=' + ID
    res = run_sql(sql_str)
    return "flash fonts finished" 

@app.route("/getCookie", methods=['POST'])
def getCookie():
    cookie = request.values['cookie']
    sql_str = 'SELECT count(id) FROM cookies WHERE cookie = "' + cookie + '"'
    res = run_sql(sql_str)
    if res[0][0] == 0:
        IP = request.remote_addr
        id_str = IP + str(datetime.now()) 
        cookie = hashlib.md5(id_str).hexdigest()
        sql_str = "INSERT INTO cookies (cookie) VALUES ('" + cookie + "')"
        run_sql(sql_str)

    return cookie



@app.route("/utils", methods=['POST'])
def utils():
    command = request.values['key']
    sql_str = ""
    if command == "keys":
        sql_str = "SELECT distinct IP, time, id, agent, label from features"
        res = run_sql(sql_str)
        # return the ip, time and the id
        return ",".join([r[0] + '~' + r[1].isoformat() + '~' + get_browser_from_agent(r[3]) + '~' + get_os_from_agent(r[3]) + '~' + str(r[2]) + '~' + str(r[4]) for r in res])

    elif command.split(',')[0] == "get_pictures_by_id":
        ID = command.split(',')[1]
        sql_str = "SELECT gpuImgs from features where id = " + ID
        res = run_sql(sql_str)
        imgs_str = res[0][0]
        return imgs_str

    elif command.split(',')[0] == "clear":
        if command.split(',')[1] == "seclab":
            clear_all_data()
            return "cleared"
        else:
            return "wrong password"

    elif command.split(',')[0] == "get_details":
        res = {}
        ID = command.split(',')[1]
        db = mysql.get_db()
        cursor = db.cursor()
        sql_str = "SELECT * FROM features WHERE id = '" + ID +"'"
        cursor.execute(sql_str)
        db.commit()
        row = cursor.fetchone()
        for i in range(len(row)):
            value = row[i]
            name = cursor.description[i][0]
            res[name] = value

        return flask.jsonify(res)

    elif command.split(',')[0] == "label":
        label = command.split(',')[1]
        #db = mysql.get_db()
        #cursor = db.cursor()
        sql_str = "INSERT INTO labels (id, date_created, label) VALUES (null, null, '" + label +  "')"
        #cursor.execute(sql_str)
        #db.commit()
        run_sql(sql_str)
        return "label created"
    elif command.split(',')[0] == "delete-entry":
        ID = command.split(',')[1]
        sql_str = "SELECT gpuimgs FROM features where id = " + ID
        res = run_sql(sql_str)
        res_str = res[0][0].split(',')
        # delete from features table
        sql_str = "DELETE FROM features WHERE ID = " + ID
        run_sql(sql_str)

        for r in res_str:
            pic_id = r.split('_')[1]
            sql_str = "delete from pictures where id = " + pic_id
            run_sql(sql_str)
            os.system("rm " + pictures_path + pic_id + ".png")

    elif command == "get_groups":
        sql_str = "SELECT id,label  from labels"
        res = run_sql(sql_str)
        return '~'.join(['$'.join(map(str,r)) for r in res]) 




@app.route("/result", methods=['POST'])
def get_result():
    image_id = request.values['image_id']
    sql_str = "SELECT dataurl from pirctures where ID={image_id}"
    db = mysql.get_db()
    cursor = db.cursor()
    cursor.execute(sql_str)
    db.commit()
    return cursor.fetchone()[0]

@app.route("/pictures", methods=['POST'])
def store_pictures():
    # get ID for this picture
    image_b64 = request.values['imageBase64']
    hash_value = hashlib.md5(image_b64).hexdigest()

    db = mysql.get_db()
    cursor = db.cursor()
    sql_str = "INSERT INTO pictures (dataurl) VALUES ('" + hash_value + "')"
    cursor.execute(sql_str)
    db.commit()

    sql_str = "SELECT LAST_INSERT_ID()"
    cursor.execute(sql_str)
    ID = cursor.fetchone()
    db.commit()


    # remove the define part of image_b64
    image_b64 = re.sub('^data:image/.+;base64,', '', image_b64)
    # decode image_b64
    image_data = image_b64.decode('base64')
    image_data = cStringIO.StringIO(image_data)
    image_PIL = Image.open(image_data)
    image_PIL.save("/home/sol315/pictures/" + str(hash_value) + ".png")
    return hash_value 

@app.route('/details', methods=['POST'])
def details():
    res = {}
    ID = request.get_json()["ID"]
    db = mysql.get_db()
    cursor = db.cursor()
    sql_str = "SELECT * FROM features WHERE browser_fingerprint = '" + ID +"'"
    cursor.execute(sql_str)
    db.commit()
    row = cursor.fetchone()
    for i in range(len(row)):
        value = row[i]
        name = cursor.description[i][0]
        res[name] = value

    if 'fonts' in res:
        fs = list(res['fonts'])
        for i in range(len(mask)):
            fs[i] = str(int(fs[i]) & mask[i] & mac_mask[i])
        res['fonts'] = ''.join(fs)

    return flask.jsonify(res)

@app.route('/features', methods=['POST'])
def features():
    agent = ""
    accept = ""
    encoding = ""
    language = ""
    IP = ""

    try:
        agent = request.headers.get('User-Agent')
        accpet = request.headers.get('Accept')
        encoding = request.headers.get('Accept-Encoding')
        language = request.headers.get('Accept-Language')
        IP = request.remote_addr
    except:
        pass

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
            "gpuImgs", 
            "timezone", 
            "plugins", 
            "cookie", 
            "localstorage", 
            "adBlock", 
            "cpu_cores", 
            "canvas_test", 
            "audio",
            "flashFonts",
            "cc_audio",
            "hybrid_audio"
            ]

    cross_feature_list = [
            "timezone",
            "jsFonts",
            "langsDetected",
            "audio"
            ]
    

    result = request.get_json()

    single_hash = "single"
    single_hash_str = "single"
    cross_hash = "cross"

    #with open("fonts.txt", 'a') as f:
        #f.write(result['fonts'] + '\n')

    jsFonts = list(result['jsFonts'])

    cnt = 0
    for i in range(len(jsFonts)):
        if jsFonts[i] == '1':
            cnt += 1

    result['agent'] = agent
    result['accept'] = accept
    result['encoding'] = encoding
    result['language'] = language
    

    print agent
           
    feature_str = "IP"
    value_str = "'" + IP + "'"


    for feature in feature_list:
        
        if result[feature] is not "":
            value = result[feature]
        else:
            value = "NULL"
        
        # set hash_str as the pure value from js
        hash_str = str(value)

        feature_str += "," + feature
        # for gpu imgs
        if feature == "gpuImgs":
            # only keep the pure value of every result
            hash_str = ",".join(v.split('_')[0] for k, v in value.iteritems())
            # change value to str
            value = ",".join('%s_%s' % (k, v) for k, v in value.iteritems())
        else:
            value = str(value)

#        if feature == "cpu_cores" and type(value) != 'int':
#           value = -1
#fix the bug for N/A for cpu_cores
        if feature == 'cpu_cores':
            value = int(value)

        if feature == 'langsDetected':
            value = str("".join(value))
            value = value.replace(" u'", "")
            value = value.replace("'", "")
            value = value.replace(",", "_")
            value = value.replace("[", "")
            value = value.replace("]", "")
            value = value[1:]

        # if feature is gpuImgs
        # we need to ignore the picture id
        value_str += ",'" + str(value) + "'"
        #print feature, hash_object.hexdigest()
        single_hash_str += hash_str


    result['jsFonts'] = jsFonts
    for feature in cross_feature_list:
        cross_hash += str(result[feature])
        hash_object = hashlib.md5(str(result[feature]))

    hash_object = hashlib.md5(single_hash_str)
    single_hash = hash_object.hexdigest()

    hash_object = hashlib.md5(cross_hash)
    cross_hash = hash_object.hexdigest()

    # this is the cookie of this computer
    label = result['label']

    feature_str += ',browser_fingerprint,computer_fingerprint_1,label'
    value_str += ",'" + single_hash + "','" + cross_hash + "','" + label + "'"

    db = mysql.get_db()
    cursor = db.cursor()
    sql_str = "INSERT INTO features (" + feature_str + ") VALUES (" + value_str + ");"
    cursor.execute(sql_str)
    db.commit()

    sql_str = "SELECT LAST_INSERT_ID()"
    cursor.execute(sql_str)
    ID = cursor.fetchone()[0]
    db.commit()

    print (single_hash, cross_hash, ID)
    return flask.jsonify({"single": single_hash, "cross": cross_hash, "id": ID})
