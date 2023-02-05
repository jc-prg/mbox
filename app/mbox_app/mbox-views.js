//--------------------------------------
// jc://music-box/, (c) Christoph Kloth
//--------------------------------------
// views for all media types
//--------------------------------------

var mbox_list_count  = 3;
var mbox_list_pos    = 0;
var mbox_list_load   = 0;
var mbox_list_amount = 0;
var mbox_list_last   = 0;
var mbox_list_char   = [];
var mbox_list_data   = {};


function mboxViewsCalcRowEntries() {

	setTextById("mbox_temp","<div class=\"album_cover\" id=\"album_test_size\">test</div>" );
	var row_width       = document.getElementById("frame3").offsetWidth - 10; 		//width - 2x padding
	var album_width     = document.getElementById("album_test_size").offsetWidth + 6;	//width + 2x margin
	var max_albums      = Math.round(row_width/album_width);
	setTextById("mbox_temp","");
	return max_albums;
	}

function mboxViewsList_load(data,type) {
	if (data["LOAD"]["UUID"]) { var loaded_uuid = data["LOAD"]["UUID"]; }
	else                      { var loaded_uuid = ""; }
	
	if (type == "album")         { mboxAlbumAll_load(filter="",uuid=loaded_uuid); }
	else if (type == "playlist") { mboxPlaylists_load(filter="",playlist_uuid=loaded_uuid) ; }
	else if (type == "radio")    { mboxStreams_load(stream_uuid=loaded_uuid); }
	else                         { }
	
	//console.log(data);
	}

