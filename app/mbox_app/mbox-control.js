//--------------------------------------
// jc://music-box/, (c) Christoph Kloth
//--------------------------------------
// file mbox control at the bottom 
// of the page (loaded by auto update)
//--------------------------------------
/* INDEX:
function mboxControlGroups()
function mboxControl_load()
function mboxControl(data)
function mboxControlVolumeSet(volume)
function mboxControlVolumeShow(volume,mute)
function mboxControlVolumeControl(volume, mute)
function mboxControlShowUUID(uuid)
function mboxControlReloadView()
function mboxControlPlaying_show(uuid="",uuid_song="",playing=0)
function mboxControlPlaying_delete ()
function mboxControlPanel_open()
function mboxControlPanel_close()
function mboxControlPanel_toggle()
function mboxControlPanel_hide(complete=false)
function mboxControlPanel_show()
function mboxControlCheckLoading(data)
function mboxControlCheckStatus ()
function mboxControlSetStatus (color)
function mboxControlToggleMode()
function mboxControlToggleDevice ()
function mboxControlToggleFilter (setting="toggle")
function mboxControlToggleFilter_show ()
*/
//--------------------------------------

var mboxControlPanel_open     = false;
var mboxControlPanel_progress = false;


// Write menu with groups ...
//-----------------------------------------------------------

function mboxControlGroups() {
        var text    = "";
        var cover   = [mbox_icon_dir+mbox_icons["album_bw"],mbox_icon_dir+mbox_icons["playlist_bw"],mbox_icon_dir+mbox_icons["radio_bw"]];
        var descr   = [lang("ALBUM"),lang("PLAYLIST"),lang("PODCAST")];
        var onclick = [
                        "mboxAlbumAll_load();",
                        "mboxPlaylists_load();",
                        "mboxStreams_load();"
                        ];

        text += "<div style='width:325px;margin:auto;'>";
        for (var i=0;i<cover.length;i++) {
                text += "<div class=\"album_cover small\" style=\"background:url("+cover[i]+");background-size:cover;background-repeat:no-repeat;vertical-align:botton;border:none;\" onclick='" + onclick[i] + "'></div>";
                text += "<div class=\"album_cover_descr\" onclick=\"" + onclick[i] + "\">" + descr[i] + "</div>";
                }
        text += "</div>";
        setTextById("frame1",text);
        }


//-----------------------------------------------------------

