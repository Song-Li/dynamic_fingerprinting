import os
import glob
import csv

def is_float(string):
	try:
		float(string)
		return True
	except ValueError:
		return False

# Chrome, Firefox, Safari, SamsungBrowser, Edge
def count_changes(lines, percentages):
	browsers = ['Chrome', 'Firefox', 'Safari', 'SamsungBrowser', 'Edge']
	browser_percentages = {}
	version_percentages = {}
	browser_every_percentages = {}
	version_every_percentages = {}
	for line in lines:
		browser_before = {}
		version_before = None
		browser_after = {}
		version_after  = None
		if 'agent' in line:
			index = lines.index(line)
			before_list = line.split("set")[1].split("'")[1::2]
			after_list = line.split("set")[2].split("'")[1::2]
			for item in before_list:
				item = item.strip(";)")
				test = item.replace("_", "")
				if '/' in item:
					if item.split("/")[0] in browsers:
						if item.split("/")[0] not in browser_every_percentages:
							browser_every_percentages[item.split("/")[0]] = {}
						browser_before[item.split("/")[0]] = item.split("/")[1].split(".")[0]
				elif '_' in item and test.isdigit():
					version_before = item
				else:
					continue
			for item in after_list:
				item = item.strip(";)")
				test = item.replace("_", "")
				if '/' in item:
					if item.split("/")[0] in browsers:
						if item.split("/")[0] not in browser_percentages:
							browser_percentages[item.split("/")[0]] = {}
						browser_after[item.split("/")[0]] = item.split("/")[1].split(".")[0]
				elif '_' in item and test.isdigit():
					version_after = item
				else:
					continue

			for key in browser_before:
				if key in browser_after:
					if browser_before[key] != browser_after[key]:
						if browser_after[key] not in browser_percentages[key]:
							browser_percentages[key][browser_after[key]] = percentages[index]
						else:
							browser_percentages[key][browser_after[key]] += percentages[index]
						if browser_before[key] not in browser_every_percentages[key]:
							browser_every_percentages[key][browser_before[key]] = {}
							browser_every_percentages[key][browser_before[key]][browser_after[key]] = percentages[index]
						else:
							if browser_after[key] not in browser_every_percentages[key][browser_before[key]]:
								browser_every_percentages[key][browser_before[key]][browser_after[key]] = percentages[index]
							else:
								browser_every_percentages[key][browser_before[key]][browser_after[key]] += percentages[index]

			if version_before != None and version_after != None and version_before != version_after:
				if version_after not in version_percentages:
					version_percentages[version_after] = percentages[index]
				else:
					version_percentages[version_after] += percentages[index]
				if version_before not in version_every_percentages:
					version_every_percentages[version_before] = {}
					version_every_percentages[version_before][version_after] = percentages[index]
				else:
					if version_after not in version_every_percentages[version_before]:
						version_every_percentages[version_before][version_after] = percentages[index]
					else:
						version_every_percentages[version_before][version_after] += percentages[index]


	print "\nbrowser\n"
	print browser_percentages
	print "\nversion\n"
	print version_percentages
	print "\nbrowser every change\n"
	print browser_every_percentages
	print "\nversion every chang\n"
	print version_every_percentages

	return browser_percentages, version_percentages, browser_every_percentages, version_every_percentages


if __name__ == '__main__':
	dirs = ['audio', 'canvastest', 'cookie', 'encoding', 'gpu', 'ipcity', 'ipcountry', 'ipregion', 
			'jsFonts', 'langsdetected', 'language', 'localstorage', 'plugins']
	path = '/Users/xueqi/projs/dynamic_fingerprinting/research/analyze/changeres'
	output_path = '/Users/xueqi/Desktop/'
	for dir_name in dirs:
		print dir_name
		for filename in glob.glob(os.path.join(path + '/' + dir_name, '*')):
			lines = []
			percentages = []
			with open(filename, 'r') as file: 
				for line in file:
					line = line.strip('\n')
					if is_float(line):
						percentages.append(float(line))
					elif 'doing' in line:
						continue
					else:	
						lines.append(line)

			a, b, c, d = count_changes(lines, percentages)
			write_file = csv.writer(open(filename+".csv", "w+"))

			write_file.writerow(['browsers final changes'])
			for key1, val1 in a.items():
				for key2, val2 in val1.items():
					write_file.writerow([key1, "", key2, val2])

			write_file.writerow([''])
			write_file.writerow(['versions final changes'])
			for key1, val1 in b.items():
				write_file.writerow(["", key1, val1])

			write_file.writerow([''])
			write_file.writerow(['browsers every changes'])
			for key1, val1 in c.items():
				for key2, val2 in val1.items():
					for key3, val3 in val2.items():
						write_file.writerow([key1, key2, key3, val3])

			write_file.writerow([''])
			write_file.writerow(['versions every changes'])
			for key1, val1 in d.items():
				for key2, val2 in val1.items():
					write_file.writerow([key1, key2, val2])
