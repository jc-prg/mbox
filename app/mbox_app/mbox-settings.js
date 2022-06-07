//--------------------------------------
// jc://music-box/, (c) Christoph Kloth
//--------------------------------------
// create settings pages
//--------------------------------------

var MusicDir = "/mbox_music/";


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

function mboxSettingsStatus_load()  {

    appFW.requestAPI("GET",["status"],"",mboxSettingsStatus, "wait");
    }

function mboxSettingsStatus (data) {

	var text    = "";
	var stage   = "Prod Stage"; if (test) { stage = "Test Stage"; }
	var player  = new jcPlayer("player");
	var message = new jcMsg("message");
	var slider  = new jcSlider("slider");
	
	var table		= new jcTable("settings_status");
	table.table_width	= "100%";
	table.columns		= 2;

	text += table.start();
	text += table.row_one("<hr/>");
	text += table.row_one("<center><b>"+lang("INFORMATION")+"</b></center>");
	text += table.row_one("<hr/>");
	text += table.row( ["<b>mBox-Client:",	appTitle + " " + appVersion + "<br/>(" + stage + ")"] );
	text += table.row( ["<b>mBox-Server:",	data["API"]["name"] + " " + data["API"]["version"] + "<br/>(" + data["API"]["stage"] + ")"] );
	text += table.row( ["<b>mBox-Help (Beta):",	"<a href='/mbox_help/help_DE.html' target='_blank'>Deutsche Hilfe (German)</a>"] );

	text += table.row_one("<hr/>");
	text += table.row( ["<b>jcApp:",		appFW.appVersion ] );
	text += table.row( ["<b>jcAppFramework:",	appFwVersion ] );
	text += table.row( ["<b>jcMessage:",		message.appVersion ] );
	text += table.row( ["<b>jcPlayer:",		player.appVersion ] );
	text += table.row( ["<b>jcSlider:",		slider.appVersion ] );
	text += table.row( ["<b>jcUpload:",		mbox_upload.appVersion ] );

	text += table.row_one("<hr/>");	
	text += table.row( ["<b>Modus:", 		mbox_mode ] );
	text += table.row( ["<b>Playing:", 		data["STATUS"]["playback"]["playing"] ] );
	text += table.row( ["<b>Active Device:", 	data["STATUS"]["active_device"] ] );
	text += table.row( ["<b>Window:", 		document.body.clientWidth + "x" + document.body.clientHeight ] );
	text += table.row( ["<b>Internet:",		internetConnect ] );
	text += table.row_one("<hr/>");
	
	if (data["STATUS"]["playback"]["status"] == "") {
		text += table.row( ["<b>Status:",	 "idle" ] );
		}
	else {
		text += table.row( ["<b>Status:",	 data["STATUS"]["playback"]["status"] + " (<a href='' onclick='alert(\"" + data["STATUS"]["playback"]["file"] + "\")'>filename</a>)" ] );
		}
	
	text += table.row_one("<hr/>");
	text += table.row( ["<b>Files:", 		data["STATUS"]["statistic"]["files"] ] );
	text += table.row( ["<b>Tracks:", 		data["STATUS"]["statistic"]["tracks"] ] );
	text += table.row( ["<b>Artists:", 		data["STATUS"]["statistic"]["albums"] ] );
	text += table.row( ["<b>Albums:", 		data["STATUS"]["statistic"]["album_info"] ] );
	text += table.row( ["<b>Playlists:",		data["STATUS"]["statistic"]["playlists"] ] );
	text += table.row( ["<b>Web-Radio:",		data["STATUS"]["statistic"]["radio"] ] );
	text += table.row_one("<hr/>");
	text += table.end();

	setTextById("setting1",text);

	//---------------------------------

	text = "";

	text += table.start();
	text += table.row_one("<hr/>");
	text += table.row_one("<center><b>Test Settings</b></center>");
	text += table.row_one("<hr/>");
	text += table.row_one( button( "uploadImage();", "Upload Image" ) + button( "mboxCoverTogglePrint();", "Cover Images" ) );

	text += table.row_one("<hr/>");
	text += table.row_one("<center><b>"+lang("LOADING_TIME")+"</b></center>");
	text += table.row_one("<hr/>");
	text += table.row( ["<b>Initial load:",		Math.round(data["STATUS"]["system"]["server_start_duration"]*10)/10+" s" ] );
	text += table.row( ["<b>Running for:",		Math.round(data["STATUS"]["system"]["server_running"]) +" s" ] );

	text += table.row_one("<hr/>");
	text += table.row( ["<b>API request:", 		"<div id=\"duration_api_request\">Please Wait</div>" ] );
	text += table.row( ["<b>DB request:",			"<div id=\"duration_db_request\">Please Wait</div>" ] );
	text += table.row( ["<b>DB request per file:",	"<div id=\"duration_db_request_per_file\">Please Wait</div>" ] );

	text += table.row_one("<hr/>");
	text += table.row_one("<center><b>"+lang("DISC_SPACE")+"</b></center>");
	text += table.row_one("<hr/>");
	text += table.row( ["<b>System Used:",		Math.round(data["STATUS"]["system"]["space_main_used"]/1024/1024*10)/10+" GByte" ] );
	text += table.row( ["<b>System Total:",		Math.round(data["STATUS"]["system"]["space_main_available"]/1024/1024*10)/10+" GByte" ] );
	text += table.row( ["<b>Data Used:",			Math.round(data["STATUS"]["system"]["space_usb_used"]/1024/1024*10)/10+" GByte" ] );
	text += table.row( ["<b>Data Total:",			Math.round(data["STATUS"]["system"]["space_usb_available"]/1024/1024*10)/10+" GByte" ] );

	text += table.row_one("<hr/>");
	text += table.row_one("<center><b>" + lang("SIMULATE_CMD") + "</b></center>");
	text += table.row_one("<hr/>");

	question = "Load Card UUID?";
	onclick  = "var card_uuid = document.getElementById(#card_uuid#).value;mboxCardSimulate(card_uuid);";
	cmd1     = "appMsg.confirm('" + question + "','" + onclick + "', 260);";

	text += table.row(["<input id='card_uuid' style='width:120px;'/>",button( cmd1, "Simulate Card" )]);
	text += table.row_one("<hr/>");

	cmd1  = "appFW.requestAPI('GET',['volume','up'],'','')";
	cmd2  = "appFW.requestAPI('GET',['volume','down'],'','')";
	cmd3  = "appFW.requestAPI('GET',['volume','mute'],'','')";
	cmd4  = "appFW.requestAPI('GET',['play_next','1'],'','')";
	cmd5  = "appFW.requestAPI('GET',['pause'],'','')";
	cmd6  = "appFW.requestAPI('GET',['play_last','1'],'','')";
	
	text += table.row(["Volume",    mboxHtmlSimpleButton( cmd2, "Vol-", "", 49 ) + mboxHtmlSimpleButton( cmd3, "Mute", "", 49 )  + mboxHtmlSimpleButton( cmd1, "Vol+", "", 49 ) ]);
	text += table.row(["Playback",  mboxHtmlSimpleButton( cmd6, "Back", "", 49 ) + mboxHtmlSimpleButton( cmd5, "Pause", "", 49 ) + mboxHtmlSimpleButton( cmd4, "Next", "", 49 ) ]);
	
	text += table.row_one("<hr/>");
	text += table.end();

	setTextById("setting2",text);
	mboxSettingsStatusPerformance_load();

	//---------------------------------

	var demo_p = "";
	var demo_a = "";
	for (var key in data["DATA"]["album_info"]) { demo_a = key; }
	for (var key in data["DATA"]["playlists"])  { demo_p = key; }

	text = "";
	text += table.start();
	text += table.row_one("<hr/>");
	text += table.row_one("<center><b>" + lang("RELOAD_DATA") + "</b></center>");
	text += table.row_one("<hr/>");

	var onclick = ""; var question = ""; var cmd = "";

	question = "<br/>"+lang("QUESTION_RELOAD");
	onclick  = "appFW.setAutoupdateLoading();appFW.requestAPI(#PUT#,[#load#,#all#],##,mboxHtmlShowLoading);";
	var cmd1 = "appMsg.confirm('" + question + "','" + onclick + "', 260);";

	question = "<br/>"+lang("QUESTION_LOAD_NEW");
	onclick  = "appFW.setAutoupdateLoading();appFW.requestAPI(#PUT#,[#load#,#new#],##,mboxHtmlShowLoading);";
	var cmd2 = "appMsg.confirm('" + question + "','" + onclick + "', 260);";

	question = "<br/>" + lang("QUESTION_LOAD_IMG");
	onclick  = "appFW.requestAPI(#PUT#,[#load#,#images#],##,mboxHtmlShowLoading)";
	var cmd3 = "appMsg.confirm('" + question + "','" + onclick + "', 260);";

	text    += table.row_one( button( cmd1, "Reload Data" ) + button( cmd2, "Load New Data" ) + button( cmd3, "Load New Images" ));
	text    += table.row_one("<hr/>");

	question = "<br/>"+lang("QUESTION_RESTORE_JSON");
	onclick  = "appFW.requestAPI(#PUT#,[#backup#,#json2db#],##,mboxHtmlShowJson)";
	cmd1     = "document.getElementById('json2db').disabled = true;";
	cmd1	+= "document.getElementById('json2db').innerHTML = '" + lang("PLEASE_WAIT") + "';";
	cmd1    += "appMsg.confirm('" + question + "','" + onclick + "', 260);";

	question = "<br/>"+lang("QUESTION_BACKUP2JSON");
	onclick  = "appFW.requestAPI(#PUT#,[#backup#,#db2json#],##,mboxHtmlShowJson)";
	cmd2     = "document.getElementById('db2json').disabled = true;";
	cmd2    += "document.getElementById('db2json').innerHTML = '" + lang("PLEASE_WAIT") + " ...';";
	cmd2    += "appMsg.confirm('" + question + "','" + onclick + "', 260);";

	text    += table.row_one( button( cmd1, "Restore (JSON 2 DB)", "json2db" ) + button( cmd2, "Backup (DB 2 JSON)", "db2json" ));

	text += table.row_one("<hr/>");
	text += table.row_one("<center><b>Development</b></center>");
	text += table.row_one("<hr/>");
	text += table.end();
	
	text += "<ul>";
      	text += "<li>" + add_link( RESTurl + "api/status/", "API-Link: Status") + "</li>";
      	text += "<li>" + add_link( RESTurl + "api/db/all/-/", "API-Link: List all") + "</li>";
      	text += "<li>" + add_link( RESTurl + "api/play/test/", "API-Link: Play Demo") +" </li>";
     	text += "<li>" + add_link( RESTurl + "api/speak/LETS-GO/", "API-Link: Play Message &quot;LETS-GO&quot;") +"</li>";
      	text += "<li>" + add_link( RESTurl + "api/data/album_info/test/", "API-Link: List Album Demo") + "</li>";
      	text += "<li>" + add_link( RESTurl + "api/ui/", "API-Link: Swagger UI") + "</li>";
      	text += "<li>" + add_link( RESTurl_noport + ":" + couchdb_port +"/", "API-Link: CouchDB") + "</li>";
      	text += "<li>" + add_link( RESTurl_noport + ":" + couchdb_port +"/_utils/", "API-Link: CouchDB Admin-Panel") + "</li>";
      	text += "<li>" + add_link( RESTurl_noport + ":" + couchdb_port +"/albums/main/", "API-Link: CouchDB Sample Access") + "</li>";
	text += "</ul>";

	setTextById("setting3",text);
	}

function mboxSettingsStatusPerformance_load() {

    appFW.requestAPI("GET",["db","all","-"],"",mboxSettingsStatusPerformance, "wait");
    }

function mboxSettingsStatusPerformance(data) {
	setTextById("duration_api_request",		Math.round(data["REQUEST"]["load-time-app"]/1000*10)/10+" s &nbsp; &nbsp; (all data)");
	setTextById("duration_db_request",		Math.round(data["REQUEST"]["load-time"]*1000)/1000+" s");
	setTextById("duration_db_request_per_file",	Math.round(data["REQUEST"]["load-time"]/dict_size(data["DATA"]["files"])*1000)/1000+" s &nbsp; &nbsp; ("+dict_size(data["DATA"]["files"])+")");
	}
