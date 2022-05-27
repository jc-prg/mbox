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
from flask_cors import CORS

start_time = time.time()
mbox.start_time = start_time

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


if __name__ == "__main__":
    logging.info("Start WebServer ..." + server_init.time_since_start())
    mbox.start_duration = time.time() - mbox.start_time
    server_init.thread_speak.speak_message("LETS-GO")
    app.run(debug=mbox.DEBUG, port=stage.server_port, use_reloader=False)
