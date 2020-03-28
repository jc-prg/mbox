//--------------------------------------
// jc://music-box/, (c) Christoph Kloth
//--------------------------------------
// main functions to load the app
//--------------------------------------
/* INDEX:
function appPrintMenu()
function appPrintStatus_load()
function appPrintStatus(data)
function appCheckUpdates_msg(data)
function appCheckUpdates()
*/
//--------------------------------------

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

var mboxApp = new jcApp("mbox", RESTurl, "status", "api/");	// cmd: <device>/<cmd>
mboxApp.init("data_log", "error_log", reloadInterval, appPrintStatus );
mboxApp.timeout = -1; 							// timeout in milliseconds (-1 for no timeout)
mboxApp.load();
mboxApp.setAutoupdate( mboxControlCheckStatus );

//--------------------------------
// additional apps to write menus, remotes, messages
//--------------------------------

var appMenu     = new appMenuDefinition("appMenu", ["menuItems","menuItems2"], "navTitle" );
var appMsg      = new jcMsg(      	"appMsg" );
//var appCookie   = new jcCookie(         "appCookie");
var reload      = true;

//--------------------------------
// load volume slider
//--------------------------------

var mboxSlider  = new jcSlider( name="mboxSlider", container="audio_slider");
//mboxSlider.setPosition(false,"200px",false,"200px");
mboxSlider.setPosition(top="45px",bottom=false,left=false,right="10px");
mboxSlider.init(0,100,mbox_device);
mboxSlider.setOnChange(mboxControlVolumeSet);
mboxSlider.setShowVolume(mboxControlVolumeShow);

// ----------------- => fct. for testing <= ------------------


appCheckUpdates();		// check if app is up-to-date
appPrintStatus_load();		// initial load of data (default: Album)


//--------------------------------

function appPrintMenu() {

	// initial menu ...
	appMenu.empty();     // load data to class

	var mbox_filter_show = "";
	if (mbox_filter == true) { mbox_filter_show = "hide"; }
	else			 { mbox_filter_show = "show"; }

	appMenu.add_script( "mboxControlToggleMode();           appPrintStatus_load(); if(mbox_settings){mboxSettingsToggle();}", "Modus: " + mbox_mode );
	appMenu.add_script( "mboxControlToggleDevice();         appPrintStatus_load(); if(mbox_settings){mboxSettingsToggle();}", lang("DEVICE") + ": " + mbox_device );
	
	if (mbox_mode == "Album") {
		appMenu.add_script( "mboxControlToggleFilter(); appPrintStatus_load(); if(mbox_settings){mboxSettingsToggle();}", "Filter: " + mbox_filter_show );
		}
	
	appMenu.add_line();
	appMenu.add_script( "mboxCardList_load();  if(mbox_settings){mboxSettingsToggle();printAllStatusLoad();};", lang("RFID_CARDS") );
	appMenu.add_script( "mboxSettingsToggle(); mboxSettingsStatus_load(); appPrintStatus_load();", lang("SETTINGS") );
	
	appMenu.add_line();
        appMenu.add_script( "mboxCoverTogglePrint();", lang("COVER_IMAGES"));
        
        appMenu.set_title( appTitle + mbox_mode );

	mboxSlider.init(0,100,mbox_device);
	}


//--------------------------------
// print after loading data (callback)
//--------------------------------

function appPrintStatus_load() { reload=true; mboxApp.requestAPI('GET',["status"],"",appPrintStatus,"","appPrintStatus_load"); }
function appPrintStatus(data) {

	// print menu
	appPrintMenu();

	// initial app data ...
	setTextById("remote3",  appTitle + " (" + data["API"]["name"] + ": " + data["API"]["version"] + " / " + 
				data["STATUS"]["active_device"] + ") " + mboxCardWriteRFID(data["LOAD"]["RFID"]) );

	if (mboxCardWriteRFID(data["LOAD"]["RFID"]) != "") { mboxControlSetStatus("blue"); }

	// write icon menu and lists
	if (reload) {

		// write icons for 3 modes
		mboxControlGroups();
		
		// wriete volume slider (default = hidden)
		mboxSlider.init(data);

		// write menu entrie for 3 modes
		if (mbox_mode == "Album")    { mboxAlbumAll_load(); }
		if (mbox_mode == "Playlist") { mboxPlaylistAll_load(); }
		if (mbox_mode == "Radio")    { mboxStream_load(); }

		reload = false;
		}

	// set info and control for playback
	mboxControl(data);
	mboxControlCheckLoading(data);
	}

//--------------------------------
// send add commands
//--------------------------------

function appCheckUpdates_msg(data) {

        if (!data || !data["STATUS"]["check-version"]) { return; } // unclear, why sometimes no data are returned ...
        
        var msg = data["STATUS"]["check-version"];
        message = "<br/></b><i>"+msg["Msg"]+"</i>";

        appMsg.wait(lang("LOADING_APP")+" ..."+message, "");

        if (msg["Code"] == "800") { setTimeout(function(){appMsg.hide();},3000); }
        if (msg["Code"] == "801") { setTimeout(function(){appMsg.hide();},3000); }
        if (msg["Code"] == "802") { appUpdate = true; }
        }

//--------------------------------

function appCheckUpdates() {
	console.log("Check version: "+appVersion);
        appMsg.wait(lang("LOADING_APP")+" ...", ""); 
        mboxApp.requestAPI("GET",["version", appVersion], "", appCheckUpdates_msg, "wait");
        }
	
//-----------------------------
// EOF