function mboxControl_load()            { appFW.requestAPI('GET', ["status"], "", mboxControl,"","mboxControl_load"); }
function mboxControl(data) {

	var d           = data["STATUS"]["playback"];
	var l           = data["STATUS"]["load_data"];
	if (!d)	{ return; }
	
	var type        = d["device"];
	var type_sub    = d["type"];
	var volume      = d["volume"];
	var mute        = d["mute"];
	var status      = d["status"];
	var playing     = d["playing"];

	var load_new    = l["reload_new"];
	var load_all    = l["reload_all"];
		
	if (data["STATUS"]["system"] && data["STATUS"]["system"]["server_connection"] && data["STATUS"]["system"]["server_connection"]["INTERNET"]) {
		internetConnect = data["STATUS"]["system"]["server_connection"]["INTERNET"];
		}
	else {
		internetConnect = "UNKNOWN";
		}
	
	console.debug("mboxControl: playing="+playing+" / load_new="+load_new+" / load_all="+load_all);
	if (playing == 1 || load_new || load_all) 	{ appFW.setAutoupdateLoading(true, "mboxControl"); }
	else						{ appFW.setAutoupdateLoading(false,"mboxControl"); mboxControlPlaying_show(); }

	if (mbox_device == "remote") {	
		if (playing != 1)	{ mboxControlPanel_hide(); }
		else			{ mboxControlPanel_show(); mboxControlPanel_delay = 0; }
		}
	else 				{ mboxControlPanel_show(); mboxControlPanel_delay = 0; }

	var text       = "";
	var uuid       = "";
	var audio      = "";

	if (getTextById("audioPlayer")) { audio = getTextById("audioPlayer"); }
	
	text    += "<div style='width:100%;'>";
	text    += "<div class='mbox_ctrl_info'>";

	// local player
	if (mbox_device == "local") { 
		// keep current player or create new container for local player
		text += "<div id='audioPlayer'>"+audio+"</div>";

		// set current value to slider
		if (mboxPlayer) { mboxSlider.set_value(Math.round(mboxPlayer.volume*100)); }
		}

	// remote player
	else {
		// set current value to slider
		mboxSlider.set_value(Math.round(volume*100));

		// Info for running music, if music box
		if (type != "radio" || (d["podcast"] && d["podcast"] != {})) {
			var song        = d["song"];
			var playlist    = d["playlist"];
			var p_position  = d["playlist_pos"];
			var p_length    = d["playlist_len"];

			if ("playlist_uuid" in d && d["playlist_uuid"].length > 0)	{ uuid 	= d["playlist_uuid"]; }
			else 								{ uuid 	= song["uuid_album"]; }
			if (song)							{ uuid_song 	= song["uuid"]; }
			else								{ uuid_song 	= ""; }

			// calculate position in song
			var song_length = Math.round(d["length"]);
			var song_left_s = Math.round(d["length"] - (d["position"]));
			var song_left   = convert_second2time( Math.round(d["length"] - (d["position"])) );

			// Show album and titel ...
			if (song) { if (song["info"] == "Title loaded" && playing != 0) {
				if (song["artist"] != undefined) {
					text += "&nbsp;<b>" + song["artist"] + "</b><br/>";
					text += "&nbsp;" + song["title"] + " (" + p_position + "/" + p_length + ")<br/>"; //+uuid;
					}
				else {
					text += "&nbsp;<b>" + song["album"] + "</b><br/>";
					text += "&nbsp;" + song["title"] + " (" + p_position + "/" + p_length + ")<br/>"; //+uuid;
					}
				}

			// No song loaded ...
		  	else {
				text += "<i>"+lang("SELECT_MUSIC_ITEM") +"</i><br/>&nbsp;";
			} } }

		// Info for running music, if web stream / radio
		else if (type == "radio") {
			var channel     = d["stream"];
			var title       = d["stream"]["title"];
			var description = d["stream"]["description"];
			var info        = d["stream"]["stream_info"];
			uuid            = channel["uuid"];
			//console.log(channel["uuid"]);

			if (channel && channel["uuid"] && playing != 0) {
				if (d["channel_info"]) 	{ text += "<b>" + d["channel_info"] + "</b><br/> (<a href=\"" + info + "\" target=\"_blank\" style=\"color:white\">www</a>) ... "+description+"<br/>"; }
				else 				{ text += "<b>" + title + "</b><br/> " + description + ": <a href=\"" + info + "\" target=\"_blank\" style=\"color:white\">"+info+"</a><br/>"; }
				//text += "<i>" + status + "</i><br/>";
				}
		  	else {	text += "<i>"+lang("SELECT_MUSIC_ITEM") +"</i><br/>&nbsp;";
				}
			}
		}
	text += "</div>";
	text += "</div>";
	
	var color ="";
	if (mbox_device == "local")	{ color = "green" }
	else				{ color = "blue"; }

	if (playing != 0 || mbox_device == "local") {
	
		// Control to open and close ...
		var display_open  = "block";
        	var display_close = "none";

		// check if open ...
		var on_off = "";
		if (mboxControlPanel_open)  { on_off = " on1"; display_open="none"; display_close="block"; }
		else			     { on_off = " off1"; }

		text += "<div class='mbox_ctrl_open' id='ctrl_open' style='display:"+display_open+";'>";
		text += mboxHtmlButton("open", "mboxControlPanel_toggle();",   color, "right");
		text += "</div>";

		text += "<div class='mbox_ctrl_open' id='ctrl_close' style='display:"+display_close+";'>";
		text += mboxHtmlButton("close", "mboxControlPanel_toggle();",   "red", "right");
		text += "</div>";
		}
	else {
		//mboxControlPanel_close();
		}

	// volume control
	text += mboxControlVolumeControl(volume,mute);
	if (playing == 0 || playing == 1) {
		text += mboxPlayerRemote(song,uuid,playing);
		}
        setTextById("mbox_control", text);
        
        mboxPlayerProgressSet( status, song_length, song_left, song_left_s );

	if (audio == "" && mbox_device == "local") { mboxPlayerLocal(0,false); }
	}


//---------------------------------------------
// show / control volume
//---------------------------------------------

