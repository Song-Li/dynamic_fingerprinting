import urllib2
import urllib
import re
import json
import time

size = 0
start = time.time()
for i in range(2,1213):
    response = urllib2.urlopen('http://rj.baidu.com/soft/lists/0/' + str(i))
    html = response.read()
    p = re.compile(r' {"data(.*)}};')
    #remove the ;
    json_str = p.search(html).group(0)[0:-1]
    softwares = json.loads(json_str)['data']['softList']
    for software in softwares['list']:
        print "Speed: " + "%.2f" % (size / (time.time() - start)) + "M/s. " + str(size) + "M of data downloaded Time: " + str(int(time.time() - start)) + "s"
        download_url = software['url']
        if download_url.find(".exe") == -1:
            continue
        software_name = download_url[download_url.rfind('/') + 1:download_url.rfind('.exe') + 4]
        download_file = urllib.URLopener()
        length = urllib.urlopen(download_url).info().getheaders("Content-Length")[0]
        this_size = int(length) / 1024 / 1024
        size += this_size
        print "Downloading..." + download_url + " Size: " + str(this_size) + "M"
        try:
            download_file.retrieve(download_url, "./downloaded/" + software_name)
        except:
            print "error: ", download_url

