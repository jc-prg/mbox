//--------------------------------------
// jc://music-box/, (c) Christoph Kloth
//--------------------------------------
// show album list and details
//--------------------------------------
/* INDEX:
function mboxListCount()
function mboxAlbumAll_load(filter="",uuid="")
function mboxAlbumAll_reload()
function mboxAlbumAll(data, uuid)
function mboxAlbumAll_filter(album_info,filters)
function mboxAlbumFilterPath(data,selected)
function mboxAlbumFilterArtist(data,selected)
function mboxAlbumList(data)
function mboxAlbumInfo_load(uuid)
function mboxAlbumInfo_close()
function mboxAlbumInfo(data)
function mboxAlbumDelete(title,uuid)
function mboxAlbumDelete_exec(uuid,title)
function mboxAlbumDelete_msg(data,title)
function mboxAlbumTrackInfo_load(uuid)
function mboxAlbumTrackInfo(data)
function mboxAlbumTrackRow(id, dataTracks, album=true, artist=false, count=0, trackinfo=false)
function mboxAlbumEmptyAll()
function mboxAlbumEmptyBelow()
function mboxAlbumWriteBelow(text)
*/
//--------------------------------------

function mboxListCount() {
	var width = document.body.clientWidth;
	var mbox_list_count;
	
	if (width > 1250)	{ mbox_list_count = 9; }
	else if (width > 705)	{ mbox_list_count = 6; }
	else			{ mbox_list_count = 3; }
	
	return mbox_list_count;
	}


// Load album views
//--------------------------------------

function mboxAlbumAll_load(filter="",uuid="") {
	if (filter["UUID"]) 	{ filter = ">>"+filter["UUID"]; } 	// load after API call
	else 			{ filter = filter+">>"+uuid; }		// load by filter function
	appFW.requestAPI("GET",["db","album_info",filter], "", [mboxAlbumAll, uuid],"","mboxAlbumAll_New");
	scrollToTop();
	}
	
function mboxAlbumAll_reload() { mboxAlbumAll(data=mbox_list_data); }
function mboxAlbumAll(data, uuid) {

	mbox_list_data   = data;
	var entries_info = data["DATA"]["album_info"];
	var the_filter   = [""];

	// create filter
	if ("db_filter" in data["REQUEST"]) {
	        var filter_uuid     = data["REQUEST"]["db_filter"].split(">>");
		var filters         = filter_uuid[0];
		entry_active        = filter_uuid[1];
		the_filter          = filters.split(":");
		}
	else {	filters = ""; }
	var filter = mboxAlbumAll_filter(entries_info,filters);
	
	// create sort keys
	var sort_keys = ["artist","album"];

	// create list view
	mboxViews_list(type="Album", data=entries_info, selected_uuid=uuid, filter_key=the_filter, filter_text=filter, sort_keys=sort_keys, callTrackList="mboxAlbumList");
	}
	

// Filter definition
//--------------------------------------

function mboxAlbumAll_filter(album_info,filters) {
	var filter = "";
	filter += "<div class='album_filter'>";
	filter += mboxHtmlTableNew("start",true,"310px");
	filter += mboxHtmlTableNew(["<i>"+lang("CATEGORY")+":", 	mboxAlbumFilterPath(album_info,filters) ], ["90px","210px"] );	
	filter += mboxHtmlTableNew("end");
	filter += "</div><div class='album_filter'>";
	filter += mboxHtmlTableNew("start",true,"310px","");
	filter += mboxHtmlTableNew(["<i>"+lang("BAND_ARTIST")+":", 	mboxAlbumFilterArtist(album_info,filters) ], ["90px","210px"] );
	filter += mboxHtmlTableNew("end");
	filter += "</div>";
	return filter;
	}	

//--------------------------------------

