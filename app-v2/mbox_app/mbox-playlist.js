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
function mboxPlaylistTrackRow(data, uuid, column, uuid_pl="", count_pl=0, color=0)
function mboxPlaylistTrackLine(column=1,color)
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

// Load stream views
//--------------------------------------

function mboxPlaylists_load(filter="",playlist_uuid="-")  { 
	if (filter["UUID"])     { filter = filter["UUID"]; }
	else                    { filter = filter+">>"+playlist_uuid; }
	appFW.requestAPI("GET",["db","playlists--cards",filter], "", [mboxPlaylists,playlist_uuid]);
	scrollToTop();
	}
	
function mboxPlaylists_reload() { mboxPlaylists(data=mbox_list_data); }
function mboxPlaylists(data, uuid="") {

	mbox_list_data   = data;
	var entries_info = data["DATA"]["playlists"];

	// create filter
	var filter     = "";
	var the_filter = [""];
	
	// create sort keys
	var sort_keys = ["title","description"];

	// create list view
	mboxViews_list(type="Playlist", data=entries_info, selected_uuid=uuid, filter_key=the_filter, filter_text=filter, sort_keys=sort_keys, callTrackList="mboxPlaylistOne");
	}
	


// List tracks of playlist
//--------------------------------------

function mboxPlaylistOne_load2(uuid) { appFW.requestAPI("GET",["data",uuid,"-"], "", mboxPlaylistOne); }
function mboxPlaylistOne_load(i,uuid) {
	//console.error("Load:"+uuid+"/"+i);
	var count = 3;
        var width = document.body.clientWidth;
        if (width > 1250) { mbox_list_count = 6; }

        mbox_list_pos = ((Math.floor((i-1)/mbox_list_count)+1) * mbox_list_count );
        if (mbox_list_pos > mbox_list_amount) { mbox_list_pos = mbox_list_amount; }

        appFW.requestAPI("GET",["data",uuid,"-"],"",mboxPlaylistOne );
        }

//--------------------------------------

