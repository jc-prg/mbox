//--------------------------------------
// jc://music-box/, (c) Christoph Kloth
//--------------------------------------
// show album list and details
//--------------------------------------
/* INDEX:
function mboxAlbumAll_load(filter="",uuid="")
function mboxAlbumAll_reload()
function mboxAlbumAll(data, uuid)
function mboxAlbumAll_filter(album_info,filters)
function mboxAlbumFilterPath(data,selected)
function mboxAlbumFilterArtist(data,selected)
function mboxAlbumList(data)
function mboxInfo_album_load(uuid)
function mboxAlbumInfo_load(uuid)
function mboxAlbumInfo_close()
function mboxAlbumInfo(data)
function mboxAlbumDelete(title,uuid)
function mboxAlbumDelete_exec(uuid,title)
function mboxAlbumDelete_msg(data,title)
function mboxAlbumTrackInfo_load(uuid)
function mboxAlbumTrackInfo(data)
*/
//--------------------------------------


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
	mboxViewsList(type="album", data=entries_info, selected_uuid=uuid, filter_key=the_filter, filter_text=filter, sort_keys=sort_keys, callTrackList="mboxViewsTrackList");
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

function mboxAlbumList(data)		{ mboxViewsTrackList(data, "album"); }
function mboxInfo_album_load(uuid)	{ mboxAlbumInfo_load(uuid); }

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


//--------------------------------------
// EOF

