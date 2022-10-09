//--------------------------------------
// jc://music-box/, (c) Christoph Kloth
//--------------------------------------
// create cover for list and detail views
// and return cover for print view
//--------------------------------------

function mboxCoverAlbumInfo(nr,url_list,act,uuid) {
	var border          = "";
	var border_selected = "border:2px solid red;";
	var size            = "50px";

	if (nr == 1) { if (act == "track")  { border = border_selected; } select = "track"; }
	if (nr == 2) { if (act == "dir")    { border = border_selected; } select = "dir"; }
	if (nr == 3) { if (act == "upload") { border = border_selected; } select = "upload"; }
	if (nr == 4) { if (act == "url")    { border = border_selected; } select = "url"; }

	var img       = "<div class='album_cover' style='height:"+size+";width:"+size+";background:gray;cursor:default;"+border+"' title='"+select+"'></div>";
	var close_cmd = "";

	if 	(uuid.indexOf("r_")>=0)	{ close_cmd = "mboxStreamInfo_close"; }
	else if (uuid.indexOf("a_")>=0)	{ close_cmd = "mboxAlbumInfo_close"; }
	else if (uuid.indexOf("p_")>=0)	{ close_cmd = "mboxPlaylistInfo_close"; }

	if (url_list) {
	    if (url_list.length > 0) {
		if (nr == 1) { url = mbox_cover_dir + url_list[0];     if (act == "track")  { border = border_selected; } select = "track"; }
		if (nr == 2) { url = mbox_music_dir + url_list[0];     if (act == "dir")    { border = border_selected; } select = "dir"; }
		if (nr == 3) { url = mbox_cover_upl_dir + url_list[0]; if (act == "upload") { border = border_selected; } select = "upload"; }
		if (nr == 4) { url = url_list[0];                      if (act == "url")    { border = border_selected; } select = "url"; }

		var onclick = "appFW.requestAPI('PUT',['images','set_active','"+uuid+"','"+select+"'], '', " + close_cmd + " );";
		img = "<img src=\"" + url + "\" class='album_cover' style='height:"+size+";width:"+size+";"+border+"' onclick=\""+onclick+"\" title=\"("+select+": 1 von "+url_list.length+")\">&nbsp;";

		console.debug("mboxCoverAlbumInfo - URL:" + url);
        	console.debug("mboxCoverAlbumInfo - FIRST FILE:" + url_list[0]);
	    }	}
	else {
		}

	//img = "<a href='" + url + "' target='_blank'>" + img + "</a>";
	return img;
	}

function mboxCoverAlbum(artist,album) {
    // return cover for list and detail view
	var albums        = dataAlbums[artist][album];
	var i             = 0;
	var cover         = "";

	// check for images and return the first image as album image
	for (var key in albums) {
		if (albums[key][0]["cover_image"] > 0 && i < 1) {
			cover = mbox_cover_dir + albums[key][0]["cover_image_url"];
			i++;
			}
		}
	return cover;
	}
	
function mboxCoverAlbum_new(id,data) {
    // return cover for list and detail view

	var albumInfo;
	var i             = 0;
	var cover         = "";
	var active        = "";

	if (data && data["uuid"])  { albumInfo     = data; }
	else if (data)             { albumInfo     = data[id]; }
	else                       { return; }
	
	if (albumInfo["cover_images"]) {
		var images   = albumInfo["cover_images"];
		var position = 0;

		if (images["active"] && images["active"] != "none" && images[images["active"]].length > 0) {
			active = images["active"];
			if (images["active"] == "upload")  { cover = mbox_cover_upl_dir + images["upload"][position]; }
			if (images["active"] == "dir")     { cover = mbox_music_dir     + images["dir"][position]; }
			if (images["active"] == "track")   { cover = mbox_cover_dir     + images["track"][position]; }
			if (images["active"] == "url")     { cover = images["url"][position]; }
			}
		cover=encodeURI(cover);
		}

	if (checkImgExists && active != "url") {
		if (mboxCoverAlbum_checkFile(cover)) { return cover; }
		else                                 { return ""; }
		}
	else { return cover; }
	}
	
