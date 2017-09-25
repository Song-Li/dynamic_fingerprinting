import pandas as pd
import datetime
from database import Database

db = Database('uniquemachine')
df = pd.read_sql('select * from features;', con=db.get_db())    

cookies = df.groupby('label')

length = 0
for key, items in cookies:
    if items['browser_fingerprint'].nunique() > 1:
        min_time = datetime.datetime.now()
        max_time = datetime.datetime.now() - datetime.timedelta(days = 100)
        for index, row in items.iterrows():
            if min_time > row['time']:
                min_time = row['time']
                min_row = row
            if max_time < row['time']:
                max_time = row['time']
                max_row = row
        if max_time - min_time > datetime.timedelta(days = 2):
            length += 1

    if min_row['gpuimgs'] == max_row['gpuimgs']:
        print min_row['gpuimgs']
        print max_row['gpuimgs']
        print "======================================================="

print length
