from paperlib import Paperlib
from database import Database

def main():
    db = Database('forpaper345') 
    paperlib = Paperlib(db)
    #paperlib.feature_change_by_browser_date_paper('browserfingerprint')
    #paperlib.feature_change_by_date_paper('agent')
    paperlib.feature_distribution_by_date('browser')
    #paperlib.new_return_user_by_date()
    #paperlib.get_all_feature_change_by_date()
    #paperlib.feature_latex_table_paper()
    #paperlib.life_time_median()
    #lower, upper, number = paperlib.verify_browserid_by_cookie()
    #print 'lower: {}, upper: {}, total: {}'.format(len(lower), len(upper), number)

if __name__ == "__main__":
    main()