function mboxViewsList(type, data, selected_uuid="", filter_key="", filter_html="", sort_keys=[], callTrackList="", chapter_rows=true) {

	var text             = "";
	var print            = mboxCoverListStart();
	var default_cover    = mbox_icon_dir + mbox_icons[type];
	
	var entry_info       = data;
	var entry_active     = selected_uuid;
	var last_chapter     = "";
	var entry_active_no1 = 0;
	var entry_active_no2 = 0;
	
	mbox_mode            = type; 
	mbox_cover_list      = [];		// reset cover list (to show cover of all albums, playlists, ...)

	// preset for vars to place detailviews etc.
	var entry_in_row     = 0;
	var entry_next_empty = false;
	var entries_per_row  = mboxViewsCalcRowEntries();
	var entries_total    = 0;
	var row_per_chapter  = false;	
	if (entries_per_row >= 9 && chapter_rows) { row_per_chapter = true; }
	var chapter_detail   = 0;
	var chapter_number   = 0;
	var chapter_total    = 0;
	
	// sort entries ... define keys in sort_keys=[]
	var sorted_entries = [];
	for (var key in entry_info) {
		var sort_string = "";
		for (var i=0;i<sort_keys.length;i++) {
			if (i==0) { sort_string += entry_info[key][sort_keys[0]].toUpperCase() + "||"; }		
			sort_string    += entry_info[key][sort_keys[i]] + "||";
			}
		sort_string    += key;
		sorted_entries.push( sort_string );
		}
	sorted_entries.sort();
	
	// filter entries
	var filtered_entries = [];
    for (var a=0;a<sorted_entries.length;a++) {
        var keys           = sorted_entries[a].split("||");
        var uuid           = keys[sort_keys.length+1];
        var isvalidfilter  = false;
        if (filter_key[0] != "search") {

            if (entry_info[uuid] && filter_key[0] in entry_info[uuid] && entry_info[uuid][filter_key[0]].indexOf(filter_key[1]) > -1)
                { isvalidfilter = true; }
            }
        else {
            var search_text = filter_key[1].toLowerCase();
            if (entry_info[uuid] && entry_info[uuid]["title"] && entry_info[uuid]["title"].toLowerCase().includes(search_text))
                { isvalidfilter = true; }
            if (entry_info[uuid] && entry_info[uuid]["album"] && entry_info[uuid]["album"].toLowerCase().includes(search_text))
                { isvalidfilter = true; }
            if (entry_info[uuid] && entry_info[uuid]["artist"] && entry_info[uuid]["artist"].toLowerCase().includes(search_text))
                { isvalidfilter = true; }
            }

        if (filter_key == "" || isvalidfilter) {
            filtered_entries.push( sorted_entries[a] );
            }
        }
	if (filtered_entries != sorted_entries) { isvalidfilter = true; }
	
	// count chapters based on first character
	var chapter_last = "";
	for (var a=0;a<filtered_entries.length;a++) {
		var chapter     = filtered_entries[a].substring(0,1);
		if (chapter != chapter_last) { chapter_total += 1; chapter_last = chapter;}
		}
	entries_total = filtered_entries.length;
	if (mbox_show_char) { entries_total += chapter_total; }
	
	// list albums
	var i              = 1;
	if (filtered_entries.length == 0) { text += "<div>" + lang("NODATA_RELOAD") + "</div>"; }
	else { for (var a=0;a<filtered_entries.length;a++) {
	
		var keys        = filtered_entries[a].split("||");
		var chapter     = keys[0].substring(0,1);
		var uuid        = keys[sort_keys.length+1];		
		var title       = keys[1];
		var description = "";
		if (keys.length > 3) {description = keys[2];}
		
		var entry_line          = false;
		var entry_detail        = false;
		var entry_empty         = false;
		var entry_character	    = false;
		var entry_detail_last   = false;
		var entry_detail_number = 0;
		
		if (a == filtered_entries.length-1) { entry_detail_last = true; }

		if (filter_key == "" || isvalidfilter) {
			
			// check if new row without chapters
			if (mbox_show_char == false) {}

			// print cover with character and empty album, if new line per chapter
			else {
				if (last_chapter != chapter) { // && isvalidfilter == false) {
					i++;
					chapter_number++;	
					entry_character         = true;
					if (row_per_chapter) {
						entry_in_row    = 1;	
						}
					if (row_per_chapter && a >= 1) { 
						entry_line      = true; 
						entry_detail    = true; 
						}
					}
				else {
					entry_in_row++;
					if (row_per_chapter && entry_in_row == entries_per_row) { 
						entry_in_row     = 1;
						entry_next_empty = true;
						}
					if (entry_next_empty) { 
						entry_next_empty = false; 
						entry_empty      = true; 
						entry_detail     = true; 
						chapter_number++;
						}
					}
				if (row_per_chapter == false) {
					entry_detail_number = (Math.trunc((i-1)/entries_per_row)+1) * entries_per_row;
					}
				}
			if (entry_detail_number > entries_total)	{ entry_detail_number = entries_total; }
			
			if (entry_detail)    { text += mboxViewsDetail( chapter_number-1, last_chapter ); }
			if (entry_empty)     { text += mboxViewsEmpty(  chapter_number, chapter ); }
			if (entry_line)      { text += "<hr style='float:left;width:99%;border:#aaa solid 0.5px;'/>"; }
			if (entry_character) { text += mboxViewsChapter( chapter_number, chapter, last_chapter ); text += mboxHtmlEntryDetail( i-1 ); }
			
			// define commands	
			var cmd_play = "appFW.requestAPI('GET',['play', '" + uuid + "'],'',mboxControl);";
			if (row_per_chapter) { var cmd_open = "mboxViewsLoadDetails('" + chapter + "_" + chapter_number + "','" + i + "','" + uuid + "',"+callTrackList+",'"+type+"');"; }
			else                 { var cmd_open = "mboxViewsLoadDetails('" + entry_detail_number + "',"+i+",'" + uuid + "',"+callTrackList+",'"+type+"');"; }
			
			// check if podcast (images loaded from URL if internet is available)
        		if (entry_info[uuid] && entry_info[uuid]["podcast"] && entry_info[uuid]["podcast"]["title"]) { entry_info[uuid]["cover_images"] = entry_info[uuid]["podcast"]["cover_images"]; }

			// print entry
			var text1, print1;
			var cover = mboxCoverAlbum_new( uuid, entry_info );
			[text1, print1] = mboxViewsEntry(count=i, uuid=uuid, title=title, description=description, cover=cover, cmd_open=cmd_open, cmd_play=cmd_play);
			if (text1 != "") { i++; text += text1; print += print1; }

			// check if active entry to be loaded in the end
			if (row_per_chapter && uuid == entry_active)	{ entry_active_no1 = chapter + "_" + chapter_number; entry_active_no2 = i; }
			else if (uuid == entry_active)		{ entry_active_no1 = entry_detail_number;            entry_active_no2 = i; }

			if (entry_detail_last)	{ text += mboxViewsDetail( chapter_number, chapter ); }		
			}
			
		last_chapter = chapter;
		mbox_list_amount = i;
		} }

	// add box to add playlist or stream
	if (type != "album") {		
		if (type == "radio") 		{ var onclick  = "mboxStreamAdd_dialog(\"ADD_ENTRY\");"; }
		else if (type == "playlist")	{ var onclick  = "mboxPlaylistAdd_dialog(\"ADD_ENTRY\");"; }
		text += "<hr style='float:left;width:99%;border:#aaa solid 0.5px;'/>"; 
		text += mboxCoverSeparator( "<img src=\""+mbox_icon_dir+"add_"+type+".png\" style=\"height:50px;width:50px;margin-top:10px;\">", onclick );
		text += mboxHtmlEntryDetail('ADD_ENTRY');
		}
				
	text  += mboxViewsDetail(chapter_number+1,last_chapter);
	print += mboxCoverListEnd();

	setTextById("frame3", text);
	setTextById("ontop",  print);

	// set and show filter if defined
	if (filter_html != "RELOAD") { setTextById("frame2", filter_html); }
	if (filter_html == "")	     { mboxControlToggleFilter(false); }
	else                         { mboxControlToggleFilter(true); }

	// load track list, if uuid is defined
	if (entry_active && entry_active != "" && entry_active != "-") {	
		if (typeof entry_active_no1 == 'string' || entry_active_no1 instanceof String) { entry_active_no1 = "\""+entry_active_no1+"\""; }
		if (typeof entry_active_no2 == 'string' || entry_active_no2 instanceof String) { entry_active_no2 = "\""+entry_active_no2+"\""; }
		
		cmd   ='mboxViewsLoadDetails(pos='+entry_active_no1+', i='+entry_active_no2+', uuid=\"'+entry_active+'\", callTrackList='+callTrackList+', type=\"'+type+'\");';
		console.debug(cmd);
		eval(cmd);
		document.getElementById("scrollto_"+entry_active.replace(/-/g,"")).scrollIntoView();
		}
	}

