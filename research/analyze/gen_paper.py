from paperlib import Paperlib
from paperlib_helper import Paperlib_helper
from database import Database
from feature_lists import *

def main():
    db = Database('forpaper345') 
    paperlib = Paperlib(db)
    paperlib.draw_change_reason_by_date()
    #df = db.load_data(table_name = 'patched_tablefeaturechanges')
    #paperlib.feature_latex_table(get_table_feature_list(), df, output_file = './tmpout.dat')
    #paperlib.fingerprint_distribution()
    #df = db.load_data(filling = False, table_name = 'patched_all_pandas')
    #paperlib.feature_latex_table(get_browserid_list(), df, output_file = './res/table_bylabelchanges.dat')
    #db.generate_new_column(['ispc'], df, [db.ispc], aim_table = 'final_pandas')
    #paperlib.update_influence()
   # paperlib.change_reason_by_cookie(feature_name = 'browserid')
    #paperlib.get_statics()
    #paperlib.gpu_type_cnt()
   # paperlib.gpu_inference()
    #db.pandas_patches(df, export_table = 'patched_all_pandas')
    #paperlib.feature_correlation(df)
    #paperlib.cookie_pattern()
    #paperlib.generate_overall_change_database(feature_list = get_table_feature_list(), keepip = True, groupby_key = 'label', aim_table_name = 'bylabelchanges')
    #paperlib.generate_overall_change_database(feature_list = get_browserid_list(), keepip = True, groupby_key = 'label', aim_table_name = 'bylabelchanges')
    #paperlib.number_feature_per_feature_with_changes(df, 'browserid', 'browserfingerprint', max_num = 8, percentage = False)
    #df = db.load_data(table_name = 'tablefeaturechanges', limit = 10000)
    #paperlib.feature_correlation(df)
    #db.pandas_patches(df, export_table = 'patched_pandas')
    #paperlib.rebuild_fingerprintchanges()
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
