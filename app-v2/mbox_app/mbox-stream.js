//--------------------------------------
// jc://music-box/, (c) Christoph Kloth
//--------------------------------------
// List radio channels
//--------------------------------------
/* INDEX:
function mboxStream_load()
function mboxStream(data)
function mboxStreamChannel_load(i,uuid)
function mboxStreamChannel(data)
function mboxPodcastTrackRow(id, dataTracks, album=true, artist=false, count=0, trackinfo=false)
function mboxStreamWriteAudioPlayer(title,file,divid)
function mboxStreamInfo_load(uuid)
function mboxStreamInfo(data)
function mboxStreamTrackInfo_load(stream_uuid, track_uuid)
function mboxStreamTrackInfo(data, track_uuid)
function mboxStreamInfo_close()
function mboxStreamEdit_load(uuid)
function mboxStreamEdit(data)
function mboxStreamDelete(uuid,title)
function mboxStreamDelete_exec(uuid,title)
function mboxStreamDelete_msg(data,title)
function mboxStreamAdd()
function mboxStreamAdd_dialog(i)
function mboxStreamAdd_msg(data)
*/
//--------------------------------------


//--------------------------------------

function mboxStream_load()  { appFW.requestAPI("GET",["db","radio","-"],"", mboxStream); scrollToTop(); }
function mboxStream(data) {
	var text          = "";
	var print 	  = mboxCoverListStart();
	var default_cover = mbox_icon_dir + mbox_icons["radio"]; // "img/cd2.png";
	var radio_data    = data["DATA"]["radio"];
	var a             = 0;
	mbox_cover_list   = [];
	mbox_mode         = 'Radio'; 

	// sort by radio name
	var sorted_r   = [];
	var by_title = {};
	for (var key in radio_data) { if (radio_data[key]["title"]) {
		//console.log(key + "/" + radio_data[key]["title"]);
		sorted_r.push( radio_data[key]["title"] );
		by_title[radio_data[key]["title"]] = key;
		} }
        sorted_r.sort();

	// list all radio channels
	for (var i=0;i<sorted_r.length;i++) {

		var key      = sorted_r[i];
		var uuid     = by_title[key];
		var cmd_open = "mboxAlbumEmptyAll();mboxStreamChannel_load('"+(i+1)+"','" + uuid + "');"; 
		var cmd_play = "appFW.requestAPI('GET',['play', '" + uuid + "'],'',mboxControl);";
		var cover    = default_cover;

		// check cover, load via URL if PodCast
	        if (radio_data[uuid]["podcast"] && radio_data[uuid]["podcast"]["title"]) {
	        	radio_data[uuid]["cover_images"] = radio_data[uuid]["podcast"]["cover_images"];        	
	        	}
		cover = mboxCoverAlbum_new(uuid,radio_data);

		// print playlist cover
		text += mboxHtmlScrollTo( "start", uuid );
		text += mboxHtmlToolTip( "start" );

		// write cover
		text += mboxCoverList( uuid, cover, "<b>" + key + "</b><br/>"+lang("STREAM"), cmd_open, cmd_play );
		if (cover != "") { print += mboxCoverListEntry( uuid, cover ); }

		// write tooltip
		text += mboxHtmlToolTip( "end", i+1, "<b>" + key + "</b>" );
		text += mboxHtmlScrollTo( "end" );
		text += mboxHtmlEntryDetail( i+1 );

		a = i+1;
		}

        var onclick = "mboxStreamAdd_dialog("+(a+1)+");";
//	text += mboxCoverSeparator( "+", onclick );
	text += mboxCoverSeparator( "<img src=\""+mbox_icon_dir+"/stream_add.png\" style=\"height:50px;width:50px;margin-top:10px;\">", onclick );
	text += mboxHtmlEntryDetail( a+1 );

	mbox_list_amount = sorted_r.length+1;
	print += mboxCoverListEnd();

	setTextById("frame2", ""); // no filter defined yet
	setTextById("frame3", text);
	setTextById("ontop",  print);

	document.getElementById("frame2").style.display="none";
	}


// Load data albums and list ...
//--------------------------------------

function mboxStreamChannel_load(i,uuid) {
        var count = 3;
        var width = document.body.clientWidth;
        if (width > 1250) { mbox_list_count = 6; }

        mbox_list_pos = ((Math.floor((i-1)/mbox_list_count)+1) * mbox_list_count );
        if (mbox_list_pos > mbox_list_amount) { mbox_list_pos = mbox_list_amount; }

        //mboxAlbumEmptyAll();
        appFW.requestAPI("GET",["data",uuid,"-"],"", mboxStreamChannel );
        }