function mboxViewsChapter(count, title, last_title) {

	var text     = "";
	var cover    = mbox_icon_dir + mbox_icons["album"];
	act_char    = title.substring(0,1);
	last_title += " ";
	last_char   = last_title.substring(0,1);

    cover = cover.replace("'", "\\'");
	text += "<div class=\"album_cover character\" style=\"background:url('" + cover + "');\">";
	text += "<div class=\"album_sort\">" + act_char + "</div>";
	text += "</div>";

	return text;
	}
	
function mboxViewsEmpty(count,title) {
	var act_char  = title.substring(0,1);
	var text      = "";
	text += "<div class=\"album_cover empty\"></div>";
	return text;
	}
	
function mboxViewsDetail(count,title) {
	var act_char  = title.substring(0,1);
	mbox_list_char.push(act_char + "_" + count);
	var text      = "";
	text += "<div class=\"album_detail\" id=\"album_" + act_char + "_" + count + "\" style=\"display:none\">test " + count + " / " + document.body.clientWidth + "</div>";
	return text;
	}

function mboxViewsEntry(count, uuid, title, description, cover, cmd_open, cmd_play) {

	var text  = "";
	var print = "";

	text += mboxHtmlScrollTo( "start", uuid );
	text += mboxHtmlToolTip(  "start" );

	// check if error	
	if (title.indexOf("#error") >= 0) {
		title = "<font color='"+mbox_color[appTheme]["warning"]+"'>" + title + "</font>";
		}
	 
	// write cover
	text += mboxCoverList( uuid, cover, "<b>"+title+"</b><br/>"+description, cmd_open, cmd_play, "album" );
	if (cover != "") { print += mboxCoverListEntry( uuid, cover ); }

	// write tooltip
	text += mboxHtmlToolTip(  "end", count, "<b>" + title + ":</b> " + description );
	text += mboxHtmlScrollTo( "end" );
	text += mboxHtmlEntryDetail( count );

	return [text, print];
	}

