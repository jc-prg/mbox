//--------------------------------------
// jc://music-box/, (c) Christoph Kloth
//--------------------------------------
// list and edit playlists
//--------------------------------------
/* INDEX:
function mboxPlaylistAll_load(filter="",uuid="")
function mboxPlaylistAll(data)
function mboxPlaylistOne_load2(uuid)
function mboxPlaylistOne_load(i,uuid)
function mboxPlaylistOne(data)
function mboxPlaylistReload(uuid)
function mboxPlaylistEdit_load(uuid)
function mboxPlaylistEdit(data)
function mboxPlaylistEditAlbums_load(uuid)
function mboxPlaylistEditAlbums(data)
function mboxPlaylistEditTracks_load(uuid,source="")
function mboxPlaylistEditTracks(data)
function mboxPlaylistEditEntry_load(uuid)
function mboxPlaylistEditEntry(data)
function mboxPlaylistTrackRow(data,uuid,split=false,uuid_pl="")
function mboxPlaylistDelete(uuid,title)
function mboxPlaylistInfo_load(uuid)
function mboxPlaylistInfo(data)
function mboxPlaylistInfo_close()
function mboxPlaylistInfoDelete(data)
function mboxPlaylistInfoAdd(data)
function mboxPlaylistAdd()
function mboxPlaylistAdd_dialog(i)
function mboxPlaylistAdd_msg(data)
*/
//--------------------------------------

// show list of all playlists
//--------------------------------------

function mboxPlaylistAll_load(filter="",uuid="") {
                if (filter["UUID"])     { filter = filter["UUID"]; }
                else                    { filter = filter+">>"+uuid; }
                mboxApp.requestAPI("GET",["db","playlists--cards",filter],"", mboxPlaylistAll); //playlists--cards
		}

function mboxPlaylistAll(data) {
	var text                = "";
	var print               = mboxCoverListStart();
	var default_cover       = mbox_icons["playlist"]; // "img/cd2.png";
        var playlists           = data["DATA"]["playlists"];
        var playlist_active     = "";
        var playlist_active_no  = 0;
        var last_char           = "";

        // reset cover list (to show cover of all albums, playlists, ...)
        mbox_cover_list   = [];

        // create filter
        if ("db_filter" in data["REQUEST"]) {
                var filter_uuid    = data["REQUEST"]["db_filter"].split(">>");
                var filters        = filter_uuid[0];
                playlist_active    = filter_uuid[1];
                }

	// sort list by name
	var sortList = {};
	var sorted_lists = [];
	for (var key in playlists) {
		sortList[playlists[key]["title"]] = key;
		sorted_lists.push(playlists[key]["title"]);
		}
	sorted_lists.sort();

	// list
	var i = 1;
	for (var key in sorted_lists) {

		var list_title = sorted_lists[key];
		var uuid       = sortList[list_title];

		//console.log(list_id + "/" + list_title);

		var cmd_open = "mboxEmptyAlbum();mboxPlaylistOne_load('"+i+"','"+uuid+"')"; 
		var cmd_play = "mboxApp.requestAPI('GET',['play', '" + uuid + "'],'',mboxControl);";
		if (uuid == playlist_active) { playlist_active_no = i; }

		// check cover
		cover = mboxCoverAlbum_new("",playlists[uuid]);

		// print playlist cover
		text += mboxScrollTo( "start", uuid );
		text += mboxToolTip( "start" );

  		// write cover
		text += mboxCoverList( uuid, cover, "<b>" + list_title + "</b><br/>"+lang("PLAYLIST"), cmd_open, cmd_play );
		if (cover != "") { print += mboxCoverListEntry( uuid, cover ); }

		// write tooltip
		text += mboxToolTip( "end", i, list_title );
		text += mboxScrollTo( "end" );
		text += mboxAlbumDetail( i );

		i++;
		}

        var onclick  = "mboxPlaylistAdd_dialog("+i+");"
//	text += mboxCoverSeparator( "+", onclick );
	text += mboxCoverSeparator( "<img src=\"icon/list_add.png\" style=\"height:50px;width:50px;margin-top:10px;\">", onclick );
	text += mboxAlbumDetail( i );

        mbox_list_amount = i; /// IRGENDWO IST NOCH DER WURM DRIN ...
	print += mboxCoverListEnd();

	setTextById("remote4", ""); // no filter defined yet
	setTextById("remote2", text);
	setTextById("ontop",   print);

        if (playlist_active != "") {
                mboxPlaylistOne_load(playlist_active_no,playlist_active);
                if (document.getElementById('scrollto_'+playlist_active)) {
	                document.getElementById('scrollto_'+playlist_active).scrollIntoView();
	                }
                }
	}


