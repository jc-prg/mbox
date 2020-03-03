//--------------------------------------
// jc://music-box/, (c) Christoph Kloth
//--------------------------------------
// file mbox control at the bottom 
// of the page (loaded by auto update)
//--------------------------------------
/* INDEX:
function mboxWriteGroups()
function mboxControlLoad()
function mboxControl (data)
function mboxControlChangePosition(e)
function mboxControlProgressPrint()
function mboxControlProgress()
function mboxControlProgressTime()
function mboxVolumeControl(volume, mute)
function mboxPlaylistControl(uuid)
function mboxShowUUID(uuid)
function mboxRadioControl(uuid)
function mboxShowPlaying(uuid,uuid_song,playing)
function mboxButton2( sendCmd, label )
function mboxControl_open()
function mboxCheckLoading(data)
function mboxCheckStatus ()
function mboxDeletePlaying ()
function mboxSetStatus (color)
function mboxToggleDevice ()
function mboxToggleFilter ()
*/
//--------------------------------------

mbox_control_open = false;

// Write menu with groups ...
//-----------------------------------------------------------

function mboxWriteGroups() {
        var text    = "";
        var cover   = [mbox_icons["album_bw"],mbox_icons["playlist_bw"],mbox_icons["radio_bw"]];
        var descr   = ["Album/CD","Playlist","Stream"];
        var onclick = [
                        "mboxAlbumAllLoad();",
                        "mboxPlaylistAll_load();",
                        "mboxRadioLoad();",
                        ];

        text += "<div style='width:325px;margin:auto;'>";
        for (var i=0;i<cover.length;i++) {
               text += "<div class=\"album_cover small\" style=\"background:url("+cover[i]+");background-size:cover;background-repeat:no-repeat;vertical-align:botton;border:none;\" onclick='" + onclick[i] + "'></div>";
                text += "<div class=\"album_cover_descr\" onclick='" + onclick[i] + "'>" + descr[i] + "</div>";
                }
        text += "</div>";
        setTextById("remote1",text);
        }


//-----------------------------------------------------------

