#!/usr/bin/python3
#------------------------------------
# check if buttons pressed and send request
# to mbox REST API
# by jc://design/
#------------------------------------

import RPi.GPIO as GPIO
import time
import requests

import modules.config_stage as stage
import modules.config_mbox  as mbox
import modules_gpio.config  as gpio
import modules.jcJson       as jcJSON

# set start time and write title/version/stage
#----------------------------------------------

mbox.start_time = time.time()

# start and configure logging
#----------------------------------------------

stage.init_logging( mbox.APIname_BTN + mbox.APIversion + "   (" + str(stage.rollout) + "/"+str(stage.log_level)+")", '/log/server_BUTTONS.log' )

if (stage.log_level != "error"): 
   GPIO.setwarnings(False)

#-----------------------------------
# init
#-----------------------------------

# read from file, which stage should be use ... to switch between stages during runtime
def get_active_stage():
  settings = jcJSON.read("../../active")
  return settings["active_stage"]
  return "prod"

if stage.test == True:
  logging.info("Start button module: TEST STAGE ("+get_active_stage()+")")
  url  = "http://"+stage.server_ip+":"+str(stage.server_port)+"/api/"
  this_stage = "test"

else:
  logging.info("Start button module: PROD STAGE ("+get_active_stage()+")")
  url  = "http://"+stage.server_ip+":"+str(stage.server_port)+"/api/"
  this_stage = "prod"


#-----------------------------------

pins         = gpio.button_pins

cmd          = {}
cmd["up"]    = url+"volume/up/"
cmd["mute"]  = url+"volume/mute/"
cmd["down"]  = url+"volume/down/"
cmd["pause"] = url+"pause/"
cmd["next"]  = url+"play_next/1/"
cmd["back"]  = url+"play_last/1/"

wait         = 0.3

#----------------------

def setup():
    GPIO.setmode(GPIO.BOARD)       # Numbers GPIOs by physical location
    for key in pins:
        GPIO.setup(int(pins[key]), GPIO.IN, pull_up_down=GPIO.PUD_UP)    # Set BtnPin's mode is input, and pull up to high level(3.3V)

def loop():
    while True:

       time.sleep(wait)
       # check if ative stage
       if (get_active_stage() == this_stage):

          # if active check input
          for key in pins:
            if GPIO.input(pins[key]) == GPIO.LOW: # Check whether the button is pressed or not.
               call_api(key)
               print(key)


def destroy():
    GPIO.cleanup()                     # Release resource


def call_api(button):
    logging.info("... pressed: " + button)
    if button == "mute":
      time.sleep(1)

    try:
       if button != "":
         response  = requests.put(url+"set-button/" + button + "/")
         if "volume" in cmd[button]: response  = requests.get(cmd[button])
       else:
         response  = requests.put(url+"set-button/no_button/")
       if response:
           data = response.json()
           #logging.info("Volume: " + str(round(data["STATUS"]["playback"]["volume"] * 10)))
    except requests.exceptions.RequestException as e:
       logging.debug("Error connecting to API: " + str(e))
       data      = {}
       return


#-----------------------------------

if __name__ == '__main__':     # Program start from here
    setup()
    try:
        loop()
    except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child program destroy() will be  executed.
        destroy()


#-----------------------------------
