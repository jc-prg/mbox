//--------------------------------------
// jc://music-box/, (c) Christoph Kloth
//--------------------------------------
// Player - LOCAL and REMOTE
//--------------------------------------
// local player requires modules/jc-player/jc-player-*.js
// ... fill playlist for local player via:
/*
mbox_playlist_queue["type"]     = "album";
mbox_playlist_queue["scrollto"] = "scrollto_" + uuid.replace(/-/g,"");
mbox_playlist_queue["album"]	= {
		"album"        : "<album-title>",
		"title"        : "<album-title>",
		"artist"       : "<artist-name>",
		"uuid"         : "<album-uuid>",
		"tracks"       : ["<uuid-1>","<uuid-2>"],
		"cover_image"  : "<url-cover-image>",
		}
mbox_playlist_queue["tracks"]	= [
		"<uuid-1>" : {
			"title"  : "...",
			"artist" : "...",
			"file"   : "...",
			},
		"<uuid-2>" : {
			"title" : "...",
			"artist" : "...",
			"file"  : "...",
			},
		]
*/
//--------------------------------------
/* INDEX:
function mboxPlayerLocal(position=0, play=true)
function mboxPlayerRemote(song,uuid,playing)
function mboxPlayerControlPlaylist_advanced(uuid)
function mboxPlayerControlPlaylist(uuid)
function mboxPlayerControlStream(uuid)
function mboxPlayerProgress()
function mboxPlayerProgressPrint()
function mboxPlayerProgressTime()
function mboxPlayerProgressSet( status, song_length, song_left, song_left_s )
function mboxPlayerJumpToPosition(e)
function mboxPlayerButton( button, cmd="", color="blue", small="", display="block" )
function mboxPlayerButtonText( button, cmd="", color="blue", small="", display="block" )
*/
//--------------------------------------

var mboxPlayer;

//--------------------------------------
// LOCAL PLAYER
//--------------------------------------

function mboxPlayerLocal(position=0, play=true) {

	if (!mboxPlayer) { mboxPlayer = new jcPlayer("mboxPlayer","audioPlayer", mbox_music_dir, mbox_cover_dir, "apps/"); }

	mboxPlayer.activeTrack              	  = position;
	mboxPlayer.activeCtrl["info_cover"] 	  = false;
	mboxPlayer.activeCtrl["info_short"] 	  = true;
	mboxPlayer.activeCtrl["progress_padding"] = "0";
	mboxPlayer.init();

	console.log(mbox_playlist_queue);

	if (play) {
		mboxPlayer.load(mbox_playlist_queue);
		mboxPlayer.play();
		}
	}

//--------------------------------------
// REMOTE PLAYER
//--------------------------------------


function mboxPlayerRemote(song,uuid,playing) {

	var text = "";

	// playback control
	var display_player = "hidden";
	if (playing != 0) { display_player = "visible"; }

	// check if control panel open
	var on_off = "";
	if (mboxControlPanel_open)  { on_off = " on1";  } //display_open="none"; display_close="block"; }
	else			     { on_off = " off1"; } //display_open="block"; display_close="none";  }

	// print player
	if (mbox_device != "local") {
		text += "<div class='mbox_ctrl_info_player"+on_off+"' style='width:95%;float:left;visibility:"+display_player+";' id='mbox_control_info'>";
		text += "<hr/>";
		if (song)         {
			uuid_song   = song["uuid"];
			text += "<div style='width:100%;float:left;'>"
			text += mboxPlayerControlPlaylist(uuid);
			text += "</div>";
			text += "<div style='width:100%;float:left;'>"
			text += "<hr/>";
			text += mboxPlayerProgressPrint();
			text += "</div>";
			mboxControlPlaying_show(uuid,uuid_song,playing);
			}
		else		  { mboxControlPlaying_delete(); }
		text += "</div>";
		}
	return text;
	}
	
	