function mboxViewsLoadDetails(pos, i, uuid, callTrackList, type) {

	// define position where to show album details
	mbox_list_last = i;
	mbox_list_pos  = pos;
	
	// in case type is not given, identify type from uuid
	if (type == undefined) {
		if (uuid.indexOf("r_") > -1) { type = "radio"; }
		if (uuid.indexOf("a_") > -1) { type = "album"; }
		if (uuid.indexOf("p_") > -1) { type = "playlist"; }		
		}

	// show connecting triangle
	mboxViewsShowTriangle(i);

	// Load Album into the calculated DIV
	console.log("mboxViewsLoadDetails: "+type);
	appFW.requestAPI("GET",["data",uuid,"-"], "", [callTrackList, type] );
	}

function mboxViewsTrackListHeader(uuid, type, entry, title, description, length) {

	var text          = "";
	var length        = "";
	var default_cover = mbox_icon_dir + mbox_icons[type]; // "album" -> type

	// Format length if exists
	if (entry["albumlength"]) {
		length = " <font color='gray'>(" + convert_second2time(Math.round(entry["albumlength"])) + ")</font>";
		}

	// Check if Cover exists
        var cover       = mboxCoverAlbum_new(uuid,entry);
	var onclick     = "mboxCoverAlbum_alert(\""+cover+"\");";
        if (cover == "") { cover = default_cover; onclick = ""; }

	// Write album cover
    cover = cover.replace("'", "\\'");
	text += "<div id=\"scrollto2_"+uuid.replace(/-/g,"")+"\">";
	text += "<div class=\"album_cover\" style=\"background:url('"+cover+"');background-size:contain;background-position:center;background-repeat:no-repeat;\" onclick='" + onclick + "'>";
	text += "</div>";

	// write album infos
	text += "<div class=\"album_infos new\">";
	text += "<b>" + title + "</b> <font color='#383838'><i>["+type+"]</i></font>";
	text += "<br/><i>" + description + "</i><br/>";
	text += length;
	text += "</div>";
	text += mboxHtmlButton("delete",  "mboxViewsEmptyBelow();mboxViewsHideTriangle(mbox_list_last);mbox_last_uuid='';", "opac",   "small small2");

        // player control (in box)
	text += "<div class=\"album_control new\">";
	text += "<div class=\"player_active big\" id=\"playing_"+uuid+"\" style=\"display:none;\"><img src=\""+mbox_icon_dir+mbox_icons["playing"]+"\" style=\"height:20px;width:20px;margin:2px;\"></div>";
	text += mboxPlayerControlEntry(uuid);
	text += mboxHtmlButton("info", "mboxViews_Info('"+uuid+"','"+type+"');", "red");
	text += mboxCardInfoIcon(entry, uuid);
	text += "</div>";
	text += "<div style=\"width:100%;float:left;\"><hr/></div>";
	
	return text;
	}

function mboxViews_Info(uuid, type) {
	if (type == "album")         { mboxAlbumInfo_load(uuid); }
	else if (type == "playlist") { mboxPlaylistInfo_load(uuid); }
	else if (type == "radio")    { mboxStreamInfo_load(uuid); }
	}

function mboxViews_InfoTable(title, info_data, height) {

	var text		= "";
	var table		= new jcTable("info_table");
	table.table_width	= "100%";
	table.columns		= 2;
	
	text += "<b>"+title+ "</b><br/>";	
	text += table.start();
	text += table.row_one("<hr/>");
	for (var i=0;i<info_data.length;i++) {
		if (info_data[i][0] == "LINE")	{ text += table.row_one("<hr/>"); }
		else					{ text += table.row( [ "<i>"+info_data[i][0]+":</i>", info_data[i][1] ] ); }
		}
	text += table.row_one("<hr/>");
	text += table.end();

	appMsg.confirm(text,"",height);
	}