// List tracks of playlist
//--------------------------------------

function mboxPlaylistOne_load2(uuid) { 
	//console.error("Load2:"+uuid);
	mboxApp.requestAPI("GET",["data",uuid,"-"], "", mboxPlaylistOne); 
	}
	
function mboxPlaylistOne_load(i,uuid) {
	//console.error("Load:"+uuid+"/"+i);
	var count = 3;
        var width = document.body.clientWidth;
        if (width > 1250) { mbox_list_count = 6; }

        mbox_list_pos = ((Math.floor((i-1)/mbox_list_count)+1) * mbox_list_count );
        if (mbox_list_pos > mbox_list_amount) { mbox_list_pos = mbox_list_amount; }

        mboxApp.requestAPI("GET",["data",uuid,"-"],"",mboxPlaylistOne );
        }

function mboxPlaylistOne(data) {

	var text       = "";
        var uuid       = data["DATA"]["_selected_uuid"];
	var albums     = data["DATA"]["_selected"];
	var track_list = [];
	if (data["DATA"]["_selected"] && data["DATA"]["_selected"]["tracks"]) {
		track_list = data["DATA"]["_selected"]["tracks"];
		}

        // check cover
	var default_cover = mbox_icons["playlist"];
	var cover = mboxCoverAlbum_new("",albums);
	if (!cover) { cover = default_cover; }

        // Log
        if (albums) 	{ console.log("playlist-id: "+uuid+"/"+albums["title"]); }
	else 		{ console.error("mboxPlaylistOne: "+uuid+"/"+data["DATA"]["_selected_uuid"]); console.error(data); }

	// Write playlist cover
	text += "<div class=\"album_cover\" style=\"background:url("+cover+");background-size:contain;background-position:center;background-repeat:no-repeat;\" onclick='" + onclick + "'>";
	text += "</div>";

	// write playlist infos
	text += "<div class=\"album_infos new\">";
	text +=   "<b>" + albums["title"] + "</b><br/><i>" + albums["description"] + "</i><br/>";
        text += "</div>";
        text += mboxButton("delete",  "mboxEmptyBelow();", "opac", "small small2");

        // player control (in box)
	text += "<div class=\"album_control new\">";

	// control for box
	if (mbox_device != "local") {
		text += "<div class=\"player_active big\" id=\"playing_"+albums["uuid"]+"\" style=\"display:none;\"><img src=\""+mbox_icons["playing"]+"\" style=\"height:20px;width:20px;margin:2px;\"></div>";
	        text += mboxButton("play",  "mboxApp.requestAPI('GET',['play', '" + uuid + "'],'', mboxControl);", "blue");
        	text += mboxButton("pause", "mboxApp.requestAPI('GET',['pause'],'',                mboxControl);", "blue");
	        text += mboxButton("stop",  "mboxApp.requestAPI('GET',['stop'],'',                 mboxControl);", "blue");
	        text += mboxButton("empty");
		}

       	text += mboxButton("info", "mboxPlaylistInfo_load('"+uuid+"')", "red");

	// show and edit rfid card
	if ("card_id" in albums && albums["card_id"] != "") 	{
		text += "<div id=\"show_card\">";
		text += mboxButton("card",  "", "green");
		text += "</div>";
		text += CardID(albums["uuid"]);
		}
	else {
		text += "<div id=\"show_card\">";
		text += "</div>";
		text += CardID(albums["uuid"]);
		}
        text += "</div>";
	text += "<div style=\"width:100%;float:left;\"><hr/></div>";

	// container for tracks & player
	text += "<div class=\"album_tracks\" id=\"album_tracks\">Loading ...</div>"; // first column
	text += "<div class=\"album_tracks\" id=\"album_tracks2\">&nbsp;</div>"; // second column
	text += "<div class=\"album_tracks\">&nbsp;</div>";

	//setTextById("remote1",text);
        mboxWriteBelow(text);

	if (track_list.length > 0) { 
	    setTimeout(function(){
		setTextById("album_tracks","");
		setTextById("album_tracks2","");
		for (var i=0; i < track_list.length;i++) {
			var split = false;
			if (i >= Math.round(track_list.length/2)) { split = true; } // split if half of the list
			mboxPlaylistTrackRow(data,track_list[i],split,uuid);
			//console.log(i + " / " + track_list.length + " - " + split);
		} }, 2000); }
	else {
		setTextById("album_tracks",lang("PLAYLIST_EMPTY"));
		}
	}


