import os
import shlex, subprocess #  subprocess.run(args, *, stdin=None, input=None, stdout=None, stderr=None, shell=False, timeout=None, check=False)
import json
import re
import urllib
import logging
import platform    # For getting the operating system name
import pythonping
import time

import modules.config_stage    as stage

run_logging = logging.getLogger("run-cmd")
run_logging.setLevel(stage.logging_level)

# execute command incl. "&"
#--------------------------

def runCmdOs(cmd_line):
    out = os.system(cmd_line)
    run_logging.debug("Run CMD: " +cmd_line)
    return out


# execute command without "&"
#--------------------------

def runCmd(cmd_line):
    r = ""
    a = []

    a = shlex.split(cmd_line)
    p = subprocess.Popen(a, stdout=subprocess.PIPE, shell=False)
    out, err = p.communicate()
    if out:
      out = out.decode('utf-8')
    if err:
      err = err.decode('utf-8')
    return out, err



# init logging settings
#--------------------------

def file_logging(logging_string, logging_file="/log/load_metadata.log"):
    '''
    write string into logging file
    '''
    file1 = open(logging_file, "a")
    file1.write(logging_string+"\n")
    file1.close()
    return
    


def file_logging_init(logging_file="/log/load_metadata.log"):
    '''
    write string into logging file
    '''
    ts = time.gmtime()
    readable = time.strftime("%Y-%m-%d %H:%M:%S", ts)
    file1 = open(logging_file, "w")
    file1.write(readable+"\n")
    file1.close()
    return

    
def init_logging(log_string,logfilename=""):
    """
    Initialize logging and print software title
    Log-level: DEBUG, INFO, WARNING, ERROR, CRITICAL
    """
    
    level_data = stage.logging_level_data
    level      = stage.logging_level
    
    if stage.log_to_file == "yes":
    
       if logfilename == "": logfilename = stage.log_filename
       if logfilename == "": logfilename = "/log/server.py"

       logging.basicConfig(filename=logfilename,
                       filemode='a',
                       format='%(asctime)s | %(levelname)-8s %(name)-10s | %(message)s',
                       datefmt='%d.%m.%y %H:%M:%S',
                       level=level)

       if log_level == "DEBUG" or log_level == "INFO":
          run_logging.info("Start - Log-Level "+log_level+" ...")
          run_logging.info("--------------------------------")
          run_logging.info(log_string)
          run_logging.info("--------------------------------")       
       elif log_level == "WARNING":
          run_logging.warning("Start: "+log_string+" ("+log_level+") ...")
       else:
          run_logging.error("Start: "+log_string+" ("+log_level+") ...")

    else:
       logging.basicConfig(level=level,  
                        format='%(levelname)-8s %(name)-10s | %(message)s')
                  
    log = logging.getLogger("werkzeug")
    log.setLevel(logging.WARNING)
    
    log = logging.getLogger("charset_normalizer")
    log.setLevel(logging.WARNING)
                      
    logging_level      = level
    logging_level_data = level_data

# ping a server e.g. to check internet connection
#--------------------------

def ping(host):
    """
    Returns True if host (str) responds to a ping request.
    Remember that a host may not respond to a ping (ICMP) request even if the host name is valid.
    """

    response_list = pythonping.ping(host, size=40, count=1)
    run_logging.info("PING "+host+": "+str(response_list).split("\n")[0])
    
    if "Reply from "+host in str(response_list): return True 
    
    response_list = pythonping.ping(host, size=40, count=1)
    run_logging.info("PING "+host+": "+str(response_list).split("\n")[0])

    if "Reply from "+host in str(response_list): return True 
    else:                                        return False