function mboxAlbumFilterPath(data,selected) {

	var command  = "mboxAlbumAll_load(document.getElementById('filter_album').value);";
	var filter   = "<select id='filter_album' onchange=\""+command+"\"  class=\"album_filter_dropdown\">"; 
	var criteria = "albumpath:";
	var list     = [];

	for (key in data) {
		if (data[key]["albumpath"].indexOf("/") > -1)	{ path = data[key]["albumpath"].split("/"); }
		else 						{ path = data[key]["albumpath"].split("_"); }
			
		console.debug("mboxAlbumFilterPath");
		console.debug(path);
		
		if (path.length > 0) {
			if (path[0] != "" && list.indexOf(path[0])==-1)	{ list.push(path[0]); }
			else if (path[0] == "" && list.indexOf(path[1])==-1)	{ list.push(path[1]); }
			}
		}

	list.sort();
	filter += "<option></option>";
	for (var i=0;i<list.length;i++) {
		if (criteria+list[i] == selected) 	{ sel = " selected"; }
		else					{ sel = ""; }
		filter += "<option"+sel+" value='" + criteria + list[i] + "'>" + list[i] + "</option>";
		}
	filter += "<select>";
	filter += "<button onclick=\""+command+"\" class=\"album_filter_button\">&gt;</button>";
	return filter;
	}

//--------------------------------------

function mboxAlbumFilterArtist(data,selected) {

	var command = "mboxAlbumAll_load(document.getElementById('filter_artist').value);";
	var filter   = "<select id='filter_artist' onchange=\""+command+"\" class=\"album_filter_dropdown\">"; 
	var criteria = "artist:";
	var list     = [];

	for (key in data) {
		artist = data[key]["artist"];
		if (list.indexOf(artist)<0) {
			list.push(artist);
			}
		}

	list.sort();
	filter += "<option></option>";
	for (var i=0;i<list.length;i++) {
		if (criteria+list[i] == selected) 	{ sel = " selected"; }
		else					{ sel = ""; }
		filter += "<option"+sel+" value='"+ criteria + list[i] + "'>" + list[i] + "</option>";
		}
	filter += "<select>";
	filter += "<button onclick=\""+command+"\" class=\"album_filter_button\">&gt;</button>";
	return filter;
	}


// List albums tracks of an album
//--------------------------------------

