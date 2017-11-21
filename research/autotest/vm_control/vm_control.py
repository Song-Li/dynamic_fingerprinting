# -*-coding:utf-8-*-
# import sys
# reload(sys)
# sys.setdefaultencoding('utf8')

import os
import time

i = 0
t = 0
while(1):
	f = open('/Users/wangningfei/Desktop/Lehigh_Research/YinzhiCao/sharedfilewithwin7/test_finish.txt','r')
	lines_f = f.readlines()
	# print line_f
	if len(lines_f) == 0:
		continue
	if 'finished' in lines_f[0]:
		f.close()
		break
	f.close()
	# f = open('/Users/wangningfei/Desktop/Lehigh_Research/YinzhiCao/sharedfilewithwin/******','w+')
	f1 = open('/Users/wangningfei/Desktop/Lehigh_Research/YinzhiCao/sharedfilewithwin7/test_finish_ins.txt','r')
	# lines = f.readlines()
	lines_f1 = f1.readlines()
	f1.close()
	if t == 1:
		# time.sleep(5)
		if len(lines_f1) == 0:
			continue
		if '1' in lines_f1[0]:
			if i == 1:
				os.system('vboxmanage controlvm win7_1 savestate')
				time.sleep(10)
				os.system('VBoxManage unregistervm win7_1')
				time.sleep(1)
				os.system('rm -r /Users/wangningfei/VirtualBox\ VMs/win7_1')
				t = 0
				f_change = open('/Users/wangningfei/Desktop/Lehigh_Research/YinzhiCao/sharedfilewithwin7/choco_install_ins.txt','r')
				lines_change = f_change.readlines()
				f_change.close()
				f_change_w = open('/Users/wangningfei/Desktop/Lehigh_Research/YinzhiCao/sharedfilewithwin7/choco_install_ins.txt','w+')
				for ii in range(1, len(lines_change)):
				# for line_change in lines_change:
				# 	if ii == 0:
				# 		ii += 1
				# 		continue
				# 	# print line
					f_change_w.write(lines_change[ii])
				f_change_w.close()
			else:
				os.system('vboxmanage controlvm win7_2 savestate')
				time.sleep(10)
				os.system('VBoxManage unregistervm win7_2')
				time.sleep(1)
				os.system('rm -r /Users/wangningfei/VirtualBox\ VMs/win7_2')
				t = 0
				f_change = open('/Users/wangningfei/Desktop/Lehigh_Research/YinzhiCao/sharedfilewithwin7/choco_install_ins.txt','r')
				lines_change = f_change.readlines()
				f_change.close()
				f_change_w = open('/Users/wangningfei/Desktop/Lehigh_Research/YinzhiCao/sharedfilewithwin7/choco_install_ins.txt','w+')
				for ii in range(1, len(lines_change)):
				# for line_change in lines_change:
				# 	if ii == 0:
				# 		ii += 1
				# 		continue
				# 	# print line
					f_change_w.write(lines_change[ii])
				f_change_w.close()
			f2 = open('/Users/wangningfei/Desktop/Lehigh_Research/YinzhiCao/sharedfilewithwin7/test_finish_ins.txt','w+')
			# lines_f2 = f2.readlines()
			f2.write('0')
			f2.close()
		continue
	if i == 0:
		os.system('vboxmanage clonevm win7 --name win7_1')
		os.system('vboxmanage registervm /Users/wangningfei/VirtualBox\ VMs/win7_1/win7_1.vbox')
		os.system('vboxmanage startvm win7_1')
		time.sleep(10)
		os.system('vboxmanage controlvm win7_1 poweroff')
		time.sleep(10)
		os.system('vboxmanage startvm win7_1')
		time.sleep(60)
		t = 1
		i = 1
		continue
	if i == 1:
		os.system('vboxmanage clonevm win7 --name win7_2')
		os.system('vboxmanage registervm /Users/wangningfei/VirtualBox\ VMs/win7_2/win7_2.vbox')
		os.system('vboxmanage startvm win7_2')
		time.sleep(10)
		os.system('vboxmanage controlvm win7_2 poweroff')
		time.sleep(10)
		os.system('vboxmanage startvm win7_2')
		time.sleep(60)
		t = 1
		i = 0 
		continue
	# time.sleep()
	# os.system('')