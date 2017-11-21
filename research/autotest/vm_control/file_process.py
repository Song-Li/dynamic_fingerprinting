# -*-coding:utf-8-*-
# import sys
# reload(sys)
# sys.setdefaultencoding('utf8')

# while(1):
f1 = open("choco_install_ins.txt",'r')
# f = open("choco_app_name.txt",'r')
lines = f1.readlines()
f1.close()
f = open("choco_install_ins.txt",'w')
# next(lines)
i = 0
# print lines[-1]
if 'hadoop' in lines[0]:
	f.write(lines[0])
	f.close()
	break
for line in lines:

	if i == 0:
		i += 1
		continue
	# print line
	f.write(line)
f.close()

