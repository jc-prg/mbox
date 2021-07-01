//--------------------------------------
// jc://music-box/, (c) Christoph Kloth
//--------------------------------------
// views for all media types
//--------------------------------------
/* INDEX:
function mboxListCount_New()
function mboxViews_list(type, data, selected_uuid="", filter_key="", filter_text="", sort_keys=[], callTrackList="")
function mboxViews_chapter(count, title, last_title)
function mboxViews_empty(count,title)
function mboxViews_detail(count,title)
function mboxViews_entry(count, uuid, title, description, cover, cmd_open, cmd_play)
function mboxViews_loadDetails(pos, i, uuid, callTrackList)
function mboxViews_showTriangle(i)
function mboxViews_hideTriangle(i)
function mboxViews_emptyAll()
function mboxViews_emptyBelow()
function mboxViews_writeBelow(text)
*/
//--------------------------------------

var mbox_list_count  = 3;
var mbox_list_pos    = 0;
var mbox_list_load   = 0;
var mbox_list_amount = 0;
var mbox_list_last   = 0;
var mbox_list_char   = [];
var mbox_list_data   = {};

// Define Lists per row
//--------------------------------------

function mboxListCount_New() {
	setTextById("mbox_temp","<div class=\"album_cover\" id=\"album_test_size\">test</div>" );
	var row_width       = document.getElementById("frame3").offsetWidth - 10; 		//width - 2x padding
	var album_width     = document.getElementById("album_test_size").offsetWidth + 6;	//width + 2x margin
	var max_albums      = Math.round(row_width/album_width);
	setTextById("mbox_temp","");
	return max_albums;
	}

// List media
//--------------------------------------

