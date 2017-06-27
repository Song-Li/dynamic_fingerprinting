from database import Database
import argparse

class Analyzer():
    ignores = ['id', 'time', 'browser_fingerprint', 'computer_fingerprint_1', "fonts"]
    db = Database('uniquemachine')
    cols = db.run_sql("SHOW COLUMNS FROM features")

    def __init__(self):
        pass

    def check_imgs_difference_by_str(self, str_1, str_2):
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

    def check_fonts_difference_by_str(self, str_1, str_2):
        """
        check the differences of two font lists
        vars: str_1, str_2
        return: the differences
        """
        if str_1 == None or str_2 == None:
            return ([], [])
        fonts_1 = str_1.split('_')
        fonts_2 = str_2.split('_')
        f1 = []
        f2 = []
        for f in fonts_1:
            if f not in fonts_2:
                f1.append(f)

        for f in fonts_2:
            if f not in fonts_1:
                f2.append(f)

        return (f1, f2)

    def output_diff(self, keys, values):
        length = len(keys)
        for i in range(length):
            print '\t'+ str(keys[i]) + ': \t' + str(values[i])

            
    def check_difference_by_id(self, base_id, entry_id, detail):
        """
        check the difference of two entries based on the ids
        vars: id1, id2, print details or not
        return: the array of differences
        """
        base_entry = self.db.get_entry_by_id('features', base_id)
        compare_entry = self.db.get_entry_by_id('features', entry_id)
        length = len(base_entry)
        res = {}
        for i in range(length):
            if self.cols[i][0] in self.ignores:
                continue
            if base_entry[i] != compare_entry[i]:
                if self.cols[i][0] == 'gpuimgs':
                    diff = self.check_imgs_difference_by_str(base_entry[i], compare_entry[i])
                    if len(diff) == 0:
                        continue
                    res[self.cols[i][0]] = diff
                    if (detail):
                        print self.cols[i][0]
                        self.output_diff(diff.keys(), diff.values())
                elif self.cols[i][0] == 'flashFonts':
                    diff = self.check_fonts_difference_by_str(base_entry[i], compare_entry[i])
                    res[self.cols[i][0]] = diff
                    if detail == True:
                        print self.cols[i][0]
                        self.output_diff([base_id, entry_id], diff)
                else:
                    res[self.cols[i][0]] = [base_entry[i], compare_entry[i]]
                    if detail == True:
                        print self.cols[i][0]
                        self.output_diff([base_id, entry_id], [base_entry[i], compare_entry[i]])
        return res

    def cal_gpuimgs_distance(self, diff):
        return (1, "change the video card")

    def cal_flashFonts_distance(self, diff):
        return (1, "add fonts " + str(diff[1]))

    def cal_agent_distance(self, diff):
        return (1, "change agent to " + diff[1])


    def cal_distance(self, diff):
        dis = 0
        way = ""
        for feature in diff:
            if feature == "gpuimgs":
                gpuimgs_change = self.cal_gpuimgs_distance(diff[feature])
                dis += gpuimgs_change[0]
                way += gpuimgs_change[1]
            elif feature == "agent":
                agent_change = self.cal_agent_distance(diff[feature])
                dis += agent_change[0]
                way += agent_change[1]
            elif feature == "flashFonts":
                flashFonts_change = self.cal_flashFonts_distance(diff[feature])
                dis += flashFonts_change[0]
                way += flashFonts_change[1]
            elif feature == "label":
                dis += 0
            else:
                dis += 1
            way += '_'

        return (dis, way)
        

    def check_difference_by_group(self, firefox_version, base_group, compare_group, detail):
        """
        check the difference of two groups
        """
        sql_str = "SELECT id FROM features WHERE agent like '%" + str(firefox_version) + "%' and label like '%" + base_group + "%'"
        base_id = self.db.run_sql(sql_str)[0][0]
        sql_str = "SELECT id FROM features WHERE agent like '%" + str(firefox_version) + "%' and label like '%" + compare_group + "%'"
        compare_id = self.db.run_sql(sql_str)[0][0]
        diff = self.check_difference_by_id(base_id, compare_id, detail)
        return diff


    def cal_all_distances(self, aim):
        """
        calculate the distance between aim and all other entries
        """
        sql_str = "SELECT id FROM features"
        all_ids = self.db.run_sql(sql_str) 
        length = len(all_ids)
        distances = []
        min_distance = 0x3fffffff
        min_index = -1
        for i in range(length):
            if aim == all_ids[i][0]:
                continue
            dis = self.cal_distance(self.check_difference_by_id(aim, all_ids[i][0]))
            distances.append(dis)
            if min_distance > dis:
                min_distance = dis
                min_index = all_ids[i][0]

        return distances

    
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-g", "--group", nargs = '*', action="store", help="Input the key word of two groups")
    parser.add_argument("-v", "--firefox_version", type=int, action="store", help = "Input the firefox version")
    parser.add_argument("-a", "--all", type=int, action = "store", help = "Compare all data pairs in database")
    parser.add_argument("-d", "--detail", action = "store_true", help = "Compare all data pairs in database")
    parser.add_argument("-i", "--id", type=int, nargs = '*', action = "store", help = "Compare all data pairs in database")
    args = parser.parse_args()
    analyzer = Analyzer()
    if args.all != None and args.all != 0:
        distance = analyzer.cal_all_distances(args.all)
        print distance
    elif args.id != None:
        ids = args.id
        diff = analyzer.check_difference_by_id(ids[0], ids[1], args.detail)
        distance = analyzer.cal_distance(diff)
        print distance 
    else:
        groups = args.group
        firefox_version = args.firefox_version
        if firefox_version == None:
            firefox_version = 0
        if groups == None:
            print "Please use -h to see the usage. Key words needed here"
            return 0
        diff = analyzer.check_difference_by_group(firefox_version, groups[0], groups[1], args.detail)
        distance = analyzer.cal_distance(diff)
        print distance



if __name__ == "__main__":
    main()