// List albums tracks of an album
//--------------------------------------

function mboxStreamChannel(data) {

        if (!data["DATA"]["_selected"]) { 
                console.error("Fehler mboxStreamChannel"); 
                console.error(data);  
                return; 
                }

        var text          = "";
        var uuid          = data["DATA"]["_selected_uuid"];
        var radio_data    = data["DATA"]["_selected"];
        var default_cover = mbox_icon_dir + mbox_icons["radio"];

        // log ...
        if (radio_data) {
	        console.debug("Show Radio Channel: " + uuid + "/" + radio_data["title"]);
		}
		
        if (radio_data["podcast"] && radio_data["podcast"]["title"]) {
		// handover data to local player
		mbox_playlist_queue["type"]		= "podcast";
		mbox_playlist_queue["album"]		= radio_data;
		mbox_playlist_queue["scrollto"]	= "scrollto_" + uuid.replace(/-/g,"");
		mbox_playlist_queue["tracks"]		= radio_data["podcast"]["tracks"];
		mbox_playlist_queue["url"]		= undefined;
        	}
        else {
		// handover data to local player
		mbox_playlist_queue["type"]		= "stream";
		mbox_playlist_queue["album"]		= radio_data;
		mbox_playlist_queue["scrollto"]	= "scrollto_" + uuid.replace(/-/g,"");
		mbox_playlist_queue["tracks"]		= {};
		mbox_playlist_queue["url"]		= radio_data["stream_url2"];
		}
		
	console.log(mbox_playlist_queue);

        // check if podcast data exists		
        podcast = false;
        if (radio_data["podcast"] && radio_data["podcast"]["title"]) {
        	radio_data["title"]        = radio_data["podcast"]["title"];        	
        	radio_data["cover_images"] = radio_data["podcast"]["cover_images"];        	
        	radio_data["description"]  = radio_data["podcast"]["description"];
        	radio_data["description"] += "<br/><i>("+radio_data["podcast"]["track_count"]+" Tracks)</i>";
        	radio_data["stream_info"]  = radio_data["podcast"]["stream_info"];
        	radio_data["tracks"]       = radio_data["podcast"]["tracks"];
        	radio_data["track_list"]   = radio_data["podcast"]["track_list"];
		podcast = true;
        	}

        // Check if Cover exists
        cover = mboxCoverAlbum_new(uuid,radio_data);
        if (!cover) { cover = default_cover; }
        
        // Write album cover
        var onclick    = "mboxCoverAlbum_alert(\""+cover+"\");";        
        text += "<div class=\"album_cover\" style=\"background:url("+cover+");background-size:contain;background-position:center;background-repeat:no-repeat;\" onclick='" + onclick + "'>";
        text += "</div>";

        // write album infos
        text += "<div class=\"album_infos new\">";
        text +=   "<b>" + radio_data["title"] + "</b><br/>" + radio_data["description"] + "<br/>";
        text += "</div>";
        text += mboxHtmlButton("delete",  "mboxAlbumEmptyBelow();", "opac",   "small small2");

        // player control (in box)
        text += "<div class=\"album_control new\">";
        text += "<div class=\"player_active big\" id=\"playing_"+uuid+"\" style=\"display:none;\"><img src=\""+mbox_icon_dir + mbox_icons["playing"]+"\" style=\"height:20px;width:20px;margin:2px;\"></div>";
        
	if (mbox_device != "local") {
      		text += mboxHtmlButton("play",  "appFW.requestAPI('GET',['play', '" + uuid + "'],'',mboxControl);", "blue");
        	text += mboxHtmlButton("stop",  "appFW.requestAPI('GET',['stop'],'',mboxControl);", "blue");
        	text += mboxHtmlButton("empty");
		}
		
	if (mbox_device != "remote") {
        	text += mboxHtmlButton("play",  "mboxPlayerLocal();",	"green");
        	text += mboxHtmlButton("stop",  "mboxPlayer.stop();",	"green");
		text += mboxHtmlButton("empty");
		}

        text += mboxHtmlButton("info",  "mboxStreamInfo_load('"+uuid+"');",  "red");

        // show and edit rfid card
        if ("card_id" in radio_data)        {
                text += "<div id=\"show_card\">";
                text += mboxHtmlButton("card",  "", "green");
                text += "</div>";
                text += mboxCardEditLink(uuid);
                }
        else {
                text += "<div id=\"show_card\">";
                text += "</div>";
                text += mboxCardEditLink(uuid);
                }
                
	text += "</div>";
	text += "<div style=\"width:100%;float:left;\"><hr/></div><center>";
	
	// write website link
	if (radio_data["stream_info"] != "") {
		text += lang("WEBSITE")+": <a href=\"" + radio_data["stream_info"] + "\" target=\"_blank\">"+ radio_data["stream_info"] + "</a>";
		text += "</center><div style=\"width:100%;float:left;\"><hr/></div>";
		}

        // write tracks
        if (podcast) {
        	var uuids      = radio_data["track_list"];  
        	var max        = uuids.length;
        	var columns    = mboxListCount_New()/3;
        	var per_column = Math.trunc(max/columns);
        	if (per_column != max/columns) { per_column += 1; }
        	
        	var column    = 1;
		text += "<div class=\"album_tracks\">";
        	for (var i=0; i<uuids.length; i++) {
        		text += mboxPodcastTrackRow(id=uuids[i], dataTracks=radio_data["tracks"], album=true, artist=false, count=i, trackinfo=false);        		
        		if (i+1 == column*per_column) {
				text   += "</div><div class=\"album_tracks\">";
				column += 1;
        			}
			}
		text += "</div>";
		}
	else {
		text += "<div class=\"album_tracks\">";
		text += "&nbsp;";
		text += "</div>";
		}

        mboxAlbumWriteBelow(text);
        }