function mboxCoverAlbum_alert(cover) {
	var img   = "<img src=\""+cover+"\" class='album_cover_alert'>";
	appMsg.confirm(img,"",380);
	}

function mboxCoverAlbum_checkFile(image_url) {

	var http = new XMLHttpRequest();
	http.open('HEAD', image_url, false);
	http.send();
	return http.status != 404;
	}

function mboxCoverTogglePrint() {
    // show / hide print view
	if (document.getElementById("ontop").style.display == "none") 	{ document.getElementById("ontop").style.display = "block"; }
	else								{ document.getElementById("ontop").style.display = "none"; }
	}

function mboxCoverList( uuid, cover="", description="", cmd_open="", cmd_play="", type="album" ) {
    // LIST COVER
	var text          = "";
	var button_play   = "";
	var default_cover = mbox_icon_dir + mbox_icons[type];
	var icon_playing  = mbox_icon_dir + mbox_icons["playing"];

    if (mbox_device == "remote") {
        button_play = "<div class=\"player_button small white\" onclick=\"" + cmd_play + "\"><img src=\"" + mbox_icon_dir + "play.png\" style=\"width:9px;height:9px;margin:2px;\"></div>";
    }

	if (cover == "") {
                cover = default_cover;
                text += "<div class=\"album_cover\" style=\"background:url('" + cover + "');\" onclick=\"" + cmd_open + "\">";
		text += button_play;
                text += "<div class=\"player_active\" id=\"playing2_" + uuid + "\" style=\"display:none;\"><img src=\"" + icon_playing + "\" style=\"width:10px;height:10px;margin:2px;\"></div>";
                text += "<br/><br/>";
                text += description + "<br/>";
                text += "</div>";
                }
        else {
        	cover = cover.replace("'", "\\'");
            text += "<div class=\"album_cover\" style=\"background:url('" + cover + "');background-size:cover;background-repeat:no-repeat;vertical-align:botton;\" onclick=\"" + cmd_open + "\">";
            text += button_play;
            text += "<div class=\"player_active\" id=\"playing2_" + uuid + "\" style=\"display:none;\"><img src=\"" + icon_playing + "\" style=\"width:10px;height:10px;margin:2px;\"></div>";
            text += "</div>";
		}

	return text;
	}

function mboxCoverListStart() {
	var print = "<div class=\"print_album_back\"><div>";
        print += "<br>&nbsp;&nbsp;<b>"+lang("COVER_PRINT_VIEW_1")+"</b> "+lang("COVER_PRINT_VIEW_4");
        print += "&nbsp;&nbsp;"+lang("COVER_PRINT_VIEW_2");
        print += " <a style=\"cursor:pointer;color:blue;\" onclick=\"mboxCoverTogglePrint();\"><u>"+lang("COVER_PRINT_VIEW_3")+"</u></a><br>";
        print += "</div>";
	return print;
	}

function mboxCoverListEnd() {

	return "</div>";
	}

function mboxCoverListEntry(id,cover) {
        cover = cover.replace("'", "\\'");
        return "<div class=\"print_album_cover\" id=\"printCover_" + id + "\"onclick=\"document.getElementById('printCover_" + id + "').style.display='none';\" style=\"background:url('"+cover+"');background-size:cover;background-repeat:no-repeat;vertical-align:botton;\"></div>";
	}

function mboxCoverSeparator( content, cmd ) {

	var text = "";
        text += "<div class=\"album_cover\" style=\"background:#eeeeee;background-size:cover;background-position:center;background-repeat:no-repeat;\" onclick='" + cmd + "'>";
        text += "<div class=\"album_plus\">" + content + "</div>";
        text += "</div>";
	return text;
	}
