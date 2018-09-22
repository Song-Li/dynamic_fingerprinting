feature_list = [ 
        "IP",
        "agent",
        "httpheaders",
        "accept",
        "encoding",
        "language",
        "timezone", 

        "plugins", 
        "cookie", 
        "WebGL", 
        "localstorage", 
        "fp2_addbehavior",
        "fp2_opendatabase",

        "langsdetected",
        "jsFonts",
        "canvastest", 

        "inc", 
        "gpu", 
#        "gpuimgs", 
        "cpucores", 
        "audio",
        "fp2_cpuclass",
        "fp2_colordepth",
        "fp2_pixelratio",

        "ipcity",
        "ipregion",
        "ipcountry",

        "fp2_liedlanguages",
        "fp2_liedresolution",
        "fp2_liedos",
        "fp2_liedbrowser",

        "browserfingerprint"
        ]

ori_feature_list = [ 
        "IP",
        "agent",
        "httpheaders",
        "accept",
        "encoding",
        "language",
        "timezone", 

        "plugins", 
        "cookie", 
        "WebGL", 
        "localstorage", 
        "fp2_addbehavior",
        "fp2_opendatabase",

        "langsdetected",
        "jsFonts",
        "canvastest", 

        "inc", 
        "gpu", 
        "gpuimgs", 
        "cpucores", 
        "audio",
        "fp2_cpuclass",
        "fp2_colordepth",
        "fp2_pixelratio",

        "fp2_liedlanguages",
        "fp2_liedresolution",
        "fp2_liedos",
        "fp2_liedbrowser",

        "clientid",
        "label",
        "uniquelabel",
        "time",
        "browserfingerprint"
        ]

fingerprint_feature_list = [
        "agent",
        "httpheaders",
        "accept",
        "encoding",
        "language",
        "timezone", 

        "plugins", 
        "cookie", 
        "WebGL", 
        "localstorage", 
        "fp2_addbehavior",
        "fp2_opendatabase",

        "langsdetected",
        "jsFonts",
        "canvastest", 

        "inc", 
        "gpu", 
        "gpuimgs", 
        "cpucores", 
        "audio",
        "fp2_cpuclass",
        "fp2_colordepth",
        "fp2_pixelratio",
        "resolution",

        "ipcity",
        "ipregion",
        "ipcountry",

        "fp2_liedlanguages",
        "fp2_liedresolution",
        "fp2_liedos",
        "fp2_liedbrowser"
        ]

table_feature_list = [
        "agent",
        "browser",
        "os",
        "device",
        "httpheaders",
        "accept",
        "encoding",
        "language",
        "timezone", 

        "plugins", 
        "cookie", 
        "WebGL", 
        "localstorage", 
        "fp2_addbehavior",
        "fp2_opendatabase",

        "langsdetected",
        "jsFonts",
        "canvastest", 

        "inc", 
        "gpu", 
        "partgpu",
        "gpuimgs", 
        "cpucores", 
        "audio",
        "fp2_cpuclass",
        "fp2_colordepth",
        "fp2_pixelratio",
        "resolution",

        "ipcity",
        "ipregion",
        "ipcountry",

        "fp2_liedlanguages",
        "fp2_liedresolution",
        "fp2_liedos",
        "fp2_liedbrowser",
        "browserfingerprint",
        "noipfingerprint"
        ]

fingerprint_change_feature_list = [
        "agent",
        #"httpheaders",
        #"accept",
        "encoding",
        "language",
        "timezone", 

        "plugins", 
        "cookie", 
        "WebGL", 
        "localstorage", 
        "fp2_addbehavior",
        "fp2_opendatabase",

        "langsdetected",
        "jsFonts",
        "canvastest", 

        "inc", 
        "gpu", 
        "cpucores", 
        "audio",
        "fp2_cpuclass",
        "fp2_colordepth",
        "fp2_pixelratio",

        #"ipcity",
        #"ipregion",
        #"ipcountry",

        "fp2_liedlanguages",
        "fp2_liedresolution",
        "fp2_liedos",
        "fp2_liedbrowser"
        ]

def get_ori_feature_list():
    return ori_feature_list

def get_feature_list():
    return feature_list

def get_fingerprint_feature_list():
    return fingerprint_feature_list

def get_fingerprint_change_feature_list():
    return fingerprint_change_feature_list

def get_table_feature_list():
    return table_feature_list