function mboxControlLoad()            { mboxApp.requestAPI('GET', ["status"], "", mboxControl,"","mboxControlLoad"); }
function mboxControl (data) {

        var text       = "";
	var d          = data["STATUS"]["playback"];
	var type       = d["device"];
	var volume     = d["volume"];
	var mute       = d["mute"];
	var status     = d["status"];
	var playing    = d["playing"];
	var uuid       = "";
	var audio      = "";

	if (getTextById("audioPlayer") != false) { audio = getTextById("audioPlayer"); }

	text  += "<div style='width:100%;'>";
	text  += "<div class='mbox_ctrl_info'>";

	// local player
	if (mbox_device == "local") { text += "<div id='audioPlayer'>"+audio+"</div>"; 	}

	// remote player
	else {
		// Info for running music, if music box
		if (type == "music_box") {
			var song        = d["song"];
			var playlist    = d["playlist"];
			var p_position  = d["playlist_pos"];
			var p_length    = d["playlist_len"];

			if ("playlist_uuid" in d && d["playlist_uuid"].length > 0) {
				uuid = d["playlist_uuid"];
				}
			else {	uuid = song["uuid_album"];
				}

			if (song)	{ uuid_song   = song["uuid"]; }
                        else		{ uuid_song   = ""; }

			// calculate position in song
			var song_length = Math.round(d["length"]);
			var song_left_s = Math.round(d["length"] - (d["position"]));
			var song_left   = convert_second2time( Math.round(d["length"] - (d["position"])) );

			// Show album and titel ...
			if (song) { if (song["info"] == "Title loaded" && playing != 0) {
				text += "&nbsp;<b>" + song["artist"] + "</b><br/>";
				text += "&nbsp;" + song["title"] + " (" + p_position + "/" + p_length + ")<br/>";
				//text += "<i>" + status + "</i><br/>";
				}

			// No song loaded ...
		  	else {
				text += "<i>"+lang("SELECT_MUSIC_ITEM") +"</i><br/>&nbsp;";
			} } }

		// Info for running music, if web stream / radio
		else if (type == "radio") {
			var channel	= d["stream"];
			var title       = d["stream"]["title"];
			var description = d["stream"]["description"];
			var info        = d["stream"]["stream_info"];
			uuid            = channel["uuid"];
			console.log(channel["uuid"]);

			if (channel && channel["uuid"] && playing != 0) {
				if (d["channel_info"]) 	{ text += "<b>" + d["channel_info"] + "</b> (<a href=\"" + info + "\" target=\"_blank\" style=\"color:white\">www</a>) ... "+description+"<br/>"; }
				else 			{ text += "<b>" + title + "</b>: " + description + " (<a href=\"" + info + "\" target=\"_blank\" style=\"color:white\">www</a>)<br/>"; }
				text += "<i>" + status + "</i><br/>";  			//text += "<i>" + status + " ("+channel["uuid"]+")</i><br/>";
				}
		  	else {	text += "<i>"+lang("SELECT_MUSIC_ITEM") +"</i><br/>&nbsp;";
				}
			}
		else {
			text += "<i>"+lang("DEVICE_UNKNOWN") +"</i><br/>&nbsp;";
			}
		}
	text += "</div>";
	text += "</div>";

	if (playing != 0) {
		// Control to open and close ...
		var display_open  = "block";
        	var display_close = "none";

		// check if open ...
		var on_off = "";
		if (mbox_control_open)  { on_off = " on1"; display_open="none"; display_close="block"; }
		else			{ on_off = " off1"; }

		text += "<div class='mbox_ctrl_open' id='ctrl_open' style='display:"+display_open+";'>";
		text += mboxButton("open", "mboxControl_open();",   "blue", "right");
		text += "</div>";

		text += "<div class='mbox_ctrl_open' id='ctrl_close' style='display:"+display_close+";'>";
		text += mboxButton("close", "mboxControl_open();",   "red", "right");
		text += "</div>";
		}

	// volume control
	text += mboxVolumeControl(volume,mute);

	// playback control
	var display_player = "hidden";
	if (playing != 0) { display_player = "visible"; }

	if (mbox_device != "local") {
		text += "<div class='mbox_ctrl_info_player"+on_off+"' style='width:95%;float:left;visibility:"+display_player+";' id='mbox_control_info'>";
		text += "<hr/>";
		if (song)         {
			text += "<div style='width:100%;float:left;'>"
			text += mboxPlaylistControl(uuid);
			text += "</div>";
			text += "<div style='width:100%;float:left;'>"
			text += "<hr/>";
			text += mboxControlProgressPrint();
			text += "</div>";
			mboxShowPlaying(uuid,uuid_song,playing);
			}
		else if (channel) { text += mboxRadioControl(uuid);    mboxShowPlaying(uuid,playing); }
		else		  { mboxDeletePlaying(); }
		text += "</div>";
		}

        setTextById("mbox_control",      	text);

	if (document.getElementById("mbox_progresstime")) {
		if (song_left) { setTextById("mboxPlayer_progresstime", 	"[ -" + song_left + " ]" ); }
		mboxControlProgress();
		setTextById("mbox_progresstime", 	song_left_s );
		setTextById("mbox_progresspercentage", 	song_length );
		setTextById("mbox_status",	 	status );
		
		progressbar = document.getElementById("mboxPlayer_progressbar");
		progressbar.addEventListener("click", mboxControlChangePosition, false);
		}
	else {	mboxControlProgress(); } // to deactivate "setInterval"

	if (audio == "" && mbox_device == "local") { localPlayer(0,false); }
	}

//---------------------------------------------

function mboxControlChangePosition(e) {
        var xPosition   = e.clientX;
        var yPosition   = e.clientY;
        var progressbar = document.getElementById("mboxPlayer_progressbar");
        var width       = progressbar.offsetWidth;
        
	var bodyRect   = document.body.getBoundingClientRect(),
	    elemRect   = progressbar.getBoundingClientRect(),
	    offset     = elemRect.left - bodyRect.left;
	    
	var pos        = xPosition - offset;
	var percentage = Math.round( pos / width * 100);

	console.log("Position: " + xPosition + "/" + Math.round(pos) + "/" + percentage );
	mboxApp.requestAPI('GET',['play_jump',percentage], '', mboxControl);
	mboxControlLoad();
	}


