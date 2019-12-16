//--------------------------------------
// jc://music-box/, (c) Christoph Kloth
//--------------------------------------
// list and edit playlists
//--------------------------------------

function mboxPlaylistAllLoad(filter="",uuid="") {
                if (filter["UUID"])     { filter = filter["UUID"]; }
                else                    { filter = filter+">>"+uuid; }
                mboxApp.requestAPI("GET",["db","playlists--cards",filter],"", mboxPlaylistAll); //playlists--cards
		}

function mboxPlaylistAll(data) {
	var text                = "";
	var print               = listCoverStart();
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

		var cmd_open = "mboxEmptyAlbum();mboxPlaylistOneLoad('"+i+"','"+uuid+"')"; 
		var cmd_play = "mboxApp.requestAPI('GET',['play', '" + uuid + "'],'',mboxControl);";
		if (uuid == playlist_active) { playlist_active_no = i; }

		// check cover
		cover = mboxAlbumCover2("",playlists[uuid]);

		// print playlist cover
		text += mboxScrollTo( "start", uuid );
		text += mboxToolTip( "start" );

  		// write cover
		text += mboxCoverList( uuid, cover, "<b>" + list_title + "</b><br/>Playlist", cmd_open, cmd_play );
		if (cover != "") { print += listCoverEntry( uuid, cover ); }

		// write tooltip
		text += mboxToolTip( "end", i, list_title );
		text += mboxScrollTo( "end" );
		text += mboxAlbumDetail( i );

		i++;
		}

        var onclick  = "mboxAddListDialog("+i+");"
//	text += mboxCoverSeparator( "+", onclick );
	text += mboxCoverSeparator( "<img src=\"icon/list_add.png\" style=\"height:50px;width:50px;margin-top:10px;\">", onclick );
	text += mboxAlbumDetail( i );

        mbox_list_amount = i; /// IRGENDWO IST NOCH DER WURM DRIN ...
	print += listCoverEnd();

	setTextById("remote4", ""); // no filter defined yet
	setTextById("remote2", text);
	setTextById("ontop",   print);

        if (playlist_active != "") {
                mboxPlaylistOneLoad(playlist_active_no,playlist_active);
                if (document.getElementById('scrollto_'+playlist_active)) {
	                document.getElementById('scrollto_'+playlist_active).scrollIntoView();
	                }
                }
	}

function mboxAddListDialog(i) {
	var onclick2 = "document.getElementById('album_"+(i)+"').style.display='none';";
        var text  =  "<b>"+lang("ADD_PLAYLIST")+":</b><br/><br/><table>";
        text += "<tr><td>"+lang("TITLE")+":</td><td><input id=\"playlist_title\" style=\"width:150px\"></input></td></tr>";
        text += "<tr><td>"+lang("DESCRIPTION")+":</td><td><input id=\"playlist_description\" style=\"width:150px\"></input></td></tr>";
        text += "</table><br/>";
        text += button("add_playlist();",lang("ADD"),"add_playlist");
        text += button(onclick2,lang("CLOSE"),"close_playlist");
	setTextById("album_"+i,text);
	document.getElementById("album_"+i).style.display="block";
	}



// List tracks of playlist
//--------------------------------------

function mboxPlaylistOneLoad2(uuid) { 
	//console.error("Load2:"+uuid);
	mboxApp.requestAPI("GET",["data",uuid,"-"], "", mboxPlaylistOne); 
	}
	
function mboxPlaylistOneLoad(i,uuid) {
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
	var cover = mboxAlbumCover2("",albums);
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

       	text += mboxButton("info", "mboxPlaylistInfoLoad('"+uuid+"')", "red");

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
			mboxTrackRowPL(data,track_list[i],split,uuid);
			//console.log(i + " / " + track_list.length + " - " + split);
		} }, 2000); }
	else {
		setTextById("album_tracks","Playlist ist leer.");
		}
	}