function mboxControlVolumeSet(volume) {
	if (volume >= 0 && volume <= 100) {
		if (mbox_device != "local") 	{ appFW.requestAPI('GET',['volume','set:'+volume], '', mboxControl); }
		else				{ volume = volume / 100;  mboxPlayer.volumeSet(volume);  mboxControl_load(); }
		}
	else if (volume == "mute") {
		if (mbox_device != "local") 	{ appFW.requestAPI('GET',['volume','mute'], '', mboxControl); }
		else				{ mboxPlayer.volumeMute(); mboxControl_load(); }
		}
	else {
		console.warn("mboxControlVolumeSet: Value out of range ("+volume+")");
		}
	}
	
//---------------------------------------------

function mboxControlVolumeShow(volume,mute) {
	return;

	// NOT USED ANY MORE ... ->  mboxControlVolumeControl

	var vol_col = "white";
	// check volume and show in navigation bar
	if (mbox_device == "local") {
		var vol_color = "lightgreen";
		if (mboxPlayer) { volume = mboxPlayer.volume; if (mboxPlayer.audio.muted) { mute = true; } else { mute = false; }}
		else		{ volume = 0; }
		}
        // check audio status and show in navigation bar
        if (Math.round(volume*20/1) < 1 || mute == true || mute == 1) {
                document.getElementById("audio1").style.display = "none";
                document.getElementById("audio2").style.display = "block";
                if (mbox_device != "local") 	{ vol_color = "gray"; }
		else				{ vol_color = "green"; }
                }
        else {
                document.getElementById("audio1").style.display = "block";
                document.getElementById("audio2").style.display = "none";
                }

	// check volume and show in navigation bar
	if (volume > 1) { volume = volume / 100; }
        var volume  = Math.round( volume * 20 / 1 );
        var vol_str = "<font color='" + vol_color + "'>";
        for (var i=0; i<volume; i++) { vol_str += "I"; }
        vol_str += "</font>";
        for (var i=0; i<20-volume; i++) { vol_str += "I"; }

	setTextById("audio3", vol_str);
	}

//---------------------------------------------

function mboxControlVolumeControl(volume, mute) {

	// buttons for bottom control
	var text      = "";
	var vol_color = "white";

	// check volume and show in navigation bar
	if (mbox_device == "local") {
		var vol_color = "lightgreen";
		if (mboxPlayer) { volume = mboxPlayer.volume; if (mboxPlayer.audio.muted) { mute = 1; } else { mute = 0; } }
		else		{ volume = 0; }
		}
		
	console.log("---------->> mboxControlVolume: mute="+mute + " / volume=" + volume);

        // check audio status and show in navigation bar
        if (Math.round(volume*20/1) < 1 || mute == 1 || mute == true) { // CHECK !!! 1 -> true ???
                document.getElementById("audio1").style.display = "none";
                document.getElementById("audio2").style.display = "block";
                if (mbox_device != "local") 	    { vol_color = "gray"; }
		else				    { vol_color = "green"; }
                }
        else {	// mute
                document.getElementById("audio1").style.display = "block";
                document.getElementById("audio2").style.display = "none";
                }

	// check volume and show in navigation bar
        var volume  = Math.round( volume * 20 / 1 );
        var vol_str = "<font color='" + vol_color + "'>";
        for (var i=0; i<volume; i++) { vol_str += "I"; }
        vol_str += "</font>";
        for (var i=0; i<20-volume; i++) { vol_str += "I"; }

	setTextById("audio3", vol_str);

	setOnclickById("audio1", "mboxSlider.show_hide();");
	setOnclickById("audio2", "mboxSlider.show_hide();");
	setOnclickById("audio3", "mboxSlider.show_hide();");
	setOnclickById("audio4", "mboxSlider.show_hide();");

	return text;
	}


// show album / playlist / ...
//--------------------------------------