function mboxPlaylistOne(data) {

	var text		= "";
	var playlist_uuid	= data["DATA"]["_selected_uuid"];
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

	// handover data to local player
	mbox_playlist_queue["type"]		= "list";
	mbox_playlist_queue["album"]		= albums;
	mbox_playlist_queue["album"]["tracks"] = track_list_complete;
	mbox_playlist_queue["scrollto"]	= "scrollto_" + playlist_uuid.replace(/-/g,"");
	mbox_playlist_queue["tracks"]		= data["DATA"]["tracks"];

	console.debug(mbox_playlist_queue);
	
        // check cover
	var default_cover = mbox_icon_dir + mbox_icons["playlist"];
	var cover = mboxCoverAlbum_new("",albums);
	if (!cover) { cover = default_cover; }

        // Log
        if (albums) 	{ console.log("playlist-id: "+playlist_uuid+"/"+albums["title"]); }
	else 		{ console.error("mboxPlaylistOne: "+playlist_uuid+"/"+data["DATA"]["_selected_uuid"]); console.error(data); return; }

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
	text += mboxPlayerControlEntry(playlist_uuid);
	text += mboxHtmlButton("info", "mboxPlaylistInfo_load('"+playlist_uuid+"');", "red");
	text += mboxCardInfoIcon(albums, playlist_uuid);
	text += "</div>";
	text += "<div style=\"width:100%;float:left;\"><hr/></div>";

        // count tracks & columns
        var columns = Math.trunc( mboxListCount_New() / 3 );
        var total_tracks = track_list.length;
        for (var i=0; i < track_list.length;i++) {
        	if (track_list[i].includes("a_")) {
        		if (track_list_album && track_list_album[track_list[i]]) {
	        		total_tracks += track_list_album[track_list[i]].length;
	        		}
        		}
        	}
        total_tracks += 1;
        	
	// container for tracks & player
        for (var i=1; i <= columns; i++) { text += "<div class=\"album_tracks\" id=\"album_tracks"+i+"\"></div>"; }
	text += "<div class=\"album_tracks\">&nbsp;</div>";
	setTextById("album_tracks1","<center>&nbsp;<br/>Loading<br/>&nbsp;</center>");
        	
        mboxAlbumWriteBelow(text);
        
	// create track list
	if (track_list.length > 0) { 
	    setTimeout(function(){
		
		var title_num = track_list.length;
		for (var i=0; i < track_list.length;i++) { if (track_list_album[track_list[i]]) {
		 	if (track_list[i].includes("a_")) { title_num = title_num + track_list_album[track_list[i]].length; }
		 	} }
		 	
		//alert(title_num);
		var k             = 0;
		var color         = 1;
		var column_number = 0;
		var column_tracks = Math.round(total_tracks / columns);
		var playlist_no   = 0;
		
		for (var i=0; i < track_list.length; i++) {

			// if entry is a track
			if (track_list[i].includes("t_")) {
				k           += 1;
				playlist_no += 1;
				column_number = 1 + Math.trunc((k-1) / column_tracks);		
				console.debug(column_number + " = " + k + " / " + column_tracks);
				mboxPlaylistTrackRow(data=data, uuid=track_list[i], column=column_number, uuid_pl=playlist_uuid, count_pl=playlist_no);
				}
				
			// if entry is an album
			else if (track_list[i].includes("a_")) {
				if (color == 1)	{ color = 3; }
				else			{ color = 1; }
				
				// if album exists search for tracks in the album
				if (track_list_album[track_list[i]]) {
					k += 1;
					column_number = 1 + Math.trunc((k-1) / column_tracks);				
					console.debug(column_number + " = " + k + " / " + column_tracks);
					
					mboxPlaylistTrackLine(column_number,color);
					mboxPlaylistTrackRow(data=data, uuid=track_list[i], column=column_number, uuid_pl=playlist_uuid, count_pl=playlist_no, color=(color+1));
					mboxPlaylistTrackLine(column_number,color);
					var tracks_album1  = track_list_album[track_list[i]];
					var tracks_album2  = tracks_album1; // Album Sort server side
					
					for (var j=0;j<tracks_album2.length;j++) {
						k           += 1;
						playlist_no += 1;
						column_number = 1 + Math.trunc((k-1) / column_tracks);				
						console.debug(column_number + " = " + k + " / " + column_tracks);
						
						mboxPlaylistTrackRow(data=data, uuid=tracks_album2[j], column=column_number, uuid_pl=playlist_uuid, count_pl=playlist_no);
						}
					mboxPlaylistTrackLine(column_number,color);
					}
				// else just print album (error message)
				else {
					k += 1;
					column_number = 1 + Math.trunc((k-1) / column_tracks);				
					console.debug(column_number + " = " + k + " / " + column_tracks);
					
					mboxPlaylistTrackRow(data=data, uuid=track_list[i], column=column_number, uuid_pl=playlist_uuid, count_pl=playlist_no, color=(color+1));
					}
				}

				
			//console.log(i + " / " + track_list.length + " - " + split);
		} }, 1000); }
	else {
		setTextById("album_tracks","<center>&nbps;<br/>"+lang("PLAYLIST_EMPTY")+"<br/>&nbsp;</center>");
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

function mboxPlaylistEdit_load(uuid) { appFW.requestAPI("GET",["data",uuid,"-"], "", mboxPlaylistEdit); 	} //console.log("1"+uuid);}
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

//function mboxPlaylistEditAlbums_load(uuid) { appFW.requestAPI("GET",["db","albums--album_info",uuid],"", mboxPlaylistEditAlbums ); }
function mboxPlaylistEditAlbums_load(uuid) { appFW.requestAPI("GET",["db","artists",uuid],"", mboxPlaylistEditAlbums ); }
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
	var sep	= "||";
	var ids	= uuid_filter.split(sep);	// list of IDs, uuid of playlist first
	var uuid	= ids[0];       		// id of album (selected ...)
	var filter	= ids[1];
	if (filter == "") { filter = "-"; }

	appFW.requestAPI("GET",["data",uuid,filter], "", mboxPlaylistEditTracks);
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
			var onclick_add	=  "appFW.requestAPI('PUT',['playlist_items','add',   '"+filter+"','"+uuid+"'],'', mboxPlaylistAddTrackInfo);";

			text_album	+= " <b class=\"album_edit_pl\"   onclick=\""+onclick_add+"\">(+)</b> &nbsp;"; 
			text_album	+= "<b>"+lang("ALBUM_COMPLETE")+":</b> " + album["album"] + "<br/>";

			for (var i=0;i<tracklist.length;i++) {
				var onclick_add    =  "appFW.requestAPI('PUT',['playlist_items','add',   '"+filter+"','"+tracklist[i]+"'],'', mboxPlaylistAddTrackInfo);";
				var onclick_delete =  "appFW.requestAPI('PUT',['playlist_items','delete','"+filter+"','"+tracklist[i]+"'],'', mboxPlaylistDeleteTrackInfo);";

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
				var onclick_delete  =  "appFW.requestAPI('PUT',['playlist_items','delete','"+filter+"', '"+tracklist[i]+"'],'', mboxPlaylistDeleteTrackInfo);";
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

function mboxPlaylistEditEntry_load(uuid) { appFW.requestAPI("GET",["data",uuid,"uuid,title,description"],"", mboxPlaylistEditEntry ); }
function mboxPlaylistEditEntry(data) { mboxDataEdit( data ); }  // -> mbox-data.js


// track title row
//--------------------------------------

function mboxPlaylistTrackRow(data, uuid, column, uuid_pl="", count_pl=0, color=0) {

	var text       = "";
	var cmd        = "";
	var no         = column;
	var albuminfo  = data["DATA"]["album_info"];
	var trackinfo  = data["DATA"]["tracks"];

	// if track exists ...
        if (trackinfo && trackinfo[uuid]) {

		var track    = trackinfo[uuid];
		var position = count_pl - 1;

	        var length = "";
        	if (track["length"]) {
                	length = " <font color='gray'>(" + convert_second2time(Math.round(track["length"])) + ")</font>";
                	}

		// Controls to play Track ...
		cmd += "<div class=\"album_tracks_control\"  style=\"background:"+mbox_track_color[color]+";\">";
		if (mbox_device == "local")	{ cmd += mboxHtmlButton("play",  "mboxPlayerLocal(" + position + ");", "green",   "small right"); }		 
		else 				{ cmd += mboxHtmlButton("play",  "appFW.requestAPI('GET',['play_position', '"+uuid_pl+"',"+position	+"],'',mboxControl);", "blue", "small right"); }
		cmd += "<div class=\"player_active right\" id=\"playing3_"+uuid+"\" style=\"display:none;\"><img src=\""+mbox_icon_dir+mbox_icons["playing"]+"\" style=\"width:10px;height:10px;margin:2px;\"></div>";
		cmd += "</div>";

		// Show Title if exist ...
        	text += "<div class=\"album_tracks_title\"  style=\"background:"+mbox_track_color[color]+";\">";
		text += count_pl+". <b>" +track["title"] + "</b><br/>";
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
        	cmd += mboxHtmlButton("delete",  "appFW.requestAPI('PUT',['playlist_items','delete', '"+uuid_pl+"','"+uuid+"'],'',mboxPlaylistDeleteTrack);", "red", "small right");
       	cmd += "</div>";

        	text += "<div class=\"album_tracks_title\">";
        	if (uuid.includes("a_")) { text += "<b style='color:red'>"+lang("ALBUM")+" "+lang("NOT_FOUND")+"</b><br/>"; }
        	else			 { text += "<b style='color:red'>"+lang("TRACK")+" "+lang("NOT_FOUND")+"</b><br/>"; }
		text += uuid;
       	text += "</div>" + cmd;
		}

	addTextById("album_tracks"+no,text);
        }

function mboxPlaylistTrackLine(column=1,color) {
	addTextById("album_tracks"+column,"<div class=\"album_tracks_line\"><hr style=\"color:"+mbox_track_color[color]+"\"/></div>");
	}

// delete playlist (from dialog to confirm to message)
//---------------------------

function mboxPlaylistDelete(uuid,title) {
	text    = lang("PLAYLIST_DELETE_ASK") + ": <b>"+title+"</b>?";
	cmd     = "mboxPlaylistDelete_exec('"+uuid+"','"+title+"');";
	appMsg.confirm(text,cmd,150,true);
	}
	
function mboxPlaylistDelete_exec(uuid,title) {
	appFW.requestAPI('DELETE',['data',uuid],'',[mboxPlaylistDelete_msg,title]);
	}

function mboxPlaylistDelete_msg(data,title) {
	mboxDataReturnMsg(data,lang("PLAYLIST_DELETED")+"<br/><b>"+title,lang("PLAYLIST_DELETE_ERROR")+"<br/><b>"+title);
        mboxPlaylists_load();
        }


// radio info as popup (incl. some settings ...)
//--------------------------------------

function mboxPlaylistInfo_load(uuid) { appFW.requestAPI("GET",["data",uuid,"-"],"", mboxPlaylistInfo ); }
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
		mboxPlaylists_load('', param[0]);
		setTextById("playlistEditingInfo","");
		}, 1000);
	}

function mboxPlaylistDeleteTrack(data) {
	mboxDataReturnMsg(data,lang("TRACK_DELETED"),lang("TRACK_DELETE_ERROR")); 
	mboxPlaylists_load('', data["LOAD"]["UUID"]);
	}

function mboxPlaylistAddTrackInfo(data) {
	var sep = "||";
	setTextById("playlistEditingInfo","Füge Eintrag zu "+data["LOAD"]["UUID"] +" hinzu ...");
	setTimeout(function(){
		param = data["REQUEST"]["c-param"].split(" ");
		mboxPlaylistEditTracks_load(param[0]+sep+param[0]);
		mboxPlaylists_load('', param[0]);
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
        appFW.requestAPI('POST',['data','playlists',title+'||'+descr], '', mboxPlaylistAdd_msg);
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