// edit playlist // NOCH DER WURM DRIN?!
//--------------------------------------

function mboxPlaylistEditLoad(uuid) { mboxApp.requestAPI("GET",["data",uuid,"-"], "", mboxPlaylistEdit); 	} //console.log("1"+uuid);}
function mboxPlaylistEdit(data) {

	var sep    = "||";
	var uuid   = data["DATA"]["_selected_uuid"];
	var list   = data["DATA"]["_selected"];			//dataLists[uuid]["title"];
	var tracks = list["tracks"];
        var albums = data["DATA"]["albums"];			//dataAlbums;
	var text   = "";

	console.log("Edit dialog playlist: "+uuid);

	text += "<b>Playliste &quot;" + list["title"] + "&quot; bearbeiten</b><br/>&nbsp;<br/>";
	text += "<i>Neue Titel ...</i>";
	text += "<div id='selectAlbumContainer'>Loading ...</div>";
	text += "<div class='album_edit_list' id='selectTrack'>Loading ...</div>";
	text += "<i>Enthaltene Titel ...</i>";
    	text += "<div class='album_edit_list' id='selectTrackList'>Loading ...</div>";
	text += "<div id='playlistEditingInfo' style='color:red;'></div>";

	appMsg.confirm("<div style=\"text-align:left;\">" + text + "</div>", "", 450);

	mboxPlaylistEditTracksLoad(sep+uuid);						// Load data of playlist (to delete tracks)
	mboxPlaylistEditAlbumsLoad(uuid);
	}


// radio info as popup (incl. some settings ...)
//--------------------------------------

function mboxPlaylistInfoLoad(uuid) { mboxApp.requestAPI("GET",["data",uuid,"-"],"", mboxPlaylistInfo ); }
function mboxPlaylistInfo(data) {
        var text   = "";
        var album  = data["DATA"]["_selected"];
        var uuid   = data["DATA"]["_selected_uuid"];
        var url    = RESTurl + "mbox/read/playlists/"+uuid+"/";
        var size   = Math.round(album["albumsize"]/1024/1024*100)/100;
        var cardid = album["card_id"]; if (!cardid) { cardid = "Keine Karte verkn&uuml;pft."; }

	if ("tracks" in album) {} else {album["tracks"] = [];}

        var cover = "";
        if (album["cover_images"]) {
                cover += mboxAlbumInfoCover(1, album["cover_images"]["track"],  album["cover_images"]["active"], uuid);
                cover += mboxAlbumInfoCover(2, album["cover_images"]["dir"],    album["cover_images"]["active"], uuid);
                cover += mboxAlbumInfoCover(3, album["cover_images"]["upload"], album["cover_images"]["active"], uuid);
                cover += mboxAlbumInfoCover(4, album["cover_images"]["web"],    album["cover_images"]["active"], uuid);
                }
        else {  cover += "Altes Datenformat oder keine Bilder vorhanden, Titelinfos neu laden!";
                }

        var edit = "";
        edit += mboxButton("image_add", "mboxUploadImage('"+uuid+"','playlist','"+album["title"]+"');", "red");
        edit += mboxButton("list_edit", "mboxPlaylistEditLoad('"+album["uuid"]+"');",          "red");
        edit += mboxButton("edit",  	"mboxPlaylistEditEntryLoad('"+album["uuid"]+"');",          "red");
        edit += mboxButton("delete",  	"mboxDeletePlaylist('"+uuid+"','"+album["title"]+"');",         "red");


        text += "<b>Playlist Informationen</b><br/>";
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


function mboxPlaylistInfoClose() {
	setTimeout(function(){ mboxPlaylistLoad(); }, 2000);
        appMsg.hide();
        }

// edit single entry
//---------------------------

function mboxPlaylistEditEntryLoad(uuid) { mboxApp.requestAPI("GET",["data",uuid,"uuid,title,description"],"", mboxDataEdit ); }
// -> mbox-data.js


// reload after adding or deleting a track (BUG?)
//---------------------------

function mboxReloadPlaylist(uuid) {
	mboxPlaylistOneLoad2(uuid);
	mboxPlaylistEditLoad(uuid); // doent work ... reload of all data required / or load track list dynamically
	}

// delete playlist (dialog to confirm)
//---------------------------

function mboxDeletePlaylist(uuid,title) {
	text    = "Playlist <b>"+title+"</b> wirklich l&ouml;schen?";
	cmd     = "mboxApp.requestAPI(#DELETE#,[#data#,#"+uuid+"#],##, mboxPlaylistAllLoad);";
	appMsg.confirm(text,cmd,150,true);
	}


// write track list with edit & delete link
//---------------------------

function mboxPlaylistEditAlbumsLoad(uuid) {mboxApp.requestAPI("GET",["db","albums--album_info",uuid],"", mboxPlaylistEditAlbums ); }
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
	text += "<select id='selectArtist' class='album_edit_select' ";
	text += "onchange='mboxPlaylistEditAlbumsLoad(\""+uuid+sep+"\"+document.getElementById(\"selectArtist\").value);'>";

	for (var i=0;i<list_artists.length;i++) {
		var sel = "";
		if (selected && selected == list_artists[i] ) { sel = " selected"; }
		text += "<option value='"+list_artists[i]+"' "+sel+">" + list_artists[i] + "</option>";
		}

	text += "</select>&nbsp;<br/>";	

	// drop down "albums"
	text += "<select id='selectAlbum' class='album_edit_select' ";
	text += "onchange='mboxPlaylistEditTracksLoad(document.getElementById(\"selectAlbum\").value);' ";
	text += "onload='mboxPlaylistEditTracksLoad(document.getElementById(\"selectAlbum\").value);'>";

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
	mboxPlaylistEditTracksLoad(document.getElementById("selectAlbum").value);
	}

