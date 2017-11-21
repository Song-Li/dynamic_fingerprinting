from selenium import webdriver
import time
import os

url = "http://www.baidu.com"
os.system("cd /")
os.system("cd C:\\Users\\Ningfei\\Desktop")
f = open("app_name.txt")
lines = f.readlines()

for line in lines:
	print line
	install_ins = 'NinitePro.exe /silent report.txt /select ' + line.split('\t')[-1]
	# time.sleep(20)
	print install_ins
	os.system(install_ins)
	# time.sleep(15)
	rep = open('report.txt')
	k = rep.readlines()
	# print k[0].split('\n')[0]
	if k[0].split('\n')[0] == 'OK':
		print "install success"
		browser = webdriver.Chrome()
		browser.get(url)
		browser.quit()	

	log = open('log.txt', 'a')
	log.write(line)
	for ii in range(0, len(k)):
		log.write(k[ii])
	log.write('\n')
	log.close()
	
	# # url_new = url + line.split('\n')[0]

	time.sleep(5)
	
	# print uninstall_ins	
	# browser.quit()
	if k[0].split('\n')[0] == 'OK':
		# print "install success"
		a = line.split('\t')[-1]
		uninstall_ins = 'NinitePro.exe /select ' + a.split('\n')[0] + ' /silent report.txt /uninstall'

		os.system(uninstall_ins)
	# time.sleep(25)
		print "uninstall success"
	rep.close()
