//--------------------------------------
// jc://music-box/, (c) Christoph Kloth
//--------------------------------------
// show album list and details
//--------------------------------------
/* INDEX:
function mboxEmptyBelow()
function mboxWriteBelow(text)
function mboxAlbumAllLoad(filter="",uuid="")
function mboxAlbumAll(data)
function mboxAlbumAll_section(count,title,last_title)
function mboxAlbumAll_album(count,uuid,title,description,cover,cmd_open,cmd_play)
function mboxCreateAlbumFilter(data,selected)
function mboxCreateArtistFilter(data,selected)
function mboxAlbumLoad(i,uuid)
function mboxListAlbum(data)
function mboxTrackInfoLoad(uuid)
function mboxTrackInfo(data)
function mboxAlbumInfoLoad(uuid)
function mboxAlbumInfoClose()
function mboxAlbumInfo(data)
function mboxAlbumDelete(album,uuid)
function mboxAlbumTrackRow(id,dataTracks,album=true,artist=false,count=0)
function show_triangle(i)
function hide_triangle(i)
function mboxEmptyAlbum()
*/
//--------------------------------------

var mbox_list_count  = 3;
var mbox_list_pos    = 0;
var mbox_list_load   = 0;
var mbox_list_amount = 0;
var mbox_list_last   = 0;


// Write / delete details info below the album in the list
//----------------------------------------

function mboxEmptyBelow() {		// delete all infos from last loading
	var divID = "";
	for (var i=0;i<=mbox_list_amount;i++) {
		divID = "album_"+i;
		if (document.getElementById(divID)) {
			document.getElementById(divID).style.display = "none";
			setTextById(divID, "");
			}
		}
	}

//--------------------------------------

function mboxWriteBelow(text) {		// write details to box below
	
	var divID = "";
	mboxEmptyBelow();			// delete old entries
	divID = "album_"+mbox_list_pos;		// write album info to next slot depending on width

	//console.log("--"divID+"--"+mbox_list_pos);
	if (document.getElementById(divID)) {
		document.getElementById(divID).style.display = "block";
		setTextById(divID, text);
		}

	mboxWriteGroups();
	if (document.getElementById(divID)) { return divID; }
	}


// List albums
//--------------------------------------

function mboxAlbumAllLoad(filter="",uuid="") {
		if (filter["UUID"]) 	{ filter = ">>"+filter["UUID"]; } 	// load after API call
		else 			{ filter = filter+">>"+uuid; }		// load by filter function
		mboxApp.requestAPI("GET",["db","album_info",filter], "", mboxAlbumAll,"","mboxAlbumAll");
		}

//--------------------------------------