function mboxViewsTrackList(data, type) {   


	var text         = "";
	var entry        = data["DATA"]["_selected"];				// albums -> entry
	var entry_uuid   = data["DATA"]["_selected_uuid"];
	var track_data   = data["DATA"]["tracks"];
	var track_list   = entry["tracks"];
	var track_list_complete = [];
	var track_list_album    = {};
	var track_info          = "";

	console.log("mboxViewsTrackList: "+type+"/"+entry_uuid);
	if (type == undefined) {
		if (entry_uuid.indexOf("r_") > -1) { type = "radio"; }
		if (entry_uuid.indexOf("a_") > -1) { type = "album"; }
		if (entry_uuid.indexOf("p_") > -1) { type = "playlist"; }		
		}

	mbox_last_uuid = entry_uuid;
	
	// set type specific title, description ... and for streams additional metadata
	if (type == "album") {
		var title		 = entry["artist"];
		var description	 = entry["album"];
		}
	else if (type == "playlist") {
		var title		 = entry["title"];
		var description	 = entry["description"];
		}
	else if (type == "radio" && entry["podcast"] && entry["podcast"]["title"]) {
		var podcast_keys = ["title","description","cover_images","stream_info","tracks","track_list"];
		for (var i=0;i<podcast_keys.length;i++) { entry[podcast_keys[i]] = entry["podcast"][podcast_keys[i]]; }
		var title		 = entry["title"];
		var description	 = entry["description"] + "<br/><i>("+entry["podcast"]["track_count"]+" Tracks)</i>";
		track_list		 = entry["track_list"];
		track_data		 = entry["tracks"];
		data["DATA"]["tracks"]  = entry["tracks"];
		}
	else if (type == "radio") {
		var title		 = entry["title"];
		var description	 = entry["description"];
		}

	// create playlist including all tracks from included albums --> albums & playlists
	for (var i=0;i<track_list.length;i++) {
		if (track_list[i].includes("t_")) { track_list_complete.push( track_list[i] ); }
		else if (track_list[i].includes("a_"))	{ 
			if (data["DATA"]["album_info"][track_list[i]]) {
				album_tracks = data["DATA"]["album_info"][track_list[i]]["tracks"];
				for (var j=0;j<album_tracks.length;j++) { track_list_complete.push( album_tracks[j] ); }
				track_list_album[track_list[i]] = album_tracks;
				}
			else {
				track_list_complete.push( track_list[i] );
				}
			}
		}
		
	// header for the detail view with tracks
	text += mboxViewsTrackListHeader(entry_uuid, type, entry, title, description);
	
	// podcast or stream info
	if (entry["stream_info"] && entry["stream_info"] != "") {
		text += "<center>"+lang("WEBSITE")+": <a href=\"" + entry["stream_info"] + "\" target=\"_blank\">"+ entry["stream_info"] + "</a>";
		text += "</center><div style=\"width:100%;float:left;\"><hr/></div>";
		}

        // count tracks & columns
        var columns          = Math.trunc( mboxViewsCalcRowEntries() / 3 );
        var track_list_local = [];
        var total_tracks     = track_list.length;
        
        for (var i=0; i < track_list.length;i++) {
        	if (track_list[i].includes("a_")) {
        		if (track_list_album && track_list_album[track_list[i]]) {
	        		total_tracks += track_list_album[track_list[i]].length;
	        		}
	        	Array.prototype.push.apply(track_list_local,track_list_album[track_list[i]]);
        		}
        	else {
	        	track_list_local.push(track_list[i]);
        		}
        	}
        total_tracks += 1;
        
	// fill local playlist queue
	console.log(track_list_local);
	mboxPlayerAdd2Queue(type, entry_uuid, entry, track_data, track_list_local);	

	// create columns for tracks
        for (var i=1; i <= columns; i++) { text += "<div class=\"album_tracks\" id=\"album_tracks"+i+"\"></div>"; }
	text += "<div class=\"album_tracks\">&nbsp;</div>";
	setTextById("album_tracks1","<center>&nbsp;<br/>Loading<br/>&nbsp;</center>");
	mboxViewsWriteBelow(text);
	
	// type specific settings
	var last_cd = "";
	if (type == "album") {
		var withartist    = false;
		var withtrackinfo = false;
		if (title == "Compilation") { withartist = true; }
		if (entry["sort_by_filename"] != true) { withtrackinfo = true; }
        for (var i=0;i<track_list.length;i++) {
            if (track_data[track_list[i]] && "disc_num" in track_data[track_list[i]]) {
                if (last_cd == "") { last_cd = track_data[track_list[i]]["disc_num"]; }
                if (last_cd != track_data[track_list[i]]["disc_num"]) { withtrackinfo = true; }
                }
            }
		}
	else {
		var withartist    = true;
		var withtrackinfo = true;
		}

	// create track list
	if (track_list.length > 0) {
	    setTimeout(function(){
		
		var title_num = track_list.length;
		for (var i=0; i < track_list.length;i++) { if (track_list_album[track_list[i]]) {
		 	if (track_list[i].includes("a_")) { title_num = title_num + track_list_album[track_list[i]].length; }
		 	} }
		 	
		var playlist_pos  = 0; // can differ to playlist_no if error (in playlist)
		var playlist_no   = 0;
		var color         = 1;
		var column_number = 0;
		var column_tracks = Math.round(total_tracks / columns);
		
		for (var i=0; i < track_list.length; i++) {
		
			// if entry is a track
			if (track_list[i].includes("t_")) {
				playlist_pos += 1;
				playlist_no  += 1;
				column_number = 1 + Math.trunc((playlist_pos-1) / column_tracks);		
				console.debug(column_number + " = " + playlist_pos + " / " + column_tracks);
				mboxViewsTrackListRow(data=data, uuid=track_list[i], type=type, column=column_number, uuid_pl=entry_uuid, count_pl=playlist_no, color="", 	withtrackinfo=withtrackinfo, withartist=withartist );
				}
				
			// if entry is an album
			else if (track_list[i].includes("a_")) {
				if (color == 1)	{ color = 3; }
				else			{ color = 1; }
				
				// if album exists search for tracks in the album
				if (track_list_album[track_list[i]]) {
					playlist_pos += 1;
					column_number = 1 + Math.trunc((playlist_pos-1) / column_tracks);				
					console.debug(column_number + " = " + playlist_pos + " / " + column_tracks);
					
					mboxViewsTrackListLine(column_number,color);
					mboxViewsTrackListRow(data=data, uuid=track_list[i], type=type, column=column_number, uuid_pl=entry_uuid, count_pl=playlist_no, color=(color+1));
					mboxViewsTrackListLine(column_number,color);
					
					var tracks_album1  = track_list_album[track_list[i]];
					var tracks_album2  = tracks_album1; // Album Sort server side
					
					for (var j=0;j<tracks_album2.length;j++) {
						playlist_pos += 1;
						playlist_no  += 1;
						column_number = 1 + Math.trunc((playlist_pos-1) / column_tracks);				
						console.debug(column_number + " = " + playlist_pos + " / " + column_tracks);
						
						mboxViewsTrackListRow(data=data, uuid=tracks_album2[j], type=type, column=column_number, uuid_pl=entry_uuid, count_pl=playlist_no);
						}
					mboxViewsTrackListLine(column_number, color);
					}
				// else just print entry (=> error message)
				else {
					playlist_pos += 1;
					column_number = 1 + Math.trunc((playlist_pos-1) / column_tracks);				
					console.debug(column_number + " = " + playlist_pos + " / " + column_tracks);
					
					mboxViewsTrackListRow(data=data, uuid=track_list[i], type=type, column=column_number, uuid_pl=entry_uuid, count_pl=playlist_no, color=(color+1));
					}
				}

				
			//console.log(i + " / " + track_list.length + " - " + split);
		} }, 1000); }
	else {
		setTextById("album_tracks","<center>&nbps;<br/>"+lang("PLAYLIST_EMPTY")+"<br/>&nbsp;</center>");
		}
		
	setTimeout(function(){
		document.getElementById("scrollto2_"+entry_uuid.replace(/-/g,"")).scrollIntoView();
		window.scrollBy(0,-100);
		}, 1000);			
	}

