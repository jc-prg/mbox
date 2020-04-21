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
//function mboxPlaylistEditAlbums_load(uuid)
function mboxPlaylistEditAlbums_load(uuid)
function mboxPlaylistEditAlbums(data)
function mboxPlaylistEditTracks_load(uuid_filter,source="")
function mboxPlaylistEditTracks(data)
function mboxPlaylistEditEntry_load(uuid)
function mboxPlaylistEditEntry(data)
function mboxPlaylistTrackRow(data,uuid,split=false,uuid_pl="",color=0)
function mboxPlaylistTrackLine(split=false,color)
function mboxPlaylistDelete(uuid,title)
function mboxPlaylistDelete_exec(uuid,title)
function mboxPlaylistDelete_msg(data,title)
function mboxPlaylistInfo_load(uuid)
function mboxPlaylistInfo(data)
function mboxPlaylistInfo_close()
function mboxPlaylistDeleteTrackInfo(data)
function mboxPlaylistDeleteTrack(data)
function mboxPlaylistAddTrackInfo(data)
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
        mbox_mode               = 'Playlist'; 

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

		var cmd_open = "mboxAlbumEmptyAll();mboxPlaylistOne_load('"+i+"','"+uuid+"')"; 
		var cmd_play = "mboxApp.requestAPI('GET',['play', '" + uuid + "'],'',mboxControl);";
		if (uuid == playlist_active) { playlist_active_no = i; }

		// check cover
		cover = mboxCoverAlbum_new("",playlists[uuid]);

		// print playlist cover
		text += mboxHtmlScrollTo( "start", uuid );
		text += mboxHtmlToolTip( "start" );

  		// write cover
		text += mboxCoverList( uuid, cover, "<b>" + list_title + "</b><br/>"+lang("PLAYLIST"), cmd_open, cmd_play );
		if (cover != "") { print += mboxCoverListEntry( uuid, cover ); }

		// write tooltip
		text += mboxHtmlToolTip( "end", i, list_title );
		text += mboxHtmlScrollTo( "end" );
		text += mboxHtmlEntryDetail( i );

		i++;
		}

        var onclick  = "mboxPlaylistAdd_dialog("+i+");"
//	text += mboxCoverSeparator( "+", onclick );
	text += mboxCoverSeparator( "<img src=\"icon/list_add.png\" style=\"height:50px;width:50px;margin-top:10px;\">", onclick );
	text += mboxHtmlEntryDetail( i );

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

function mboxPlaylistOne_load2(uuid) { mboxApp.requestAPI("GET",["data",uuid,"-"], "", mboxPlaylistOne); }
function mboxPlaylistOne_load(i,uuid) {
	//console.error("Load:"+uuid+"/"+i);
	var count = 3;
        var width = document.body.clientWidth;
        if (width > 1250) { mbox_list_count = 6; }

        mbox_list_pos = ((Math.floor((i-1)/mbox_list_count)+1) * mbox_list_count );
        if (mbox_list_pos > mbox_list_amount) { mbox_list_pos = mbox_list_amount; }

        mboxApp.requestAPI("GET",["data",uuid,"-"],"",mboxPlaylistOne );
        }

//--------------------------------------

