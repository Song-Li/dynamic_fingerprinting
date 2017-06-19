import MySQLdb
import ConfigParser, os

config = ConfigParser.ConfigParser()
config.read('password.ignore')
print config.get('mysql', 'username')
db = MySQLdb.connect(host='localhost',
                     user=user_name,
                     passwd = password,
                     db='uniquemachine')
