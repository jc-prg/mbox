# ---------------------------------
# mbox Stage Configuration
# ---------------------------------
# Please edit not here, but the orginial configuration file. This files is created using a template.
# ---------------------------------
# this script will be replace by
# the rollout script for PROD stage

rollout      = "test"

data_dir     = "/projects/git/data/test"
data_backup  = "/projects/git/data/test/couchdb_backup/"
data_db      = "http://mbox:mbox@192.168.1.10:5106/"

mount_system = "/"
mount_data   = "/"

demo_card    = "125,232,21,163"

server_port = 5006
server_ip   = "192.168.1.10"

if rollout == "test": test  = True
else:                 test  = False

#### -> add more dir data