// row of podcasts
//--------------------------------------

function mboxPodcastTrackRow(id, dataTracks, album=true, artist=false, count=0, trackinfo=false) {

	var track       = dataTracks[id];
	var text        = "";
	var cmd         = "";
	var stream_uuid = track["album_uuid"];

	var length = "";
	if (track["duration"]) { length = " <font color='gray'>(" + track["duration"] + ")</font>"; }

	console.debug("Debug UUID: " + id + " / Podcast UUID: " + stream_uuid + " / " + track["album"] + " / " + track["sort_pos"] + " / " + track["sort"]);
	console.debug(track);

	// track playback control
	cmd  += "<div class=\"album_tracks_control\">";
	if (mbox_device != "remote") 	{
		cmd += mboxHtmlButton("play",  "mboxPlayerLocal(" + count + ");", "green",   "small right"); 
		}
	if (mbox_device != "local") 	{
		cmd += mboxHtmlButton("play",  "appFW.requestAPI('GET',['play_position', '"+stream_uuid+"', '"+count+"'],'',mboxControl);", "blue", "small right");
		cmd += "<div class=\"player_active right\" id=\"playing3_"+id+"\" style=\"display:none;\"><img src=\"" + mbox_icon_dir + mbox_icons["playing"] + "\" style=\"width:10px;height:10px;margin:2px;\"></div>";
		}
	cmd  += "</div>";

	text += "<div class=\"album_tracks_title\">";
	
	// track
	text += "<table><tr><td style='width:20px;vertical-align:top;padding:0px'>";
	text += (count+1);
	text += ".</td><td>";
	text += "<div class='album_track_title_shorten' onclick='mboxStreamTrackInfo_load(\"" + stream_uuid + "\", \"" + id + "\")' style='cursor:pointer;'><b>" + track["title"] + "</b></div><br/>";
	text += "<div class='album_track_description_shorten'>" + track["description"] + "</div>";
	text += "<font color='gray'>" + track["publication"] + "</font>";
	text += length;
	text += "</td></tr></table>";

	text += "</div>";
	text += cmd;

	return text;
	}


// show audio player for one audio file
//--------------------------------------

function mboxStreamWriteAudioPlayer(title,file,divid) {

        var text = "";
        text += title + "<hr/>";
        text += "<audio controls style=\"width:100%\">";
        text += "<source src=\"" + file + "\" type=\"audio/mpeg\">";
        text += "</audio>";
        //text += file;

        setTextById(divid,text);
        }


// radio info as popup (incl. some settings ...)
//--------------------------------------