function mboxControlShowUUID(uuid="") {

	// scroll to album / playlist / streaming entry
	//document.getElementById('scrollto_'+uuid.replace(/-/g,"")).scrollIntoView();

	// reload and open album / playlist entry
	if (uuid != "") {
		console.log(uuid);
		if (uuid.indexOf("p_") >= 0) 		{ mboxPlaylists_load("",uuid); }
		else if (uuid.indexOf("a_") >= 0) 	{ mboxAlbumAll_load("",uuid); }
		else if (uuid.indexOf("r_") >= 0) 	{ mboxStreams_load(uuid); }
		else if (uuid == "album")		{ mboxAlbumAll_load(); }
		else if (uuid == "playlist")		{ mboxPlaylists_load(); }
		else if (uuid == "radio")		{ mboxStreams_load(); }
		else {
			console.warn("mboxControlShowUUID ... uuid is not valid");
			}
		}
	else {
		console.warn("mboxControlShowUUID ... uuid missing");
		}
	}
	
function mboxControlReloadView() {
	if (mbox_mode == "album")		{ mboxAlbumAll_load("",mbox_last_uuid); }
	else if (mbox_mode == "radio")	{ mboxStreams_load(mbox_last_uuid); }
	else if (mbox_mode == "playlists")	{ mboxPlaylists_load("",mbox_last_uuid); }
	}


//--------------------------------------
// show which album, playlist or channel plays
//--------------------------------------

function mboxControlPlaying_show(uuid="",uuid_song="",playing=0) {

	activeElements = document.getElementsByClassName("player_active");

	for (var i=0;i<activeElements.length;i++) {
		element = activeElements[i];
		if (playing == 1) {
			if (element.id == "playing_"+uuid)			{ element.style.display = "block"; }
			else if (element.id == "playing2_"+uuid) 		{ element.style.display = "block"; }
			else if (element.id == "playing3_"+uuid) 		{ element.style.display = "block"; }
			else if (element.id == "playing_"+uuid_song)		{ element.style.display = "block"; }
			else if (element.id == "playing2_"+uuid_song) 	{ element.style.display = "block"; }
			else if (element.id == "playing3_"+uuid_song) 	{ element.style.display = "block"; }
			else 							{ element.style.display = "none"; }
			}
		else 								{ element.style.display = "none"; }
		}

	return;
	}

//--------------------------------------

function mboxControlPlaying_delete () {
	for (var i=0;i<mbox_cover_list.length;i++) {
		if (document.getElementById("playing_"  + mbox_cover_list[i])) {document.getElementById("playing_"  + mbox_cover_list[i]).style.display = "none"; }
		if (document.getElementById("playing2_" + mbox_cover_list[i])) {document.getElementById("playing2_" + mbox_cover_list[i]).style.display = "none"; }
		}
	}


//--------------------------------------
// open and close mbox control at the bottom of the page
//--------------------------------------

function mboxControlPanel_open() 	{ if (mboxControlPanel_open == false) { mboxControlPanel_toggle(); } }
function mboxControlPanel_close() 	{ if (mboxControlPanel_open == true)  { mboxControlPanel_toggle(); } }
function mboxControlPanel_toggle() {

	if (mboxControlPanel_progress) { return; }
	mboxControlPanel_progress = true;
		
	if (mboxControlPanel_open == false) {
		if (cssClassExists(id='mbox_control',check='show')) { cssClassChange(id='mbox_control', from='show'); }
		cssClassChange(id='mbox_control', from='off',to='on');
		cssClassChange(id='mbox_control_info', from='off1', to='on1');
		
		elementHidden('ctrl_close');
		elementVisible('ctrl_open');

		mboxControlPanel_open = true;
		}
	else {
		cssClassChange(id='mbox_control', from='on',to='off');
		cssClassChange(id='mbox_control_info', from='on1', to='off1');

		elementHidden('ctrl_open');
		elementVisible('ctrl_close');

		mboxControlPanel_open = false;
		}

	mboxControlPanel_progress = false;
	}

//--------------------------------------

var mboxControlPanel_delay = 0;

function mboxControlPanel_hide(complete=false) {

	if (mboxControlPanel_delay < 2) { mboxControlPanel_delay += 1; return; }
	mboxControlPanel_delay = 0;
		
	if (mboxControlPanel_progress) { return; } else { mboxControlPanel_progress = true; }
	if (complete || cssClassExists(id='mbox_control',check='on')) {		
		cssClassChange(id='mbox_control', from='on',to='off');
		setTimeout(function() {		
			cssClassChange(id='mbox_control', from='off',to='hide');
			mboxControlPanel_open     = false;
			mboxControlPanel_progress = false;
			}, 2000);
		return;
		}
	else if (cssClassExists(id='mbox_control',check='off'))	{ cssClassChange(id='mbox_control', from='off',to='hide'); }
	else if (cssClassExists(id='mbox_control',check='show'))	{ cssClassChange(id='mbox_control', from='show',to='hide'); }
	else 								{ cssClassChange(id='mbox_control', from='',to='hide'); }

	mboxControlPanel_open     = false;
	mboxControlPanel_progress = false;
	}

