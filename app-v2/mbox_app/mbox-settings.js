//--------------------------------------
// jc://music-box/, (c) Christoph Kloth
//--------------------------------------
// create settings pages
//--------------------------------------
/* INDEX:
function mboxSettingsToggle()
function mboxSettingsStatus_load()
function mboxSettingsStatus (data)
function mboxSettingsStatusPerformance_load()
function mboxSettingsStatusPerformance(data)
*/
//--------------------------------------

var MusicDir = "/mbox_music/";

// show / hide settings page
// -----------------------------------------------------

function mboxSettingsToggle() {
	var div_settings = [ "setting1", "setting2", "setting3", "setting4" ];
	var div_frames   = [ "frame1", "frame2", "frame3", "frame4" ];

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

function mboxSettingsStatus_load()  { appFW.requestAPI("GET",["status"],"",mboxSettingsStatus, "wait"); }
function mboxSettingsStatus (data) {

	var text    = "";
	var stage   = "Prod Stage"; if (test) { stage = "Test Stage"; }
	var player  = new jcPlayer("player");
	var message = new jcMsg("message");
	var slider  = new jcSlider("slider");

	text += "<center><b>"+lang("INFORMATION")+"</b></center>";
	text += "<hr/>";
	text += mboxHtmlTable("start");
	text += mboxHtmlTable("<b>mBox-Client:",	appTitle + " " + appVersion + "<br/>(" + stage + ")");
	text += mboxHtmlTable("<b>mBox-Server:",	data["API"]["name"] + " " + data["API"]["version"] + "<br/>(" + data["API"]["stage"] + ")");
	text += mboxHtmlTable("end");
	text += "<hr/>";
	text += mboxHtmlTable("start");
	text += mboxHtmlTable("<b>jcApp:",		appFW.appVersion);
	text += mboxHtmlTable("<b>jcAppFramework:",	appFwVersion);
	text += mboxHtmlTable("<b>jcMessage:",	message.appVersion);
	text += mboxHtmlTable("<b>jcPlayer:",		player.appVersion);
	text += mboxHtmlTable("<b>jcSlider:",		slider.appVersion);
	text += mboxHtmlTable("end");
	text += "<hr/>";
	text += mboxHtmlTable("start");
	text += mboxHtmlTable("<b>Modus:", 		mbox_mode);
	text += mboxHtmlTable("<b>Playing:", 		data["STATUS"]["playback"]["playing"]);
	text += mboxHtmlTable("<b>Active Device:", 	data["STATUS"]["active_device"]);
	text += mboxHtmlTable("<b>Window:", 		document.body.clientWidth + "x" + document.body.clientHeight);
	text += mboxHtmlTable("end");
	text += "<hr/>";
	text += mboxHtmlTable("start");
	text += mboxHtmlTable("<b>Status:",	 	data["STATUS"]["playback"]["status"] + " (" + data["STATUS"]["playback"]["file"] + ")");
	text += mboxHtmlTable("end");
	text += "<hr/>";
	text += mboxHtmlTable("start");
	text += mboxHtmlTable("<b>Files:", 		data["STATUS"]["statistic"]["files"] );
	text += mboxHtmlTable("<b>Tracks:", 		data["STATUS"]["statistic"]["tracks"] );
	text += mboxHtmlTable("<b>Artists:", 		data["STATUS"]["statistic"]["albums"] );
	text += mboxHtmlTable("<b>Albums:", 		data["STATUS"]["statistic"]["album_info"] );
	text += mboxHtmlTable("<b>Playlists:",		data["STATUS"]["statistic"]["playlists"] );
	text += mboxHtmlTable("<b>Web-Radio:",		data["STATUS"]["statistic"]["radio"] );
	text += mboxHtmlTable("end");

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
	text += mboxHtmlTable("start");
	text += mboxHtmlTable("<b>Initial load:",		Math.round(data["STATUS"]["system"]["server_start_duration"]*10)/10+" s" );
	text += mboxHtmlTable("<b>Running for:",		Math.round(data["STATUS"]["system"]["server_running"]) +" s" );
	text += mboxHtmlTable("end");

	text += "<hr/>";
	text += mboxHtmlTable("start");
/*
	text += mboxHtmlTable("<b>API request:",		Math.round(data["REQUEST"]["load-time-app"]/1000*10)/10+" s &nbsp; &nbsp; (all data)" );
	text += mboxHtmlTable("<b>DB request:",		Math.round(data["REQUEST"]["load-time"]*1000)/1000+" s" );
	text += mboxHtmlTable("<b>DB request per file:",	Math.round(data["REQUEST"]["load-time"]/dict_size(data["DATA"]["files"])*1000)/1000+" s &nbsp; &nbsp; ("+dict_size(data["DATA"]["files"])+")" );
*/
	text += mboxHtmlTable("<b>API request:", 		"<div id=\"duration_api_request\">Please Wait</div>" );
	text += mboxHtmlTable("<b>DB request:",		"<div id=\"duration_db_request\">Please Wait</div>" );
	text += mboxHtmlTable("<b>DB request per file:",	"<div id=\"duration_db_request_per_file\">Please Wait</div>" );
	text += mboxHtmlTable("end");
	text += "<hr/>";

	text += "<center><b>"+lang("DISC_SPACE")+"</b></center>";
	text += "<hr/>";
	text += mboxHtmlTable("start");
	text += mboxHtmlTable("<b>System Used:",		Math.round(data["STATUS"]["system"]["space_main_used"]/1024/1024*10)/10+" GByte" );
	text += mboxHtmlTable("<b>System Total:",	        Math.round(data["STATUS"]["system"]["space_main_available"]/1024/1024*10)/10+" GByte" );

	text += mboxHtmlTable("<b>Data Used:",		Math.round(data["STATUS"]["system"]["space_usb_used"]/1024/1024*10)/10+" GByte" );
	text += mboxHtmlTable("<b>Data Total:",		Math.round(data["STATUS"]["system"]["space_usb_available"]/1024/1024*10)/10+" GByte" );
	text += mboxHtmlTable("end");
	text += "<hr/>";

	setTextById("setting2",text);
	mboxSettingsStatusPerformance_load();

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
	onclick  = "appFW.setAutoupdateLoading();appFW.requestAPI(#PUT#,[#load#,#all#],##,mboxHtmlShowLoading);";
        cmd      = "appMsg.confirm('" + question + "','" + onclick + "', 260);";
	text    += button( cmd, "Reload Data" );

	question = "<br/>"+lang("QUESTION_LOAD_NEW");
	onclick  = "appFW.setAutoupdateLoading();appFW.requestAPI(#PUT#,[#load#,#new#],##,mboxHtmlShowLoading);";
        cmd      = "appMsg.confirm('" + question + "','" + onclick + "', 260);";
	text    += button( cmd, "Load New Data" );

	question = "<br/>" + lang("QUESTION_LOAD_IMG");
	onclick  = "appFW.requestAPI(#PUT#,[#load#,#images#],##,mboxHtmlShowLoading)";
        cmd      = "appMsg.confirm('" + question + "','" + onclick + "', 260);";
	text    += button( cmd, "Load New Images" );

	text += "<hr/>";

	question = "<br/>"+lang("QUESTION_RESTORE_JSON");
	onclick  = "appFW.requestAPI(#PUT#,[#backup#,#json2db#],##,mboxHtmlShowJson)";
        cmd      = "document.getElementById('json2db').disabled = true;";
        cmd	+= "document.getElementById('json2db').innerHTML = '" + lang("PLEASE_WAIT") + "';";
        cmd     += "appMsg.confirm('" + question + "','" + onclick + "', 260);";
	text    += button( cmd, "Restore (JSON 2 DB)", "json2db" );

	question = "<br/>"+lang("QUESTION_BACKUP2JSON");
	onclick  = "appFW.requestAPI(#PUT#,[#backup#,#db2json#],##,mboxHtmlShowJson)";
        cmd      = "document.getElementById('db2json').disabled = true;";
        cmd	+= "document.getElementById('db2json').innerHTML = '" + lang("PLEASE_WAIT") + " ...';";
        cmd     += "appMsg.confirm('" + question + "','" + onclick + "', 260);";
	text    += button( cmd, "Backup (DB 2 JSON)", "db2json" );

	text += "<hr/></center>";
	question = "Load Card UUID?";
	onclick  = "var card_uuid = document.getElementById(#card_uuid#).value;mboxCardSimulate(card_uuid);";
	cmd      = "appMsg.confirm('" + question + "','" + onclick + "', 260);";

	text += mboxHtmlTable("start");
	text += mboxHtmlTable("<input id='card_uuid' style='width:120px;'/>",button( cmd, "Simulate Card" ));
	text += mboxHtmlTable("end");
	text += "<br/>";
	text += "<hr/>";

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

function mboxSettingsStatusPerformance_load() { appFW.requestAPI("GET",["db","all","-"],"",mboxSettingsStatusPerformance, "wait"); }
function mboxSettingsStatusPerformance(data) {
	setTextById("duration_api_request",		Math.round(data["REQUEST"]["load-time-app"]/1000*10)/10+" s &nbsp; &nbsp; (all data)");
	setTextById("duration_db_request",		Math.round(data["REQUEST"]["load-time"]*1000)/1000+" s");
	setTextById("duration_db_request_per_file",	Math.round(data["REQUEST"]["load-time"]/dict_size(data["DATA"]["files"])*1000)/1000+" s &nbsp; &nbsp; ("+dict_size(data["DATA"]["files"])+")");
	}

//----------------------------------------------------------------
// EOF
