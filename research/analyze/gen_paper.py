from paperlib import Paperlib
from database import Database


def main():
    db = Database('forpaper') 
    paperlib = Paperlib(db)
    #paperlib.feature_latex_table_paper()
    paperlib.life_time_median()


if __name__ == "__main__":
    main()
