import difflib

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

    def agent_diff(self, agent1, agent2):
        """
        handle agent diff specially
        """
        parts1 = self.pre_handle_agent(agent1)
        parts2 = self.pre_handle_agent(agent2)

        res = self.feature_diff(parts1, parts2, sep = ' ')
        return res
