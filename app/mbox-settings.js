//--------------------------------------
// jc://music-box/, (c) Christoph Kloth
//--------------------------------------
// create settings pages
//--------------------------------------
/* INDEX:
function settingsToggle()
function settingsStatusLoad()
function settingsStatus (data)
function settingsStatus_PerformanceLoad()
function settingsStatus_Performance(data)
function mboxShowLoading(data)
function mboxShowJson(data)
*/
//--------------------------------------

var MusicDir = "/mbox_music/";

// show / hide settings page
// -----------------------------------------------------

function settingsToggle() {
	var div_settings = [ "setting1", "setting2", "setting3", "setting4" ];
	var div_frames   = [ "remote1", "remote2", "remote3", "remote4" ];

	if (document.getElementById("setting1").style.display == "none") {
		for (var key in div_settings) { document.getElementById(div_settings[key]).style.display = "block"; }
		for (var key in div_frames)   { document.getElementById(div_frames[key]).style.display   = "none"; }
		mbox_settings = true;
		}
	else {
		for (var key in div_settings) { document.getElementById(div_settings[key]).style.display = "none"; }
		for (var key in div_frames)   { document.getElementById(div_frames[key]).style.display   = "block"; }
		mbox_settings = false;
		}
	}

// write status information to settings page ...
// -----------------------------------------------------

