import MySQLdb
import ConfigParser, os

config = ConfigParser.ConfigParser()
db = MySQLdb.connect(host='localhost',
                     user=user_name,
                     passwd = password,
                     db='uniquemachine')
