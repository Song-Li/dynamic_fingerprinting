# input the agent string
# return the os type
def get_os_from_agent(agent):
    agent = agent.lower()
    # respect the order of os
    os_list = [
            'windows phone',
            'win',
            'android',
            'linux',
            'iphone',
            'ipad',
            'mac'
            ]
    os = ""
    for os in os_list:
        if os in agent:
            return os
    return 'other'

def get_browser_from_agent(agent):
    agent = agent.lower()
    # respect the order of browser
    browser_list = [
            'firefox',
            'opera',
            'chrome',
            'safari',
            'trident'
            ]
    for browser in browser_list:
        if browser in agent:
            return browser
    return 'other'

def get_browser_version(agent):
    # return the string of browser and version number
    # if it's others, just return other
    agent = agent.lower()
    browser = get_browser_from_agent(agent)
    if browser == 'other':
        return 'other'
    idx = agent.index(browser)
    res = agent[idx:].split(' ')[0]
    return res

def get_os_version(agent):
    # return the string of os and version number
    agent = agent.lower()
    os = get_os_from_agent(agent)
    idx = 0
    if os == 'other':
        return 'other'
    if os == 'iphone' or os == 'ipad' or os == 'mac':
        os = '; '
        idx = agent.index(os) + 2
    else:
        idx = agent.index(os)
    # in case that the os is the last part inside the ()
    res = agent[idx:].split(')')[0]
    res = res.split(';')[0]
    return res

def get_browser_change(agent_1, agent_2):
    browser_1 = get_browser_from_agent(agent_1)
    browser_2 = get_browser_from_agent(agent_2)
    if browser_1 != browser_2:
        return 1 
    browser_1 = get_browser_version(agent_1)
    browser_2 = get_browser_version(agent_2)
    if browser_1 != browser_2:
        return 2
    return 0 


def get_os_change(agent_1, agent_2):
    os_1 = get_os_from_agent(agent_1)
    os_2 = get_os_from_agent(agent_2)
    if os_1 != os_2:
        return 1
    os_1 = get_os_version(agent_1)
    os_2 = get_os_version(agent_2)
    if os_1 != os_2:
        return 2
    return 0


def get_agent_change(agent_1, agent_2):
    browser_change = get_browser_change(agent_1, agent_2)
    # 3 is the number of state of browser change
    os_change = 3 + get_os_change(agent_1, agent_2) 
    return browser_change, os_change
    