function mboxAlbumList(data) {

	var text 	  = "";
	//var albums        = data["answer"]["album"];
	//var track_list    = data["answer"]["tracks"];
	//console.log(data["DATA"]);	

	var albums        = data["DATA"]["_selected"];
	var uuid          = data["DATA"]["_selected_uuid"];
	var track_list    = data["DATA"]["tracks"];
	var album         = albums["album"];
	var artist        = albums["artist"];
	var default_cover = mbox_icon_dir + mbox_icons["album"]; //"img/cd2.png";

	var length = "";
	if (albums["albumlength"]) {
		length = " <font color='gray'>(" + convert_second2time(Math.round(albums["albumlength"])) + ")</font>";
		}

	// fill local playlist queue
	mbox_playlist_queue["type"]     = "album";
	mbox_playlist_queue["album"]    = albums;
	mbox_playlist_queue["scrollto"] = "scrollto_" + uuid.replace(/-/g,"");
	mbox_playlist_queue["tracks"]   = track_list;
	
	console.debug(mbox_playlist_queue);

	// Check if Cover exists
        var cover       = mboxCoverAlbum_new(uuid,albums);
        if (cover == "") { cover = default_cover; }

	console.log("album-id: "+albums["uuid"]+"/"+uuid + " ("+cover+")");

	// Write album cover
        var onclick    = "mboxCoverAlbum_alert(\""+cover+"\");";
	text += "<div id=\"scrollto2_"+uuid.replace(/-/g,"")+"\">";
	text += "<div class=\"album_cover\" style=\"background:url('"+cover+"');background-size:contain;background-position:center;background-repeat:no-repeat;\" onclick='" + onclick + "'>";
	text += "</div>";

	// write album infos
	text += "<div class=\"album_infos new\">";
	text +=   "<b>" + artist + "</b><br/><i>" + album + "</i><br/>";
	text +=   length;
	text += "</div>";
	text += mboxHtmlButton("delete",  "mboxViews_emptyBelow();mboxViews_hideTriangle(mbox_list_last);", "opac",   "small small2");

        // player control (in box)
	text += "<div class=\"album_control new\">";
	text += mboxPlayerControlEntry(uuid);
	text += mboxHtmlButton("info", "mboxAlbumInfo_load('"+uuid+"');", "red");
	text += mboxCardInfoIcon(albums, uuid);
	text += "</div>";
	text += "<div style=\"width:100%;float:left;\"><hr/></div>";

	// write tracks
	text += "<div class=\"album_tracks\">";
	var tracks 	= {}
	var i      	= 0;
	var a      	= 0;
	var withartist    = false;
	var withtrackinfo = false;

	// check, if compilation ... than show artist in row
	if (artist == "Compilation") { withartist = true; }

        // check, how many columns in the track list are required
	var mbox_list_count	= mboxListCount();
	var columns            = mbox_list_count/3;
	
	// prepare track list
	var sorted_tracks	= albums["tracks"];
	var show_num		= true;
	var max    		= albums["tracks"].length;
	if (Math.round(max/columns) < (max/columns)) { max += 1; }

	// check if more than one CD	
	var last_cd = "";
	for (var i=0;i<sorted_tracks.length;i++) {
		if ("disc_num" in track_list[sorted_tracks[i]]) {
			if (last_cd == "") { last_cd = track_list[sorted_tracks[i]]["disc_num"]; }
			if (last_cd != track_list[sorted_tracks[i]]["disc_num"]) { withtrackinfo = true; }
			}
		}
		
	// create rows in columns
	var row_number		= 0;
	for (var i=0;i<sorted_tracks.length;i++) {
		row_number++;
		var position = row_number-1;
		text += mboxAlbumTrackRow(id=sorted_tracks[i], dataTracks=track_list, album=show_num, artist=withartist, count=position, trackinfo=withtrackinfo);
		if (row_number == Math.round(max/columns)) 	{ text += "</div><div class=\"album_tracks\">"; }
		if (row_number == 2*Math.round(max/columns)) 	{ text += "</div><div class=\"album_tracks\">"; }
		}
		
	text += "</div>";
	text += "</div>";

	mboxAlbumWriteBelow(text);
	
	setTimeout(function(){
		document.getElementById("scrollto2_"+uuid.replace(/-/g,"")).scrollIntoView();
		window.scrollBy(0,-100);
		}, 1000);
	}

// album info as popup (incl. some settings ...)
//--------------------------------------