//---------------------------------------------

function mboxControlProgressPrint() {

	var progress = "";
	if (document.getElementById("mboxPlayer_progress")) { progress = document.getElementById("mboxPlayer_progress").style.width; }

	var player;
	player  = "<table border='0' width='100%'>";
	player += "<tr id='mboxPlayer_tr_progress'>";
	player +=    "<td class='mboxPlayer_td_time'><center>";
	player +=       "<div id=\"mboxPlayer_progresstime\"></div>";
	player +=       "<div id=\"mbox_status\"             style=\"display:none;\"></div>";
	player +=       "<div id=\"mbox_progresstime\"       style=\"display:none;\"></div>";
	player +=       "<div id=\"mbox_progresspercentage\" style=\"display:none;\"></div>";
	player +=    "</center></td>";
	player +=    "<td class='mboxPlayer_td_progress'>";
	player +=       "<div id=\"mboxPlayer_progressbar\"><div id=\"mboxPlayer_progress\" style=\"width:" + progress + "\"></div></div>";
	player += "</td></tr>";
	player += "</table>";
	return player;
	}

// ID for set Interval
var mboxControlProgress_ID = -1;

// set Interval if player control for box available
function mboxControlProgress() {
	if (document.getElementById("mbox_progresstime")) {
		if (mboxControlProgress_ID == -1) {
			mboxControlProgress_ID = setInterval(function(){ mboxControlProgressTime(); },1000);
			console.log("Set Intervall with ID "+mboxControlProgress_ID);
			}
		}
	else if (mboxControlProgress_ID != -1) {
		clearInterval( mboxControlProgress_ID );
		mboxControlProgress_ID = -1;
		console.log("Clear Intervall with ID "+mboxControlProgress_ID);
		}
	}

// calulate and show time
//----------------------------------
function mboxControlProgressTime() {
	var status	 	= document.getElementById("mbox_status").innerHTML;
	var seconds_left 	= document.getElementById("mbox_progresstime").innerHTML;
	var time_left		= convert_second2time(seconds_left);

	// set new time if playing
	if (seconds_left > 0 && status == "play")	{ setTextById( "mbox_progresstime", seconds_left - 1); }
	else			{ } // mboxControlLoad(); }
	setTextById( "mboxPlayer_progresstime", "[ -" + time_left + " ]" );

	// set progress
	var hundred 	= document.getElementById("mbox_progresspercentage").innerHTML;
	var progress    = (hundred - seconds_left) / hundred * 100;

	document.getElementById("mboxPlayer_progress").style.width = progress + "%";
	//console.log(hundred + " - " + progress+"%");
	}


//---------------------------------------------
// show / control volume
//---------------------------------------------

function mboxVolumeControl(volume, mute) {


	// buttons for top control
	var top = "";
	if (mbox_device != "local") {
		top += mboxButton("vol+", "mboxApp.requestAPI('GET',['volume','up'],   '', mboxControl);", "blue big");
		top += mboxButton("mute", "mboxApp.requestAPI('GET',['volume','mute'], '', mboxControl);", "blue big");
		top += mboxButton("vol-", "mboxApp.requestAPI('GET',['volume','down'], '', mboxControl);", "blue big");
		}
	else {
		top += mboxButton("vol+", "if (mboxPlayer) { mboxPlayer.volumeUp();   mboxVolumeControl(); }", "green big");
		top += mboxButton("mute", "if (mboxPlayer) { mboxPlayer.volumeMute(); mboxVolumeControl(); }", "green big");
		top += mboxButton("vol-", "if (mboxPlayer) { mboxPlayer.volumeDown(); mboxVolumeControl(); }", "green big");
		}

	// buttons for bottom control
	var text      = "";
	var vol_color = "white";

	// check volume and show in navigation bar
	if (mbox_device == "local") {
		var vol_color = "lightgreen";
		if (mboxPlayer) { volume = mboxPlayer.volume; if (mboxPlayer.audio.muted) { mute = 1; } else { mute = 0; }}
		else		{ volume = 0; }
		}

        // check audio status and show in navigation bar
        if (Math.round(volume*20/1) < 1 || mute == 1) {
                document.getElementById("audio1").style.display = "block";
                document.getElementById("audio2").style.display = "none";
                if (mbox_device != "local") 	{ vol_color = "gray"; }
		else				{ vol_color = "green"; }
                }
        else {
                document.getElementById("audio1").style.display = "none";
                document.getElementById("audio2").style.display = "block";
                }

	// check volume and show in navigation bar
        var volume  = Math.round( volume * 20 / 1 );
        var vol_str = "<font color='" + vol_color + "'>";
        for (var i=0; i<volume; i++) { vol_str += "I"; }
        vol_str += "</font>";
        for (var i=0; i<20-volume; i++) { vol_str += "I"; }


	setTextById("audio3", vol_str);
	setTextById("audio_ctrl", top);

	setOnclickById("audio1", "changeVisibility('audio_ctrl');");
	setOnclickById("audio2", "changeVisibility('audio_ctrl');");
	setOnclickById("audio3", "changeVisibility('audio_ctrl');");
	setOnclickById("audio4", "changeVisibility('audio_ctrl');");

	return text;
	}