function mboxAlbumAll(data) {

	//console.log(data);

	if (!data) { return; } // unclear, why sometimes no data are returned ...

	var text             = "";
	var print            = mboxCoverListStart();
	var default_cover    = mbox_icons["album"];
	var album_info       = data["DATA"]["album_info"];
	var album_active     = "";
	var album_active_no  = 0;
	var last_chapter     = "";

	// reset cover list (to show cover of all albums, playlists, ...)
	mbox_cover_list   = [];

	// create filter
	if ("db_filter" in data["REQUEST"]) {
	        var filter_uuid     = data["REQUEST"]["db_filter"].split(">>");
		var filters         = filter_uuid[0];
		album_active        = filter_uuid[1];
		var the_filter      = filters.split(":");
		}
	else {	filters 	   = "";
		}

	var filter = "";
	filter += "<div class='album_filter'>";
	filter += mboxTableNew("start",true,"300px");
	filter += mboxTableNew(["<i>Kategorie:", 		mboxCreateAlbumFilter(album_info,filters) ], true );	
	filter += mboxTableNew("end");
	filter += "</div><div class='album_filter'>";
	filter += mboxTableNew("start",true,"300px");
	filter += mboxTableNew(["<i>Band / K&uuml;nstler:", 	mboxCreateArtistFilter(album_info,filters) ], true );
	filter += mboxTableNew("end");
	filter += "</div>";

	setTextById("remote4",filter);

	// ..................................

	var sorted_entries = [];
	for (var key in album_info) {
		var sort_string = "";
		sort_string    += album_info[key]["artist"].toUpperCase() + "||";
		sort_string    += album_info[key]["artist"] + "||";
		sort_string    += album_info[key]["album"]  + "||";
		sort_string    += key;
		sorted_entries.push( sort_string );
		}
	sorted_entries.sort();

	// list albums
	var i = 1;
	if (sorted_entries.length == 0) { text += "<div>" + lang("NODATA_RELOAD") + "</div>"; }
		
	for (var a=0;a<sorted_entries.length;a++) {

		var keys    = sorted_entries[a].split("||");
		var uuid    = keys[3];
		var album   = keys[2];
		var artist  = keys[1];
		var chapter = keys[0];
		var text1   = "";
		var print1  = "";
		var isvalidfilter = false;

		if (the_filter[0] in album_info[uuid] && album_info[uuid][the_filter[0]].indexOf(the_filter[1]) > -1) { isvalidfilter = true; }

		if (filters == "" || isvalidfilter) {

			// print cover with charakter ...
			if (mbox_show_char) {
				if (last_chapter != chapter) {
					text1 = mboxAlbumAll_section(i,chapter,last_chapter);
					if (text1 != "") { i++; text += text1; }
					}
				last_chapter = chapter;
				}

			//console.log("SORT: "+sorted_artists[key].substring(0,1)+"_"+sorted_artists[key]+"/"+sorted_albums[key2]);
			var onclick_open  = "mboxAlbumLoad('" + i + "','" + uuid + "');"; 				// load album details
		        var onclick_play  = "mboxApp.requestAPI('GET',['play', '" + uuid + "'],'',mboxControl);"; 	// play album remote
			var cover    	  = default_cover;

			if (uuid == album_active) { album_active_no = i; }
			if (uuid) {
				cover           = mboxCoverAlbum_new(uuid,album_info);         // Check if Cover exists
				[text1, print1] = mboxAlbumAll_album(i,uuid,album,artist,cover,onclick_open,onclick_play);
				if (text1 != "") { i++; text += text1; print += print1; }   // text = album list; print is cover for print out
				}
			}
			//if (Number.isInteger(a / 6)) { setTextById("remote2",text); }
		mbox_list_amount = i;
		}
	print += mboxCoverListEnd();

	setTextById("remote2",text);
	setTextById("ontop",print);

	if (album_active && album_active != "") {
		mboxAlbumLoad(album_active_no,album_active);
		document.getElementById('scrollto_'+album_active.replace(/-/g,"")).scrollIntoView();
		}
	}


// chapter list entry
//---------------------------------------------------------

function mboxAlbumAll_section(count,title,last_title) {

	var text     = "";
	var cover    = mbox_icons["album"];
	act_char    = title.substring(0,1);
	last_title += " ";
	last_char   = last_title.substring(0,1);

	if (act_char && act_char != last_char) {
		text += "<div class=\"album_cover character\" style=\"background:url(" + cover + ");\">";
		text += "<div class=\"album_sort\">" + act_char + "</div>";
		text += "</div>";
		text += "<div class=\"album_detail\" id=\"album_" + count + "\" style=\"display:none\">test " + count + " / " + document.body.clientWidth + "</div>";
		}

	return text;
	}

// album list entry
//---------------------------------------------------------

function mboxAlbumAll_album(count,uuid,title,description,cover,cmd_open,cmd_play) {

	var text  = "";
	var print = "";

	text += mboxScrollTo( "start", uuid );
	text += mboxToolTip(  "start" );

	// write cover
	text += mboxCoverList( uuid, cover, "<b>"+title+"</b><br/>"+description, cmd_open, cmd_play, "album" );
	if (cover != "") { print += mboxCoverListEntry( uuid, cover ); }

	// write tooltip
	text += mboxToolTip(  "end", count, "<b>" + title + ":</b> " + description );
	text += mboxScrollTo( "end" );
	text += mboxAlbumDetail( count );

	return [text, print];
	}



