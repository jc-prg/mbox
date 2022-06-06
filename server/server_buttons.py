#!/usr/bin/python3
# ------------------------------------
# check if buttons pressed and send request
# to mbox REST API
# by jc://design/
# ------------------------------------

import RPi.GPIO as GPIO
import time
import logging
import requests

import modules.config_stage as stage
import modules.config_mbox as mbox
import modules_gpio.config as gpio
import modules.json_db as jcJSON
import modules.run_cmd as jcCmd

# set start time and write title/version/stage
# ----------------------------------------------

mbox.start_time = time.time()

# start and configure logging
# ----------------------------------------------

jcCmd.init_logging(mbox.api_name_BTN + mbox.api_version + "   (" + str(stage.rollout) + "/" +
                   str(stage.log_level) + ")", '/log/server_BUTTONS.log')

if stage.log_level != "error":
    GPIO.setwarnings(False)


def get_active_stage():
    """
    read from file, which stage should be used ... to switch between stages during runtime
    """
    settings = jcJSON.read("../../active")
    return settings["active_stage"]


if stage.test:
    logging.info("Start button module: TEST STAGE (" + get_active_stage() + ")")
    url = "http://" + stage.server_ip + ":" + str(stage.server_port) + "/api/"
    this_stage = "test"

else:
    logging.info("Start button module: PROD STAGE (" + get_active_stage() + ")")
    url = "http://" + stage.server_ip + ":" + str(stage.server_port) + "/api/"
    this_stage = "prod"

# -----------------------------------

pins = gpio.button_pins

cmd = {
    "up": url + "volume/up/",
    "mute": url + "volume/mute/",
    "down": url + "volume/down/",
    "pause": url + "pause/",
    "next": url + "play_next/1/",
    "back": url + "play_last/1/",
    "error": url + "button_error/"
}

wait = 0.3
error_time = 10 / wait


def setup():
    GPIO.setmode(GPIO.BOARD)  # Numbers GPIOs by physical location
    for key in pins:
        GPIO.setup(int(pins[key]), GPIO.IN,
                   pull_up_down=GPIO.PUD_UP)  # Set BtnPin's mode is input, and pull up to high level(3.3V)


def loop():
    """
    loop to check if key is pressed -> call api
    """
    last_key = ""
    same_key = 0

    while True:
        time.sleep(wait)
        # check if active stage
        if get_active_stage() == this_stage:

            # if active check input
            for key in pins:

                if GPIO.input(pins[key]) == GPIO.LOW:  # Check whether the button is pressed or not.
                    call_api(key)
                    if last_key != key:
                        last_key = key
                        same_key = 0
                    else:
                        same_key += 1

            if last_key != "" and GPIO.input(pins[last_key]) != GPIO.LOW:
                same_key = 0
                last_key = ""

#                if last_key == key:
#                    last_key = ""
#                    same_key = 0

            if same_key > error_time:
                logging.warning("Same key is pressed for more than " + str(error_time * wait) + "s!")
                press_time = same_key * wait
                call_api("error", [last_key, press_time])
                time.sleep(1)


def destroy():
    GPIO.cleanup()  # Release resource


def call_api(button, param=None):
    logging.info("... pressed: " + button)
    if button == "mute":
        time.sleep(1)

    try:
        if button == "error":
            request_url = url + "button_error/" + str(param[0]) + "/" + str(param[1]) + "/"
            response = requests.put(request_url)
            logging.info(request_url)

        elif button != "":
            response = requests.put(url + "set-button/" + button + "/")
            if "volume" in cmd[button]:
                response = requests.get(cmd[button])
        else:
            response = requests.put(url + "set-button/no_button/")

        if response:
            data = response.json()
            logging.debug("response: " + str(data))

    except requests.exceptions.RequestException as e:
        logging.debug("Error connecting to API: " + str(e))
        data = {}
        return


# -----------------------------------

if __name__ == '__main__':  # Program start from here
    setup()
    try:
        loop()
    except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child program destroy() will be  executed.
        destroy()

# -----------------------------------
