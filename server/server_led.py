#!/usr/bin/python3
# ------------------------------------
# get events via REST API from mbox
# and control LED ...
# by jc://design/
# ------------------------------------

import RPi.GPIO as GPIO
import time
import requests
import logging
import signal
import subprocess

import modules.json_db as json_db
import modules.run_cmd as run_cmd
import modules.config_stage as stage
import modules.config_mbox as mbox
import modules_gpio.light as led
import modules_gpio.config as gpio

# set start time and write title/version/stage
# ----------------------------------------------

mbox.start_time = time.time()
blink_LED = {"error": 0, "wifi": 0, "rfid": 0, "stage": 0, "sleep": 0, "main": 0}

# start and configure logging
# ----------------------------------------------

run_cmd.init_logging(
    mbox.api_name_LED + mbox.api_version + "   (" + str(stage.rollout) + "/" + str(stage.log_level) + ")",
    '/log/server_LED.log')

if stage.log_level != "error":
    GPIO.setwarnings(False)


# -----------------------------------
# init
# -----------------------------------

# read from file, which stage should be use ... to switch between stages during runtime
def get_active_stage():
    settings = json_db.read("../../active")
    return settings["active_stage"]


if stage.test is True:
    logging.info("Start LED module: TEST STAGE (" + get_active_stage() + ")")
    url = "http://" + stage.server_ip + ":" + str(stage.server_port) + "/api/"
    this_stage = stage.rollout
else:
    logging.info("Start LED module: PROD STAGE (" + get_active_stage() + ")")
    url = "http://" + stage.server_ip + ":" + str(stage.server_port) + "/api/"
    this_stage = stage.rollout

# -----------------------------------

cmd = {"status": url + "status/"}
wait = 0.5
ProcessRunning = True
ServerRunning = False
other = ""

# ----------------------


def call_api(command):
    data1 = {}
    logging.debug("Read API: " + command)

    try:
        response = requests.get(cmd[command])
        data1 = response.json()
    except requests.exceptions.RequestException as e:
        logging.info("Error connecting to API: " + str(e))
        data1 = {}

    return data1


