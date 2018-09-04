from database import Database
from forpaper import *
from extractinfo import *

def get_success_rate(db_name, by_feature_name = 'browser'):
    """
    get the success of table "features"  of a db
    success rate is defined as jsFonts is not NULL
    """
    db = Database(db_name)
    df = db.load_data(feature_list = ['jsFonts', 'time', by_feature_name],
            table_name = 'handled_features')
    df = round_time_to_day(df)
    min_date = min(df['time'])
    max_date = max(df['time'])
    lendate = (max_date - min_date).days
    datelist = [min_date + datetime.timedelta(days = i) for i in range(lendate + 3)]
    success_fail = {}
    for date in datelist:
        success_fail[date] = {}

    # get the success fail rate for every val in feature
    # and for every day
    # we get the number of feature val
    # sort them by the number of appearance
    feature_val_list = {}
    for row in tqdm(df.itertuples()):
        jsFonts = getattr(row, 'jsFonts')
        time = getattr(row, 'time')
        feature_val = getattr(row, by_feature_name)

        if feature_val in feature_val_list:
            feature_val_list[feature_val] += 1
        else:
            feature_val_list[feature_val] = 1

        if feature_val not in success_fail[time]:
            success_fail[time][feature_val] = [0,0]
        if pd.notnull(jsFonts):
            success_fail[time][feature_val][0] += 1
        else:
            success_fail[time][feature_val][1] += 1


    feature_val_list = sorted(feature_val_list.iteritems(), key = lambda(k, v): (-v, k))

    f = safeopen('./res/success_rate_{}.dat'.format(by_feature_name), 'w')
    f.write('Date\t')
    for feature_val in feature_val_list:
        f.write('{}({})\t'.format(feature_val[0].replace(' ', '_'), feature_val[1]))
    f.write('\n')
    
    res = sorted(success_fail.iteritems())
    for row in res:
        cur_date = row[0]
        f.write('{}-{}-{}\t'.format(cur_date.year, cur_date.month, cur_date.day))
        for feature_val in feature_val_list:
            # here we just keep the value of feature
            # ignore the detailed number of appearance
            feature_val = feature_val[0]

            percentage = 0
            if feature_val in row[1]:
                item = row[1][feature_val]
                total = item[1] + item[0]
                if total != 0:
                    percentage = float(item[0]) / float(total)
            f.write('{0:.3f}\t'.format(percentage))
        f.write('\n')
    f.close()

def feature_distribution_by_date(feature_name, percentage = False):
    """
    for a feature, get the distribution of different values
    this function will return a stacked dat file
    """
    show_number = 10
    db = Database('forpaper345')
    df = db.load_data(feature_list = ['time', feature_name], table_name = 'handled_features')
    min_date = min(df['time'])
    min_date = min_date.replace(microsecond = 0, second = 0, minute = 0, hour = 0)
    max_date = max(df['time'])
    lendate = (max_date - min_date).days
    datelist = [min_date + datetime.timedelta(days = i) for i in range(lendate + 3)]
    # round time to day
    df = round_time_to_day(df)
    grouped = df.groupby([feature_name, 'time'])
    res = {}
    total_numbers = {}
    daily_all_numbers = {}
    for date in datelist:
        res[date] = {}
        daily_all_numbers[date] = 0

    for key, group in tqdm(grouped):
        cur_number = len(group.index)

        daily_all_numbers[key[1]] += cur_number
        if key[0] not in res[key[1]]:
            res[key[1]][key[0]] = 0
        res[key[1]][key[0]] += cur_number

        if key[0] not in total_numbers:
            total_numbers[key[0]] = 0
        total_numbers[key[0]] += cur_number


    f = safeopen('./featureNumberByDate/{}_all'.format(feature_name), 'w')
    total_numbers = sorted(total_numbers.iteritems(), key=lambda (k,v): (-v,k))
    total_numbers = total_numbers[:show_number]
    # print feature names
    for val in total_numbers:
        f.write('{} '.format(val[0]))
    f.write('others\n')

    if percentage:
        for date in datelist:
            for feature in res[date]:
                # avoid divide by zero
                if daily_all_numbers[date] == 0:
                    daily_all_numbers[date] = 1
                res[date][feature] = float(res[date][feature]) / float(daily_all_numbers[date])


    for date in datelist:
        cur_sum = 0
        f.write('{}-{}-{}'.format(date.year, date.month, date.day))
        for feature in total_numbers:
            if feature[0] not in res[date]:
                f.write(' 0')
                continue
            cur_sum += res[date][feature[0]]
            f.write(' {}'.format(res[date][feature[0]]))
        if percentage:
            f.write(' {}\n'.format(1.0 - cur_sum))
        else:
            f.write(' {}\n'.format(daily_all_numbers[date] - cur_sum))
    f.close()

def cookie_distribution(df):
    #TODO not sure how to write this
    """
    anylise the cookie, for multi cookie single browserid
    """
    pass

def main():
    db = Database('forpaper345')
    #db.generate_new_column(['os', 'browser'], 'features', [get_os_from_agent, get_browser_from_agent], aim_table = 'handled_features')
    #feature_distribution_by_date('os', percentage = True)
    #get_success_rate(db_name = 'forpaper345', by_feature_name = 'os')

if __name__ == '__main__':
    main()