//---------------------------

function mboxPlaylistEditTracksLoad(uuid,source="") { 
	mboxApp.requestAPI("GET",["db","all",uuid], "", mboxPlaylistEditTracks); 
	//console.log("mboxPlaylistEditTracksLoad:"+source+"/"+uuid);
	}
	
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
		var onclick3   = "mboxApp.requestAPI('PUT',['playlist_items','add',   '" + ids[1] + "','" + uuid + "'],'', mboxInfoAdd);";
		var onclick4   = "mboxApp.requestAPI('PUT',['playlist_items','delete','" + ids[1] + "','" + uuid + "'],'', mboxInfoDelete);";

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
			var onclick1   =  "mboxApp.requestAPI('PUT',['playlist_items','add',   '"+ids[1]+"','"+tracklist[i]+"'],'', mboxInfoAdd);";
			var onclick2   =  "mboxApp.requestAPI('PUT',['playlist_items','delete','"+ids[1]+"','"+tracklist[i]+"'],'', mboxInfoDelete);";
			var found      = true;

			if (uuid == "" || tracks.length > 0 && tracks.includes(tracklist[i]))
					{ text_album += " <b class=\"album_delete_pl\" onclick=\""+onclick2+"\">(-)</b> &nbsp;"; }
			else		{ text_album += " <b class=\"album_edit_pl\"   onclick=\""+onclick1+"\">(+)</b> &nbsp;"; }

			if (tracklist[i] in trackinfo) 		{ text_album += trackinfo[tracklist[i]]["title"]; }
			else if (tracklist[i] in albuminfo) 	{ text_album += "<b>Ganzes Album:</b> " + albuminfo[tracklist[i]]["album"]; }
			else 					{ text_album += "<i>Not found: " + tracklist[i] + "</i>"; found = false; }
			text_album += "<br/>";
			}
		setTextById("selectTrack", text_album);
		}

	// PLAYLIST - delete track	
	if (tracks.length > 0) {
		for (var i=0;i<tracks.length;i++) {
			var onclick2   =  "mboxApp.requestAPI('PUT',['playlist_items','delete','"+ids[1]+"','"+tracks[i]+"'],'', mboxInfoDelete);";
			var found      = true;
			text_playlist += " <b class=\"album_delete_pl\" onclick=\""+onclick2+"\">(-)</b> &nbsp;";

			if (tracks[i] in trackinfo)	{ text_playlist += trackinfo[tracks[i]]["title"]; }
			else if (tracks[i] in albuminfo){ text_playlist += "<b>Ganzes Album:</b> " + albuminfo[tracks[i]]["album"]; }
			else 				{ text_playlist += "<i>Not found: " + tracks[i] + "</i>"; found = false; }
			
			text_playlist += "<br/>";
			}
		setTextById("selectTrackList", text_playlist);
		}
	}