def loop():
    """
    read volume and switch on LED to show level
    """
    global light, ProcessRunning, other

    blink_status_error = 0  # blinking error
    blink_status_wifi = 0  # blinking wifi info
    volume_steps = 0  # no playback for a while ...

    first_run = 1
    act_active = ""
    last_active = ""

    last_play = time.time()
    last_play_wait = 180
    last_play_act = False

    light_error = "0"
    light_stage = "1"
    light_rfid = "0"
    light_play = "0"
    light_wifi = "0"

    light.other = "000000"
    light.volume = 0

    while ProcessRunning:

        # switch on/off
        act_active = get_active_stage()
        # logging.info("STAGE..."+act_active+"/"+last_active+"//"+this_stage)

        if act_active == "" or act_active != last_active:
            logging.info("STAGE...DIFFERENT (" + act_active + ")")
            if act_active == this_stage:
                light.start_gpio()
            else:
                light.stop_gpio()
            last_active = act_active
            light.stage = this_stage

        # initial
        if first_run == 1:
            time.sleep(wait)
            a = 0
            light.other = "111111"
            while a <= 10:
                light.volume = a
                time.sleep(0.3)
                a += 1

            light.other = "111111"
            time.sleep(wait * 3)
            first_run = 0

        else:
            # set status lights | N/A - Error=RED - Wifi=YELLOW - Playing=GREEN - Stage=WHITE - RFID=BLUE
            light.other = "1" + str(light_error) + str(light_wifi) + str(light_play) + \
                          str(light_stage) + str(light_rfid)

            # reduce requests
            time.sleep(wait)

            # check if active stage
            if act_active == this_stage:

                # if active check volume and show
                light_error = "0"
                data = call_api("status")

                if "API" in data:
                    logging.debug(str(data["API"]))

                # check stage
                if this_stage == "test":
                    light_stage = blink("stage")
                else:
                    light_stage = "1"

                # check wifi status
                if "STATUS" in data and "system" in data["STATUS"] and "server_connection" in data["STATUS"]["system"]:

                    check_data = data["STATUS"]["system"]["server_connection"]
                    if "WIFI" in check_data["TYPE"] and "CONNECTED" in check_data["CONNECT"]:
                        logging.debug(check_data["TYPE"])
                        light_wifi = "1"

                    elif "HOTSPOT" in check_data["TYPE"]:
                        logging.debug(check_data["TYPE"])
                        if blink_status_wifi < 3:
                            light_wifi = "1"
                        else:
                            light_wifi = "0"

                    else:
                        logging.debug(check_data["TYPE"])
                        if blink_status_wifi == 0:
                            light_wifi = "1"
                        elif blink_status_wifi == 1:
                            light_wifi = "0"
                        elif blink_status_wifi == 2:
                            light_wifi = "1"
                        elif blink_status_wifi == 3:
                            light_wifi = "0"
                        elif blink_status_wifi == 4:
                            light_wifi = "1"
                        else:
                            light_wifi = "0"

                if blink_status_wifi < 6:
                    blink_status_wifi += 1
                else:
                    blink_status_wifi = 0

                # check playing status
                if "STATUS" in data and "playback" in data["STATUS"] and "playing" in data["STATUS"]["playback"]:

                    if data["STATUS"]["playback"]["playing"] == 1:
                        light_play = "1"
                        last_play = time.time()
                    else:
                        light_play = "0"

                # LED Saver ... ;-)
                if time.time() > last_play + last_play_wait:
                    last_play_act = True
                else:
                    last_play_act = False

                if last_play_act:
                    if volume_steps > 9 and blink_LED["main"] == 0:
                        volume_steps = 0
                    elif blink_LED["main"] == 0:
                        volume_steps += 1
                    light.volume = volume_steps + 11

                # if card is detected ...
                if "LOAD" in data and "RFID" in data["LOAD"]:
                    light_rfid = "0"
                    if data["LOAD"]["RFID"] == stage.demo_card:
                        first_run = 1

                    elif data["LOAD"]["RFID"] != "":
                        light_rfid = "1"
                        logging.info(data["LOAD"]["RFID"])

                    if "CARD" in data["LOAD"] and data["LOAD"]["CARD"] == "unknown":
                        light_rfid = blink("rfid")
                        logging.info("-> Card not known!")

                # if not mute show volume level
                if "STATUS" in data:
                    light_error = "0"
                    if "playback" in data["STATUS"] and \
                            data["STATUS"]["playback"]["mute"] == 0 and \
                            last_play_act is False:

                        light.volume = round(data["STATUS"]["playback"]["volume"] * 10)
                        logging.debug("Volume: " + str(light.volume))
                        # logging.info(this_stage+":Volume: "+str(light.volume))

                    # else blink with 1 LED
                    elif last_play_act is False:
                        light.volume = blink("sleep")
                        logging.debug("Volume: MUTE")

                # else blink with 1. LED - red (not connected)
                else:
                    light_error = blink("error")
                    light.volume = 0
                    logging.debug("Volume: ERROR")

        blink("main")



def blink(type):
    """
    decide when to switch on / off an LED
    """
    global blink_LED
    if type not in blink_LED:
        logging.warning("Type '"+type+"' doesn't exist!")
    elif blink_LED[type] == 0:
        blink_LED[type] = 1
    else:
        blink_LED[type] = 0
    return blink_LED[type]


def end_all(end1, end2):
    global light, ProcessRunning

    ProcessRunning = False
    light.stop()


def check_running():
    psAx1 = subprocess.check_output(["ps", "ax"])
    if "server.py" in str(psAx1):
        return True
    else:
        return False


# -----------------------------------


# Hook the SIGINT
signal.signal(signal.SIGINT, end_all)

# init logging
logging.basicConfig(level=logging.INFO)
logging.info("Start LED control ...")

# -----------------------------------

if __name__ == '__main__':
    light = led.lightThread(3, "Thread LED Control", 1, this_stage)
    light.start()
    light.destroy

    loop()

# -----------------------------------