function mboxViewsTrackListLine(column=1, color="gray") {

	addTextById("album_tracks"+column, "<div class=\"album_tracks_line\"><hr style=\"color:"+mbox_track_color[color]+"\"/></div>");
	}

function mboxViewsTrackListRow( data, uuid, type, column, uuid_pl="", count_pl=0, color=0, withtrackinfo=true, withartist=true ) {

	var text       = "";
	var cmd        = "";
	var no         = column;
	var albuminfo  = data["DATA"]["album_info"];
	var trackinfo  = data["DATA"]["tracks"];
	
	// if track exists -> track information
        if (trackinfo && trackinfo[uuid]) {

		var track    = trackinfo[uuid];
		var position = count_pl - 1;

	        var length = "";
        	if (track["length"]) 	{ length = convert_second2time(Math.round(track["length"])); }
		if (track["duration"])	{ 
			if (track["duration"].indexOf(":") > -1)	{ length = track["duration"]; if (length.indexOf("00:") == 0) { length = length.replace("00:",""); } }
			else						{ length = convert_second2time(Math.round(track["duration"])); }
			}

		// Controls to play Track ...
		cmd += "<div class=\"album_tracks_control\"  style=\"background:"+mbox_track_color[color]+";\">";
		if (mbox_device == "local")	{ cmd += mboxHtmlButton("play",  "mboxPlayerLocal(" + position + ");", "green",   "small right"); }		 
		else 				{ cmd += mboxHtmlButton("play",  "appFW.requestAPI('GET',['play_position', '"+uuid_pl+"','"+position+"'],'',mboxControl);", "blue", "small right"); }
		cmd += "<div class=\"player_active right\" id=\"playing3_"+uuid+"\" style=\"display:none;\"><img src=\""+mbox_icon_dir+mbox_icons["playing"]+"\" style=\"width:10px;height:10px;margin:2px;\"></div>";
		cmd += "</div>";
		
		
		if (type == "album" || type == "playlist") {
			var onclick		= "mboxAlbumTrackInfo_load(\"" + uuid + "\")";
			var style_title	= "style='cursor:pointer;'";
			var class_description	= "";
			var title		= track["title"];
			var description	= "";
			var information        = "";
			if (withtrackinfo)	{ description += track["artist"] + "/" + track["album"] + "<br/>"; }
			else if (withartist)	{ description += track["artist"] + "<br/>"; }
			if (length)		{ information += " (" + length + ")"; }
			} 
		else if (type == "radio" || type == "podcast") {
			var onclick		= "mboxStreamTrackInfo_load(\"" + uuid_pl + "\", \"" + uuid + "\")";
			var style_title	= "style='cursor:pointer;'";
			var class_description	= "class='album_track_description_shorten'";
			var title		= track["title"];
			var description	= track["description"];
			var information        = "";
			if (track["publication"])	{ information += track["publication"] + " "; }
			if (length)			{ information += "(" + length + ")"; }
			} 
		else { 
			var onclick		= "";
			var style_title	= "";
			var class_description	= "";
			var title		= track["title"];
			var description	= "";
			var information        = "("+type+")";
			}

		// track
        	text += "<div class=\"album_tracks_title\"  style=\"background:" + mbox_track_color[color] + ";\">";
		text += "<table><tr><td style='width:20px;vertical-align:top;padding:0px'>" + count_pl + ".</td><td>";
		text += "<div class='album_track_title_shorten' onclick='" + onclick + "' " + style_title + "><b>" + title + "</b></div><br/>";
		text += "<div "+class_description+">" + description + "</div>";
		text += "<font color='gray'>" + information + "</font>";
		text += "</td></tr></table>";
		text += "</div>";

		// playing info and play button
        	text += cmd;
                }

	// if album exists -> album title
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
        	if (uuid.includes("a_"))	{ text += "<b style='color:"+mbox_color[appTheme]["warning"]+"'>"+lang("ALBUM")+" "+lang("NOT_FOUND")+"</b><br/>"; }
        	else				{ text += "<b style='color:"+mbox_color[appTheme]["warning"]+"'>"+lang("TRACK")+" "+lang("NOT_FOUND")+"</b><br/>"; }
		text += uuid;
       	text += "</div>" + cmd;
		}

	addTextById("album_tracks"+no,text);
        }

function mboxViewsShowTriangle(i) {
	elementVisible("album_tri1_"+i);
	elementVisible("album_tri2_"+i);
	for (var a=1;a<mbox_list_amount;a++) {
		if (a != i) {
			mboxViewsHideTriangle(a);
			}
		}
	}

function mboxViewsHideTriangle(i) {
	elementHidden("album_tri1_"+i);
	elementHidden("album_tri2_"+i);
	}

function mboxViewsEmptyAll() {

	setTextById("frame1","");
	}

function mboxViewsEmptyBelow() {		// delete all infos from last loading
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

function mboxViewsWriteBelow(text) {		// write details to box below
	
	var divID = "";
	mboxViewsEmptyBelow();			// delete old entries
	divID = "album_"+mbox_list_pos;		// write album info to next slot depending on width

	//console.log("--"divID+"--"+mbox_list_pos);
	if (document.getElementById(divID)) {
		document.getElementById(divID).style.display = "block";
		setTextById(divID, text);
		}

	mboxControlGroups();
	if (document.getElementById(divID)) { return divID; }
	}

