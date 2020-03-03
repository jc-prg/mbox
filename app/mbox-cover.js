//--------------------------------------
// jc://music-box/, (c) Christoph Kloth
//--------------------------------------
// create cover for list and detail views
// and return cover for print view
//--------------------------------------
/* INDEX:
function mboxCoverAlbumInfo(nr,url_list,act,uuid)
function mboxCoverAlbum(artist,album)
function mboxCoverAlbum_new(id,data)
function mboxCoverAlbum_checkFile(image_url)
function mboxCoverTogglePrint()
function mboxCoverListStart()
function mboxCoverListEnd()
function mboxCoverListEntry(id,cover)
*/
//--------------------------------------

function mboxCoverAlbumInfo(nr,url_list,act,uuid) {
	var border  = "";
	var size    = "50px";

	if (nr == 1) { if (act == "track")  { border = "border:2px solid red;"; } select = "track"; }
	if (nr == 2) { if (act == "dir")    { border = "border:2px solid red;"; } select = "dir"; }
	if (nr == 3) { if (act == "upload") { border = "border:2px solid red;"; } select = "upload"; }
	if (nr == 4) { if (act == "web")    { border = "border:2px solid red;"; } select = "web"; }

        var img       = "<div class='album_cover' style='height:"+size+";width:"+size+";background:gray;cursor:default;"+border+"' title='"+select+"'></div>";
	var close_cmd = "";

	if 	(uuid.indexOf("r_")>=0) { close_cmd = "mboxRadioInfo_close"; }
	else if (uuid.indexOf("a_")>=0) { close_cmd = "mboxAlbumInfoClose"; }
	else if (uuid.indexOf("p_")>=0) { close_cmd = "mboxPlaylistInfo_close"; }

	if (url_list) {
	    if (url_list.length > 0) {
		if (nr == 1) { url = mbox_cover_dir + url_list[0];     if (act == "track")  { border = "border:2px solid red;"; } select = "track"; }
		if (nr == 2) { url = mbox_music_dir + url_list[0];     if (act == "dir")    { border = "border:2px solid red;"; } select = "dir"; }
		if (nr == 3) { url = mbox_cover_upl_dir + url_list[0]; if (act == "upload") { border = "border:2px solid red;"; } select = "upload"; }
		if (nr == 4) { url = url_list[0];                      if (act == "web")    { border = "border:2px solid red;"; } select = "web"; }

		var onclick = "mboxApp.requestAPI('PUT',['images','set_active','"+uuid+"','"+select+"'], '', " + close_cmd + " );";
		img = "<img src='" + url + "' class='album_cover' style='height:"+size+";width:"+size+";"+border+"' onclick=\""+onclick+"\" title=\"("+select+": 1 von "+url_list.length+")\">&nbsp;";

		console.log("URL:" + url);
        	console.log("FIRST FILE:" + url_list[0]);
	    }	}
	else {
		}


	//img = "<a href='" + url + "' target='_blank'>" + img + "</a>";
	return img;
	}


// return cover for list and detail view
//--------------------------------------

function mboxCoverAlbum(artist,album) {
	var albums        = dataAlbums[artist][album];
	var i             = 0;
	var cover	  = "";

	// check for images and return the first image as album image
	for (var key in albums) {
		if (albums[key][0]["cover_image"] > 0 && i < 1) {
			cover = mbox_cover_dir + albums[key][0]["cover_image_url"];
			i++;
			}
		}
	return cover;
	}

// return cover for list and detail view
//--------------------------------------

function mboxCoverAlbum_new(id,data) {

	var albumInfo;
	var i              = 0;
	var cover	   = "";

	if (data && data["uuid"]) 	{ albumInfo     = data; }
	else if (data)			{ albumInfo     = data[id]; }
	else				{ return; }

	if (albumInfo["cover_images"]) {
		var images   = albumInfo["cover_images"];
		var position = 0;

		if (images["active"] && images["active"] != "none" && images[images["active"]].length > 0) {
			if (images["active"] == "upload") 	{ cover = mbox_cover_upl_dir + images["upload"][position]; }
			if (images["active"] == "dir") 		{ cover = mbox_music_dir     + images["dir"][position]; }
			if (images["active"] == "track") 	{ cover = mbox_cover_dir     + images["track"][position]; }
			if (images["active"] == "web") 		{ cover = images["web"][position]; }
			}
		cover=encodeURI(cover);
		}

	if (checkImgExists) {
		if (mboxCoverAlbum_checkFile(cover))	{ return cover; }
		else					{ return ""; }
		}
	else { return cover; }
	}
	
//--------------------------------------

function mboxCoverAlbum_checkFile(image_url) {

	var http = new XMLHttpRequest();
	http.open('HEAD', image_url, false);
	http.send();
	return http.status != 404;
	}


//--------------------------------------
// show / hide print view
//--------------------------------------

function mboxCoverTogglePrint() {
	if (document.getElementById("ontop").style.display == "none") 	{ document.getElementById("ontop").style.display = "block"; }
	else								{ document.getElementById("ontop").style.display = "none"; }
	}

//--------------------------------------
// LIST COVER
//--------------------------------------


function mboxCoverListStart() {
	var print = "<div class=\"print_album_back\">";
        print += "<br>&nbsp;&nbsp;<b"+lang("COVER_PRINT_VIEW_1")+"</b> "+lang("COVER_PRINT_VIEW_2")+" <a style=\"cursor:pointer;\" onclick=\"mboxCoverTogglePrint();\"><u>"+lang("COVER_PRINT_VIEW_3")+"</u></a><br>";
//        print += "<br>&nbsp;&nbsp;<b>Album-Cover für den Ausdruck:</b> Klicke auf ein Cover, um es auszublenden (z.B. wenn schon gedruckt). Klicke <a style=\"cursor:pointer;\" onclick=\"mboxCoverTogglePrint();\"><u>hier</u></a>, um diese Ansicht zu schließen.<br>";
	return print;
	}

function mboxCoverListEnd() {
	return "</div>";
	}

function mboxCoverListEntry(id,cover) {
	return "<div class=\"print_album_cover\" id=\"printCover_" + id + "\"onclick=\"document.getElementById('printCover_" + id + "').style.display='none';\" style=\"background:url("+cover+");background-size:cover;background-repeat:no-repeat;vertical-align:botton;\"></div>";
	}










































