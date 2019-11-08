import os
import shlex, subprocess #  subprocess.run(args, *, stdin=None, input=None, stdout=None, stderr=None, shell=False, timeout=None, check=False)
import json
import re
import urllib

# execute command incl. "&"
#--------------------------

def runCmdOs(cmd_line):
    out = os.system(cmd_line)
    logging.debug("Run CMD: " +cmd_line)
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

