#!/usr/bin/python3
"""
Main module of the server file
"""

import time
import logging
import modules.config_stage as stage
import modules.config_mbox as mbox
import modules.run_cmd as run_cmd
import modules.server_init as server_init
import connexion
import sys
import signal
import traceback
import threading
from flask_cors import CORS

start_time = time.time()
mbox.start_time = start_time


def on_exit(signum, handler):
    """
    Clean exit on Strg+C
    All shutdown functions are defined in the "finally:" section in the end of this script
    """
    print('\nSTRG+C pressed! (Signal: %s)' % (signum,))
    # ... add here things to be paused

    while True:
        if confirm == "":
            confirm = input('Enter "yes" to cancel program now or "no" to keep running [yes/no]: ').strip().lower()

        if confirm == 'yes':
            print("Cancel!\n")
            # ... add here things to be stopped correctly
            time.sleep(5)
            sys.exit()
        elif confirm == 'no':
            # ... add her things to be unpaused
            print("Keep running!\n")
            break
        else:
            confirm = ""
            print('Sorry, no valid answer...\n')
        pass


def on_kill(signum, handler):
    """
    Clean exit on kill command
    All shutdown functions are defined in the "finally:" section in the end of this script
    """
    print('\nKILL command detected! (Signal: %s)' % (signum,))
    logging.warning('KILL command detected! (Signal: %s)' % (signum,))
    logging.info("---------------------------------------")
    logging.info("Starting shutdown ...")
    # ... insert here things to be stopped correctly
    time.sleep(3)
    logging.info("Stopped.")
    logging.info("---------------------------------------")
    sys.exit()


def on_exception(exc_type, value, trace_back):
    """
    grab all exceptions and write them to the logfile (if active)
    """
    tb_str = ''.join(traceback.format_exception(exc_type, value, trace_back))
    logging.error("Exception:\n\n" + tb_str + "\n")


def on_exception_setting():
    """
    Workaround for `sys.excepthook` thread bug from:
    http://bugs.python.org/issue1230540

    Call once from the main thread before creating any threads.
    """
    init_original = threading.Thread.__init__

    def init(self, *args, **kwargs):

        init_original(self, *args, **kwargs)
        run_original = self.run

        def run_with_except_hook(*args2, **kwargs2):
            try:
                run_original(*args2, **kwargs2)
            except Exception:
                sys.excepthook(*sys.exc_info())

        self.run = run_with_except_hook

    threading.Thread.__init__ = init


print("----------------------------------------------------------------")
print(mbox.api_name + mbox.api_version + "   (" + str(stage.rollout) + "/" + str(stage.log_level).upper() + ")")
print("----------------------------------------------------------------")

run_cmd.init_logging(mbox.api_name + mbox.api_version + "   (" + str(stage.rollout) + "/" + str(stage.log_level) + ")", "")
server_init.start_modules()

logging.info("Load web server on port "+str(stage.client_port)+" ..." + server_init.time_since_start())
app = connexion.App(__name__, specification_dir="./")
CORS(app.app)

logging.info("Load REST API on port "+str(stage.server_port)+" ..." + server_init.time_since_start())
app.add_api("modules/server_api.yml")


# set system handler
on_exception_setting()
sys.excepthook = on_exception
signal.signal(signal.SIGINT, on_exit)
signal.signal(signal.SIGTERM, on_kill)


if __name__ == "__main__":
    logging.info("Start WebServer ..." + server_init.time_since_start())
    mbox.start_duration = time.time() - mbox.start_time
    server_init.thread_speak.speak_message("LETS-GO")
    server_init.thread_music_ctrl.wait_for_other_services = False
    app.run(debug=mbox.DEBUG, port=stage.server_port, use_reloader=False)
