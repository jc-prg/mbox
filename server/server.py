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

# start and configure logging
#----------------------------------------------

stage.init_logging( mbox.APIname + mbox.APIversion + "   (" + str(stage.rollout) + "/"+str(stage.log_level)+")", '/log/server.log' )

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

# Add the swagger.yml file to configure the endpoints
logging.info("Load API Specification ..." + init.time_since_start())
app.add_api("modules_api/swagger.yml")


if __name__ == "__main__":

  logging.info("Start WebServer ..."  + init.time_since_start())
  mbox.start_duration = time.time() - mbox.start_time
  init.thread_speak.speak_message("LETS-GO")

  app.run(debug=mbox.DEBUG,port=stage.server_port,use_reloader=False)

