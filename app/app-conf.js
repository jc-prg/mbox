//--------------------------------------
// jc://music-box/, (c) Christoph Kloth
//--------------------------------------
// app configuration
//--------------------------------------


// REST API configuration

var appVersion     = "v0.7.1";
var appTitle       = "jc://mbox/";

var RESTip         = location.host;
var ip             = RESTip.split(":");

var RESTurl        = "http://"+ip[0]+":"+server_port+"/";
var RESTurl_noport = "http://"+ip[0];

// presets

var dataAll	= {};
var dataConfig	= {};

var appUpdate        = false;
var showImg          = true;	// preset: show images if defined (otherwise text)
var checkImgExists   = false;   // check if album cover exists using http-requests (takes time ...)
var eMsg             = false;
var reloadInterval   = 5;	// reload data every x seconds
var connect2stage    = "Prod";	// default stage to connect to (changed if rm3_test == true)

var showButtonTime   = 0.2;     // time to show LED when button pressed
var showButton       = false;   // default: show pressed button in headline
var deactivateButton = false;   // default: deactivate buttons if device is not ON

var colors         = [ "red", "green", "darkgreen", "blue", "darkblue" ];
var colors_dev     = [];

var show_error     = ""; // onClick=\"javascript:showErrorLog();\""; // not implemented any more
var status_green   = "<div id='green' "+show_error+"></div>";
var status_yellow  = "<div id='yellow' "+show_error+"></div>";
var status_gray    = "<div id='gray' "+show_error+"></div>";
var status_red     = "<div id='red' "+show_error+"></div>";

var status_mute    = "rec_mute"; // -> show in <nav-info id="audio2"> 	// changed based on server settings
var status_vol     = "rec_vol";  // -> show in <nav-info id="audio1"> 	// changed based on server settings
var status_vol_max = 74;         // -> calculate in percent		// changed based on server settings


// Standard-Definition
//----------------------------------

var button_color  = {};
var button_img    = {};
var makro_def     = {};
var device_status = {};

// ------------------------------------------
// EOF


