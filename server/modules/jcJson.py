import json, codecs
import logging
from os import path

import modules.config_mbox    as mbox

jsonPath    = mbox.music_data
jsonAppDir  = path.dirname(path.abspath(__file__))
jsonSettingsPath = ""

#--------------------------------------------

def init():
    '''global settings'''

    global jsonPath, jsonAppDir, jsonSettings, jsonSettingsFile
    jsonSettingsPath = path.join(jsonAppDir, jsonPath)


#--------------------------------------------

def read(file):
    '''read data from json file'''

    d = {}
    file1 = file+".json"
    file2 = path.join(jsonAppDir,jsonPath,file1)
    logging.debug(file2)
    with open(file2) as json_data:
        d = json.load(json_data)
    return d


#--------------------------------------------

def write(file, data):
    '''write data to readable json file'''

    d = {}
    file1 = file+".json"
    file2 = path.join(jsonAppDir,jsonPath,file1)

    with open(file2, 'wb') as outfile:
        json.dump(data, codecs.getwriter('utf-8')(outfile), ensure_ascii=False, sort_keys=True, indent=4)
        #json.dump(data, outfile, ensure_ascii=False, sort_keys=True, indent=4)


#--------------------------------------------
# to remove a key from dict use:
# my_dict.pop('key', None)


