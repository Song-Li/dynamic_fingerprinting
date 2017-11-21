# -*-coding:utf-8-*-
# import sys
# reload(sys)
# sys.setdefaultencoding('utf8')

f1 = open("choco_install_ins.txt",'a')
f = open("choco_app_name.txt",'r')
lines = f.readlines()
i = 1
for line in lines:
	if '</span>' not in line:
		if '</a>' not in line:
			if 'choco' in line:
				a = line.split('\n')[0]
				a = a + ' -y' + '\n'
				f1.write(a)
				i += 1

print i
f.close()
f1.close()
