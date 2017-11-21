# -*-coding:utf-8-*-
# import sys
# reload(sys)
# sys.setdefaultencoding('utf8')

import string
import time
import re
import requests
import urllib
import urllib2
import numpy as np


def get_content(url):

    html=urllib.urlopen(url)
    content=html.read()
    html.close()
    return content

def get_url(info):
    req2=r'<input type="checkbox" class="js-homepage-app-checkbox" name="apps" value="(.+?)"'
    pat2=re.compile(req2) 
    con2=re.findall(pat2,info)
    return con2


url = 'https://ninite.com/'
info = get_content(url)
info1 = get_url(info)

f1 = open("app_name.txt",'a')
for i in range(0,len(info1)):
    info1[i] = info1[i]+"\n"
    f1.write(info1[i])
f1.close()