function mboxPlaylistOne(data) {

	var text		= "";
        var uuid		= data["DATA"]["_selected_uuid"];
	var albums		= data["DATA"]["_selected"];
	var track_list		= [];
	var track_list_complete = [];
	var track_list_album    = {};
	
	if (data["DATA"]["_selected"] && data["DATA"]["_selected"]["tracks"]) {
		track_list = data["DATA"]["_selected"]["tracks"];
		}

	// create playlist including all tracks from included albums
	for (var i=0;i<track_list.length;i++) {
		if (track_list[i].includes("t_"))	{ track_list_complete.push( track_list[i] ); }
		else if (track_list[i].includes("a_"))	{ 
			if (data["DATA"]["album_info"][track_list[i]]) {
			
				album_tracks = data["DATA"]["album_info"][track_list[i]]["tracks"];
// SORT ???
				for (var j=0;j<album_tracks.length;j++) {
					track_list_complete.push( album_tracks[j] );
					}
				track_list_album[track_list[i]] = album_tracks;
				}
			else {
				track_list_complete.push( track_list[i] );
				}
			}
		}

	// fill local playlist queue
	if (mbox_device == "local") {
	
		// handover data to local player
		mbox_playlist_queue["type"]		= "list";
		mbox_playlist_queue["album"]		= albums;
		mbox_playlist_queue["album"]["tracks"]	= track_list_complete;
		mbox_playlist_queue["scrollto"]		= "scrollto_" + uuid.replace(/-/g,"");
		mbox_playlist_queue["tracks"]		= data["DATA"]["tracks"];

		console.debug(mbox_playlist_queue);
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
        text += mboxHtmlButton("delete",  "mboxAlbumEmptyBelow();", "opac", "small small2");

        // player control (in box)
	text += "<div class=\"album_control new\">";

	// control for box
	if (mbox_device != "local") {
		text += "<div class=\"player_active big\" id=\"playing_"+albums["uuid"]+"\" style=\"display:none;\"><img src=\""+mbox_icons["playing"]+"\" style=\"height:20px;width:20px;margin:2px;\"></div>";
	        text += mboxHtmlButton("play",  "mboxApp.requestAPI('GET',['play', '" + uuid + "'],'', mboxControl);", "blue");
        	text += mboxHtmlButton("pause", "mboxApp.requestAPI('GET',['pause'],'',                mboxControl);", "blue");
	        text += mboxHtmlButton("stop",  "mboxApp.requestAPI('GET',['stop'],'',                 mboxControl);", "blue");
	        text += mboxHtmlButton("empty");
		}
	if (mbox_device != "remote") {
        	text += mboxHtmlButton("play",  "mboxPlayerLocal();",	"green");
        	text += mboxHtmlButton("pause", "mboxPlayer.pause();",	"green");
        	text += mboxHtmlButton("stop",  "mboxPlayer.stop();",	"green");
        	//text += mboxHtmlButton("next",  "mboxHtmlShowDataObject(mbox_playlist_queue);",	"green");
	        text += mboxHtmlButton("empty");
		}

       	text += mboxHtmlButton("info", "mboxPlaylistInfo_load('"+uuid+"')", "red");

	// show and edit rfid card
	if ("card_id" in albums && albums["card_id"] != "") 	{
		text += "<div id=\"show_card\">";
		text += mboxHtmlButton("card",  "", "green");
		text += "</div>";
		text += mboxCardEditLink(albums["uuid"]);
		}
	else {
		text += "<div id=\"show_card\">";
		text += "</div>";
		text += mboxCardEditLink(albums["uuid"]);
		}
        text += "</div>";
	text += "<div style=\"width:100%;float:left;\"><hr/></div>";

	// container for tracks & player
	text += "<div class=\"album_tracks\" id=\"album_tracks\">Loading ...</div>"; // first column
	text += "<div class=\"album_tracks\" id=\"album_tracks2\">&nbsp;</div>"; // second column
	text += "<div class=\"album_tracks\">&nbsp;</div>";

	//setTextById("remote1",text);
        mboxAlbumWriteBelow(text);

	if (track_list.length > 0) { 
	    setTimeout(function(){
		setTextById("album_tracks","");
		setTextById("album_tracks2","");
		
		var title_num = track_list.length;
		for (var i=0; i < track_list.length;i++) { if (track_list_album[track_list[i]]) {
		 	if (track_list[i].includes("a_")) { title_num = title_num + track_list_album[track_list[i]].length; }
		 	} }
		 	
		//alert(title_num);
		var k = 0;
		var color = 1;
		for (var i=0; i < track_list.length;i++) {
			var split = false;
			if (k >= Math.round(title_num/2)) { split = true; } // split if half of the list
			k += 1;
			
			// if entry is a track
			if (track_list[i].includes("t_")) {
				mboxPlaylistTrackRow(data,track_list[i],split,uuid);
				}
				
			// if entry is an album
			else if (track_list[i].includes("a_")) {
				if (color == 1)	{ color = 3; }
				else		{ color = 1; }
				
				// if album exists search for tracks in the album
				if (track_list_album[track_list[i]]) {
					mboxPlaylistTrackLine(split,color);
					mboxPlaylistTrackRow(data,track_list[i],split,uuid,(color+1));
					mboxPlaylistTrackLine(split,color);
					var tracks_album1  = track_list_album[track_list[i]];
					var tracks_album2  = mboxAlbumSortTracks(tracks_album1,data["DATA"]["tracks"]);
					
					for (var j=0;j<tracks_album2.length;j++) {
						//console.error(tracks_album[j]);
						if (k >= Math.round(title_num/2)) { split = true; } // split if half of the list
						mboxPlaylistTrackRow(data,tracks_album2[j],split,uuid);//,(color+1));
						k += 1;
						}
					mboxPlaylistTrackLine(split,color);
					}
				// else just print album (error message)
				else {
					mboxPlaylistTrackRow(data,track_list[i],split,uuid,(color+1));
					}
				}

				
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
        
	var text  	 = "";
	var empty_select = "<select class='album_edit_select'><option>Loading ...</option></select>";

	console.log("Edit dialog playlist: "+uuid);

	text += "<b>"+lang("PLAYLIST_EDIT")+": &quot;" + list["title"] + "&quot;</b><br/>&nbsp;<br/>";
	
	text += "<i>"+lang("ADD_TRACK")+" ";
	text += "<small onclick=\"mboxPlaylistEditAlbums_load('"+uuid+"');\" style=\"cursor:pointer;color:gray;\">["+lang("RELOAD")+"]</small> ...</i>";
	text += "<div id='selectAlbumContainer'>"+empty_select+"<br/>"+empty_select+"</div>";
	text += "<div id='selectTrack' class='album_edit_list' >"+lang("SELECT_ARTIST")+" ...</div>";
	
	text += "<i>"+lang("TRACKS_INSIDE")+" ";
	text += "<small onclick=\"mboxPlaylistEditTracks_load('"+uuid+sep+uuid+"');\" style=\"cursor:pointer;color:gray;\">["+lang("RELOAD")+"]</small> ...</i>";
    	text += "<div id='selectTrackList'     class='album_edit_list'>Loading ...</div>";
	text += "<div id='playlistEditingInfo' style='color:red;'></div>";

	appMsg.confirm("<div style=\"text-align:left;\">" + text + "</div>", "", 450);

	setTimeout(function() {
		mboxPlaylistEditAlbums_load(uuid);		// load dropdowns with
		mboxPlaylistEditTracks_load(uuid+sep+uuid);	// load data of playlist (to delete tracks)
		}, 1000);
	}


// load albums and write drop down menus
//---------------------------

//function mboxPlaylistEditAlbums_load(uuid) { mboxApp.requestAPI("GET",["db","albums--album_info",uuid],"", mboxPlaylistEditAlbums ); }
function mboxPlaylistEditAlbums_load(uuid) { mboxApp.requestAPI("GET",["db","artists",uuid],"", mboxPlaylistEditAlbums ); }
function mboxPlaylistEditAlbums(data) {

	var selected;
	var uuid;
	var text         = "";
	var sep          = "||";
	var list_artists = [];
	var artists      = data["DATA"]["artists"];

	if ( data["REQUEST"]["db_filter"].indexOf(sep) > -1) {	
		var temp     = data["REQUEST"]["db_filter"].split(sep);
		uuid         = temp[0];
		selected     = temp[1];
		}
	else {	uuid         = data["REQUEST"]["db_filter"];
		}

	// drop down "artists"
	list_artists = Object.keys(artists);
	list_artists.sort();
	
	text += "<select id='selectArtist' class='album_edit_select' " + 
	        "onchange='mboxPlaylistEditAlbums_load(\""+uuid+sep+"\"+document.getElementById(\"selectArtist\").value);'>";
	text += "<option value=''>"+lang("SELECT_ARTIST")+" ...</option>";;

	for (var i=0;i<list_artists.length;i++) {
		var sel = "";
		if (selected && selected == list_artists[i] ) { sel = " selected"; }
		text += "<option value='"+list_artists[i]+"' "+sel+">" + list_artists[i] + "</option>";
		}

	text += "</select>&nbsp;<br/>";	

	// drop down "albums"
	text += "<select id='selectAlbum' class='album_edit_select' ";
	text += "onchange='mboxPlaylistEditTracks_load(document.getElementById(\"selectAlbum\").value);'>";
	
	if (selected) {
		for (var i=0;i<artists[selected].length;i++) {
			key   = artists[selected][i]["uuid"];
			album = artists[selected][i]["album"];
			text += "<option value='"+key+sep+uuid+"'>" + album + "</option>";
			}
		}
	else {	text += "<option value=''>"+lang("SELECT_ARTIST")+" ...</option>";
		}

	text += "</select>&nbsp;<br/>";	

	setTextById("selectAlbumContainer", text);
	mboxPlaylistEditTracks_load(document.getElementById("selectAlbum").value);
	}

// write track lists with edit & delete link (1) tracks of select album (2) tracks of playlist
//---------------------------

function mboxPlaylistEditTracks_load(uuid_filter,source="") { 
	var sep			= "||";
	var ids			= uuid_filter.split(sep);	// list of IDs, uuid of playlist first
	var uuid		= ids[0];       		// id of album (selected ...)
	var filter		= ids[1];
	if (filter == "") { filter = "-"; }

	mboxApp.requestAPI("GET",["data",uuid,filter], "", mboxPlaylistEditTracks);
	}

function mboxPlaylistEditTracks(data) {

	var filter		= data["REQUEST"]["db_filter"];
	var uuid		= data["DATA"]["_selected_uuid"];
	var album		= data["DATA"]["_selected"];
	var tracklist		= data["DATA"]["_selected"]["tracks"];
	var trackinfo		= data["DATA"]["tracks"];
	var albuminfo		= data["DATA"]["album_info"];
	
	// ALBUM LIST - add tracks to playlist
	if (uuid.includes("a_")) {
		if (tracklist.length > 0) {
			var text_album	= "";
			var onclick_add	=  "mboxApp.requestAPI('PUT',['playlist_items','add',   '"+filter+"','"+uuid+"'],'', mboxPlaylistAddTrackInfo);";			
			
			text_album	+= " <b class=\"album_edit_pl\"   onclick=\""+onclick_add+"\">(+)</b> &nbsp;"; 
			text_album	+= "<b>"+lang("ALBUM_COMPLETE")+":</b> " + album["album"] + "<br/>";
			
			for (var i=0;i<tracklist.length;i++) {
				var onclick_add    =  "mboxApp.requestAPI('PUT',['playlist_items','add',   '"+filter+"','"+tracklist[i]+"'],'', mboxPlaylistAddTrackInfo);";			
				var onclick_delete =  "mboxApp.requestAPI('PUT',['playlist_items','delete','"+filter+"','"+tracklist[i]+"'],'', mboxPlaylistDeleteTrackInfo);";
	
				// text_album += " <b class=\"album_delete_pl\" onclick=\""+onclick_delete+"\">(-)</b> &nbsp;";
				text_album += " <b class=\"album_edit_pl\"   onclick=\""+onclick_add+"\">(+)</b> &nbsp;"; 
	
				if (tracklist[i] in trackinfo) 		{ text_album += trackinfo[tracklist[i]]["title"]; }
				else 					{ text_album += "<i>"+lang("NOT_FOUND")+": " + tracklist[i] + "</i>"; }
				
				text_album += "<br/>";
				}
			setTextById("selectTrack", text_album);
			}
		else {	setTextById("selectTrack", lang("EMPTY_LIST"));
			}
		}

	// PLAYLIST - delete track	
	if (uuid.includes("p_")) {
		if (tracklist.length > 0) {
			var text_playlist = "";
			for (var i=0;i<tracklist.length;i++) {
				var onclick_delete  =  "mboxApp.requestAPI('PUT',['playlist_items','delete','"+filter+"', '"+tracklist[i]+"'],'', mboxPlaylistDeleteTrackInfo);";
				text_playlist += " <b class=\"album_delete_pl\" onclick=\""+onclick_delete+"\">(-)</b> &nbsp;";
				
				if (tracklist[i] in trackinfo)		{ text_playlist += trackinfo[tracklist[i]]["title"] + " (" + trackinfo[tracklist[i]]["artist"] + ")<br/>"; }
				else if (tracklist[i] in albuminfo)	{ text_playlist += "<b>"+lang("ALBUM_COMPLETE")+":</b> " + albuminfo[tracklist[i]]["album"] + " (" + albuminfo[tracklist[i]]["artist"] + ")<br/>"; }
				else 					{ text_playlist += "<i>"+lang("NOT_FOUND")+": " + tracklist[i] + "</i><br/>"; }
				}
			setTextById("selectTrackList", text_playlist);
			}
		else {	setTextById("selectTrackList", lang("EMPTY_LIST"));
			}
		}
	return;
	}


// edit single entry
//---------------------------

function mboxPlaylistEditEntry_load(uuid) { mboxApp.requestAPI("GET",["data",uuid,"uuid,title,description"],"", mboxPlaylistEditEntry ); }
function mboxPlaylistEditEntry(data) { mboxDataEdit( data ); }  // -> mbox-data.js


// track title row
//--------------------------------------

function mboxPlaylistTrackRow(data,uuid,split=false,uuid_pl="",color=0) {

        var text       = "";
        var cmd        = "";
	var no         = "";
	var albuminfo  = data["DATA"]["album_info"];
	var trackinfo  = data["DATA"]["tracks"];

	// if half of the list, split ... where is defined in funct. above
	if (split==true) { no = "2";}

	// if track exists ...
        if (trackinfo && trackinfo[uuid]) {

		var track = trackinfo[uuid];

	        var length = "";
        	if (track["length"]) {
                	length = " <font color='gray'>(" + convert_second2time(Math.round(track["length"])) + ")</font>";
                	}

		// Controls to play Track ...
	       	cmd += "<div class=\"album_tracks_control\"  style=\"background:"+mbox_track_color[color]+";\">";
		if (mbox_device == "local")	{ cmd += mboxHtmlButton("play",  "writeAudioPlayer('" + uuid + "','audioPlayer');", "green",   "small right"); }
		else 				{ cmd += mboxHtmlButton("play",  "mboxApp.requestAPI('GET',['play', '"+uuid+"'],'',mboxControl);", "blue", "small right"); }
                cmd += "<div class=\"player_active right\" id=\"playing3_"+uuid+"\" style=\"display:none;\"><img src=\""+mbox_icons["playing"]+"\" style=\"width:10px;height:10px;margin:2px;\"></div>";
	       	cmd += "</div>";

		// Show Title if exist ...
        	text += "<div class=\"album_tracks_title\"  style=\"background:"+mbox_track_color[color]+";\">";
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

		// Show Title if exist ...
        	text += "<div class=\"album_tracks_headline\" style=\"background:"+mbox_track_color[color]+";\">";
                text += "<center><i>" +albuminfo[uuid]["artist"] + "<br/><b>" +albuminfo[uuid]["album"] + "</b></i></center>";
	        text += "</div>";
        	text += cmd;
		}

	// if not exists
	else {
	       	cmd += "<div class=\"album_tracks_control\">";
	       	
//		var onclick2   =  "mboxApp.requestAPI('PUT',['playlist_items','delete','"+ids[1]+"','"+tracklist[i]+"'],'', mboxPlaylistInfoDelete);";

        	cmd += mboxHtmlButton("delete",  "mboxApp.requestAPI('PUT',['playlist_items','delete', '"+uuid_pl+"','"+uuid+"'],'',mboxPlaylistDeleteTrack);", "red", "small right");
	       	cmd += "</div>";

        	text += "<div class=\"album_tracks_title\">";
        	if (uuid.includes("a_")) { text += "<b style='color:red'>"+lang("ALBUM")+" "+lang("NOT_FOUND")+"</b><br/>"; }
        	else			 { text += "<b style='color:red'>"+lang("TRACK")+" "+lang("NOT_FOUND")+"</b><br/>"; }
		text += uuid;
	       	text += "</div>" + cmd;
		}

	addTextById("album_tracks"+no,text);
        }

function mboxPlaylistTrackLine(split=false,color) {
	if (split==true) { no = "2";} else { no = ""; }
	addTextById("album_tracks"+no,"<div class=\"album_tracks_line\"><hr style=\"color:"+mbox_track_color[color]+"\"/></div>");
	}

// delete playlist (from dialog to confirm to message)
//---------------------------

function mboxPlaylistDelete(uuid,title) {
	text    = lang("PLAYLIST_DELETE_ASK") + ": <b>"+title+"</b>?";
	cmd     = "mboxPlaylistDelete_exec('"+uuid+"','"+title+"');";
	appMsg.confirm(text,cmd,150,true);
	}
	
function mboxPlaylistDelete_exec(uuid,title) {
	mboxApp.requestAPI('DELETE',['data',uuid],'',[mboxPlaylistDelete_msg,title]);
	}

function mboxPlaylistDelete_msg(data,title) {
	mboxDataReturnMsg(data,lang("PLAYLIST_DELETED")+"<br/><b>"+title,lang("PLAYLIST_DELETE_ERROR")+"<br/><b>"+title);
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
        edit += mboxHtmlButton("image_add", "mboxUploadImage('"+uuid+"','playlist','"+album["title"]+"');", "red");
        edit += mboxHtmlButton("list_edit", "mboxPlaylistEdit_load('"+album["uuid"]+"');",          "red");
        edit += mboxHtmlButton("edit",  	"mboxPlaylistEditEntry_load('"+album["uuid"]+"');",          "red");
        edit += mboxHtmlButton("delete",  	"mboxPlaylistDelete('"+uuid+"','"+album["title"]+"');",         "red");


        text += "<b>"+lang("PLAYLIST_INFORMATION")+"</b><br/>";
        text += mboxHtmlTableNew("start");
        text += "<tr><td colspan='2'><hr></td></tr>";
        text += mboxHtmlTableNew(["<i>"+lang("TITLE")+":",        album["title"] ] );
        text += mboxHtmlTableNew(["<i>"+lang("DESCRIPTION")+":",  album["description"] ] );
        text += mboxHtmlTableNew(["<i>Tracks:",	       			album["tracks"].length ] );
        text += mboxHtmlTableNew(["<i>UUID:",               "<a href='" + url + "/' target='_blank'>" + uuid + "</a>" ] );
        text += mboxHtmlTableNew(["<i>Card ID:",            "<a style='cursor:pointer;' onclick='mboxCardList_load(\""+cardid+"\");'>"    + cardid + "</a>" ] );
        text += mboxHtmlTableNew(["<i>"+lang("COVER_AVAILABLE")+":",      cover ] );
        text += "<tr><td colspan='2'><hr></td></tr>";
        text += mboxHtmlTableNew(["<i>"+lang("EDIT")+":",         edit ] );
        text += "<tr><td colspan='2'><hr></td></tr>";
        text += mboxHtmlTableNew("end");

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
	var sep = "||";
	setTextById("playlistEditingInfo","Lösche "+data["LOAD"]["UUID"] + " ...");
	setTimeout(function(){
		param = data["REQUEST"]["c-param"].split(" ");
		mboxPlaylistEditTracks_load(param[0]+sep+param[0]);
		mboxPlaylistAll_load('', param[0]);
		//mboxApp.requestAPI("GET",["db","all",document.getElementById("selectAlbum").value], "", mboxPlaylistEditTracks,"wait");
		//mboxPlaylistAll_load('', data["LOAD"]["UUID"]);
		setTextById("playlistEditingInfo","");
		}, 1000);
	}

function mboxPlaylistDeleteTrack(data) {
	mboxDataReturnMsg(data,lang("TRACK_DELETED"),lang("TRACK_DELETE_ERROR")); 
	mboxPlaylistAll_load('', data["LOAD"]["UUID"]);
	}

function mboxPlaylistAddTrackInfo(data) {
	var sep = "||";
	setTextById("playlistEditingInfo","Füge Eintrag zu "+data["LOAD"]["UUID"] +" hinzu ...");
	setTimeout(function(){
		param = data["REQUEST"]["c-param"].split(" ");
		mboxPlaylistEditTracks_load(param[0]+sep+param[0]);
		mboxPlaylistAll_load('', param[0]);
		//mboxApp.requestAPI("GET",["db","all",document.getElementById("selectAlbum").value], "", mboxPlaylistEditTracks,"wait");
		//mboxPlaylistAll_load('', data["LOAD"]["UUID"]);
		setTextById("playlistEditingInfo","");
		}, 1000);
	}


// add a playlist
//----------------------------------------------------------------

function mboxPlaylistAdd() {
        var title = document.getElementById("playlist_title").value;
        var descr = document.getElementById("playlist_description").value;
        document.getElementById("mboxPlaylistAdd").disabled = true;
        document.getElementById("mboxPlaylistAdd").innerHTML = lang("PLEASE_WAIT")+" ...";
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
	mboxDataReturnMsg(data,lang("PLAYLIST_CREATED"),lang("PLAYLIST_CREATED_ERROR"));
        mboxPlaylistAll_load();
        }

//---------------------------
// EOF