function mboxViews_list(type, data, selected_uuid="", filter_key="", filter_text="", sort_keys=[], callTrackList="") {

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

	// set data to place detailviews etc.
	var entry_in_row     = 0;
	var entry_next_empty = false;
	var entries_per_row   = mboxListCount_New();
	var row_per_chapter  = false;	
	if (entries_per_row >= 9) {
		row_per_chapter = true;
		}
	var chapter_detail  = 0;
	var chapter_number  = 0;
	
	// Sort entries ... define keys in sort_keys=[]
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
	
	// list albums
	var i              = 1;
	if (sorted_entries.length == 0) { text += "<div>" + lang("NODATA_RELOAD") + "</div>"; }
	for (var a=0;a<sorted_entries.length;a++) {
	
		var keys        = sorted_entries[a].split("||");
		var chapter     = keys[0].substring(0,1);
		var uuid        = keys[sort_keys.length+1];		
		var title       = keys[1];
		var description = "";
		if (keys.length > 3) {description = keys[2];}
		
		var entry_line          = false;
		var entry_detail        = false;
		var entry_empty         = false;
		var entry_character	 = false;
		var entry_detail_last   = false;
		var entry_detail_number = 0;
		
		if (a == sorted_entries.length-1) { entry_detail_last = true; }
		
		var isvalidfilter	 = false;
		if (filter_key[0] in entry_info[uuid] && entry_info[uuid][filter_key[0]].indexOf(filter_key[1]) > -1) { isvalidfilter = true; }

		if (filter_key == "" || isvalidfilter) {
			
			// check if new row without chapters
			if (mbox_show_char == false) {}

			// print cover with charakter and empty album, if new line per chapter
			else {
				if (last_chapter != chapter && isvalidfilter == false) {
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
			
			if (a == sorted_entries.length) { entry_detail_number = i; }
			
			if (entry_detail)		{ text += mboxViews_detail( chapter_number-1, last_chapter ); }
			if (entry_empty)	 	{ text += mboxViews_empty(  chapter_number, chapter ); }
			if (entry_line)		{ text += "<hr style='float:left;width:99%;border:#aaa solid 0.5px;'/>"; }
			if (entry_character)		{ text += mboxViews_chapter( chapter_number, chapter, last_chapter ); text += mboxHtmlEntryDetail( i-1 ); }
			
			//.............
			
			// FEHLER: wenn die letzte Reihe nicht vorständig ist, dann 'entry_detail_number' auf letztes Detail setzen ... hier nur letztes ...
			if (entry_detail_last)  { entry_detail_number = i; }	// if (a == sorted_entries.length-1) { entry_detail_last = true; }
										// wie letztes zu erwartendes Element vorher bestimmen?
					
			// define commands	
			var cmd_play = "appFW.requestAPI('GET',['play', '" + uuid + "'],'',mboxControl);";
			if (row_per_chapter)	{ var cmd_open = "mboxViews_loadDetails('" + chapter + "_" + chapter_number + "','" + i + "','" + uuid + "',"+callTrackList+");"; }
			else			{ var cmd_open = "mboxViews_loadDetails('" + entry_detail_number + "',"+i+",'" + uuid + "',"+callTrackList+");"; }
			
			// check if podcast (images loaded from URL if internet is available)
        		if (entry_info[uuid]["podcast"] && entry_info[uuid]["podcast"]["title"]) { entry_info[uuid]["cover_images"] = entry_info[uuid]["podcast"]["cover_images"]; }

			// print entry
			var text1, print1;
			var cover = mboxCoverAlbum_new( uuid, entry_info );
			[text1, print1] = mboxViews_entry(count=i, uuid=uuid, title=title, description=description, cover=cover, cmd_open=cmd_open, cmd_play=cmd_play);
			if (text1 != "") { i++; text += text1; print += print1; }

			// check if active entry to be loaded in the end
			if (row_per_chapter && uuid == entry_active)	{ entry_active_no1 = chapter + "_" + chapter_number; entry_active_no2 = i; }
			else if (uuid == entry_active)		{ entry_active_no1 = entry_detail_number;            entry_active_no2 = i; }
			//else						{ entry_active_no1 = 0;                              entry_active_no2 = 0; }

			//.............
			
			if (entry_detail_last)	{ text += mboxViews_detail( chapter_number, chapter ); }		
			}
			
		last_chapter = chapter;
		mbox_list_amount = i;
		}

	if (type != "Album") {		
		var onclick  = "mbox"+type+"Add_dialog(\"ADD_ENTRY\");";
		text += "<hr style='float:left;width:99%;border:#aaa solid 0.5px;'/>"; 
		text += mboxCoverSeparator( "<img src=\""+mbox_icon_dir+"add_"+type+".png\" style=\"height:50px;width:50px;margin-top:10px;\">", onclick );
		text += mboxHtmlEntryDetail('ADD_ENTRY');
		}
				
	text  += mboxViews_detail(chapter_number+1,last_chapter);
	print += mboxCoverListEnd();

	setTextById("frame3", text);
	setTextById("ontop",  print);

	if (filter_text != "") {
		setTextById("frame2", filter_text);
		mboxControlToggleFilter_show();
		}

	if (entry_active && entry_active != "") {	
		if (typeof entry_active_no1 == 'string' || entry_active_no1 instanceof String) { entry_active_no1 = "\""+entry_active_no1+"\""; }
		if (typeof entry_active_no2 == 'string' || entry_active_no2 instanceof String) { entry_active_no2 = "\""+entry_active_no2+"\""; }
		
		cmd   ='mboxViews_loadDetails(pos='+entry_active_no1+', i='+entry_active_no2+', uuid=\"'+entry_active+'\", callTrackList='+callTrackList+');';
		console.log(cmd);
		eval(cmd);
		//console.log(error);
		document.getElementById('scrollto_'+entry_active.replace(/-/g,"")).scrollIntoView();
		}
	}


// chapter list entry
//---------------------------------------------------------

function mboxViews_chapter(count, title, last_title) {

	var text     = "";
	var cover    = mbox_icon_dir + mbox_icons["album"];
	act_char    = title.substring(0,1);
	last_title += " ";
	last_char   = last_title.substring(0,1);

	text += "<div class=\"album_cover character\" style=\"background:url('" + cover + "');\">";
	text += "<div class=\"album_sort\">" + act_char + "</div>";
	text += "</div>";
//	text += "<div class=\"album_detail\" id=\"album_" + count + "\" style=\"display:none\">test " + count + " / " + document.body.clientWidth + "</div>";

	return text;
	}
	
function mboxViews_empty(count,title) {
	var act_char  = title.substring(0,1);
	var text      = "";
	text += "<div class=\"album_cover empty\"></div>";
	return text;
	}
	
function mboxViews_detail(count,title) {
	var act_char  = title.substring(0,1);
	mbox_list_char.push(act_char + "_" + count);
	var text      = "";
	text += "<div class=\"album_detail\" id=\"album_" + act_char + "_" + count + "\" style=\"display:none\">test " + count + " / " + document.body.clientWidth + "</div>";
	return text;
	}


// album list entry
//---------------------------------------------------------

function mboxViews_entry(count, uuid, title, description, cover, cmd_open, cmd_play) {

	var text  = "";
	var print = "";

	text += mboxHtmlScrollTo( "start", uuid );
	text += mboxHtmlToolTip(  "start" );

	// check if error	
	if (title.indexOf("#error") >= 0) {
	   if (appTheme == "dark") 	{ title = "<font color='yellow'>" + title + "</font>"; }
	   else			{ title = "<font color='red'>" + title + "</font>"; }
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



//--------------------------------------

function mboxViews_loadDetails(pos, i, uuid, callTrackList) {

	// define position where to show album details
	mbox_list_last = i;
	mbox_list_pos  = pos;

	// show connecting triangle
	mboxViews_showTriangle(i);

	// Load Album into the calculated DIV
	appFW.requestAPI("GET",["data",uuid,"-"],"", callTrackList );
	}


// show / hide triangle of active album
//----------------------------------------

function mboxViews_showTriangle(i) {
	elementVisible("album_tri1_"+i);
	elementVisible("album_tri2_"+i);
	for (var a=1;a<mbox_list_amount;a++) {
		if (a != i) {
			mboxViews_hideTriangle(a);
			}
		}
	}

function mboxViews_hideTriangle(i) {
	elementHidden("album_tri1_"+i);
	elementHidden("album_tri2_"+i);
	}


// empty and reload
//--------------------------------------

function mboxViews_emptyAll() {
	setTextById("frame1","");
	}


// Write / delete details info below the album in the list
//----------------------------------------

function mboxViews_emptyBelow() {		// delete all infos from last loading
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

function mboxViews_writeBelow(text) {		// write details to box below
	
	var divID = "";
	mboxViews_emptyBelow();			// delete old entries
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

