from database import Database
class Analyzer():
    def __init__(self):
        self.db = Database('uniquemachine')

    def test(self):
        sql_str = "SELECT count(*) FROM features where ip like '%128%'"
        print self.db.run_sql(sql_str)


def main():
    analyzer = Analyzer()
    analyzer.test()

if __name__ == "__main__":
    main()
