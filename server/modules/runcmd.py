import os
import shlex, subprocess #  subprocess.run(args, *, stdin=None, input=None, stdout=None, stderr=None, shell=False, timeout=None, check=False)
import json
import re
import urllib
import logging
import platform    # For getting the operating system name


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


def ping(host):
    """
    Returns True if host (str) responds to a ping request.
    Remember that a host may not respond to a ping (ICMP) request even if the host name is valid.
    """

    # Option for the number of packets as a function of
    param = '-n' if platform.system().lower()=='windows' else '-c'

    # Building the command. Ex: "ping -c 1 google.com"
    command = ['ping', param, '1', host]

    return subprocess.call(command) == 0
