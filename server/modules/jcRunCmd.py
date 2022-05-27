import os
import shlex
import subprocess
import logging
import pythonping
import time

import modules.config_stage as stage
import modules.config_mbox as mbox

run_logging = logging.getLogger("run-cmd")
run_logging.setLevel(stage.logging_level)

connectionStatusLast = ""
connectionStatusTime = 0


def runCmdOs(cmd_line):
    """
    execute command incl. "&"
    """
    out = os.system(cmd_line)
    run_logging.debug("Run CMD: " + cmd_line)
    return out


def runCmd(cmd_line):
    """
    execute command without "&"
    """
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


def check_disk_space(init=False):
    out = mbox.checkdisk

    if stage.mount_data != "" and stage.mount_system != stage.mount_data:

        disk_use, err = runCmd(mbox.diskuse + stage.mount_data)
        try:
            out[0] = float(disk_use.split("\t")[0])
        except Exception as e:
            run_logging.warning("0 Error in reading disk spaces (data drive) ..." + str(e))
            run_logging.warning("  - " + mbox.diskuse + stage.mount_data)

        disk_free, err = runCmd(mbox.diskfree + stage.mount_data)
        try:
            out[1] = disk_free.split("\n")[1]
            out[1] = out[1].replace(" ", "")
            out[1] = float(out[1])
        except Exception as e:
            run_logging.warning("1 Error in reading disk spaces (data drive) ..." + str(e))
            run_logging.warning("  - " + mbox.diskfree + stage.mount_data)

    if stage.mount_system != "":

        if init:
            disk_use_mount, err = runCmd(mbox.diskuse + stage.mount_system)
            try:
                out[2] = float(disk_use_mount.split("\t")[0])
            except Exception as e:
                run_logging.warning("2 Error in reading disk spaces (system drive) ..." + str(e))
                run_logging.warning("  - " + mbox.diskuse + stage.mount_system)

        disk_free_mount, err = runCmd(mbox.diskfree + stage.mount_system)
        try:
            out[3] = float(disk_free_mount.split("\n")[1])
        except Exception as e:
            run_logging.warning("3 Error in reading disk spaces (system drive) ..." + str(e))
            run_logging.warning("  - " + mbox.diskfree + stage.mount_system)

    if init:
        mbox.checkdisk = out

    run_logging.info("check_disk_space: "+str(out))
    return out


def file_logging(logging_string, logging_file=""):
    """
    init logging settings:
    write string into logging file
    """
    if stage.log_to_file_data != "yes":
        return

    if logging_file == "" and stage.log_filename_data != "":
        logging_file = stage.log_filename_data

    try:
        file1 = open(logging_file, "a")
        file1.write(logging_string + "\n")
        file1.close()
    except:
        return


def file_logging_init(logging_file="/log/load_metadata.log"):
    """
    init logging settings:
    write string into logging file
    """
    if stage.log_to_file_data != "yes":
        run_logging.debug("Log metadata to file is deactivated")
        return

    if logging_file == "" and stage.log_filename_data != "":
        logging_file = stage.log_filename_data

    ts = time.gmtime()
    readable = time.strftime("%Y-%m-%d %H:%M:%S", ts)

    try:
        file1 = open(logging_file, "w")
        file1.write("----------------------------------------------\n")
        file1.write("Load time: " + readable + "\n")
        file1.write("Log level: " + stage.log_level_data + "\n")
        file1.close()
    except Exception as e:
        run_logging.warning("Could not initiate log-file to log metadata loading: " + str(e))


def init_logging(log_string, logfilename=""):
    """
    Initialize logging and print software title
    Log-level: DEBUG, INFO, WARNING, ERROR, CRITICAL
    """

    level_data = stage.logging_level_data
    level = stage.logging_level

    if stage.log_to_file == "yes":

        if logfilename == "":
            logfilename = stage.log_filename
        if logfilename == "":
            logfilename = "/log/server.py"

        logging.basicConfig(filename=logfilename,
                            filemode='a',
                            format='%(asctime)s | %(levelname)-8s %(name)-10s | %(message)s',
                            datefmt='%d.%m.%y %H:%M:%S',
                            level=level)

        if level == "DEBUG" or level == "INFO":
            run_logging.info("Start - Log-Level " + level + " ...")
            run_logging.info("--------------------------------")
            run_logging.info(log_string)
            run_logging.info("--------------------------------")
        elif level == "WARNING":
            run_logging.warning("Start: " + str(log_string) + " (" + str(level) + ") ...")
        else:
            run_logging.error("Start: " + str(log_string) + " (" + str(level) + ") ...")

    else:
        logging.basicConfig(level=level,
                            format='%(levelname)-8s %(name)-10s | %(message)s')

    log = logging.getLogger("werkzeug")
    log.setLevel(logging.WARNING)

    log = logging.getLogger("charset_normalizer")
    log.setLevel(logging.WARNING)

    logging_level = level
    logging_level_data = level_data


def ping(host, source=""):
    """
    ping a server e.g. to check internet connection:
    Returns True if host (str) responds to a ping request.
    Remember that a host may not respond to a ping (ICMP) request even if the host name is valid.
    """

    response_list = pythonping.ping(host, size=40, count=1)
    run_logging.debug("PING " + host + ": " + str(response_list).split("\n")[0] + " (" + source + ")")

    if "Reply from " + host in str(response_list):
        return True

    response_list = pythonping.ping(host, size=40, count=1)
    run_logging.debug("PING " + host + ": " + str(response_list).split("\n")[0] + " (" + source + ")")

    if "Reply from " in str(response_list):
        return True
    else:
        return False


def check_internet_connect():
    """
    check if connection to internet exists
    """
    host_ip = stage.server_dns
    host = ['spiegel.de', 'google.com']
    ping_ip = False
    error_msg = ""

    for key in host_ip:
        if ping(key, "server1"):
            ping_ip = True
            break

    count = 0
    while count < len(host):
        try:
            connect = ping(host[count], "server2")
            if connect and ping_ip:
                error_msg = "CONNECTED"
                count = len(host)
            elif ping_ip:
                error_msg = "DNS-ERROR"
            else:
                error_msg = "NO-CONNECTION"

        except requests.exceptions.RequestException as e:
            error_msg = "NO-CONNECTION"
            logging.warning("Error connecting to INTERNET (" + host[count] + "): " + str(e))

        count = count + 1

    if error_msg == "CONNECTED":
        run_logging.info("Internet connected.")
    else:
        run_logging.warning("No internet connection (" + error_msg + ")")

    f = open("/log/internet_connect", "w+")
    f.write(error_msg)
    f.close()

    return error_msg


def connection_status():
    """
    read log files with connection status
    """
    global connectionStatusLast, connectionStatusTime

    try:
        with open(mbox.log_connection) as f:
            content1 = f.readlines()
    except:
        content1 = ["Connection not checked yet"]

    try:
        with open(mbox.log_autohotspot) as f:
            content2 = f.readlines()
    except:
        content2 = ["Autohotspot not activated"]

    if connectionStatusTime + 60 < time.time():
        content3 = check_internet_connect()
        connectionStatusLast = content3
        connectionStatusTime = time.time()
    else:
        content3 = connectionStatusLast

    return {"CONNECT": content1[0], "TYPE": content2[0], "INTERNET": content3}


