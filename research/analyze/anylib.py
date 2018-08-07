from database import Database
from forpaper import *

def get_success_rate(db_name):
    """
    get the success of table "features"  of a db
    success rate is defined as jsFonts is not NULL
    """
    db = Database(db_name)
    df = db.load_data(feature_list = ['jsFonts', 'time'], table_name = 'features')
    df = round_time_to_day(df)
    min_date = min(df['time'])
    max_date = max(df['time'])
    lendate = (max_date - min_date).days
    datelist = [min_date + datetime.timedelta(days = i) for i in range(lendate + 3)]
    success_fail = {}
    for date in datelist:
        success_fail[date] = [0,0]

    for row in tqdm(df.itertuples()):
        jsFonts = getattr(row, 'jsFonts')
        time = getattr(row, 'time')
        if pd.notnull(jsFonts):
            success_fail[time][0] += 1
        else:
            success_fail[time][1] += 1

    res = sorted(success_fail.iteritems())
    f = safeopen('./res/success_rate.dat', 'w')
    for item in res:
        total = item[1][1] + item[1][0]
        if total == 0:
            continue
        f.write('{} {} {}\n'.format(item[0], item[1], float(item[1][0]) / float(item[1][1] + item[1][0])))
    f.close()

def main():
    get_success_rate(db_name = 'forpaper')

if __name__ == '__main__':
    main()