// reload after adding or deleting a track (BUG?)
//---------------------------

function mboxPlaylistReload(uuid) {
	mboxPlaylistOne_load2(uuid);
	mboxPlaylistEdit_load(uuid); // doesnt work? ... reload of all data required / or load track list dynamically
	}

// edit playlist // NOCH DER WURM DRIN?!
//--------------------------------------

function mboxPlaylistEdit_load(uuid) { mboxApp.requestAPI("GET",["data",uuid,"-"], "", mboxPlaylistEdit); 	} //console.log("1"+uuid);}
function mboxPlaylistEdit(data) {

	var sep    = "||";
	var uuid   = data["DATA"]["_selected_uuid"];
	var list   = data["DATA"]["_selected"];			//dataLists[uuid]["title"];
	var tracks = list["tracks"];
        var albums = data["DATA"]["albums"];			//dataAlbums;
	var text   = "";

	console.log("Edit dialog playlist: "+uuid);

	text += "<b>"+lang("PLAYLIST_EDIT")+": &quot;" + list["title"] + "&quot;</b><br/>&nbsp;<br/>";
	
	text += "<i>Neue Titel ...</i>";
	text += "<div id='selectAlbumContainer'>Loading ...</div>";
	text += "<div id='selectTrack' class='album_edit_list' >Loading ...</div>";
	
	text += "<i>"+lang("TRACKS_INSIDE")+" ...</i>";
    	text += "<div id='selectTrackList'     class='album_edit_list'>Loading ...</div>";
	text += "<div id='playlistEditingInfo' style='color:red;'></div>";

	appMsg.confirm("<div style=\"text-align:left;\">" + text + "</div>", "", 450);

	mboxPlaylistEditAlbums_load(uuid);
	setTimeout(function(){
		mboxPlaylistEditTracks_load(sep+uuid);						// Load data of playlist (to delete tracks)
		}, 1000);
	}


// load albums and write drop down menus
//---------------------------

function mboxPlaylistEditAlbums_load(uuid) { mboxApp.requestAPI("GET",["db","albums--album_info",uuid],"", mboxPlaylistEditAlbums ); }
function mboxPlaylistEditAlbums(data) {

	var uuid	 = "";
	var text         = "";
	var sep          = "||";
	var list_artists = [];
	var selected;

	var albums       = data["DATA"]["albums"];
	var album_info   = data["DATA"]["album_info"];

	if ( data["REQUEST"]["db_filter"].indexOf(sep) > -1) {	
		var temp     = data["REQUEST"]["db_filter"].split(sep);
		uuid         = temp[0];
		selected     = temp[1];
		}
	else {	uuid         = data["REQUEST"]["db_filter"];
		}

	// drop down "artists"
	for (var key in album_info) {
		if (list_artists.indexOf(album_info[key]["artist"])<0) { list_artists.push(album_info[key]["artist"]); }
		}
	list_artists.sort();
	text += "<select id='selectArtist' class='album_edit_select' " + 
	        "onchange='mboxPlaylistEditAlbums_load(\""+uuid+sep+"\"+document.getElementById(\"selectArtist\").value);'>";

	for (var i=0;i<list_artists.length;i++) {
		var sel = "";
		if (selected && selected == list_artists[i] ) { sel = " selected"; }
		text += "<option value='"+list_artists[i]+"' "+sel+">" + list_artists[i] + "</option>";
		}

	text += "</select>&nbsp;<br/>";	

	// drop down "albums"
	text += "<select id='selectAlbum' class='album_edit_select' ";
	text += "onchange='mboxPlaylistEditTracks_load(document.getElementById(\"selectAlbum\").value);' ";
	text += "onload='mboxPlaylistEditTracks_load(document.getElementById(\"selectAlbum\").value);'>";

	for (var key in album_info) {
		if (selected) {
			if (selected == album_info[key]["artist"]) {
				text += "<option value='"+key+sep+uuid+"'>" + album_info[key]["album"] + "</option>";
				}
			}
		else if (album_info[key]["artist"] == list_artists[0]) {
			text += "<option value='"+key+sep+uuid+"'>" + album_info[key]["album"] + "</option>";
			}
		}

	text += "</select>&nbsp;<br/>";	

	setTextById("selectAlbumContainer", text);
	mboxPlaylistEditTracks_load(document.getElementById("selectAlbum").value);
	}