function mboxStreamInfo_load(uuid) { appFW.requestAPI("GET",["data",uuid,"-"],"", mboxStreamInfo ); }
function mboxStreamInfo(data) {
        var text   = "";
        var album  = data["DATA"]["_selected"];
        var uuid   = data["DATA"]["_selected_uuid"];

        var url    = RESTurl + "api/data/"+uuid+"/--";
        var size   = Math.round(album["albumsize"]/1024/1024*100)/100;
        var cardid = album["card_id"]; if (!cardid) { cardid = lang("CARD_NOT_CONNECTED"); }

	var cover  = "";
        if (album["cover_images"]) {
                cover += mboxCoverAlbumInfo(1, album["cover_images"]["track"],  album["cover_images"]["active"], uuid);
                cover += mboxCoverAlbumInfo(2, album["cover_images"]["dir"],    album["cover_images"]["active"], uuid);
                cover += mboxCoverAlbumInfo(3, album["cover_images"]["upload"], album["cover_images"]["active"], uuid);
                cover += mboxCoverAlbumInfo(4, album["cover_images"]["web"],    album["cover_images"]["active"], uuid);
                }
        else {
                cover += lang("DATA_OLD_FORMAT");
                }

	var edit = "";
        edit += mboxHtmlButton("image_add",	"mboxUploadImage('"+uuid+"','radio','"+album["title"]+"');",                     "red");
        edit += mboxHtmlButton("edit",  	"mboxStreamEdit_load('"+uuid+"');",                                                "red");
        edit += mboxHtmlButton("delete",  	"mboxAlbumDelete('"+album["title"]+": "+album["description"]+"','"+uuid+"');",   "red");

        text += "<b>"+lang("STREAM_INFORMATION")+"</b><br/><br/>";
        text += mboxHtmlTableNew("start");
        text += "<tr><td colspan='2'><hr></td></tr>";
        text += mboxHtmlTableNew(["<i>"+lang("TITLE")+":",		album["title"] ] );
        text += mboxHtmlTableNew(["<i>"+lang("DESCRIPTION")+":",	album["description"] ] );
        text += mboxHtmlTableNew(["<i>"+lang("INFORMATION")+":",	"<a href=\"" + album["stream_info"] + "\" target=\"_blank\">" + album["stream_info"] + "</a>" ] );
        text += mboxHtmlTableNew(["<i>"+lang("STREAM")+" URL:",	"<a href=\"" + album["stream_url"] + "\" target=\"_blank\">" + album["stream_url"] + "</a>" ] );
        text += mboxHtmlTableNew(["<i>"+lang("STREAM")+" URL:",	"<a href=\"" + album["stream_url2"] + "\" target=\"_blank\">" + album["stream_url2"] + "</a>" ] );
        text += mboxHtmlTableNew(["<i>"+lang("STREAM")+" UUID:",	"<a href='" + url + "/' target='_blank'>" + uuid + "</a>" ] );
        text += mboxHtmlTableNew(["<i>"+lang("CARD_ID")+":",		"<a style='cursor:pointer;' onclick='mboxCardList_load(\""+cardid+"\");'>"    + cardid + "</a>" ] );
        if (album["podcast"] != {}) {
		text += "<tr><td colspan='2'><center><i><hr/>Podcast Info<hr/></i></center></td></tr>";
		text += mboxHtmlTableNew(["<i>"+lang("TITLE")+":",           album["podcast"]["title"] ] );
		text += mboxHtmlTableNew(["<i>"+lang("DESCRIPTION")+":",     album["podcast"]["description"] ] );        	        
		text += mboxHtmlTableNew(["<i>"+lang("TRACKS")+":",	       album["podcast"]["track_count"]+" Tracks" ] );        	        
		text += mboxHtmlTableNew(["<i>"+lang("INFORMATION")+":",	"<a href=\"" + album["podcast"]["stream_info"] + "\" target=\"_blank\">" + album["podcast"]["stream_info"] + "</a>" ] );
        	text += "<tr><td colspan='2'><hr></td></tr>";
		}
        text += mboxHtmlTableNew(["<i>"+lang("COVER_AVAILABLE")+":", 	cover ] );
        text += "<tr><td colspan='2'><hr></td></tr>";
        text += mboxHtmlTableNew(["<i>"+lang("EDIT")+":",       	edit ] );
        text += "<tr><td colspan='2'><hr></td></tr>";
        text += mboxHtmlTableNew("end");

        appMsg.confirm(text,"",450);
        }

//----------------------------------------

