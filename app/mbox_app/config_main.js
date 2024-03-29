//--------------------------------
// config menu and main functions
//--------------------------------

var app_frame_count       = 4;
var app_frame_style       = "frame_column wide";
var app_frames_sidebyside = false;
var app_setting_count     = 4;
var app_setting_style     = "setting_bg";
var app_last_load         = 0;
var app_title             = "jc://music-box/";	// add your app title (default defined in app-fw/app-conf.is)
var app_version           = "v1.2.7";			// add your app version (default defined in app-fw/app-conf.is)
var app_api_dir           = "api/";			// add your api dir (default defined in app-fw/app-conf.is)
var app_api_status        = "status";			// add your api status command (default defined in app-fw/app-conf.is)
var app_loading_image     = ""; 			// add your loading image (default defined in app-fw/app-conf.is)
var app_reload_interval   = 5;  			// add your reloading interval (default=5s)

//--------------------------------
// mbox specific initialization
//--------------------------------

var UploadScript    = "mbox_app/upload.php";
var checkImgExists  = false;
var mboxSlider      = new jcSlider( name="mboxSlider", container="mbox_audio_slider");
var internetConnect = "Started";
reloadInterval      = app_reload_interval;

//--------------------------------
// create menu entries
//--------------------------------

function app_menu_entries() {
	// define the menu here
	// or set "app_menu = [];" if another menu functions should be used
	
	var mbox_filter_show = "";
	if (mbox_filter == true)	{ mbox_filter_show = "hide"; }
	else				{ mbox_filter_show = "show"; }


        var descr   = [lang("ALBUM"),lang("PLAYLIST"),lang("STREAM")];

	var app_menu = [
		//[lang("INDEX"),        		"link", "/index.html"],
		[lang("ALBUM"),			"script",	"mboxAlbumAll_load();   if(mbox_settings) {mboxSettingsToggle();}"],
		[lang("PLAYLIST"),			"script",	"mboxPlaylists_load();  if(mbox_settings) {mboxSettingsToggle();}"],
		[lang("STREAM-PODCAST"),		"script",	"mboxStreams_load();    if(mbox_settings) {mboxSettingsToggle();}"],
		["LINE"],
		["Modus: "+mbox_mode,			"script",	"mboxControlToggleMode();   appPrintStatus_load(); if(mbox_settings) {mboxSettingsToggle();}"],
		[lang("DEVICE")+": "+mbox_device,	"script",	"mboxControlToggleDevice(); appPrintStatus_load(); if(mbox_settings) {mboxSettingsToggle();}"],
		];		

	if (mbox_mode == "Album") {
		app_menu = app_menu.concat([
		["Filter: "+mbox_filter_show,		"script",	"mboxControlToggleFilter(); appPrintStatus_load(); if(mbox_settings){mboxSettingsToggle();}"]
		]);
		}
		
	app_menu = app_menu.concat([
		[lang("RFID_CARDS"),			"script", 	"mboxCardList_load();  if(mbox_settings){mboxSettingsToggle();printAllStatusLoad();};"],
		[lang("COVER_IMAGES"),			"script",	"mboxCoverTogglePrint();"],
		["LINE"],
		[lang("SETTINGS"),  			"script", 	"mboxSettingsToggle(); mboxSettingsStatus_load(); appPrintStatus_load();" ],
		[lang("HELP")+" (German)",		"link",	"/mbox_help/help_DE.html"],
		]);
			
	return app_menu;
	}

	
//--------------------------------
// function to request status, update menu etc. (including initial load)
//--------------------------------

function app_status(data) {

	// check if RFID card detected
	detected_card = mboxCardWriteRFID(data["LOAD"]["RFID"],data["LOAD"]["CARD"],data["DATA"]["SHORT"]);

	// initial app data ...
	var appInfo = appTitle + " (" + data["API"]["name"] + ": " + data["API"]["version"] + " / " + data["STATUS"]["active_device"] + ") " + detected_card;
	setTextById("frame4", "<center>" + appInfo + "</center>" );

	if (reload) { 

		// write icons for 3 modes
		mboxControlGroups();
		
		// write volume slider (default = hidden)
		mboxSlider.setPosition(top="45px",bottom=false,left=false,right="10px");
		mboxSlider.setOnChange(mboxControlVolumeSet);
		mboxSlider.setShowVolume(mboxControlVolumeShow);
		mboxSlider.init(0,100,mbox_device);

		// write menu entrie for 3 modes
		if (mbox_mode == "album")    { mboxAlbumAll_load("", mbox_last_uuid); }
		if (mbox_mode == "playlist") { mboxPlaylists_load("", mbox_last_uuid); }
		if (mbox_mode == "radio")    { mboxStreams_load(); }

		setNavTitle(appTitle);
		reload = false;
		}

	// set info and control for playback
	mboxControl(data);
	mboxControlCheckLoading(data);
	}
	
//--------------------------------
// add code when forced a reload
//--------------------------------

function app_force_reload(data) {
	}
	
//--------------------------------
// add code for initialization
//--------------------------------

function app_initialize(data) {
	}
	
//--------------------------------
// add code when menu icon is clicked
//--------------------------------

function app_click_menu() {
	}
	
//--------------------------------
// add code when theme changed
//--------------------------------

function app_theme_changed(theme) {
	if (theme == "dark")	{ mbox_icon_dir	= "mbox_img/icon_dark/"; }
	else			{ mbox_icon_dir	= "mbox_img/icon/"; }
	}
	
//--------------------------------
// add code when screen size changed
//--------------------------------

var app_screen_size_width_old  = "";
var app_screen_size_height_old = "";

function app_screen_size_changed(width, height) {
	console.debug("Changed screen size to " + width + "x" + height);
	
	// reload views if width changes
	if (app_screen_size_width_old != width) {
		if (mbox_mode == "album")		{ mboxAlbumAll_reload("",mbox_last_uuid); }
		else if (mbox_mode == "radio")	{ mboxStreams_reload(); }
		else if (mbox_mode == "playlist")	{ mboxPlaylists_reload("", mbox_last_uuid); }
		}

	app_screen_size_width_old  = width;
	app_screen_size_height_old = height;
	}

//--------------------------------
//EOF
