from database import Database
class Analyzer():
    def __init__(self):
        self.db = Database('uniquemachine')
        self.cols = self.db.run_sql("SHOW COLUMNS FROM features")

    def check_difference_by_id(self, base_id, entry_id):
        """
        check the difference of two entries based on the ids
        vars: id1, id2
        return: the array of differences
        """
        base_entry = self.db.get_entry_by_id('features', base_id)
        compare_entry = self.db.get_entry_by_id('features', entry_id)
        length = len(base_entry)
        for i in range(length):
            if base_entry[i] != compare_entry[i]:
                print self.cols[i][0], base_entry[i]
        

def main():
    analyzer = Analyzer()
    analyzer.check_difference_by_id(2, 1)



if __name__ == "__main__":
    main()
