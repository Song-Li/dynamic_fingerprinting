# -*-coding:utf-8-*-
# import sys
# reload(sys)
# sys.setdefaultencoding('utf8')

#install choco: @powershell -NoProfile -ExecutionPolicy Bypass -Command "iex ((new-object net.webclient).DownloadString('https://chocolatey.org/install.ps1'))" && SET PATH=%PATH%;%ALLUSERSPROFILE%\chocolatey\bin

import os
from selenium import webdriver
import time

os.system('z:')
url = "http://www.baidu.com"
f = open("choco_install_ins.txt")
lines = f.readlines()

# for line in lines:
line = lines[0]
print line

a = os.system(line)
if a == 0:
	print "install success"
	browser = webdriver.Chrome()
	browser.get(url)
	browser.quit()	
	log = open('log.txt', 'a')
	log.write(line)
	log.write('success')
	log.write('\n')
	log.close()
else:
	print "install fail"
	log = open('log.txt', 'a')
	log.write(line)
	log.write('unsuccess')
	log.write('\n')
	log.close()

f1 = open('test_finish.txt','w+')
# f = open("choco_app_name.txt",'r')
# lines1 = f1.readlines()
if 'hadoop' in line:
	# f.write(lines1[0])
	f1.write('finished')
	f1.close()
else:
	f1.write('no')
	f1.close()
	# break
f2 = open('test_finish_ins.txt','w+')
			# lines_f2 = f2.readlines()
f2.write('1')
f2.close()