// write track lists with edit & delete link (1) tracks of select album (2) tracks of playlist
//---------------------------

function mboxPlaylistEditTracks_load(uuid,source="") { mboxApp.requestAPI("GET",["db","all",uuid], "", mboxPlaylistEditTracks); }
function mboxPlaylistEditTracks(data) {

	var sep			= "||";
	var ids			= data["REQUEST"]["db_filter"].split(sep);	// list of IDs, uuid of playlist first
	var uuid		= ids[0];                        			// uuid of album (selected ...)
	var text_album		= "";
	var text_playlist	= "";

	console.log("mboxPlaylistEditTracks: "+ids[0]+"/"+ids[1]);
        console.log(data["REQUEST"]);

	var tracklist 		= [];
        var tracks		= data["DATA"]["playlists"][ids[1]]["tracks"];
	var trackinfo 		= data["DATA"]["tracks"];                      	// var trackinfo = dataTracks;
        var albuminfo 		= data["DATA"]["album_info"];
        

        // ALBUM LIST - add or delete album
	if (uuid != "") {
                tracklist = data["DATA"]["album_info"][uuid]["tracks"];

		// 1st option: add complete album
		var onclick3   = "mboxApp.requestAPI('PUT',['playlist_items','add',   '" + ids[1] + "','" + uuid + "'],'', mboxPlaylistAddTrackInfo);";
		var onclick4   = "mboxApp.requestAPI('PUT',['playlist_items','delete','" + ids[1] + "','" + uuid + "'],'', mboxPlaylistDeleteTrackInfo);";

		if (tracks.length > 0) {
			if (tracks.includes(uuid))	{ text_album += "<b class=\"album_delete_pl\" onclick=\""+onclick4+"\">(-)</b> &nbsp;"; }
			else				{ text_album += "<b class=\"album_edit_pl\" onclick=\""+onclick3+"\">(+)</b> &nbsp;"; }
			}
		else	{ text_album += "<b class=\"album_edit_pl\" onclick=\""+onclick3+"\">(+)</b> &nbsp;"; }
			
		text_album += "<i><b>Ganzes Album:</b> "+data["DATA"]["album_info"][uuid]["album"]+"</i><br/>";
		}

	// ALBUM LIST - add or delete track
	if (tracklist.length > 0) {
		for (var i=0;i<tracklist.length;i++) {
			var onclick1   =  "mboxApp.requestAPI('PUT',['playlist_items','add',   '"+ids[1]+"','"+tracklist[i]+"'],'', mboxPlaylistAddTrackInfo);";
			var onclick2   =  "mboxApp.requestAPI('PUT',['playlist_items','delete','"+ids[1]+"','"+tracklist[i]+"'],'', mboxPlaylistDeleteTrackInfo);";
			var found      = true;

			if (uuid == "" || tracks.length > 0 && tracks.includes(tracklist[i]))
					{ text_album += " <b class=\"album_delete_pl\" onclick=\""+onclick2+"\">(-)</b> &nbsp;"; }
			else		{ text_album += " <b class=\"album_edit_pl\"   onclick=\""+onclick1+"\">(+)</b> &nbsp;"; }

			if (tracklist[i] in trackinfo) 		{ text_album += trackinfo[tracklist[i]]["title"]; }
			else if (tracklist[i] in albuminfo) 	{ text_album += "<b>"+lang("ALBUM_COMPLETE")+":</b> " + albuminfo[tracklist[i]]["album"]; }
			else 					{ text_album += "<i>"+lang("NOT_FOUND")+": " + tracklist[i] + "</i>"; found = false; }
			text_album += "<br/>";
			}
		setTextById("selectTrack", text_album);
		}

	// PLAYLIST - delete track	
	if (tracks.length > 0) {
		for (var i=0;i<tracks.length;i++) {
			var onclick2   =  "mboxApp.requestAPI('PUT',['playlist_items','delete','"+ids[1]+"','"+tracks[i]+"'],'', mboxPlaylistDeleteTrackInfo);";
			var found      = true;
			text_playlist += " <b class=\"album_delete_pl\" onclick=\""+onclick2+"\">(-)</b> &nbsp;";

			if (tracks[i] in trackinfo)	{ text_playlist += trackinfo[tracks[i]]["title"]; }
			else if (tracks[i] in albuminfo){ text_playlist += "<b>"+lang("ALBUM_COMPLETE")+":</b> " + albuminfo[tracks[i]]["album"]; }
			else 				{ text_playlist += "<i>"+lang("NOT_FOUND")+": " + tracks[i] + "</i>"; found = false; }
			
			text_playlist += "<br/>";
			}
		setTextById("selectTrackList", text_playlist);
		}
	}


