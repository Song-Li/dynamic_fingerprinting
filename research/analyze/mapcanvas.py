import pandas as pd
from datetime_truncate import truncate
import operator
import collections
from tqdm import *
from math import sin, cos, sqrt, atan2, radians
import re
from extractinfo import *
import json
from urllib2 import urlopen
import datetime
from database import Database
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import os
import bisect

global df

def featureDiff(f1, f2):
    return f1 != f2 and 'None' not in str(f1) and 'None' not in str(f2) and pd.notnull(f1) and pd.notnull(f2) 

counted_features = [ 
        "agent",
        "accept",
        "encoding",
        "language",
        "langsdetected",
        "resolution",
        "jsFonts",
        "WebGL", 
        "inc", 
        "gpu", 
        "gpuimgs", 
        "timezone", 
        "plugins", 
        "cookie", 
        "localstorage", 
        "adblock", 
        "cpucores", 
        "canvastest", 
        "audio",
#        "ccaudio",
#        "hybridaudio",
        "touchSupport",
        "doNotTrack",
        "fp2_colordepth", 
        "fp2_sessionstorage",
        "fp2_indexdb",
        "fp2_addbehavior",
        "fp2_opendatabase",
        "fp2_cpuclass",
        "fp2_pixelratio",
        "fp2_platform",
        "fp2_liedlanguages",
        "fp2_liedresolution",
        "fp2_liedos",
        "fp2_liedbrowser",
        "fp2_webgl",
        "fp2_webglvendoe",
        "ipcity",
        "ipregion",
        "ipcountry"
        ]
if __name__ == "__main__()":
    main()