//--------------------------------------

function mboxCreateAlbumFilter(data,selected) {

	var filter   = "<select id='filter_album' onchange=\"mboxAlbumAllLoad(document.getElementById('filter_album').value);\"  class=\"album_filter_dropdown\">"; 
	var criteria = "albumpath:";
	var list     = [];

	for (key in data) {
		path = data[key]["albumpath"].split("_");
		if (path.length > 0 && list.indexOf(path[1])==-1) {
			list.push(path[1]);
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
	return filter;
	}

//--------------------------------------

function mboxCreateArtistFilter(data,selected) {

	var filter   = "<select id='filter_artist' onchange=\"mboxAlbumAllLoad(document.getElementById('filter_artist').value);\" class=\"album_filter_dropdown\">"; 
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
	return filter;
	}



// Load data albums and list ...
//--------------------------------------

function mboxAlbumLoad(i,uuid) {

	// calculate which <DIV> is the right last in this row (to show in the next row) ... responsive design
	var count = 3;
	var width = document.body.clientWidth;
	if (width > 705) { mbox_list_count = 6; }
	else		 { mbox_list_count = 3; }

	mbox_list_pos = ((Math.floor((i-1)/mbox_list_count)+1) * mbox_list_count );
	if (mbox_list_pos >= mbox_list_amount) { mbox_list_pos = mbox_list_amount-1; }

	// show connecting triangle
	show_triangle(i);
	mbox_list_last = i;

	// Load Album into the calculated DIV
	mboxApp.requestAPI("GET",["data",uuid,"-"],"", mboxListAlbum );
	}


// List albums tracks of an album
//--------------------------------------

function mboxListAlbum(data) {

	var text 	  = "";
	//var albums        = data["answer"]["album"];
	//var track_list    = data["answer"]["tracks"];

	console.log(data["DATA"]);

	var albums        = data["DATA"]["_selected"];
	var uuid          = data["DATA"]["_selected_uuid"];
	var track_list    = data["DATA"]["tracks"];
	var album         = albums["album"];
	var artist        = albums["artist"];
	var default_cover = mbox_icons["album"]; //"img/cd2.png";

	var length = "";
	if (albums["albumlength"]) {
		length = " <font color='gray'>(" + convert_second2time(Math.round(albums["albumlength"])) + ")</font>";
		}

	// fill local playlist queue
	mbox_playlist_queue["type"]     = "album";
	mbox_playlist_queue["album"]    = albums;
	mbox_playlist_queue["scrollto"] = "scrollto_" + uuid.replace(/-/g,"");
	mbox_playlist_queue["tracks"]   = track_list;

	// Check if Cover exists
        var cover  = mboxCoverAlbum_new(uuid,albums);
        if (cover == "") { cover = default_cover; }

	console.log("album-id: "+albums["uuid"]+"/"+uuid + " ("+cover+")");

	// Write album cover
	text += "<div id=\"scrollto2_"+uuid.replace(/-/g,"")+"\">";
	text += "<div class=\"album_cover\" style=\"background:url("+cover+");background-size:contain;background-position:center;background-repeat:no-repeat;\" onclick='" + onclick + "'>";
	text += "</div>";

	// write album infos
	text += "<div class=\"album_infos new\">";
	text +=   "<b>" + artist + "</b><br/><i>" + album + "</i><br/>";
	text +=   length;
        text += "</div>";
        text += mboxButton("delete",  "mboxEmptyBelow();hide_triangle(mbox_list_last);", "opac",   "small small2");

        // player control (in box)
	text += "<div class=\"album_control new\">";

	if (mbox_device != "local") {
		text += "<div class=\"player_active big\" id=\"playing_"+uuid+"\" style=\"display:none;\"><img src=\""+mbox_icons["playing"]+"\" style=\"height:20px;width:20px;margin:2px;\"></div>";
        	text += mboxButton("play",  "mboxApp.requestAPI('GET',['play', '" + uuid + "'],'',mboxControl);", "blue");
	        text += mboxButton("pause", "mboxApp.requestAPI('GET',['pause'],'',mboxControl);",                     "blue");
        	text += mboxButton("stop",  "mboxApp.requestAPI('GET',['stop'],'',mboxControl);",                      "blue");
	        text += mboxButton("empty");
		}
	if (mbox_device != "remote") {
        	text += mboxButton("play",  "localPlayer();",                      	"green");
        	text += mboxButton("pause", "mboxPlayer.pause();",                      "green");
        	text += mboxButton("stop",  "mboxPlayer.stop();",                      "green");
        	//text += mboxButton("next",  "show_data_object(mbox_playlist_queue);",	"green");
	        text += mboxButton("empty");
		}

	var album1  = album.replace(/'/g,"\\'");
	var artist1 = artist.replace(/'/g,"\\'");

        text += mboxButton("info",  "mboxAlbumInfoLoad('"+uuid+"');",                         "red");

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

	// write tracks
	text += "<div class=\"album_tracks\">";
	var tracks 	= {}
	var i      	= 0;
	var a      	= 0;
	var max    	= albums["tracks"].length;
	var withartist	= false;

	// check, if compilation ... than show artist in row
	if (artist == "Compilation") { withartist = true; }

	// count tracks with order number
	for (var key in albums["tracks"]) {
		//console.log(albums["tracks"][key])
		tracks[key] = track_list[albums["tracks"][key]];
		a++;
		if ("track_num" in tracks[key]) {
			if (tracks[key]["track_num"][0]) { i++; }
			}
		}

	// if not so much order numbers as entries, dont sort
	if (i != a) {
		var count = 0;
		for (var key in albums["tracks"]) {
			count++;
			text += mboxAlbumTrackRow(albums["tracks"][key],track_list,true,withartist,count-1);
			if (count == Math.round(max/2)) { text += "</div><div class=\"album_tracks\">"; }
			}
		}

	// else sort titles
	else {
		var sort_t = [];
		var album  = {};
		for (var x in tracks) {
			//console.log(tracks[x]["track_num"][0] + "_" + tracks[x]["uuid"]);
			var mykey = tracks[x]["track_num"][0];
			sort_t.push(mykey);
			album[mykey] = tracks[x]["uuid"];
			}
		sort_t.sort(sortNumber);
		count = 0;
		for (var key in sort_t) {
			count++;
			text += mboxAlbumTrackRow(album[sort_t[key]],track_list,true,withartist,count-1);
			if (count == Math.round(max/2)) { text += "</div><div class=\"album_tracks\">"; }
			}

		}

	text += "</div>";
	text += "</div>";

	//setTextById("remote1",text);
	mboxWriteBelow(text);

	setTimeout(function(){
		document.getElementById("scrollto2_"+uuid.replace(/-/g,"")).scrollIntoView();
		window.scrollBy(0,-70);
		}, 2000);
	}


// track info as popup
//--------------------------------------

function mboxTrackInfoLoad(uuid) { mboxApp.requestAPI("GET",["data",uuid,"-"],"", mboxTrackInfo ); }
function mboxTrackInfo(data) {

	var text   = "";
	var track  = data["DATA"]["_selected"];
	var uuid   = data["DATA"]["_selected_uuid"];

	var size   = Math.round(track["filesize"]/1024/1024*100)/100;
	var length = convert_second2time(Math.round(track["length"]));
	var path   = track["file"];
	var url    = RESTurl + "api/data/"+track["uuid"]+"/-/";
	var url1   = RESTurl + "api/data/"+track["uuid_album"]+"/-/";
	var url2   = "/mbox_music/";


	text += "<b>Track Informationen</b><br/>";
	cover = "";
	if (track["cover_images"]) 	{ cover += mboxCoverAlbumInfo(1, track["cover_images"]["track"],  track["cover_images"]["active"], uuid); }
	else 				{ cover += lang("DATA_OLD_FORMAT"); }

	text += mboxTableNew("start");
	text += "<tr><td colspan='2'><hr></td></tr>";
	text += mboxTableNew(["<i>Title:", 		track["title"] ] );
	text += mboxTableNew(["<i>Album:", 		track["album"] ] );
	text += mboxTableNew(["<i>Interpret:", 		track["artist"] ] );
	text += mboxTableNew(["<i>Gr&ouml;&szlig;e:", 	size + " MByte / " + length + " min" ] );
	text += mboxTableNew(["<i>Track Dir:", 		"<a href='" + url2 + path + "' target='_blank'>" + path + "</a>" ] );
	text += mboxTableNew(["<i>UUID:",	 	"<a href='" + url + "' target='_blank'>" + uuid + "</a>" ] );
	text += mboxTableNew(["<i>UUID Album:", 	"<a href='" + url1 + "' target='_blank'>"    + track["uuid_album"] + "</a>" ] );
	if ("error" in track) {
		text += mboxTableNew(["<i><font color='red'>Error:</font><i>", "<i><font color='red'>"+track["error"]+"</font></i>" ] );
		}
	text += mboxTableNew(["<i>Verf&uuml;gbare Cover:",	cover ] );
	text += "<tr><td colspan='2'><hr></td></tr>";
	text += mboxTableNew("end");

	appMsg.confirm(text,"",400);
	}

// album info as popup (incl. some settings ...)
//--------------------------------------

function mboxAlbumInfoLoad(uuid) { mboxApp.requestAPI("GET",["data",uuid,"-"],"", mboxAlbumInfo ); }
function mboxAlbumInfoClose() { setTimeout(function(){ mboxAlbumAllLoad(); }, 2000); appMsg.hide(); }
function mboxAlbumInfo(data) {

	var text   = "";
	var album  = data["DATA"]["_selected"];
	var uuid   = data["DATA"]["_selected_uuid"];

	var url    = RESTurl + "api/data/";
	var url2   = RESTurl + "api/data/";
	var size   = Math.round(album["albumsize"]/1024/1024*100)/100;
	var length = convert_second2time(Math.round(album["albumlength"]));
	var cardid = album["card_id"]; if (!cardid) { cardid = "Keine Karte verkn&uuml;pft."; } else { cardid =  "<a href='" + url2 + cardid + "/' target='_blank'>" + cardid + "</a>" ; }
	var path   = album["albumpath"].replace(/\_/gi,"/");

	var cover = "";
	if (album["cover_images"]) {
		cover += mboxCoverAlbumInfo(1, album["cover_images"]["track"],  album["cover_images"]["active"], uuid);
		cover += mboxCoverAlbumInfo(2, album["cover_images"]["dir"],    album["cover_images"]["active"], uuid);
		cover += mboxCoverAlbumInfo(3, album["cover_images"]["upload"], album["cover_images"]["active"], uuid);
		}
	else {	cover += lang("DATA_OLD_FORMAT");
		}

	var edit = "";
        edit += mboxButton("image_add",  "mboxUploadImage('"+uuid+"','album','"+album["album"]+"');",                "red");
        edit += mboxButton("delete", "mboxAlbumDelete('"+album["artist"]+": "+album["album"]+"','"+uuid+"');", 	"red");


	text += "<b>Album " + lang("INFORMATION") + "</b><br/>";

	text += mboxTableNew("start");
	text += "<tr><td colspan='2'><hr></td></tr>";
	text += mboxTableNew(["<i>Album:", 		album["album"] ] );
	text += mboxTableNew(["<i>Interpret:", 		album["artist"] ] );
	text += mboxTableNew(["<i>Genres:", 		album["genres"] ] );
	text += mboxTableNew(["<i>Gr&ouml;&szlig;e:", 	size + " MByte / " + length + " min" ] );
	text += mboxTableNew(["<i>Album Dir:", 		path ] );
	text += mboxTableNew(["<i>UUID:",	 		"<a href='" + url + uuid + "/-/' target='_blank'>" + uuid + "</a>" ] );
	text += mboxTableNew(["<i>Card ID:",		cardid ] );
	if ("error" in album) {
		text += mboxTableNew(["<i><font color='red'>Error:</font><i>", "<i><font color='red'>"+album["error"].length + " Errors - first: " + album["error"][0]+"</font></i>" ] );
		}
	text += mboxTableNew(["<i>Verf&uuml;gbare Cover:",	cover ] );
	text += "<tr><td colspan='2'><hr></td></tr>";
	text += mboxTableNew(["<i>Bearbeiten:",		edit ] );
	text += "<tr><td colspan='2'><hr></td></tr>";
	text += mboxTableNew("end");

	appMsg.confirm(text,"",450);
	}


// delete album
//--------------------------------------

function mboxAlbumDelete(album,uuid) {
	//var cmd = "window.open('http://192.168.1.27:5006/mbox/album/delete/"+uuid+"/');";

	var cmd = "mboxApp.requestAPI('DELETE',['data', '" + uuid + "'],'', mboxDataReturnMsg ); mboxAlbumAllLoad();";
	appMsg.confirm("&nbsp;<br/>Album &quot;<b>"+album+"</b>&quot; wirklich aus der Datenbank löschen?<br/>&nbsp;<br/>(ID: "+uuid+")", cmd, 200);
	//alert("test");
	}

// track title row
//--------------------------------------

function mboxAlbumTrackRow(id,dataTracks,album=true,artist=false,count=0) {
	var track  = dataTracks[id];
	var text   = "";
	var cmd    = "";

	var length = "";
	if (track["length"]) {
		length = " <font color='gray'>(" + convert_second2time(Math.round(track["length"])) + ")</font>";
		}

	//console.log(id);

	cmd  += "<div class=\"album_tracks_control\">";

        //cmd += mboxButton("play",  "writeAudioPlayer('" + id + "','audioPlayer');", "green",   "small right");
	if (mbox_device != "remote") 	{
		cmd += mboxButton("play",  "localPlayer(" + count + ");", "green",   "small right"); 
		}
	if (mbox_device != "local") 	{
		cmd += mboxButton("play",  "mboxApp.requestAPI('GET',['play', '"+id+"'],'',mboxControl);", "blue", "small right");
		cmd += "<div class=\"player_active right\" id=\"playing3_"+id+"\" style=\"display:none;\"><img src=\""+mbox_icons["playing"]+"\" style=\"width:10px;height:10px;margin:2px;\"></div>";
		}
	cmd  += "</div>";

	text += "<div class=\"album_tracks_title\">";

	// if track in album
	if (album) {
		text += "<table><tr><td style='width:20px;vertical-align:top;padding:0px'>";
		if ("track_num" in track) {
			if (track["track_num"][0] > 0) {
				text += track["track_num"][0] + ". ";
			}	}
		text += "</td><td>";
		text += "<div class='album_track_title_shorten' onclick='mboxTrackInfoLoad(\"" + track["uuid"] + "\")' style='cursor:pointer;'>" + track["title"] + "</div>";
		if (artist) { text += "<div class='album_track_title_shorten'><i>"+track["artist"] + "</i></div>"; }
		text += "<div class='album_track_length'>" + length + "</div>";
		text += "</td></tr></table>";
		}
	// if track in playlist
	else {
		text += "<b>" +track["title"] + "</b>" + length + "<br/>";
		text += track["artist"] + "/";
		text += track["album"];
		}
	text += "</div>";
	text += cmd;

	return text;
	}


// show / hide triangle of active album
//----------------------------------------

function show_triangle(i) {
	elementVisible("album_tri1_"+i);
	elementVisible("album_tri2_"+i);
	hide_triangle(mbox_list_last);
	}

function hide_triangle(i) {
	elementHidden("album_tri1_"+i);
	elementHidden("album_tri2_"+i);
	}


// empty and reload
//--------------------------------------

function mboxEmptyAlbum() {
	setTextById("remote1","");
	}

//--------------------------------------
// EOF

