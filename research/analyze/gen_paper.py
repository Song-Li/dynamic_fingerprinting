from paperlib import Paperlib
from database import Database


def main():
    db = Database('forpaper345') 
    paperlib = Paperlib(db)
    #paperlib.get_all_feature_change_by_date()
    paperlib.feature_latex_table_paper()
    #paperlib.life_time_median()


if __name__ == "__main__":
    main()