//--------------------------------------


function mboxControlPanel_show() {

	if (mboxControlPanel_progress) { return; } else { mboxControlPanel_progress = true; }
	
	if (cssClassExists(id='mbox_control',check='hide'))		{ cssClassChange(id='mbox_control', from='hide',to='show'); }
	else if (cssClassExists(id='mbox_control',check='off'))	{}
	else if (cssClassExists(id='mbox_control',check='on'))	{}
	else if (cssClassExists(id='mbox_control',check='show'))	{}
	else								{ cssClassChange(id='mbox_control', from='',to='show'); }
		
	mboxControlPanel_progress = false;
	}


//--------------------------------------
// check if loaded ...
//--------------------------------------

function mboxControlCheckLoading(data) {

	var text      = "";
	var load_data = data["STATUS"]["load_data"];
	var progress  = load_data["reload_progress"];
	var l_new     = load_data["reload_new"];
	var l_all     = load_data["reload_all"];
	var l_time    = load_data["reload_time_left"];
	var playing   = data["STATUS"]["playback"]["playing"];

	// write info to ...
	if (document.getElementById("progress_info")) {	
		if (l_new == false && l_all == false) { progress = 100; l_time = 0; }
		if (l_new)			{ text = "Load new Data: "; }
		else if (l_all)		{ text = "Reload all Data: "; }
		else if (progress == 100) 	{ text = "Done: "; }
		setTextById("progress_info",text + Math.round(progress*100)/100+"% ("+convert_second2time(Math.round(l_time))+" min)");
		}
	}


//--------------------------------------
// CONNECTION LED
//--------------------------------------

function mboxControlCheckStatus () {
	var d    = new Date();
	var last = d.getTime() - appFW.lastConnect;
	//console.log("Last Connect: "+last);

	if (last < 15000) 		{ mboxControlSetStatus("green"); }
	else if (last < 35000) 	{ mboxControlSetStatus("yellow"); mboxControlPlaying_delete(); }
	else if (last > 65000) 	{ mboxControlSetStatus("red");    mboxControlPlaying_delete(); }

	//if

        return last;
	}


//--------------------------------------

function mboxControlSetStatus (color) {
	var led = "<div id=\""+color+"\"></div>";
	document.getElementById("statusLED").innerHTML = led;
	}


//--------------------------------------
// select active mode
//--------------------------------------

function mboxControlToggleMode() {
	if (mbox_mode == "album")         	{ mbox_mode = "playlist"; }
	else if (mbox_mode == "playlist") 	{ mbox_mode = "radio"; }
	else                              	{ mbox_mode = "album"; }

	//appMenu.set_title( appTitle + "/" + mbox_mode );
	}



//--------------------------------------
// select active device
//--------------------------------------

function mboxControlToggleDevice () {
	// switch next device setting

	if (mbox_device == "both") 		{ mbox_device = "local"; }
	else if (mbox_device == "local") 	{ mbox_device = "remote"; }
	else if (mbox_device == "remote") 	{ mbox_device = "local"; } // both ... else only local/remote
	else					{ mbox_device = "both"; }
	
	mboxControlReloadView();
	}

//--------------------------------------
// show / hide filter
//--------------------------------------

function mboxControlToggleFilter (setting="toggle") {
	// switch next device setting

	if (setting == "toggle") {
		if (mbox_filter && !mbox_settings) 	{ mbox_filter = false; }
		else					{ mbox_filter = true; }
		}
	else {	mbox_filter = setting; }
		
	mboxControlToggleFilter_show ();
	}
	
//--------------------------------------

function mboxControlToggleFilter_show () {
	// switch next device setting

	if (mbox_filter && !mbox_settings)	{ document.getElementById("frame2").style.display="block"; }
	else					{ document.getElementById("frame2").style.display="none"; }
	}
	
//--------------------------------------
// EOF