function mboxStreamTrackInfo_load(stream_uuid, track_uuid) { appFW.requestAPI("GET",["data",stream_uuid,"-"],"", [ mboxStreamTrackInfo, track_uuid ] ); }
function mboxStreamTrackInfo(data, track_uuid) {
        var text   = "";
        var stream = data["DATA"]["_selected"];
        var uuid   = data["DATA"]["_selected_uuid"];
        var track  = stream["podcast"]["tracks"][track_uuid];
        var url    = RESTurl + "api/data/"+uuid+"/--";

        text += "<b>"+lang("TRACK_INFORMATION")+"</b><br/><br/>";
        text += mboxHtmlTableNew("start");
        text += "<tr><td colspan='2'><hr></td></tr>";
        
        text += mboxHtmlTableNew(["<i>"+lang("TITLE")+":",		track["title"] ] );
        text += mboxHtmlTableNew(["<i>"+lang("DESCRIPTION")+":",	track["description"] ] );
        text += mboxHtmlTableNew(["<i>"+lang("DURATION")+":",	track["duration"] ] );
        text += mboxHtmlTableNew(["<i>"+lang("PUBLICATION")+":",	track["publication"] ] );
        text += mboxHtmlTableNew(["<i>"+lang("TRACK")+" URL:",	"<a href=\"" + track["file"] + "\" target=\"_blank\">" + track["file"] + "</a>" ] );
        text += mboxHtmlTableNew(["<i>"+lang("TRACK")+" UUID:",	track_uuid ] );
        text += mboxHtmlTableNew(["<i>"+lang("STREAM")+" UUID:",	"<a href='" + url + "/' target='_blank'>" + uuid + "</a>" ] );
        
        
        text += "<tr><td colspan='2'><hr></td></tr>";
        text += mboxHtmlTableNew("end");

        appMsg.confirm(text,"",450);
	}


//----------------------------------------

function mboxStreamInfo_close() {
	setTimeout(function(){ mboxStream_load(); }, 2000);
        appMsg.hide();        
        }

//----------------------------------------

function mboxStreamEdit_load(uuid)	{ appFW.requestAPI("GET",["data",uuid,"uuid,title,description,stream_info,stream_url,stream_url2"],"", mboxStreamEdit ); }
function mboxStreamEdit(data) 	{ mboxDataEdit(data); }
// -> mbox-data.js

// delete playlist (dialog to confirm)
//---------------------------
      
function mboxStreamDelete(uuid,title) {
	text    = lang("STREAM_DELETE_ASK") + ": <b>"+title+"</b>?";
	cmd     = "mboxStreamDelete_exec('"+uuid+"','"+title+"');";
	appMsg.confirm(text,cmd,150,true);
	}
	
function mboxStreamDelete_exec(uuid,title) {
	appFW.requestAPI('DELETE',['data',uuid],'',[mboxPlaylistDelete_msg,title]);
	}

function mboxStreamDelete_msg(data,title) {
	mboxDataReturnMsg(data,lang("STREAM_DELETED")+"<br/><b>"+title,lang("STREAM_DELETE_ERROR")+"<br/><b>"+title);
        mboxPlaylistAll_load();
        }

//----------------------------------------------------------------

function mboxStreamAdd() {
	var fields = ["stream_description","stream_radio_url","stream_stream_url","stream_image_url"];
	var param  = "";
	var title = document.getElementById("stream_title").value;

	for (var i=0;i<fields.length;i++) {
		param += document.getElementById(fields[i]).value + "||";
		}

        document.getElementById("mboxStreamAdd").disabled = true;
        document.getElementById("mboxStreamAdd").innerHTML = "Please wait ...";

        appFW.requestAPI('POST',['data','radio',encodeURIComponent(title+'||'+param)],'', mboxStreamAdd_msg);
        }

function mboxStreamAdd_dialog(i) {
        var onclick2 = "document.getElementById('album_"+(i)+"').style.display='none';";
        var text     = "<b>"+lang("ADD_STREAM")+":</b><br/><br/><table>";
        text += "<tr><td>"+lang("TITLE")+":</td>		<td><input id=\"stream_title\" style=\"width:150px\"></input></td></tr>";
        text += "<tr><td>"+lang("DESCRIPTION")+":</td> 		<td><input id=\"stream_description\" style=\"width:150px\"></input></td></tr>";
        text += "<tr><td>"+lang("WEBSITE")+" URL:</td>  	<td><input id=\"stream_radio_url\" style=\"width:150px\"></input></td></tr>";
        text += "<tr><td>"+lang("STREAM")+" URL (m3u,rss,xml):</td>	<td><input id=\"stream_stream_url\" style=\"width:150px\"></input></td></tr>";
        text += "<tr><td>"+lang("LOGO")+" URL:</td>		<td><input id=\"stream_image_url\" style=\"width:150px\"></input></td></tr>";
        text += "</table><br/>";
        text += button("mboxStreamAdd();",lang("ADD"),"mboxStreamAdd");
        text += button(onclick2,lang("CLOSE"),"close_stream");
        setTextById("album_"+i,text);
        document.getElementById("album_"+i).style.display="block";
        }

function mboxStreamAdd_msg(data) {
        var text = "";
        if (data["REQUEST"]["status"] == "success")     { text += lang("STREAM_CREATED"); } 
        else                         		        { text += lang("STREAM_CREATED_ERROR"); } 
        appMsg.alert(text);
        mboxStream_load()
        }

//----------------------------------------------------------------
// EOF
