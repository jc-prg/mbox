//--------------------------------
// jc://remote/
//--------------------------------
// WebApp Remote Control for RM3
// from Broadlink (requires server app)
//
// (c) Christoph Kloth
//--------------------------------
// Backlog:
//--------------------------------
// - get initial data from server ...
//--------------------------------

if (test == true) {
	appTitle 	+= "test/";
	connect2stage	= "Test";
	document.getElementById("navTitle").style.color="red";
	}
else {
	connect2stage	= "Prod";
	}


//--------------------------------
// app to load info and send cmd to IR device
//--------------------------------

var mboxApp     = new jcApp( "sampleApp", RESTurl, "status", "api/");     // cmd: <device>/<cmd>
mboxApp.init( "data_log", "error_log", reloadInterval, printAppStatus );
mboxApp.load( );
mboxApp.setAutoupdate( mboxCheckStatus );

//--------------------------------
// additional apps to write menus, remotes, messages
//--------------------------------

var appMenu     = new jcMenu(     "appMenu", "menuItems", "navTitle" );
var appMsg      = new jcMsg(      "appMsg" );  //rm3msg.wait("Loading App ...", "initRemote();" );
var appCookie   = new jcCookie(   "appCookie");
var reload      = true;

check_for_updates();
appMenu.init( dataAll );     // load data to class


function printAppMenu() {
	// initial menu ...
	appMenu.empty();     // load data to class

	var mbox_filter_show = "";
	if (mbox_filter == true) { mbox_filter_show = "hide"; }
	else			 { mbox_filter_show = "show"; }

	appMenu.add_script( "mboxToggleMode();printAppStatusLoad();if(mbox_settings){settingsToggle();}", "Modus: " + mbox_mode );
	appMenu.add_script( "mboxToggleDevice();printAppStatusLoad();if(mbox_settings){settingsToggle();}", "Device: " + mbox_device );
	if (mbox_mode == "Album") {
		appMenu.add_script( "mboxToggleFilter();printAppStatusLoad();if(mbox_settings){settingsToggle();}", "Filter: " + mbox_filter_show );
		}
	appMenu.add_line();
	appMenu.add_script( "mboxListCardsLoad();if(mbox_settings){settingsToggle();printAllStatusLoad();};", "RFID Cards" );
	appMenu.add_script( "settingsToggle();settingsStatusLoad();printAppStatusLoad();", "Settings" );
	appMenu.add_line();
        appMenu.add_script( "toggleCoverPrint();", "Cover Images" )
        appMenu.set_title( appTitle + mbox_mode );
	}
//--------------------------------
// print after loading data (callback)
//--------------------------------

function printAppStatusLoad() { reload=true; mboxApp.requestAPI('GET',["status"],"",printAppStatus,"","printAppStatusLoad"); }
function printAppStatus(data) {

	// print menu
	printAppMenu();

	// initial app data ...
	setTextById("remote3", appTitle + " (" + data["API"]["name"] + ": " + data["API"]["version"] 
				+ " / " + data["STATUS"]["active_device"] + ") " + writeRFID(data["LOAD"]["RFID"]) );

	if (writeRFID(data["LOAD"]["RFID"]) != "") { mboxSetStatus("blue"); }

	// write icon menu and lists
	if (reload) {
		// write icons for 3 modes
		mboxWriteGroups();

		// write menu entrie for 3 modes
		if (mbox_mode == "Album")    { mboxAlbumAllLoad(); }
		if (mbox_mode == "Playlist") { mboxPlaylistAllLoad(); }
		if (mbox_mode == "Radio")    { mboxRadioLoad(); }

		reload = false;
		}

	// set info and control for playback
	mboxControl(data);
	mboxCheckLoading(data);
	}

//--------------------------------
// send add commands
//--------------------------------

function check_for_update_msg(data) {

        if (!data || !data["STATUS"]["check-version"]) { return; } // unclear, why sometimes no data are returned ...
        
        var msg = data["STATUS"]["check-version"];
        message = "<br/></b><i>"+msg["Msg"]+"</i>";

        appMsg.wait("Loading App ..."+message, ""); //"initRemote();" );

        if (msg["Code"] == "800") { setTimeout(function(){appMsg.hide();},3000); }
        if (msg["Code"] == "801") { setTimeout(function(){appMsg.hide();},3000); }
        if (msg["Code"] == "802") { appUpdate = true; }
        }


function check_for_updates() {
	console.log("Check version: "+appVersion);
        appMsg.wait("Loading App ...", ""); // "initRemote();" );
        mboxApp.requestAPI("GET",["version", appVersion], "", check_for_update_msg, "wait");
        }


//-----------------------------
// EOF
