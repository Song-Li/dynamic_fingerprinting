import difflib
from tqdm import *
from feature_lists import *
from database import Database

class Paperlib_helper():
    def __init__(self):
        pass

    def feature_diff(self, val1, val2, sep = '_'):
        """
        except for the agent info, other features just need to seperate it by a seperator
        use difflib to find the difference
        """
        vals1 = []
        vals2 = []

        if val1 is not None:
            vals1 = str(val1).split(sep)
        if val2 is not None:
            vals2 = str(val2).split(sep)

        differ = difflib.Differ()
        diff_res = differ.compare(vals1, vals2)
        
        str1 = ""
        str2 = ""
        for diff in diff_res:
            if diff[0] == '-':
                str1 += diff[2:] + '++'
            elif diff[0] == '+':
                str2 += diff[2:] + '++'
        res_str = '{}=>{}'.format(str1, str2)
        return res_str

    def pre_handle_agent(self, agent):
        """
        replace seperators in agent string into spaces
        """
        seps = [' ', ';']
        for sep in seps:
            agent.replace(sep, ' ')
        return agent

    def remove_change_only(self, df, feature_names, browser_names, feature_list = get_fingerprint_feature_list()):
        """
        if only one feature changed, remove it
        """
        db = Database('forpaper345')
        columns = db.get_column_names('fingerprintchanges')

        length = len(feature_names)
        if length != len(browser_names):
            print ("length of features names and browser names must match")
        filtered = []

        for feature in feature_list:
            if feature not in columns:
                feature_list.remove(feature)

        for idx in tqdm(df.index):
            for i in range(length):
                feature = feature_names[i]
                browser = browser_names[i]
                row = df.iloc[idx]
                if browser == row['browser'] and df.at[idx, feature] == ''.join(str(df.at[idx, x]) for x in feature_list):
                    filtered.append(idx)
        df = df[~df.index.isin(filtered)]
        df.reset_index(drop = True, inplace = True)
        return df

    def agent_diff(self, agent1, agent2):
        """
        handle agent diff specially
        """
        parts1 = self.pre_handle_agent(agent1)
        parts2 = self.pre_handle_agent(agent2)

        res = self.feature_diff(parts1, parts2, sep = ' ')
        return res