// edit single entry
//---------------------------

function mboxPlaylistEditEntry_load(uuid) { mboxApp.requestAPI("GET",["data",uuid,"uuid,title,description"],"", mboxPlaylistEditEntry ); }
function mboxPlaylistEditEntry(data) { mboxDataEdit( data ); }  // -> mbox-data.js


// track title row
//--------------------------------------

function mboxPlaylistTrackRow(data,uuid,split=false,uuid_pl="") {

        var text       = "";
        var cmd        = "";
	var no         = "";
	var albuminfo  = data["DATA"]["album_info"];
	var trackinfo  = data["DATA"]["tracks"];


	// if half of the list, split ... where is defined in funct. above
	if (split==true) { no = "2";}

	// if track exists ...
        if (uuid in trackinfo) {

		var track = trackinfo[uuid];

	        var length = "";
        	if (track["length"]) {
                	length = " <font color='gray'>(" + convert_second2time(Math.round(track["length"])) + ")</font>";
                	}

		// Controls to play Track ...
	       	cmd += "<div class=\"album_tracks_control\">";
		if (mbox_device == "local")	{ cmd += mboxButton("play",  "writeAudioPlayer('" + uuid + "','audioPlayer');", "green",   "small right"); }
		else 				{ cmd += mboxButton("play",  "mboxApp.requestAPI('GET',['play', '"+uuid+"'],'',mboxControl);", "blue", "small right"); }
                cmd += "<div class=\"player_active right\" id=\"playing3_"+uuid+"\" style=\"display:none;\"><img src=\""+mbox_icons["playing"]+"\" style=\"width:10px;height:10px;margin:2px;\"></div>";
	       	cmd += "</div>";

		// Show Title if exist ...
        	text += "<div class=\"album_tracks_title\">";
                text += "<b>" +track["title"] + "</b><br/>";
                text += track["artist"] + "/";
                text += track["album"] + "<br/>";
		text += length;
	        text += "</div>";
        	text += cmd;
                }

	// if album exists
	else if (uuid in albuminfo) {

	        var length = "";
        	if (albuminfo[uuid]["albumlength"]) {
                	length = " <font color='gray'>(" + convert_second2time(Math.round(albuminfo[uuid]["albumlength"])) + ")</font>";
                	}

		mbox_playlist_queue["type"]     = "album";
		mbox_playlist_queue["album"]    = albuminfo[uuid];
		mbox_playlist_queue["scrollto"] = "scrollto_" + uuid.replace(/-/g,"");
		mbox_playlist_queue["tracks"]   = albuminfo[uuid]["tracks"];

		// Controls to play Track ...
	       	cmd += "<div class=\"album_tracks_control\">";
		if (mbox_device == "local")	{ cmd += mboxButton("play",  "localPlayer();", "gray", "small right"); }	        //cmd += mboxButton("play",  "writeAudioPlayer('" + uuid + "','audioPlayer');", "green",   "small right");
        	else				{ cmd += mboxButton("play",  "mboxApp.requestAPI('GET',['play', '"+uuid+"'],'',mboxControl);", "blue", "small right"); }
	       	cmd += "</div>";

		// Show Title if exist ...
        	text += "<div class=\"album_tracks_title\">";
                text += "<b><i>Album: </i>" +albuminfo[uuid]["album"] + "</b><br/>";
                text += albuminfo[uuid]["artist"]+" ";
		text += "<i>("+albuminfo[uuid]["tracks"].length+" Tracks)</i><br/>";
		text += length;
	        text += "</div>";
        	text += cmd;
		}

	// if not exists
	else {
	       	cmd += "<div class=\"album_tracks_control\">";
	       	
//		var onclick2   =  "mboxApp.requestAPI('PUT',['playlist_items','delete','"+ids[1]+"','"+tracklist[i]+"'],'', mboxPlaylistInfoDelete);";

        	cmd += mboxButton("delete",  "mboxApp.requestAPI('PUT',['playlist_items','delete', '"+uuid_pl+"','"+uuid+"'],'',mboxPlaylistDeleteTrack);", "red", "small right");
	       	cmd += "</div>";

        	text += "<div class=\"album_tracks_title\">";
                text += "<b style='color:red'>"+lang("TRACK")+"/"+lang("ALBUM")+" "+lang("NOT_FOUND")+"</b><br/>";
		text += uuid;
	       	text += "</div>" + cmd;
		}

	if (document.getElementById("album_tracks"+no)) {
		document.getElementById("album_tracks"+no).innerHTML += text;
		}
	else { console.log("error: "+"album_tracks"+no); }
        }


