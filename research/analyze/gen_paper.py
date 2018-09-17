from paperlib import Paperlib
from paperlib_helper import Paperlib_helper
from database import Database

def main():
    db = Database('forpaper345') 
    paperlib = Paperlib(db)
    paperlib.rebuild_fingerprintchanges()
    #paperlib.draw_change_reason()
    #db.rebuild_table(df, export_table = 'pandas_features')
    #paperlib.generate_overall_change_database()
    #paperlib.feature_distribution_by_date('os')
    #paperlib.feature_change_by_browser_date_paper('browserfingerprint', method = 'day')
    #paperlib.feature_change_by_date_paper('agent')
    #paperlib.new_return_user_by_date()
    #paperlib.get_all_feature_change_by_date()
    #paperlib.feature_latex_table_paper()
    #paperlib.life_time_median()
    #lower, upper, number = paperlib.verify_browserid_by_cookie()
    #print 'lower: {}, upper: {}, total: {}'.format(len(lower), len(upper), number)

if __name__ == "__main__":
    main()