function mboxAlbumInfo_load(uuid) { appFW.requestAPI("GET",["data",uuid,"-"],"", mboxAlbumInfo ); }
function mboxAlbumInfo_close() { setTimeout(function(){ mboxAlbumAll_load(); }, 2000); appMsg.hide(); }
function mboxAlbumInfo(data) {

	var text   = "";
	var album  = data["DATA"]["_selected"];
	var uuid   = data["DATA"]["_selected_uuid"];

	var url    = RESTurl + "api/data/";
	var url2   = RESTurl + "api/data/";
	var size   = Math.round(album["albumsize"]/1024/1024*100)/100;
	var length = convert_second2time(Math.round(album["albumlength"]));
	var path   = album["albumpath"].replace(/\_/gi,"/");
	var cardid = album["card_id"]; 
	
	if (!cardid) { cardid = lang("CARD_NOT_CONNECTED"); } 
	else { cardid =  "<div onclick='mboxCardList_load(\""+cardid+"\");' style='cursor:pointer;'>" + cardid + "</a>" ; }

	var cover = "";
	if (album["cover_images"]) {
		cover += mboxCoverAlbumInfo(1, album["cover_images"]["track"],  album["cover_images"]["active"], uuid);
		cover += mboxCoverAlbumInfo(2, album["cover_images"]["dir"],    album["cover_images"]["active"], uuid);
		cover += mboxCoverAlbumInfo(3, album["cover_images"]["upload"], album["cover_images"]["active"], uuid);
		}
	else {	cover += lang("DATA_OLD_FORMAT");
		}

	var title  = album["album"];
	title      = title.replace( /\'/g, " " );
	title      = title.replace( /\"/g, "&quot;" );
	var artist = album["artist"];
	artist     = artist.replace( /\#/g, " " );
	artist     = artist.replace( /\"/g, "&quot;" );

	var edit  = "";
        edit += mboxHtmlButton("image_add",  "mboxUploadImage('"+uuid+"','album','"+title+"');",                "red");
        edit += mboxHtmlButton("delete",     "mboxAlbumDelete('"+artist+": "+title+"','"+uuid+"');", 	"red");

	text += "<b>" + lang("ALBUM") + " " + lang("INFORMATION") + "</b><br/>";

	text += mboxHtmlTableNew("start");
	text += "<tr><td colspan='2'><hr></td></tr>";
	text += mboxHtmlTableNew(["<i>" + lang("ALBUM") + ":", 		album["album"] ] );
	text += mboxHtmlTableNew(["<i>" + lang("BAND_ARTIST") + ":", 	album["artist"] ] );
	text += mboxHtmlTableNew(["<i>" + lang("GENRE") + ":", 		album["genres"] ] );
	text += mboxHtmlTableNew(["<i>" + lang("SIZE") + ":", 		size + " MByte / " + length + " min" ] );
	text += mboxHtmlTableNew(["<i>" + lang("ALBUM") + " Dir:", 	path ] );
//	text += mboxHtmlTableNew(["<i>" + lang("ALBUM") + " UUID:",	"<a href='" + url + uuid + "/-/' target='_blank'>" + uuid + "</a>" ] );
	text += mboxHtmlTableNew(["<i>" + lang("CARD_ID") + ":",	cardid ] );
	if ("error" in album) {
		text += mboxHtmlTableNew(["<i><font color='red'>Error:</font><i>", "<i><font color='red'>"+album["error"].length + " Errors - first: " + album["error"][0]+"</font></i>" ] );
		}
	text += mboxHtmlTableNew(["<i>" + lang("COVER_AVAILABLE") + ":",	cover ] );
	text += "<tr><td colspan='2'><hr></td></tr>";
	text += mboxHtmlTableNew(["<i>" + lang("EDIT") + ":",		edit ] );
	text += "<tr><td colspan='2'><hr></td></tr>";
	text += mboxHtmlTableNew("end");

	appMsg.confirm(text,"",450);
	}


// delete album
//--------------------------------------

function mboxAlbumDelete(title,uuid) {
	text    = lang("ALBUM_DELETE_ASK") + ":<br/><b>"+title+"</b>?";
	cmd     = "mboxAlbumDelete_exec('"+uuid+"','"+title+"')";
	appMsg.confirm(text,cmd,150,true);
	}
	
function mboxAlbumDelete_exec(uuid,title) {
	console.error("TEST "+uuid+" / "+title);
	appFW.requestAPI('DELETE',['data',uuid],'',[mboxAlbumDelete_msg,title]); //,"wait");
	}

function mboxAlbumDelete_msg(data,title) {
	mboxDataReturnMsg(data,lang("ALBUM_DELETED")+"<br/><b>"+title,lang("ALBUM_DELETE_ERROR")+"<br/><b>"+title);
        mboxAlbumAll_load();
        }


// track info as popup
//--------------------------------------

function mboxAlbumTrackInfo_load(uuid) { appFW.requestAPI("GET",["data",uuid,"-"],"", mboxAlbumTrackInfo ); }
function mboxAlbumTrackInfo(data) {

	var text   = "";
	var track  = data["DATA"]["_selected"];
	var uuid   = data["DATA"]["_selected_uuid"];

	var size   = Math.round(track["filesize"]/1024/1024*100)/100;
	var length = convert_second2time(Math.round(track["length"]));
	var path   = track["file"];
	var url    = RESTurl + "api/data/"+track["uuid"]+"/-/";
	var url1   = RESTurl + "api/data/"+track["album_uuid"]+"/-/";
	var url2   = "/mbox_music/";

	var msg_height = 400;
	if (appTheme == "dark") 	{ color = "yellow"; }
	else				{ color = "red"; }

	text += "<b>"+lang("TRACK_INFORMATION")+ "</b><br/>";
	
	if (track["artist"].indexOf("#error") == -1) {
		cover = "";
		if (track["cover_images"]) 	{ cover += mboxCoverAlbumInfo(1, track["cover_images"]["track"],  track["cover_images"]["active"], uuid); }
		else 				{ cover += lang("DATA_OLD_FORMAT"); }

		text += mboxHtmlTableNew("start");
		text += "<tr><td colspan='2'><hr></td></tr>";
		text += mboxHtmlTableNew(["<i>"+lang("TITLE")+":", 		track["title"] ] );
		text += mboxHtmlTableNew(["<i>"+lang("ALBUM")+":", 		track["album"] ] );
		text += mboxHtmlTableNew(["<i>"+lang("BAND_ARTIST")+":",	track["artist"] ] );
		text += mboxHtmlTableNew(["<i>"+lang("SIZE")+":", 		size + " MByte / " + length + " min" ] );
		text += mboxHtmlTableNew(["<i>"+lang("TRACK")+" Dir:", 	"<a href='" + url2 + path + "' target='_blank'>" + path + "</a>" ] );
		text += mboxHtmlTableNew(["<i>UUID "+lang("TRACK")+":",	"<a href='" + url  + "' target='_blank'>" + uuid + "</a>" ] );
		text += mboxHtmlTableNew(["<i>UUID "+lang("ALBUM")+":", 	"<a href='" + url1 + "' target='_blank'>" + track["album_uuid"] + "</a>" ] );
		if ("error" in track) {
			text += mboxHtmlTableNew(["<i><font color='"+color+"'>"+lang("ERROR")+":</font><i>", "<i><font color='"+color+"'>"+track["error"]+"</font></i>" ] );
			}
		text += mboxHtmlTableNew(["<i>"+lang("COVER_AVAILABLE")+":", cover ] );
		text += "<tr><td colspan='2'><hr></td></tr>";
		text += mboxHtmlTableNew("end");
		}
	else {
		text += mboxHtmlTableNew("start");
		text += "<tr><td colspan='2'><hr></td></tr>";

		text += mboxHtmlTableNew([lang("FILE")+":", 					"<a href='" + url2 + path + "' target='_blank'>" + path + "</a>" ] );
		text += mboxHtmlTableNew(["UUID "+lang("TRACK")+":",				"<a href='" + url  + "' target='_blank'>" + uuid + "</a>" ] );
		text += mboxHtmlTableNew(["<font color='"+color+"'>"+lang("ERROR")+":</font><i>", "<font color='"+color+"'>"+track["error"]+"</font></i>" ] );
		text += mboxHtmlTableNew(["Decoder:",						track["decoder"] ] );
				
		text += "<tr><td colspan='2'><hr></td></tr>";
		text += mboxHtmlTableNew("end");
		msg_height = 250;
		}

	appMsg.confirm(text,"",msg_height);
	}

// track title row
//--------------------------------------

function mboxAlbumTrackRow(id, dataTracks, album=true, artist=false, count=0, trackinfo=false) {
	var track    = dataTracks[id];
	var text     = "";
	var cmd      = "";
	var album_id = track["album_uuid"];

	var length = "";
	if (track["length"]) { length = " <font color='gray'>(" + convert_second2time(Math.round(track["length"])) + ")</font>"; }

	console.debug("Debug UUID: " + id + " / Album UUID: " + album_id + " / " + track["album"] + " / " + track["sort_pos"] + " / " + track["sort"]);

	cmd  += "<div class=\"album_tracks_control\">";

        //cmd += mboxHtmlButton("play",  "writeAudioPlayer('" + id + "','audioPlayer');", "green",   "small right");
	if (mbox_device != "remote") 	{
		cmd += mboxHtmlButton("play",  "mboxPlayerLocal(" + count + ");", "green",   "small right"); 
		}
	if (mbox_device != "local") 	{
		//cmd += mboxHtmlButton("play",  "appFW.requestAPI('GET',['play', '"+id+"'],'',mboxControl);", "blue", "small right");
		cmd += "<div class=\"player_active right\" id=\"playing3_"+id+"\" style=\"display:none;\"><img src=\"" + mbox_icon_dir + mbox_icons["playing"] + "\" style=\"width:10px;height:10px;margin:2px;\"></div>";
		cmd += mboxHtmlButton("play",  "appFW.requestAPI('GET',['play_position', '"+album_id+"', '"+count+"'],'',mboxControl);", "blue", "small right");
		}
	cmd  += "</div>";

	text += "<div class=\"album_tracks_title\">";

	// if track in album
	if (album) {
	
		text += "<table><tr><td style='width:20px;vertical-align:top;padding:0px'>";
		if ("sort_pos" in track)  { text += track["sort_pos"] + ". "; }

		var track_info = "";
		if (trackinfo) {
			if ("track_num" in track) { if (track["track_num"][0] > 0)	{ track_info += "Track " + track["track_num"][0]; }}
			if ("track_num" in track) { if (track["track_num"][1] > 0)	{ track_info += "/" + track["track_num"][1]; }}
			if ("disc_num" in track)  { if (track["disc_num"] > 0)	{ track_info += " - CD " + track["disc_num"] + " &nbsp; "; }}
			}
		
		var info = "<font color='gray'>" + track_info + length + "</font>";
		text += "</td><td>";
		text += "<div class='album_track_title_shorten' onclick='mboxAlbumTrackInfo_load(\"" + track["uuid"] + "\")' style='cursor:pointer;'>" + track["title"] + "</div>";
		if (artist) { text += "<div class='album_track_title_shorten'><i>"+track["artist"] + "</i></div>"; }
		text += "<div class='album_track_length'>" + info + "</div>";
		text += "</td></tr></table>";
		}
	// if track in playlist
	else {
		text += "<b>" +track["title"] + "</b>" + length + "<br/>";
		text += track["artist"] + "/";
		text += track["album"] + "<br/>";
		}
	text += "</div>";
	text += cmd;

	return text;
	}


// empty and reload
//--------------------------------------

function mboxAlbumEmptyAll() {
	setTextById("frame1","");
	}


// Write / delete details info below the album in the list
//----------------------------------------

function mboxAlbumEmptyBelow() {		// delete all infos from last loading
	var divID = "";
	for (var i=0;i<=mbox_list_amount;i++) {
		divID = "album_"+i;
		if (document.getElementById(divID)) {
			document.getElementById(divID).style.display = "none";
			setTextById(divID, "");
			}
		}
	for (var i=0;i<=mbox_list_char.length;i++) {
		divID = "album_"+mbox_list_char[i];
		if (document.getElementById(divID)) {
			document.getElementById(divID).style.display = "none";
			setTextById(divID, "");
			}
		}
	}


//--------------------------------------

function mboxAlbumWriteBelow(text) {		// write details to box below
	
	var divID = "";
	mboxAlbumEmptyBelow();			// delete old entries
	divID = "album_"+mbox_list_pos;		// write album info to next slot depending on width

	//console.log("--"divID+"--"+mbox_list_pos);
	if (document.getElementById(divID)) {
		document.getElementById(divID).style.display = "block";
		setTextById(divID, text);
		}

	mboxControlGroups();
	if (document.getElementById(divID)) { return divID; }
	}


//--------------------------------------
// EOF

