//--------------------------------------
// jc://music-box/, (c) Christoph Kloth
//--------------------------------------
// show album list and details
//--------------------------------------
/* INDEX:
function mboxListCount()
function mboxListCount_New()
function mboxAlbumAll_load(filter="",uuid="")
function mboxAlbumAll_reload()
function mboxAlbumAll(data)
function mboxAlbumAll_chapter(count, title, last_title)
function mboxAlbumAll_empty(count,title)
function mboxAlbumAll_detail(count,title)
function mboxAlbumAll_album(count,uuid,title,description,cover,cmd_open,cmd_play)
function mboxAlbumFilterPath(data,selected)
function mboxAlbumFilterArtist(data,selected)
function mboxAlbumList_load(i,uuid)
function mboxAlbumList_load_direct(pos, i,uuid)
function mboxAlbumSortTracks(track_list,track_info)
function mboxAlbumList(data)
function mboxAlbumInfo_load(uuid)
function mboxAlbumInfo_close()
function mboxAlbumInfo(data)
function mboxAlbumDelete(title,uuid)
function mboxAlbumDelete_exec(uuid,title)
function mboxAlbumDelete_msg(data,title)
function mboxAlbumTrackInfo_load(uuid)
function mboxAlbumTrackInfo(data)
function mboxAlbumTrackRow(id,dataTracks,album=true,artist=false,count=0)
function mboxAlbumShowTriangle(i)
function mboxAlbumHideTriangle(i)
function mboxAlbumEmptyAll()
function mboxAlbumEmptyBelow()
function mboxAlbumWriteBelow(text)
*/
//--------------------------------------

var mbox_list_count  = 3;
var mbox_list_pos    = 0;
var mbox_list_load   = 0;
var mbox_list_amount = 0;
var mbox_list_last   = 0;
var mbox_list_char   = [];
var mbox_list_data   = {};

//--------------------------------------

function mboxListCount() {
	var width = document.body.clientWidth;
	var mbox_list_count;
	
	if (width > 1250)	{ mbox_list_count = 9; }
	else if (width > 705)	{ mbox_list_count = 6; }
	else			{ mbox_list_count = 3; }
	
	return mbox_list_count;
	}

function mboxListCount_New() {
	setTextById("mbox_temp","<div class=\"album_cover\" id=\"album_test_size\">test</div>" );
	var row_width       = document.getElementById("frame3").offsetWidth - 10; 		//width - 2x padding
	var album_width     = document.getElementById("album_test_size").offsetWidth + 6;	//width + 2x margin
	var max_albums      = Math.round(row_width/album_width);
	setTextById("mbox_temp","");
	return max_albums;
	}


// List albums
//--------------------------------------

function mboxAlbumAll_load(filter="",uuid="") {
		if (filter["UUID"]) 	{ filter = ">>"+filter["UUID"]; } 	// load after API call
		else 			{ filter = filter+">>"+uuid; }		// load by filter function
		appFW.requestAPI("GET",["db","album_info",filter], "", mboxAlbumAll,"","mboxAlbumAll");
		}

//--------------------------------------

function mboxAlbumAll_reload() {
	mboxAlbumAll(data=mbox_list_data);
	}
	
//--------------------------------------