// control buttons for playlist - advanced
//--------------------------------------
// idea ...

function mboxPlayerControlPlaylist_advanced(uuid) {
	var text = "";

	// images / text not placed in the middle ...

	text += mboxPlayerButtonText("-10","appFW.requestAPI('GET', ['play_last','10'],  '', mboxControl);",  "blue");
	text += mboxPlayerButtonText("-5", "appFW.requestAPI('GET', ['play_last','5'],   '', mboxControl);",   "blue");
	text += mboxPlayerButton("back",   "appFW.requestAPI('GET', ['play_last','1'],   '', mboxControl);",   "blue");
	text += mboxPlayerButton("play",   "appFW.requestAPI('GET', ['play','"+uuid+"'], '', mboxControl);",   "blue");
	text += mboxPlayerButton("next",   "appFW.requestAPI('GET', ['play_next','1'],   '', mboxControl);",   "blue");
	text += mboxPlayerButtonText("+5", "appFW.requestAPI('GET', ['play_next','5'],   '', mboxControl);",   "blue");
	text += mboxPlayerButtonText("+10","appFW.requestAPI('GET', ['play_next','10'],  '', mboxControl);",  "blue");
	
	text += mboxPlayerButton("empty");
	text += mboxPlayerButton("pause","appFW.requestAPI('GET', ['pause'], 	'', mboxControl);",                    		"blue");
	text += mboxPlayerButton("stop", "appFW.requestAPI('GET', ['stop'],  	'', mboxControl); mboxControlPanel_hide(true);",	"blue");
	text += mboxPlayerButton("empty");
	text += mboxPlayerButton("goto", "mboxControlShowUUID('"+uuid+"');", "blue");

	appMsg.confirm( text, "", 260);
	}


// control buttons for playlist
//--------------------------------------

function mboxPlayerControlPlaylist(uuid) {
	var text = "";

	text += mboxPlayerButtonText("&nbsp;-5", "appFW.requestAPI('GET', ['play_last','5'],  '', mboxControl);",   "blue");
	text += mboxPlayerButton("back", "appFW.requestAPI('GET', ['play_last','1'],  '', mboxControl);",   "blue");
	text += mboxPlayerButton("play", "appFW.requestAPI('GET', ['play','"+uuid+"'],'', mboxControl);",   "blue");
	text += mboxPlayerButton("next", "appFW.requestAPI('GET', ['play_next','1'],  '', mboxControl);",   "blue");
	text += mboxPlayerButtonText("+5", "appFW.requestAPI('GET', ['play_next','5'],  '', mboxControl);",   "blue");
	text += mboxPlayerButton("empty");
	text += mboxPlayerButton("pause","appFW.requestAPI('GET', ['pause'], 		'', mboxControl);",                    		"blue");
	text += mboxPlayerButton("stop", "appFW.requestAPI('GET', ['stop'],  		'', mboxControl); mboxControlPanel_hide(true);",	"blue");
	text += mboxPlayerButton("empty");
	text += mboxPlayerButton("goto", "mboxControlShowUUID('"+uuid+"');", "blue");
//	text += mboxPlayerButton("goto", "mboxPlayerControlPlaylist_advanced('"+uuid+"');", "green");

	return text;
	}


// control buttons for radio
//--------------------------------------

function mboxPlayerControlStream(uuid) {
        var text = "";

        text += mboxPlayerButton("play",  "appFW.requestAPI('GET', ['play','"+uuid+"'],  '',	mboxControl);",				  "blue");
        text += mboxPlayerButton("pause", "appFW.requestAPI('GET', ['pause'], '', 		mboxControl);",				  "blue");
        text += mboxPlayerButton("stop",  "appFW.requestAPI('GET', ['stop'],  '', 		mboxControl);mboxControlPanel_hide(true);", "blue");

        return text;
        }


//--------------------------------------
// PROGRESS BAR
//--------------------------------------