// delete playlist (from dialog to confirm to message)
//---------------------------

function mboxPlaylistDelete(uuid,title) {
	text    = lang("PLAYLIST_DELETE_ASK") + ": <b>"+title+"</b>?";
	cmd     = "mboxPlaylistDelete_exec('"+uuid+"');";
	appMsg.confirm(text,cmd,150,true);
	console.error("1");
	}
	
function mboxPlaylistDelete_exec(uuid) {
	console.error("2");
	mboxApp.requestAPI('DELETE',['data',uuid],'',mboxPlaylistDelete_msg);
	}

function mboxPlaylistDelete_msg(data) {
	console.error("3");
	mboxReturnMsg(data,lang("PLAYLIST_DELETED"),lang("PLAYLIST_DELETE_ERROR"));
        mboxPlaylistAll_load();
        }


// radio info as popup (incl. some settings ...)
//--------------------------------------

function mboxPlaylistInfo_load(uuid) { mboxApp.requestAPI("GET",["data",uuid,"-"],"", mboxPlaylistInfo ); }
function mboxPlaylistInfo(data) {
        var text   = "";
        
        if (!data["DATA"]["_selected"]) { console.log("mboxPlaylistInfo: no [DATA][_selected]"); return; }
        
        var album  = data["DATA"]["_selected"];
        var uuid   = data["DATA"]["_selected_uuid"];
        var url    = RESTurl + "api/data/"+uuid+"/--";
        var size   = Math.round(album["albumsize"]/1024/1024*100)/100;
        var cardid = album["card_id"]; if (!cardid) { cardid = lang("CARD_NOT_CONNECTED"); }

	if ("tracks" in album) {} else {album["tracks"] = [];}

        var cover = "";
        if (album["cover_images"]) {
                cover += mboxCoverAlbumInfo(1, album["cover_images"]["track"],  album["cover_images"]["active"], uuid);
                cover += mboxCoverAlbumInfo(2, album["cover_images"]["dir"],    album["cover_images"]["active"], uuid);
                cover += mboxCoverAlbumInfo(3, album["cover_images"]["upload"], album["cover_images"]["active"], uuid);
                cover += mboxCoverAlbumInfo(4, album["cover_images"]["web"],    album["cover_images"]["active"], uuid);
                }
        else {  cover += lang("DATA_OLD_FORMAT");
                }

        var edit = "";
        edit += mboxButton("image_add", "mboxUploadImage('"+uuid+"','playlist','"+album["title"]+"');", "red");
        edit += mboxButton("list_edit", "mboxPlaylistEdit_load('"+album["uuid"]+"');",          "red");
        edit += mboxButton("edit",  	"mboxPlaylistEditEntry_load('"+album["uuid"]+"');",          "red");
        edit += mboxButton("delete",  	"mboxPlaylistDelete('"+uuid+"','"+album["title"]+"');",         "red");


        text += "<b>"+lang("PLAYLIST_INFORMATION")+"</b><br/>";
        text += mboxTableNew("start");
        text += "<tr><td colspan='2'><hr></td></tr>";
        text += mboxTableNew(["<i>"+lang("TITLE")+":",        album["title"] ] );
        text += mboxTableNew(["<i>"+lang("DESCRIPTION")+":",  album["description"] ] );
        text += mboxTableNew(["<i>Tracks:",	       			album["tracks"].length ] );
        text += mboxTableNew(["<i>UUID:",               "<a href='" + url + "/' target='_blank'>" + uuid + "</a>" ] );
        text += mboxTableNew(["<i>Card ID:",            "<a style='cursor:pointer;' onclick='mboxListCardsLoad();'>"    + cardid + "</a>" ] );
        text += mboxTableNew(["<i>"+lang("COVER_AVAILABLE")+":",      cover ] );
        text += "<tr><td colspan='2'><hr></td></tr>";
        text += mboxTableNew(["<i>"+lang("EDIT")+":",         edit ] );
        text += "<tr><td colspan='2'><hr></td></tr>";
        text += mboxTableNew("end");

        appMsg.confirm(text,"",450);
        }