function mboxAlbumAll(data) {

	//console.log(data);

	if (!data) { return; } // unclear, why sometimes no data are returned ...

	var text             = "";
	var print            = mboxCoverListStart();
	var default_cover    = mbox_icon_dir + mbox_icons["album"];
	var album_info       = data["DATA"]["album_info"];
	var album_active     = "";
	var album_active_no  = 0;
	var last_chapter     = "";
	mbox_mode            = 'Album'; 

	// fill global cache for reload on window resize
	mbox_list_data = data;

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
	filter += mboxHtmlTableNew("start",true,"310px");
	filter += mboxHtmlTableNew(["<i>"+lang("CATEGORY")+":", 	mboxAlbumFilterPath(album_info,filters) ], ["90px","210px"] );	
	filter += mboxHtmlTableNew("end");
	filter += "</div><div class='album_filter'>";
	filter += mboxHtmlTableNew("start",true,"310px","");
	filter += mboxHtmlTableNew(["<i>"+lang("BAND_ARTIST")+":", 	mboxAlbumFilterArtist(album_info,filters) ], ["90px","210px"] );
	filter += mboxHtmlTableNew("end");
	filter += "</div>";

	setTextById("frame2",filter);

	// set data to place detailviews etc.
	var album_in_row     = 0;
	var album_sub_rows   = 0;
	var albums_per_row   = mboxListCount_New();
	var album_next_empty = false;
	var row_per_chapter  = false;	
	if (albums_per_row >= 9) {
		row_per_chapter = true;
		}
	var chapter_detail  = 0;
	var chapter_number  = 0;
	var new_row         = false;
	var new_sub_row     = false;
	
	// mboxAlbumAll_chapter() -> Chapter, starting with first character of e.g. artist
	// mboxAlbumAll_empty()   -> Empty box, if row per chapter
	// mboxAlbumAll_detail()  -> Album detail, to be filled when clicked on album (position dependend on rows)
	// mboxCoverAlbum_new()   -> Album cover
	// mboxAlbumAll_album()   -> Embedded album cover with tool tips etc.

	// Sort entries (by artist)
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
	var i              = 1;
	var album_per_row  = 0;
	if (sorted_entries.length == 0) { text += "<div>" + lang("NODATA_RELOAD") + "</div>"; }
	for (var a=0;a<sorted_entries.length;a++) {

		var cover   = default_cover;
		var keys    = sorted_entries[a].split("||");
		var uuid    = keys[3];
		var album   = keys[2];
		var artist  = keys[1];
		var chapter = keys[0].substring(0,1);
		var text1   = "";
		var print1  = "";
		
		var album_line          = false;
		var album_detail        = false;
		var album_empty         = false;
		var album_character	 = false;
		var album_detail_last   = false;
		var album_detail_next   = false;
		var album_detail_number = 0;
		
		var isvalidfilter	 = false;
		var mbox_list_count	 = mboxListCount();  /// REMOVE LATER

		if (a == sorted_entries.length-1) { album_detail_last = true; }
		if (the_filter[0] in album_info[uuid] && album_info[uuid][the_filter[0]].indexOf(the_filter[1]) > -1) { isvalidfilter = true; }
		if (filters == "" || isvalidfilter) {
		
// letzter Eintrag mit row_per_chapter == true
// mehrzeilige Einträge mit row_per_chapter == true
		
			// check if new row without chapters
			if (mbox_show_char == false) {
				if (Math.round(a+1/albums_per_row) == (a+1/albums_per_row))	{ new_row = true;  }
				else								{ new_row = false; }			
				}

			// print cover with charakter and empty album, if new line per chapter
			else {
				if (last_chapter != chapter) {
					i++;
					chapter_number++;	
					album_character = true;
					if (row_per_chapter)		{
						album_in_row    = 1;	
						album_sub_rows  = 1;
						new_row         = true; 
						new_sub_row     = false;	
						}
					if (row_per_chapter && a > 1)	{ 
						album_line      = true; 
						album_detail    = true; 
						}
					}
				else {
					album_in_row++;
					new_row      = false;
					new_sub_row  = false;
					if (album_next_empty)						{ album_next_empty = false; album_empty = true; album_detail = true; chapter_number++; }
					if (row_per_chapter && album_in_row+1 == albums_per_row)	{ album_in_row = 1; album_next_empty = true; }
					}

				if (row_per_chapter == false) {
					album_detail_number = (Math.trunc((i-1)/albums_per_row)+1) * albums_per_row;
					//console.log(album_detail_number);
					}
				}
			
			if (a == sorted_entries.length) { album_detail_number = i; }
			if (album_detail)		{ text += mboxAlbumAll_detail( chapter_number-1, last_chapter ); }
			if (album_empty)	 	{ text += mboxAlbumAll_empty(  chapter_number, chapter ); }
			if (album_line)		{ text += "<hr style='float:left;width:99%;border:#aaa solid 0.5px;'/>"; }
			if (album_character)		{ text += mboxAlbumAll_chapter( chapter_number, chapter, last_chapter ); text += mboxHtmlEntryDetail( i-1 ); }
			
			//.............
			
			var onclick_play  = "appFW.requestAPI('GET',['play', '" + uuid + "'],'',mboxControl);"; 	// play album remote
			var onclick_open  = "mboxAlbumList_load('" + album_detail_number + "','" + uuid + "');"; 	// load album details
			
			if (row_per_chapter) {
				chapter_number_x = chapter_number;
				onclick_open  = "mboxAlbumList_load_direct('" + chapter + "_" + chapter_number_x + "','" + i + "','" + uuid + "');"; 				// load album details
				}
				
			if (uuid == album_active) { album_active_no = i; }
			if (uuid) {
				cover           = mboxCoverAlbum_new( uuid, album_info );  // Check if Cover exists
				[text1, print1] = mboxAlbumAll_album( i, uuid, album, artist, cover, onclick_open, onclick_play );
				if (text1 != "") { i++; text += text1; print += print1; }  // text = album list; print is cover for print out
				}

			//.............
			
			if (album_detail_last)	{ text += mboxAlbumAll_detail( chapter_number, chapter ); }

			last_chapter = chapter;
			}

		mbox_list_amount = i;
		}
	text  += mboxAlbumAll_detail(chapter_detail,last_chapter);
	print += mboxCoverListEnd();

	setTextById("frame3", text);
	setTextById("ontop", print);

	mboxControlToggleFilter_show();

	if (album_active && album_active != "") {
		mboxAlbumList_load(album_active_no,album_active);
		document.getElementById('scrollto_'+album_active.replace(/-/g,"")).scrollIntoView();
		}
	}


