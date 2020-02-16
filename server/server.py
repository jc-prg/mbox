#!/usr/bin/python3
'''Main module of the server file'''

# load basic modules and configuration
#----------------------------------------------
import time
import modules.config_stage    as stage
import modules.config_mbox     as mbox

# set start time and write title/version/stage
#----------------------------------------------
mbox.start_time = time.time()
print("--------------------------------")
print(mbox.APIname + mbox.APIversion + "   (" + str(stage.rollout) + ")")
print("--------------------------------")

# start and configure logging
#----------------------------------------------
import logging
if stage.test:
    if mbox.DEBUG:
       logging.basicConfig(level=logging.DEBUG)  # DEBUG, INFO, WARNING, ERROR, CRITICAL
       logging.debug("MBOX Start (Log-Level DEBUG) ...")
    else:
       logging.basicConfig(level=logging.INFO)   # DEBUG, INFO, WARNING, ERROR, CRITICAL
       logging.info("MBOX Start (Log-Level INFO) ...")
else:
   logging.basicConfig(filename='/log/server.log',
                       filemode='a',
                       format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                       datefmt='%d.%m.%y %H:%M:%S',
                       level=logging.WARN)

   log = logging.getLogger("werkzeug")
   log.setLevel(logging.WARN)

   logging.warn("MBOX Start (Log-Level WARN) ...")

# load API modules
#----------------------------------------------
import connexion
from connexion.resolver import RestyResolver
from flask_cors         import CORS

import modules_api.server_init as init

#----------------------------------------------

# create the application instance
logging.info("Start Server ..." + init.time_since_start())
app = connexion.App(__name__, specification_dir="./")
CORS(app.app)

# Cead the swagger.yml file to configure the endpoints
logging.info("Load API Specification ..." + init.time_since_start())
app.add_api("modules_api/swagger.yml")

if __name__ == "__main__":

  logging.info("Start WebServer ..."  + init.time_since_start())
  mbox.start_duration = time.time() - mbox.start_time
  init.thread_speek.speek_message("LETS-GO")

  app.run(debug=mbox.DEBUG,port=stage.server_port,use_reloader=False)

