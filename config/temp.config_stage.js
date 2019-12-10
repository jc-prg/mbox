//--------------------------------
// Configure stage details
//---------------------------------
// ${THIS_IS_THE_PROJECT_TEMPLATE}

var test		= false;
var rollout	 	= '${MBOX_CURRENT_STAGE}';
var couchdb_port 	= '${MBOX_DATABASE_PORT}';
var server_port 	= '${MBOX_SERVER_PORT}';

LANG                    = '${MBOX_LANGUAGE}';

if (rollout === "test")	{ test = true; }

// add more dir data