function settingsStatusLoad()  { mboxApp.requestAPI("GET",["status"],"",settingsStatus, "wait"); }
function settingsStatus (data) {

	var text  = "";
	var stage = "Prod Stage"; if (test) { stage = "Test Stage"; }

	text += "<center><b>"+lang("INFORMATION")+"</b></center>";
	text += "<hr/>";
	text += mboxTable("start");
	text += mboxTable("<b>mBox-Client:",	appTitle + " " + appVersion + "<br/>(" + stage + ")");
	text += mboxTable("<b>mBox-Server:",	data["API"]["name"] + " " + data["API"]["version"] + "<br/>(" + data["API"]["stage"] + ")");
	text += mboxTable("<b>jcApp:",		mboxApp.appVersion);
	text += mboxTable("end");
	text += "<hr/>";
	text += mboxTable("start");
	text += mboxTable("<b>Modus:", 		mbox_mode);
	text += mboxTable("<b>Status:", 	data["STATUS"]["playback"]["status"] + " (" + data["STATUS"]["playback"]["file"] + ")");
	text += mboxTable("<b>Playing:", 	data["STATUS"]["playback"]["playing"]);
	text += mboxTable("<b>Active Device:", 	data["STATUS"]["active_device"]);
	text += mboxTable("<b>Window:", 	document.body.clientWidth + "x" + document.body.clientHeight);
	text += mboxTable("end");
	text += "<hr/>";
	text += mboxTable("start");
	text += mboxTable("<b>Files:", 		data["STATUS"]["statistic"]["files"] );
	text += mboxTable("<b>Tracks:", 	data["STATUS"]["statistic"]["tracks"] );
	text += mboxTable("<b>Artists:", 	data["STATUS"]["statistic"]["albums"] );
	text += mboxTable("<b>Albums:", 	data["STATUS"]["statistic"]["album_info"] );
	text += mboxTable("<b>Playlists:",	data["STATUS"]["statistic"]["playlists"] );
	text += mboxTable("<b>Web-Radio:",	data["STATUS"]["statistic"]["radio"] );
	text += mboxTable("end");

	setTextById("setting1",text);

	//---------------------------------

	text = "";
	text += "<center><b>Test Settings ...</b></center>";
	text += "<hr/>";

	text += button( "uploadImage();", "Upload Image" );
	text += button( "mboxCoverTogglePrint();", "Cover Images" );
	text += "<hr/>";
	
	text += "<center><b>"+lang("LOADING_TIME")+"</b></center>";
	text += "<hr/>";
	text += mboxTable("start");
	text += mboxTable("<b>Initial load:",		Math.round(data["STATUS"]["system"]["server_start_duration"]*10)/10+" s" );
	text += mboxTable("<b>Running for:",		Math.round(data["STATUS"]["system"]["server_running"]) +" s" );
	text += mboxTable("end");

	text += "<hr/>";
	text += mboxTable("start");
/*
	text += mboxTable("<b>API request:",		Math.round(data["REQUEST"]["load-time-app"]/1000*10)/10+" s &nbsp; &nbsp; (all data)" );
	text += mboxTable("<b>DB request:",		Math.round(data["REQUEST"]["load-time"]*1000)/1000+" s" );
	text += mboxTable("<b>DB request per file:",	Math.round(data["REQUEST"]["load-time"]/dict_size(data["DATA"]["files"])*1000)/1000+" s &nbsp; &nbsp; ("+dict_size(data["DATA"]["files"])+")" );
*/
	text += mboxTable("<b>API request:", 		"<div id=\"duration_api_request\">Please Wait</div>" );
	text += mboxTable("<b>DB request:",		"<div id=\"duration_db_request\">Please Wait</div>" );
	text += mboxTable("<b>DB request per file:",	"<div id=\"duration_db_request_per_file\">Please Wait</div>" );
	text += mboxTable("end");
	text += "<hr/>";

	text += "<center><b>"+lang("DISC_SPACE")+"</b></center>";
	text += "<hr/>";
	text += mboxTable("start");
	text += mboxTable("<b>System Used:",		Math.round(data["STATUS"]["system"]["space_main_used"]/1024/1024*10)/10+" GByte" );
	text += mboxTable("<b>System Total:",	        Math.round(data["STATUS"]["system"]["space_main_available"]/1024/1024*10)/10+" GByte" );

	text += mboxTable("<b>Data Used:",		Math.round(data["STATUS"]["system"]["space_usb_used"]/1024/1024*10)/10+" GByte" );
	text += mboxTable("<b>Data Total:",		Math.round(data["STATUS"]["system"]["space_usb_available"]/1024/1024*10)/10+" GByte" );
	text += mboxTable("end");
	text += "<hr/>";

	setTextById("setting2",text);
	settingsStatus_PerformanceLoad();

	//---------------------------------

	var demo_p = "";
	var demo_a = "";
	for (var key in data["DATA"]["album_info"]) { demo_a = key; }
	for (var key in data["DATA"]["playlists"])  { demo_p = key; }

	text = "";

	text += "<center><b>" + lang("RELOAD_DATA") + " ...</b>";
	text += "<hr/>";

	var onclick = ""; var question = ""; var cmd = "";

	question = "<br/>"+lang("QUESTION_RELOAD");
	onclick  = "mboxApp.requestAPI(#PUT#,[#load#,#all#],##,mboxShowLoading)";
        cmd      = "appMsg.confirm('" + question + "','" + onclick + "', 260);";
	text    += button( cmd, "Reload Data" );

	question = "<br/>"+lang("QUESTION_LOAD_NEW");
	onclick  = "mboxApp.requestAPI(#PUT#,[#load#,#new#],##,mboxShowLoading)";
        cmd      = "appMsg.confirm('" + question + "','" + onclick + "', 260);";
	text    += button( cmd, "Load New Data" );

	question = "<br/>" + lang("QUESTION_LOAD_IMG");
	onclick  = "mboxApp.requestAPI(#PUT#,[#load#,#images#],##,mboxShowLoading)";
        cmd      = "appMsg.confirm('" + question + "','" + onclick + "', 260);";
	text    += button( cmd, "Load New Images" );

	text += "<hr/>";

	question = "<br/>"+lang("QUESTION_RESTORE_JSON");
	onclick  = "mboxApp.requestAPI(#PUT#,[#backup#,#json2db#],##,mboxShowJson)";
        cmd      = "document.getElementById('json2db').disabled = true;";
        cmd	+= "document.getElementById('json2db').innerHTML = '" + lang("PLEASE_WAIT") + "';";
        cmd     += "appMsg.confirm('" + question + "','" + onclick + "', 260);";
	text    += button( cmd, "Restore (JSON 2 DB)", "json2db" );

	question = "<br/>"+lang("QUESTION_BACKUP2JSON");
	onclick  = "mboxApp.requestAPI(#PUT#,[#backup#,#db2json#],##,mboxShowJson)";
        cmd      = "document.getElementById('db2json').disabled = true;";
        cmd	+= "document.getElementById('db2json').innerHTML = '" + lang("PLEASE_WAIT") + " ...';";
        cmd     += "appMsg.confirm('" + question + "','" + onclick + "', 260);";
	text    += button( cmd, "Backup (DB 2 JSON)", "db2json" );

	text += "<hr/></center>";

	text += "<center><b>Development</b></center>";
	text += "<hr/>";
	text += "<ul>";
      	text += "<li>" + add_link( RESTurl + "api/status/", "API-Link: Status") + "</li>";
      	text += "<li>" + add_link( RESTurl + "api/db/all/-/", "API-Link: List all") + "</li>";
      	text += "<li>" + add_link( RESTurl + "api/play/test/", "API-Link: Play Demo") +" </li>";
      	text += "<li>" + add_link( RESTurl + "api/data/album_info/test/", "API-Link: List Album Demo") + "</li>";
      	text += "<li>" + add_link( RESTurl + "api/ui/", "API-Link: Swagger UI") + "</li>";
      	text += "<li>" + add_link( RESTurl_noport + ":" + couchdb_port +"/", "API-Link: CouchDB") + "</li>";
      	text += "<li>" + add_link( RESTurl_noport + ":" + couchdb_port +"/_utils/", "API-Link: CouchDB Admin-Panel") + "</li>";
      	text += "<li>" + add_link( RESTurl_noport + ":" + couchdb_port +"/albums/main/", "API-Link: CouchDB Sample Access") + "</li>";
	text += "</ul>";

	setTextById("setting3",text);
	}

//----------------------------------------------------------------

function settingsStatus_PerformanceLoad() { mboxApp.requestAPI("GET",["db","all","-"],"",settingsStatus_Performance, "wait"); }
function settingsStatus_Performance(data) {
	setTextById("duration_api_request",		Math.round(data["REQUEST"]["load-time-app"]/1000*10)/10+" s &nbsp; &nbsp; (all data)");
	setTextById("duration_db_request",		Math.round(data["REQUEST"]["load-time"]*1000)/1000+" s");
	setTextById("duration_db_request_per_file",	Math.round(data["REQUEST"]["load-time"]/dict_size(data["DATA"]["files"])*1000)/1000+" s &nbsp; &nbsp; ("+dict_size(data["DATA"]["files"])+")");
	}

//----------------------------------------------------------------


function mboxShowLoading(data) {
	var text = "<b>" + lang("RELOAD_STARTED") + ":</b><br/><br/><div id='reload_info' style='border-style:solid 1px;'>x</div>";
	appMsg.alert(text);
	}

function mboxShowJson(data) {
	var text = "<b>" + lang("RELOAD_STARTED") + "</b>";
	appMsg.alert(text);
	}

//----------------------------------------------------------------
// EOF
