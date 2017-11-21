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
    req2=r'</span>(.+)'
    pat2=re.compile(req2) 
    con2=re.findall(req2,info)
    return con2

# url = 'https://chocolatey.org/packages'
# # print url
# # url = 'https://chocolatey.org/packages?q=application&sortOrder=package-download-count&page=1&prerelease=False&moderatorQueue=False'
# info = get_content(url)
# print info
# info1 = get_url(info)
# print info1

# f1 = open("choco_app_name.txt",'a')
# for i in range(0,len(info1)):
#     info1[i] = info1[i]+"\n"
#     f1.write(info1[i])
# f1.close()


for j in range(1, 177):

	url = 'https://chocolatey.org/packages?sortOrder=package-download-count&page=' + str(j) +'&prerelease=False&moderatorQueue=False'
	# print url
	# url = 'https://chocolatey.org/packages?q=application&sortOrder=package-download-count&page=1&prerelease=False&moderatorQueue=False'
	info = get_content(url)
	# print info
	info1 = get_url(info)
	# print info1
	f1 = open("choco_app_name.txt",'a')
	for i in range(0,len(info1)):

		a = info1[i].split('\r')[0]
		a = a + "\n"
		print a
		f1.write(a)
	f1.close()
	# break