//----------------------------------------------------------------

function mboxPlaylistInfo_close() {
	setTimeout(function(){ mboxPlaylistLoad(); }, 2000);
        appMsg.hide();
        }


// Show message and reload view when made a change
//----------------------------------------------------------------

function mboxPlaylistDeleteTrackInfo(data) {
	setTextById("playlistEditingInfo","Lösche "+data["LOAD"]["UUID"] + " ...");
	setTimeout(function(){
		mboxApp.requestAPI("GET",["db","all",document.getElementById("selectAlbum").value], "", mboxPlaylistEditTracks,"wait");
		mboxPlaylistAll_load('', data["LOAD"]["UUID"]);
		setTextById("playlistEditingInfo","");
		}, 1000);
	}

function mboxPlaylistDeleteTrack(data) {
	mboxReturnMsg(data,lang("TRACK_DELETED"),lang("TRACK_DELETE_ERROR")); 
	mboxPlaylistAll_load('', data["LOAD"]["UUID"]);
	}

function mboxPlaylistAddTrackInfo(data) {
	setTextById("playlistEditingInfo","Füge Eintrag zu "+data["LOAD"]["UUID"] +" hinzu ...");
	setTimeout(function(){
		mboxApp.requestAPI("GET",["db","all",document.getElementById("selectAlbum").value], "", mboxPlaylistEditTracks,"wait");
		mboxPlaylistAll_load('', data["LOAD"]["UUID"]);
		setTextById("playlistEditingInfo","");
		}, 1000);
	}


// add a playlist
//----------------------------------------------------------------

function mboxPlaylistAdd() {
        var title = document.getElementById("playlist_title").value;
        var descr = document.getElementById("playlist_description").value;
        document.getElementById("mboxPlaylistAdd").disabled = true;
        document.getElementById("mboxPlaylistAdd").innerHTML = "Please wait ...";
        mboxApp.requestAPI('POST',['data','playlists',title+'||'+descr], '', mboxPlaylistAdd_msg);
        }

//--------------------------------------

function mboxPlaylistAdd_dialog(i) {
	var onclick2 = "document.getElementById('album_"+(i)+"').style.display='none';";
        var text  =  "<b>"+lang("ADD_PLAYLIST")+":</b><br/><br/><table>";
        text += "<tr><td>"+lang("TITLE")+":</td><td><input id=\"playlist_title\" style=\"width:150px\"></input></td></tr>";
        text += "<tr><td>"+lang("DESCRIPTION")+":</td><td><input id=\"playlist_description\" style=\"width:150px\"></input></td></tr>";
        text += "</table><br/>";
        text += button("mboxPlaylistAdd();",lang("ADD"),"mboxPlaylistAdd");
        text += button(onclick2,lang("CLOSE"),"close_playlist");
	setTextById("album_"+i,text);
	document.getElementById("album_"+i).style.display="block";
	}

//--------------------------------------

function mboxPlaylistAdd_msg(data) {
	mboxReturnMsg(data,lang("PLAYLIST_CREATED"),lang("PLAYLIST_CREATED_ERROR"));
        mboxPlaylistAll_load();
        }

//---------------------------
// EOF

