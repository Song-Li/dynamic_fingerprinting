from database import Database
class Analyzer():
    ignores = ['id', 'time', 'browser_fingerprint', 'computer_fingerprint_1']
    db = Database('uniquemachine')
    cols = db.run_sql("SHOW COLUMNS FROM features")

    def __init__(self):
        pass

    def check_imgs_difference_dy_id(self, str_1, str_2):
        """
        check the differences of two gpu rendering result strs
        vars: str_1, str_2
        return: the differences
        """
        imgs_1 = str_1.split(',')
        imgs_2 = str_2.split(',')
        length = len(imgs_1)
        if len(imgs_2) != length:
            return "different number of imgs"
        imgs_1 = sorted(imgs_1, key=lambda img: int(img.split('_')[0]))
        imgs_2 = sorted(imgs_2, key=lambda img: int(img.split('_')[0]))

        res = {}
        for i in range(length):
            img_1 = imgs_1[i].split('_')[2]
            img_2 = imgs_2[i].split('_')[2]
            if img_1 != img_2:
                res[i] = (img_1, img_2)
        return res

            
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
            if self.cols[i][0] in self.ignores:
                continue
            if base_entry[i] != compare_entry[i]:
                if self.cols[i][0] == 'gpuimgs':
                    diff = self.check_imgs_difference_dy_id(base_entry[i], compare_entry[i])
                    print self.cols[i][0], diff
                else:
                    print self.cols[i][0]
        

def main():
    analyzer = Analyzer()
    analyzer.check_difference_by_id(12, 1)



if __name__ == "__main__":
    main()
