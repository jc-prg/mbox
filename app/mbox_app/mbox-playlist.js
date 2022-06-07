//--------------------------------------
// jc://music-box/, (c) Christoph Kloth
//--------------------------------------
// list and edit playlists
//--------------------------------------

function mboxPlaylists_load(filter="",playlist_uuid="-")  { 
	if (filter["UUID"])     { filter = filter["UUID"]; }
	else                    { filter = filter+">>"+playlist_uuid; }
	appFW.requestAPI("GET",["db","playlists--cards",filter], "", [mboxPlaylists,playlist_uuid]);
	scrollToTop();
	}
	
function mboxPlaylists_reload() {

    mboxPlaylists(data=mbox_list_data);
    }

function mboxPlaylists(data, uuid="") {

	mbox_list_data   = data;
	var entries_info = data["DATA"]["playlists"];

	// create filter
	var filter     = "";
	var the_filter = [""];
	
	// create sort keys
	var sort_keys = ["title","description"];

	// create list view
	mboxViewsList(type="playlist", data=entries_info, selected_uuid=uuid, filter_key=the_filter, filter_text=filter, sort_keys=sort_keys, callTrackList="mboxViewsTrackList", chapter_rows=false);
	}

function mboxPlaylistEdit_load(uuid) {

    appFW.requestAPI("GET",["data",uuid,"-"], "", mboxPlaylistEdit);
    }

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
	text += "<div id='playlistEditingInfo' style='color:"+mbox_color[appTheme]["warning"]+";'></div>";

	appMsg.confirm("<div style=\"text-align:left;\">" + text + "</div>", "", 450);

	setTimeout(function() {
		mboxPlaylistEditAlbums_load(uuid);		// load dropdowns with
		mboxPlaylistEditTracks_load(uuid+sep+uuid);	// load data of playlist (to delete tracks)
		}, 1000);
	}

function mboxPlaylistEditAlbums_load(uuid) {

    appFW.requestAPI("GET",["db","artists",uuid],"", mboxPlaylistEditAlbums );
    }

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

function mboxPlaylistEditTracks_load(uuid_filter,source="") {
	var sep	= "||";
	var ids	= uuid_filter.split(sep);	// list of IDs, uuid of playlist first
	var uuid	= ids[0];       		// id of album (selected ...)
	var filter	= ids[1];
	if (filter == "") { filter = "-"; }
    if (uuid == "") { return; }

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

function mboxPlaylistEditEntry_load(uuid) {

    appFW.requestAPI("GET",["data",uuid,"uuid,title,description"],"", mboxPlaylistEditEntry );
    }

function mboxPlaylistEditEntry(data) {

    mboxDataEdit( data );
    }  // -> mbox-data.js

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

function mboxPlaylistInfo_load(uuid) {

    appFW.requestAPI("GET",["data",uuid,"-"],"", mboxPlaylistInfo );
    }

function mboxPlaylistInfo(data) {

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
        edit += mboxHtmlButton("image_add",  "mboxUploadImage('"+uuid+"','playlist','"+album["title"]+"');", "red");
        edit += mboxHtmlButton("list_edit",  "mboxPlaylistEdit_load('"+album["uuid"]+"');",                  "red");
        edit += mboxHtmlButton("edit",       "mboxPlaylistEditEntry_load('"+album["uuid"]+"');",             "red");
        edit += mboxHtmlButton("delete",     "mboxPlaylistDelete('"+uuid+"','"+album["title"]+"');",         "red");
        
        var info_data = [
        	[ lang("TITLE"),		album["title"] ],
        	[ lang("DESCRIPTION"),		album["description"] ],
        	[ lang("TRACKS"),		album["tracks"].length ],
        	[ "UUID",			"<a href='" + url + "/' target='_blank'>" + uuid + "</a>" ],
        	[ "Card-ID",			"<a style='cursor:pointer;' onclick='mboxCardList_load(\""+cardid+"\");'>" + cardid + "</a>" ],
        	[ lang("COVER_AVAILABLE"),	cover ],
        	[ "LINE" ],
        	[ lang("EDIT"), 		edit ],
        	];

	mboxViews_InfoTable(title=lang("PLAYLIST")+" "+lang("INFORMATION"), info_data=info_data, height=450);
	}

function mboxPlaylistInfo_close() {
	setTimeout(function(){ mboxPlaylistLoad(); }, 2000);
        appMsg.hide();
        }

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

function mboxPlaylistAdd() {
        var title = document.getElementById("playlist_title").value;
        var descr = document.getElementById("playlist_description").value;
        document.getElementById("mboxPlaylistAdd").disabled = true;
        document.getElementById("mboxPlaylistAdd").innerHTML = lang("PLEASE_WAIT")+" ...";
        appFW.requestAPI('POST',['data','playlists',title+'||'+descr], '', mboxPlaylistAdd_msg);
        }

function mboxPlaylistAdd_dialog(i) {
	var text		= "";
	var onclick		= "document.getElementById('album_"+(i)+"').style.display='none';";
	var width		= 150;        
	var table		= new jcTable("add_dialog");
	table.table_width	= "100%";
	table.columns 		= 2;
	table.cells_width	= ["120px",""];
        
	text += table.start();
	text += table.row_one( "<b>"+lang("ADD_PLAYLIST")+":</b>" );
	text += table.row_one( "<hr/>" );
	text += table.row( [ lang("TITLE")+":",	"<input id=\"playlist_title\" style=\"width:"+width+"\"/>" ] );
	text += table.row( [ lang("DESCRIPTION")+":",	"<input id=\"playlist_description\" style=\"width:"+width+"\"/>" ] );
	text += table.row_one( "<hr/>" );
	text += table.row_one( button("mboxPlaylistAdd();",lang("ADD"),"mboxPlaylistAdd") + button(onclick,lang("CLOSE"),"close_playlist") );
	text += table.end();

	setTextById("album_"+i,text);
	document.getElementById("album_"+i).style.display="block";
	}

function mboxPlaylistAdd_msg(data) {
	mboxDataReturnMsg(data,lang("PLAYLIST_CREATED"),lang("PLAYLIST_CREATED_ERROR"));
	mboxPlaylists_load();
	}

