
from selenium import webdriver
import time

url = 'https://ninite.com/'


f = open("app_name.txt")
lines = f.readlines()

for line in lines:
	url_new = url + line.split('\n')[0]
	browser = webdriver.Chrome()
	browser.get(url_new)
	time.sleep(5)
	browser.quit()
# inputs = browser.find_elements_by_tag_name('input') 
# but = browser.find_elements_by_tag_name('button')
# # print but[0].get_attribute('accesskey')
# # print len(but)
# for j in range(0, len(but)):
# 	but[j].get_attribute('accesskey') == 'g'
# # print j
# f = open("app_name.txt")
# lines = f.readlines()
# # inputss = inputs[1]
# i = 1
# for line in lines:
# 	if inputs[i].get_attribute('type') == 'checkbox':
# 		if inputs[i].get_attribute('value') == line.split('\n')[0]:
# 			inputs[i].click() 
	
# 	time.sleep(2)

# 	but[j].click()

# 	inputs[i].click()
# 	time.sleep(30)

# 	i += 1

# browser.quit()

# print lines
# ********************************************
# for j in range(0,5):
# 	browser = webdriver.Chrome()
# 	browser.get('https://ninite.com/')
# 	browser.quit()
# print len(inputs)
# print len(lines)
# inputs = next(inputs)

# *********************************************
# i = 0
# for input in inputs:  
# 	# if i <= len(inputs):
# 	if i >= 1:
# 		print (lines[i-1].split('\n')[0])
# 	if input.get_attribute('type') == 'checkbox': 
# 		input.click()  
# 		time.sleep(2)
# 	i += 1 
# 	if i > len(lines):
# 		break 
# time.sleep(2)