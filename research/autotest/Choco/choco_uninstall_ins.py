# -*-coding:utf-8-*-
# import sys
# reload(sys)
# sys.setdefaultencoding('utf8')

f = open("choco_install_ins.txt",'r')
f1 = open("choco_uninstall_ins.txt",'a')
lines = f.readlines()
i = 1
for line in lines:
	a = line.split(' ')
	# print a
	b = a[0] + ' uninstall ' + a[-1]
	f1.write(b)
	i += 1
print i
f.close()
f1.close()