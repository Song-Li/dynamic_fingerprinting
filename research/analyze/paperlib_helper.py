import difflib

def feature_diff(val1, val2, sep = '_'):
    """
    except for the agent info, other features just need to seperate it by a seperator
    use difflib to find the difference
    """
    vals1 = val1.split(sep)
    vals2 = val2.split(sep)

    differ = difflib.Differ()
    diff_res = differ.compare(vals1, vals2)
    
    for diff in diff_res:
        print diff


def agent_diff(agent1, agent2):
    pass
