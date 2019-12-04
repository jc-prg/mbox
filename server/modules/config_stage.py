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
data_db      = "http://mbox:mbox@192.168.1.35:5105/"

mount_system = "/"
mount_data   = "/media/usb"

demo_card    = "185,134,169,99"

server_port = 5005
server_ip   = "192.168.1.35"

if rollout == "test": test  = True
else:                 test  = False

#### -> add more dir data