// track title row
//--------------------------------------

function mboxTrackRowPL(data,uuid,split=false,uuid_pl="") {

        var text       = "";
        var cmd        = "";
	var no         = "";
	var albuminfo  = data["DATA"]["album_info"];
	var trackinfo  = data["DATA"]["tracks"];


	// if half of the list, split ... where is defined in function above
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
        	cmd += mboxButton("delete",  "mboxApp.requestAPI('PUT',['playlist_items','del_item', '"+uuid_pl+"','"+uuid+"'],'',mboxInfoDelete);", "red", "small right");
	       	cmd += "</div>";

        	text += "<div class=\"album_tracks_title\">";
                text += "<b style='color:red'>Track/album not found</b><br/>";
		text += uuid;
	       	text += "</div>" + cmd;
		}

	if (document.getElementById("album_tracks"+no)) {
		document.getElementById("album_tracks"+no).innerHTML += text;
		}
	else { console.log("error: "+"album_tracks"+no); }
        }


// Reload editing dialog and playlist view when made a change
//----------------------------------------------------------------


function mboxInfoDelete(data) {
        //appMsg.alert("<b>Eintrag gelöscht.</b><br/>" + data["StatusMsg"] + "<br/>" + data["INFO"]["_param"]);

	setTextById("playlistEditingInfo","Lösche "+data["LOAD"]["UUID"] + " ...");
	setTimeout(function(){
		mboxApp.requestAPI("GET",["db","all",document.getElementById("selectAlbum").value], "", mboxPlaylistEditTracks,"wait");
		mboxPlaylistAllLoad('', data["LOAD"]["UUID"]);
		setTextById("playlistEditingInfo","");
		}, 1000);
	}

function mboxInfoAdd(data) {
        //appMsg.alert("<b>Eintrag hinzugefügt.</b><br/>" + data["StatusMsg"] + "<br/>" + data["INFO"]["_param"]);

	setTextById("playlistEditingInfo","Füge Eintrag zu "+data["LOAD"]["UUID"] +" hinzu ...");
	setTimeout(function(){
		mboxApp.requestAPI("GET",["db","all",document.getElementById("selectAlbum").value], "", mboxPlaylistEditTracks,"wait");
		mboxPlaylistAllLoad('', data["LOAD"]["UUID"]);
		setTextById("playlistEditingInfo","");
		}, 1000);
	}


// add a playlist
//----------------------------------------------------------------

function add_playlist() {
        var title = document.getElementById("playlist_title").value;
        var descr = document.getElementById("playlist_description").value;
        document.getElementById("add_playlist").disabled = true;
        document.getElementById("add_playlist").innerHTML = "Please wait ...";
        mboxApp.requestAPI('POST',['data','playlists',title+'||'+descr], '', add_playlist_msg);
        }

function add_playlist_msg(data) {
        var text = "";
        if (data["REQUEST"]["status"] == "success")	{ text += "Playliste mit Titel angelegt."; }
        else                         		 	{ text += "Beim Anlegen der Playliste ist ein Fehler aufgetreten."; }
        appMsg.alert(text);
        mboxPlaylistAllLoad()
        }