// chapter list entry
//---------------------------------------------------------

function mboxAlbumAll_chapter(count, title, last_title) {

	var text     = "";
	var cover    = mbox_icon_dir + mbox_icons["album"];
	act_char    = title.substring(0,1);
	last_title += " ";
	last_char   = last_title.substring(0,1);

	text += "<div class=\"album_cover character\" style=\"background:url(" + cover + ");\">";
	text += "<div class=\"album_sort\">" + act_char + "</div>";
	text += "</div>";
	text += "<div class=\"album_detail\" id=\"album_" + count + "\" style=\"display:none\">test " + count + " / " + document.body.clientWidth + "</div>";

	return text;
	}
	
function mboxAlbumAll_empty(count,title) {
	var act_char  = title.substring(0,1);
	var text      = "";
	text += "<div class=\"album_cover empty\"></div>";
	return text;
	}
	
function mboxAlbumAll_detail(count,title) {
	var act_char  = title.substring(0,1);
	mbox_list_char.push(act_char + "_" + count);
	var text      = "";
	text += "<div class=\"album_detail\" id=\"album_" + act_char + "_" + count + "\" style=\"display:none\">test " + count + " / " + document.body.clientWidth + "</div>";
	return text;
	}

// album list entry
//---------------------------------------------------------

function mboxAlbumAll_album(count,uuid,title,description,cover,cmd_open,cmd_play) {

	var text  = "";
	var print = "";

	text += mboxHtmlScrollTo( "start", uuid );
	text += mboxHtmlToolTip(  "start" );

	// write cover
	text += mboxCoverList( uuid, cover, "<b>"+title+"</b><br/>"+description, cmd_open, cmd_play, "album" );
	if (cover != "") { print += mboxCoverListEntry( uuid, cover ); }

	// write tooltip
	text += mboxHtmlToolTip(  "end", count, "<b>" + title + ":</b> " + description );
	text += mboxHtmlScrollTo( "end" );
	text += mboxHtmlEntryDetail( count );

	return [text, print];
	}



//--------------------------------------

