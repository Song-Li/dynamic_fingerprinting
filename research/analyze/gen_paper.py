from paperlib import Paperlib
from paperlib_helper import Paperlib_helper
from database import Database
from feature_lists import *

def main():
    db = Database('forpaper345') 
    #df = db.load_data(table_name = 'patched_pandas')
    paperlib = Paperlib(db)
    paperlib.change_reason_by_cookie(feature_name = 'browser')
    #paperlib.get_statics()
    #paperlib.gpu_type_cnt()
    #paperlib.gpu_inference()
    #df = db.load_data(table_name = 'patched_tablefeaturechanges')
    #db.pandas_patches(df, export_table = 'patched_all_pandas')
    #paperlib.feature_correlation(df)
    #paperlib.cookie_pattern()
    #paperlib.generate_overall_change_database(feature_list = get_table_feature_list(), keepip = True, aim_table_name = 'patched_tablefeaturechanges')
    #paperlib.number_feature_per_feature_with_changes(df, 'browserid', 'browserfingerprint', max_num = 8, percentage = False)
    #df = db.load_data(table_name = 'tablefeaturechanges', limit = 10000)
    #paperlib.feature_correlation(df)
    #paperlib.feature_latex_table(get_table_feature_list(), df, output_file = './res/feature_table_1.dat')
    #db.pandas_patches(df, export_table = 'patched_pandas')
    #paperlib.rebuild_fingerprintchanges()
    #paperlib.draw_change_reason()
    #db.rebuild_table(df, export_table = 'pandas_features')
    #paperlib.feature_distribution_by_date('os')
    #paperlib.feature_change_by_browser_date_paper('browserfingerprint', method = 'day')
    #paperlib.feature_change_by_date_paper('agent')
    #paperlib.new_return_user_by_date()
    #paperlib.get_all_feature_change_by_date()
    #paperlib.feature_latex_table()
    #paperlib.life_time_median()
    #lower, upper, number = paperlib.verify_browserid_by_cookie()
    #print 'lower: {}, upper: {}, total: {}'.format(len(lower), len(upper), number)

if __name__ == "__main__":
    main()