// ID for set Interval
var mboxPlayerProgress_ID = -1;

// set Interval if player control for box available
//---------------------------------------------

function mboxPlayerProgress() {
	if (document.getElementById("mbox_progresstime")) {
		if (mboxPlayerProgress_ID == -1) {
			mboxPlayerProgress_ID = setInterval(function(){ mboxPlayerProgressTime(); },1000);
			console.log("Set Intervall with ID "+mboxPlayerProgress_ID);
			}
		}
	else if (mboxPlayerProgress_ID != -1) {
		clearInterval( mboxPlayerProgress_ID );
		mboxPlayerProgress_ID = -1;
		console.log("Clear Intervall with ID "+mboxPlayerProgress_ID);
		}
	}

//---------------------------------------------

function mboxPlayerProgressPrint() {

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

// calculate and show time
//----------------------------------
function mboxPlayerProgressTime() {
	var status	 	= document.getElementById("mbox_status").innerHTML;
	var seconds_left 	= document.getElementById("mbox_progresstime").innerHTML;
	var time_left		= convert_second2time(seconds_left);

	// set new time if playing
	if (seconds_left > 0 && status == "play")	{ setTextById( "mbox_progresstime", seconds_left - 1); }
	else			{ } // mboxControl_load(); }
	setTextById( "mboxPlayer_progresstime", "[ -" + time_left + " ]" );

	// set progress
	var hundred 	= document.getElementById("mbox_progresspercentage").innerHTML;
	var progress    = (hundred - seconds_left) / hundred * 100;

	document.getElementById("mboxPlayer_progress").style.width = progress + "%";
	//console.log(hundred + " - " + progress+"%");
	}

// Update time
//--------------------------------------

function mboxPlayerProgressSet( status, song_length, song_left, song_left_s ) {

	// if progress bar exists
	if (document.getElementById("mbox_progresstime")) {
		if (song_left) { setTextById("mboxPlayer_progresstime", 	"[ -" + song_left + " ]" ); }
		mboxPlayerProgress();
		setTextById("mbox_progresstime", 	song_left_s );
		setTextById("mbox_progresspercentage", 	song_length );
		setTextById("mbox_status",	 	status );
		
		progressbar = document.getElementById("mboxPlayer_progressbar");
		progressbar.addEventListener("click", mboxPlayerJumpToPosition, false);
		}
		
	// else deactivate "setInterval"
	else {	mboxPlayerProgress(); }
	
	}


// react on click -> jump to position in file
//--------------------------------------

function mboxPlayerJumpToPosition(e) {
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
	appFW.requestAPI('GET',['play_jump',percentage], '', mboxControl);
	mboxControl_load();
	}

//--------------------------------------
// OTHER
//--------------------------------------

function mboxPlayerButton( button, cmd="", color="blue", small="", display="block" ) {

        var text  = "";

        if (button != "empty") {
                text +=   "<div class=\"player_button " + color + " " + small + "\" onclick=\"javascript:" + cmd + "\" style=\"display:" + display + ";\">";
                text +=   "<img src=\"" + mbox_icon_dir + button + ".png\" class=\"player_image " + small + "\"></div>";
                }
        else {  text +=   "<div class=\"player_button empty " + small + "\"></div>";
                }

        return text;
        }


//--------------------------------------

function mboxPlayerButtonText( button, cmd="", color="blue", small="", display="block" ) {

        var text  = "";

        if (button != "empty") {
                text +=   "<div class=\"player_button " + color + " " + small + "\" onclick=\"javascript:" + cmd + "\" style=\"display:" + display + ";align:center;\">";
                text +=   "<div style=\"color:black;margin:3px;margin-top:5px;\"><b>" + button + "</b></div></div>";
                }
        else {  text +=   "<div class=\"player_button empty " + small + "\"></div>";
                }

        return text;
        }


//--------------------------------------
// EOF