function mboxAlbumFilterPath(data,selected) {

	var command  = "mboxAlbumAll_load(document.getElementById('filter_album').value);";
	var filter   = "<select id='filter_album' onchange=\""+command+"\"  class=\"album_filter_dropdown\">"; 
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



// Load data albums and list ...
//--------------------------------------

function mboxAlbumList_load(i,uuid) {

	// calculate which <DIV> is the right last in this row (to show in the next row) ... responsive design
	var count = 3;
	var mbox_list_count = mboxListCount();

	mbox_list_pos = ((Math.floor((i-1)/mbox_list_count)+1) * mbox_list_count );
	if (mbox_list_pos >= mbox_list_amount) { mbox_list_pos = mbox_list_amount-1; }

	// show connecting triangle
	mboxAlbumShowTriangle(i);
	mbox_list_last = i;

	// Load Album into the calculated DIV
	appFW.requestAPI("GET",["data",uuid,"-"],"", mboxAlbumList );
	}

//--------------------------------------

function mboxAlbumList_load_direct(pos, i,uuid) {

	// define position where to show album details
	mbox_list_last = i;
	mbox_list_pos  = pos;

	// show connecting triangle
	mboxAlbumShowTriangle(i);

	// Load Album into the calculated DIV
	appFW.requestAPI("GET",["data",uuid,"-"],"", mboxAlbumList );
	}

// sort list of albums tracks by track number, if every track has a number
//--------------------------------------

function mboxAlbumSortTracks(track_list,track_info) {

	var a         = 0;
	var b         = 0;
	var dont_sort = false;
	var use_disc  = false;
	
	for (var i=0;i<track_list.length;i++) {
		if ("track_num" in track_info[track_list[i]]) {
			if (track_info[track_list[i]]["track_num"][0]) { a++; }
			if (track_info[track_list[i]]["disc_num"])     { b++; }
			}
		}
		
	if (a != track_list.length) 	{ dont_sort = true; }
	if (b > 0)			{ use_disc = true; }

	if (a == track_list.length) {
	
		// sort by "track_num"
		var sort_tracks   = [];
		var sorted_tracks = [];
		var album         = {};
		
		for (var x in track_info) {
			if (track_list.includes(x)) {
				var mykey;
				
				if (use_disc)	{ mykey = (track_info[x]["disc_num"] * 100) + track_info[x]["track_num"][0]; }
				else		{ mykey = track_info[x]["track_num"][0]; }
				
				sort_tracks.push(mykey);
				if (album[mykey] != undefined)	{ dont_sort = true; }
				else				{ album[mykey] = track_info[x]["uuid"]; } 
			}	}

		sort_tracks.sort(sortNumber);
		
		for (var i=0;i<sort_tracks.length;i++) {
			if (album[sort_tracks[i]]) {
				sorted_tracks.push(album[sort_tracks[i]]);
			}	}
			
		if (sorted_tracks.length == track_list.length && dont_sort == false)  {
			console.debug("...1"); 
			return sorted_tracks;
			}
		else						{ 
			// return unsorted list		
			console.debug("...2: "+sorted_tracks.length+"/"+track_list.length); 
			return track_list;
			}
 		}
	if (dont_sort) {
		// return unsorted list
		console.debug("...3: "+a+"/"+track_list.length); 
		return track_list;
		}
	}


// List albums tracks of an album
//--------------------------------------

function mboxAlbumList(data) {

	var text 	  = "";
	//var albums        = data["answer"]["album"];
	//var track_list    = data["answer"]["tracks"];

	console.log(data["DATA"]);
	

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

	// Check if Cover exists
        var cover       = mboxCoverAlbum_new(uuid,albums);
        if (cover == "") { cover = default_cover; }

	console.log("album-id: "+albums["uuid"]+"/"+uuid + " ("+cover+")");

	// Write album cover
        var onclick    = "mboxCoverAlbum_alert(\""+cover+"\");";
	text += "<div id=\"scrollto2_"+uuid.replace(/-/g,"")+"\">";
	text += "<div class=\"album_cover\" style=\"background:url("+cover+");background-size:contain;background-position:center;background-repeat:no-repeat;\" onclick='" + onclick + "'>";
	text += "</div>";

	// write album infos
	text += "<div class=\"album_infos new\">";
	text +=   "<b>" + artist + "</b><br/><i>" + album + "</i><br/>";
	text +=   length;
	text += "</div>";
	text += mboxHtmlButton("delete",  "mboxAlbumEmptyBelow();mboxAlbumHideTriangle(mbox_list_last);", "opac",   "small small2");

        // player control (in box)
	text += "<div class=\"album_control new\">";

	if (mbox_device != "local") {
		text += "<div class=\"player_active big\" id=\"playing_"+uuid+"\" style=\"display:none;\"><img src=\"" + mbox_icon_dir + mbox_icons["playing"] + "\" style=\"height:20px;width:20px;margin:2px;\"></div>";
        	text += mboxHtmlButton("play",  "appFW.requestAPI('GET',['play', '" + uuid + "'],'',mboxControl);",	"blue");
		text += mboxHtmlButton("pause", "appFW.requestAPI('GET',['pause'],'',mboxControl);",		"blue");
        	text += mboxHtmlButton("stop",  "appFW.requestAPI('GET',['stop'],'',mboxControl);",			"blue");
		text += mboxHtmlButton("empty");
		}
	if (mbox_device != "remote") {
        	text += mboxHtmlButton("play",  "mboxPlayerLocal();",	"green");
        	text += mboxHtmlButton("pause", "mboxPlayer.pause();",	"green");
        	text += mboxHtmlButton("stop",  "mboxPlayer.stop();",	"green");
        	//text += mboxHtmlButton("next",  "mboxHtmlShowDataObject(mbox_playlist_queue);",	"green");
	        text += mboxHtmlButton("empty");
		}

	var album1  = album.replace(/'/g,"\\'");
	var artist1 = artist.replace(/'/g,"\\'");

        text += mboxHtmlButton("info",  "mboxAlbumInfo_load('"+uuid+"');",                         "red");

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

	// write tracks
	text += "<div class=\"album_tracks\">";
	var tracks 	= {}
	var i      	= 0;
	var a      	= 0;
	var withartist	= false;

	// check, if compilation ... than show artist in row
	if (artist == "Compilation") { withartist = true; }

        // check, how many columns in the track list are required
	var mbox_list_count	= mboxListCount();
	var columns            = mbox_list_count/3;
	
	// prepare track list
	var sorted_tracks	= mboxAlbumSortTracks( albums["tracks"], track_list );
	var show_num		= true;
	var max    		= albums["tracks"].length;
	if (Math.round(max/columns) < (max/columns)) { max += 1; }
	
	var count		= 0;
	for (var i=0;i<sorted_tracks.length;i++) {
		count++;
		text += mboxAlbumTrackRow(sorted_tracks[i],track_list,show_num,withartist,count-1);
		if (count == Math.round(max/columns)) 	{ text += "</div><div class=\"album_tracks\">"; }
		if (count == 2*Math.round(max/columns)) 	{ text += "</div><div class=\"album_tracks\">"; }
		}
		
	text += "</div>";
	text += "</div>";

	//setTextById("frame1",text);
	mboxAlbumWriteBelow(text);

	setTimeout(function(){
		document.getElementById("scrollto2_"+uuid.replace(/-/g,"")).scrollIntoView();
		window.scrollBy(0,-70);
		}, 2000);
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
	var url1   = RESTurl + "api/data/"+track["uuid_album"]+"/-/";
	var url2   = "/mbox_music/";


	text += "<b>"+lang("TRACK_INFORMATION")+ "</b><br/>";
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
	text += mboxHtmlTableNew(["<i>UUID "+lang("ALBUM")+":", 	"<a href='" + url1 + "' target='_blank'>" + track["uuid_album"] + "</a>" ] );
	if ("error" in track) {
		text += mboxHtmlTableNew(["<i><font color='red'>"+lang("ERROR")+":</font><i>", "<i><font color='red'>"+track["error"]+"</font></i>" ] );
		}
	text += mboxHtmlTableNew(["<i>"+lang("COVER_AVAILABLE")+":", cover ] );
	text += "<tr><td colspan='2'><hr></td></tr>";
	text += mboxHtmlTableNew("end");

	appMsg.confirm(text,"",400);
	}

// track title row
//--------------------------------------

function mboxAlbumTrackRow(id,dataTracks,album=true,artist=false,count=0) {
	var track    = dataTracks[id];
	var text     = "";
	var cmd      = "";
	var album_id = track["uuid_album"];

	var length = "";
	if (track["length"]) {
		length = " <font color='gray'>(" + convert_second2time(Math.round(track["length"])) + ")</font>";
		}

	//console.log(id);

	cmd  += "<div class=\"album_tracks_control\">";

        //cmd += mboxHtmlButton("play",  "writeAudioPlayer('" + id + "','audioPlayer');", "green",   "small right");
	if (mbox_device != "remote") 	{
		cmd += mboxHtmlButton("play",  "mboxPlayerLocal(" + count + ");", "green",   "small right"); 
		}
	if (mbox_device != "local") 	{
		//cmd += mboxHtmlButton("play",  "appFW.requestAPI('GET',['play', '"+id+"'],'',mboxControl);", "blue", "small right");
		cmd += mboxHtmlButton("play",  "appFW.requestAPI('GET',['play_position', '"+album_id+"', '"+count+"'],'',mboxControl);", "blue", "small right");
		cmd += "<div class=\"player_active right\" id=\"playing3_"+id+"\" style=\"display:none;\"><img src=\"" + mbox_icon_dir + mbox_icons["playing"] + "\" style=\"width:10px;height:10px;margin:2px;\"></div>";
		}
	cmd  += "</div>";

	text += "<div class=\"album_tracks_title\">";

	// if track in album
	if (album) {
		text += "<table><tr><td style='width:20px;vertical-align:top;padding:0px'>";
		if ("disc_num" in track) {
			if (track["disc_num"] > 0) {
				length = "<font color='gray'>CD " + track["disc_num"] + "&nbsp; </font>" + length;
			}	}
		if ("track_num" in track) {
			if (track["track_num"][0] > 0) {
				text += track["track_num"][0] + ". ";
			}	}
		text += "</td><td>";
		text += "<div class='album_track_title_shorten' onclick='mboxAlbumTrackInfo_load(\"" + track["uuid"] + "\")' style='cursor:pointer;'>" + track["title"] + "</div>";
		if (artist) { text += "<div class='album_track_title_shorten'><i>"+track["artist"] + "</i></div>"; }
		text += "<div class='album_track_length'>" + length + "</div>";
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


// show / hide triangle of active album
//----------------------------------------

function mboxAlbumShowTriangle(i) {
	elementVisible("album_tri1_"+i);
	elementVisible("album_tri2_"+i);
	mboxAlbumHideTriangle(mbox_list_last);
	}

function mboxAlbumHideTriangle(i) {
	elementHidden("album_tri1_"+i);
	elementHidden("album_tri2_"+i);
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

