# ---------------------------------
# mbox Stage Configuration
# ---------------------------------
# Please edit not here, but the orginial configuration file. This files is created using a template.
# ---------------------------------
# this script will be replace by
# the rollout script for PROD stage

rollout      = "prod"

data_dir     = "/projects_data/prod"
data_backup  = "/projects_data/prod/couchdb_backup/"
data_db      = "http://mbox:mbox@localhost:5105/"

mount_system = "/"
mount_data   = "/"

server_port = 5005

if rollout == "test": test  = True
else:                 test  = False

#### -> add more dir data

