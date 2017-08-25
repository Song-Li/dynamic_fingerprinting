import urllib2
import urllib
import re
import json

for i in range(20):
    response = urllib2.urlopen('http://rj.baidu.com/soft/lists/' + str(i))
    html = response.read()
    p = re.compile(r' {"data(.*)}};')
    #remove the ;
    json_str = p.search(html).group(0)[0:-1]
    softwares = json.loads(json_str)['data']['softList']
    for software in softwares['list']:
        download_url = software['url']
        print "downloading..." + download_url
        if download_url.find(".exe") == -1:
            continue
        software_name = download_url[download_url.rfind('/') + 1:download_url.rfind('.exe') + 4]
        download_file = urllib.URLopener()
        download_file.retrieve(download_url, "./downloaded/" + software_name)