// control for playlist
//--------------------------------------

function mboxPlaylistControl(uuid) {
	var text = "";

	text += mboxButton("back", "mboxApp.requestAPI('GET', ['play_next','-1'],  '', mboxControlLoad);",   "blue");
	text += mboxButton("play", "mboxApp.requestAPI('GET', ['play','"+uuid+"'], '', mboxControlLoad);",   "blue");
	text += mboxButton("next", "mboxApp.requestAPI('GET', ['play_next','1'],   '', mboxControlLoad);",   "blue");
	text += mboxButton("empty");
	text += mboxButton("pause","mboxApp.requestAPI('GET', ['pause'], '', mboxControlLoad);",                    "blue");
	text += mboxButton("stop", "mboxApp.requestAPI('GET', ['stop'],  '', mboxControlLoad); mboxControl_open();","blue");
	text += mboxButton("empty");
	text += mboxButton("goto", "mboxShowUUID('"+uuid+"');", "blue");

	return text;
	}

// show album / playlist / ...
//--------------------------------------

function mboxShowUUID(uuid) {

	// scroll to album / playlist / streaming entry
	document.getElementById('scrollto_'+uuid.replace(/-/g,"")).scrollIntoView();

	// reload and open album / playlist entry
	if (uuid.indexOf("p_") >= 0) 		{ mboxPlaylistAll_load("",uuid); }
	else if (uuid.indexOf("a_") >= 0) 	{ mboxAlbumAllLoad("",uuid); }
	}


// control for radio
//--------------------------------------

function mboxRadioControl(uuid) {
        var text = "";

        text += mboxButton("play",  "mboxApp.requestAPI('GET', ['play','"+uuid+"'],  '', mboxControl);",         "blue");
        text += mboxButton("pause", "mboxApp.requestAPI('GET', ['pause'], '', mboxControl);",                    "blue");
        text += mboxButton("stop",  "mboxApp.requestAPI('GET', ['stop'],  '', mboxControl);mboxControl_open();", "blue");

        return text;
        }

// show which album, playlist or channel plays
//--------------------------------------

function mboxShowPlaying(uuid,uuid_song,playing) {


	activeElements = document.getElementsByClassName("player_active");

	for (var i=0;i<activeElements.length;i++) {
		element = activeElements[i];
		if (playing != 0) {
			if (element.id == "playing_"+uuid)		{ element.style.display = "block"; }
			else if (element.id == "playing2_"+uuid) 	{ element.style.display = "block"; }
			else if (element.id == "playing3_"+uuid) 	{ element.style.display = "block"; }
			else if (element.id == "playing_"+uuid_song)	{ element.style.display = "block"; }
			else if (element.id == "playing2_"+uuid_song) 	{ element.style.display = "block"; }
			else if (element.id == "playing3_"+uuid_song) 	{ element.style.display = "block"; }
			else 						{ element.style.display = "none"; }
			}
		else 						{ element.style.display = "none"; }
		}

	return;
	}



