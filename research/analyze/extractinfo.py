from tqdm import *
import re
import user_agents
def mobile_or_not(agent):
    mobile_str = 'Mobile|iPhone|iPod|iPad|Android|BlackBerry|IEMobile|Kindle|NetFront|Silk-Accelerated|hpwOS|webOS|Fennec|Minimo|Opera Mobi|Mini|Blazer|Dolfin|Dolphin|Skyfire|Zune'
    test_str = mobile_str.split('|')
    for test in test_str:
        if agent.find(test) != -1:
            return 1
    return 0 

def ignore_non_ascii(str1):
    """
    this function will ignore the non ascii and non latin-1 chars
    """
    if not str1:
        return 'None'
    str1 = str1.encode('latin-1', errors = 'ignore').decode('latin-1')
    str1 = str1.encode('ascii', errors = 'ignore').decode('ascii')
    return str1
# return the os fonts and the conts of the 
# contributors
def get_os_fonts(df):
    fonts = {}
    res_fonts = {}
    cnts = {}
    for idx in tqdm(df.index):
        row = df.iloc[idx]
        os = get_os_version(row['agent'])
        cur_fonts = row['jsFonts'].split('_')
        if os not in fonts:
            fonts[os] = {} 
            cnts[os] = 0
        for font in cur_fonts:
            if font not in fonts[os]:
                fonts[os][font] = 0
            else:
                fonts[os][font] += 1
        cnts[os] += 1

    for os in fonts:
        res_fonts[os] = []
        for font in fonts[os]:
            if fonts[os][font] > cnts[os] * 0.9:
                res_fonts[os].append(font)
        # convert the font list to a set
        res_fonts[os] = set(res_fonts[os])

    return res_fonts, cnts

# input the agent string
# return the full os type
def get_full_os_from_agent(agent):
    return get_os_version(agent)

# input the agent string
# return the os type
def get_os_from_agent(agent):
    parsed = user_agents.parse(agent)
    return ignore_non_ascii(parsed.os.family)

def get_browser_from_agent(agent):
    """
    return the browser type by the input agent
    from mar 20 2018, the format of Edge changed
    """
    try:
        return ignore_non_ascii(user_agents.parse(agent).browser.family)
    except:
        return "agent error"

def get_browser_version(agent):
    # return the string of browser and version number
    # if it's others, just return other
    parsed = user_agents.parse(agent)
    return ignore_non_ascii(parsed.browser.family) + ' ' + ignore_non_ascii(parsed.browser.version_string)

def get_os_version(agent):
    # return the string of os and version number
    parsed = user_agents.parse(agent)
    return ignore_non_ascii(parsed.os.family) + ' ' + ignore_non_ascii(parsed.os.version_string)

def get_all_info(agent):
    """
    return all info including: os, os_version, browser, browser_version, device
    """
    parsed = user_agents.parse(agent)
    os = ignore_non_ascii(parsed.os.family)
    device = ignore_non_ascii(parsed.device.family)
    browser = ignore_non_ascii(parsed.browser.family)
    os_version = ignore_non_ascii(parsed.os.version_string)
    browser_version = ignore_non_ascii(parsed.browser.version_string)
    return os, os_version, browser, browser_version, device


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
    

# the two strs put in this function is separated by _
# if it's separated by ' ', trans them before this function
# or use the sep param
# return the diff of str1 to str2 and str2 to str1 
def get_change_strs(str1, str2, sep = '_'):
    str1 = str(str1)
    str2 = str(str2)
    if str1 == None:
        str1 = ""
    if str2 == None:
        str2 = ""
    words_1 = set(str1.split(sep))
    words_2 = set(str2.split(sep))
    return words_1 - words_2, words_2 - words_1