//--------------------------------------
// BUTTONS
//--------------------------------------

// create button with sendCmd command
//--------------------------------------

function mboxButton2( sendCmd, label ) {
	return "<button onclick='javascript:mboxApp.sendCmd(" + sendCmd + ", mboxControl)'>" + label + "</button>";
	}



// open and close mbox control at the bottom of the page

function mboxControl_open() {

	if (mbox_control_open == false) {
		document.getElementById('mbox_control').classList.remove('off');
		document.getElementById('mbox_control').classList.add('on');
		if (document.getElementById('mbox_control_info')) {
			document.getElementById('mbox_control_info').classList.remove('off1');
			document.getElementById('mbox_control_info').classList.add('on1');
			}
                document.getElementById('ctrl_close').style.display = "none";
                document.getElementById('ctrl_open').style.display  = "block";

		mbox_control_open = true;
		}
	else {
		document.getElementById('mbox_control').classList.remove('on');
		document.getElementById('mbox_control').classList.add('off');
		if (document.getElementById('mbox_control_info')) {
			document.getElementById('mbox_control_info').classList.add('off1');
			document.getElementById('mbox_control_info').classList.remove('on1');
			}
                document.getElementById('ctrl_close').style.display = "block";
                document.getElementById('ctrl_open').style.display  = "none";

		mbox_control_open = false;
		}

	//document.getElementById('mbox_control').classList.toggle('on');
	//document.getElementById('mbox_control_info').classList.toggle('on');
	}


//--------------------------------------
// check if loaded ...
//--------------------------------------

function mboxCheckLoading(data) {

	var text      = "";
        var load_data = data["STATUS"]["load_data"];
	var progress  = load_data["reload_progress"];
	var l_new     = load_data["reload_new"];
	var l_all     = load_data["reload_all"];
	var l_time    = load_data["reload_time_left"];

	// write info to ...
	if (document.getElementById("reload_info")) {
		if (l_new == false && l_all == false) { progress = 100; }
		if (l_new) { text = "Load new Data: "; }
		if (l_all) { text = "Reload all Data: "; }
		setTextById("reload_info",text + Math.round(progress*100)/100+"% ("+convert_second2time(Math.round(l_time))+" min)");
		}
	}


//--------------------------------------
// CONNECTION LED
//--------------------------------------

function mboxCheckStatus () {
	var d    = new Date();
	var last = d.getTime() - mboxApp.lastConnect;
	//console.log("Last Connect: "+last);

	if (last < 15000) 	{ mboxSetStatus("green"); }
	else if (last < 35000) 	{ mboxSetStatus("yellow"); mboxDeletePlaying(); }
	else if (last > 65000) 	{ mboxSetStatus("red");    mboxDeletePlaying(); }

	//if

        return last;
	}

//--------------------------------------

function mboxDeletePlaying () {
	for (var i=0;i<mbox_cover_list.length;i++) {
		if (document.getElementById("playing_"  + mbox_cover_list[i])) {document.getElementById("playing_"  + mbox_cover_list[i]).style.display = "none"; }
		if (document.getElementById("playing2_" + mbox_cover_list[i])) {document.getElementById("playing2_" + mbox_cover_list[i]).style.display = "none"; }
		}
	}


//--------------------------------------

function mboxSetStatus (color) {
	var led = "<div id=\""+color+"\"></div>";
	document.getElementById("statusLED").innerHTML = led;
	}


//--------------------------------------
// select active device
//--------------------------------------

function mboxToggleDevice () {
	// switch next device setting

	if (mbox_device == "both") 		{ mbox_device = "local"; }
	else if (mbox_device == "local") 	{ mbox_device = "remote"; }
	else if (mbox_device == "remote") 	{ mbox_device = "local"; } // both ... else only local/remote
	else					{ mbox_device = "both"; }
	}

//--------------------------------------
// show / hide filter
//--------------------------------------

function mboxToggleFilter () {
	// switch next device setting

	if (mbox_filter) 		{ mbox_filter = false;  document.getElementById("remote4").style.display="none"; }
	else				{ mbox_filter = true;   document.getElementById("remote4").style.display="block"; }
	}
	



























