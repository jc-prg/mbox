//--------------------------------------
// jc://music-box/, (c) Christoph Kloth
//--------------------------------------
// List radio channels
//--------------------------------------
/* INDEX:
function mboxRadio_load()
function mboxRadio(data)
function mboxRadioChannel_load(i,uuid)
function mboxRadioChannel(data)
function mboxRadioWriteAudioPlayer(title,file,divid)
function mboxRadioInfo_load(uuid)
function mboxRadioInfo(data)
function mboxRadioInfo_close()
function mboxRadioEdit_load(uuid)
function mboxRadioEdit(data)
function mboxStreamDelete(uuid,title)
function mboxStreamDelete_exec(uuid,title)
function mboxStreamDelete_msg(data,title)
function mboxRadioAdd()
function mboxRadioAdd_dialog(i)
function mboxRadioAdd_msg(data)
*/
//--------------------------------------


//--------------------------------------

function mboxRadio_load()             { mboxApp.requestAPI("GET",["db","radio","-"],"", mboxRadio); }
function mboxRadio(data) {
        var text          = "";
	var print 	  = mboxCoverListStart();
        var default_cover = mbox_icons["radio"]; // "img/cd2.png";
	var radio_data    = data["DATA"]["radio"];
	var a             = 0;
        mbox_cover_list   = [];

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
             var cmd_open = "mboxEmptyAlbum();mboxRadioChannel_load('"+(i+1)+"','" + uuid + "');"; 
	     var cmd_play = "mboxApp.requestAPI('GET',['play', '" + uuid + "'],'',mboxControl);";
             var cover    = default_cover;

             // check cover
             cover = mboxCoverAlbum_new(uuid,radio_data);

             // print playlist cover
             text += mboxScrollTo( "start", uuid );
             text += mboxToolTip( "start" );

             // write cover
             text += mboxCoverList( uuid, cover, "<b>" + key + "</b><br/>"+lang("STREAM"), cmd_open, cmd_play );
             if (cover != "") { print += mboxCoverListEntry( uuid, cover ); }

             // write tooltip
             text += mboxToolTip( "end", i+1, "<b>" + key + "</b>" );
             text += mboxScrollTo( "end" );
             text += mboxAlbumDetail( i+1 );

	     a = i+1;
             }

        var onclick = "mboxRadioAdd_dialog("+(a+1)+");";
//	text += mboxCoverSeparator( "+", onclick );
        text += mboxCoverSeparator( "<img src=\"icon/stream_add.png\" style=\"height:50px;width:50px;margin-top:10px;\">", onclick );
	text += mboxAlbumDetail( a+1 );

        mbox_list_amount = sorted_r.length+1;
	print += mboxCoverListEnd();

	setTextById("remote4", ""); // no filter defined yet
        setTextById("remote2", text);
        setTextById("ontop",   print);
        }


// Load data albums and list ...
//--------------------------------------

function mboxRadioChannel_load(i,uuid) {
        var count = 3;
        var width = document.body.clientWidth;
        if (width > 1250) { mbox_list_count = 6; }

        mbox_list_pos = ((Math.floor((i-1)/mbox_list_count)+1) * mbox_list_count );
        if (mbox_list_pos > mbox_list_amount) { mbox_list_pos = mbox_list_amount; }

        //mboxEmptyAlbum();
        mboxApp.requestAPI("GET",["data",uuid,"-"],"", mboxRadioChannel );
        }

// List albums tracks of an album
//--------------------------------------

function mboxRadioChannel(data) {

        if (!data["DATA"]["_selected"]) { 
                console.error("Fehler mboxRadioChannel"); 
                console.error(data);  
                return; 
                }

        var text          = "";
        var uuid          = data["DATA"]["_selected_uuid"];
        var radio_data    = data["DATA"]["_selected"];
        var default_cover = mbox_icons["radio"];

        // log ...
        if (radio_data) {
	        console.debug("Show Radio Channel: " + uuid + "/" + radio_data["title"]);
		}
		
        // Check if Cover exists
        cover = mboxCoverAlbum_new(uuid,radio_data);
        if (!cover) { cover = default_cover; }

        // Write album cover
        text += "<div class=\"album_cover\" style=\"background:url("+cover+");background-size:contain;background-position:center;background-repeat:no-repeat;\" onclick='" + onclick + "'>";
        text += "</div>";

        // write album infos
        text += "<div class=\"album_infos new\">";
        text +=   "<b>" + radio_data["title"] + "</b><br/><i>" + radio_data["description"] + "</i><br/>";
        text += "</div>";
        text += mboxButton("delete",  "mboxEmptyBelow();", "opac",   "small small2");

        // player control (in box)
        text += "<div class=\"album_control new\">";
        text += "<div class=\"player_active big\" id=\"playing_"+uuid+"\" style=\"display:none;\"><img src=\""+mbox_icons["playing"]+"\" style=\"height:20px;width:20px;margin:2px;\"></div>";
	if (mbox_device != "local") {
      		text += mboxButton("play",  "mboxApp.requestAPI('GET',['play', '" + uuid + "'],'',mboxControl);", "blue");
        	text += mboxButton("stop",  "mboxApp.requestAPI('GET',['stop'],'',mboxControl);", "blue");
        	text += mboxButton("empty");
		}

        text += mboxButton("info",  "mboxRadioInfo_load('"+uuid+"');",  "red");

        // show and edit rfid card
        if ("card_id" in radio_data)        {
                text += "<div id=\"show_card\">";
                text += mboxButton("card",  "", "green");
                text += "</div>";
                text += CardID(uuid);
                }
        else {
                text += "<div id=\"show_card\">";
                text += "</div>";
                text += CardID(uuid);
                }
        text += "</div>";
        text += "<div style=\"width:100%;float:left;\"><hr/></div>";

        // write tracks
        text += "<div class=\"album_tracks\">";
	text += "Web-Seite: <a href=\"" + radio_data["stream_info"] + "\" target=\"_blank\">"+ radio_data["stream_info"] + "</a>";
        text += "</div>";
        text += "<div style=\"width:100%;float:left;\"><hr/></div>";
	//alert(radio_data["stream_url2"]);
	if (mbox_device == "local") {
        	text += "<div class=\"album_tracks_player\" id=\"audioPlayer\">";
        	text += "</div>";
		}

        mboxWriteBelow(text);
        //setTextById("remote1",text);
        if (radio_data["stream_url2"]) {
	        mboxRadioWriteAudioPlayer(radio_data["title"],radio_data["stream_url2"],"audioPlayer");
		}
        }


// show audio player for one audio file
//--------------------------------------

function mboxRadioWriteAudioPlayer(title,file,divid) {

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

function mboxRadioInfo_load(uuid) { mboxApp.requestAPI("GET",["data",uuid,"-"],"", mboxRadioInfo ); }
function mboxRadioInfo(data) {
        var text   = "";
        var album  = data["DATA"]["_selected"];
        var uuid   = data["DATA"]["_selected_uuid"];

        var url    = RESTurl + "mbox/read/radio/"+uuid+"/";
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
        edit += mboxButton("image_add", "mboxUploadImage('"+uuid+"','radio','"+album["title"]+"');",                     "red");
        edit += mboxButton("edit",  	"mboxRadioEdit_load('"+uuid+"');",                                                "red");
        edit += mboxButton("delete",  	"mboxAlbumDelete('"+album["title"]+": "+album["description"]+"','"+uuid+"');",   "red");

        text += "<b>"+lang("STREAM_INFORMATION")+"</b><br/><br/>";
        text += mboxTableNew("start");
        text += "<tr><td colspan='2'><hr></td></tr>";
        text += mboxTableNew(["<i>"+lang("TITLE")+":",              	album["title"] ] );
        text += mboxTableNew(["<i>"+lang("DESCRIPTION")+":",        	album["description"] ] );
        text += mboxTableNew(["<i>"+lang("INFORMATION")+":",	        "<a href=\"" + album["stream_info"] + "\" target=\"_blank\">" + album["stream_info"] + "</a>" ] );
        text += mboxTableNew(["<i>"+lang("STREAM")+" URL:",        	"<a href=\"" + album["stream_url"] + "\" target=\"_blank\">" + album["stream_url"] + "</a>" ] );
        text += mboxTableNew(["<i>"+lang("STREAM")+" UUID:",		"<a href='" + url + "/' target='_blank'>" + uuid + "</a>" ] );
        text += mboxTableNew(["<i>"+lang("CARD_ID")+":",         	"<a style='cursor:pointer;' onclick='mboxListCardsLoad();'>"    + cardid + "</a>" ] );
        text += mboxTableNew(["<i>"+lang("COVER_AVAILABLE")+":", 	cover ] );
        text += "<tr><td colspan='2'><hr></td></tr>";
        text += mboxTableNew(["<i>"+lang("EDIT")+":",       		edit ] );
        text += "<tr><td colspan='2'><hr></td></tr>";
        text += mboxTableNew("end");

        appMsg.confirm(text,"",450);
        }

//----------------------------------------

function mboxRadioInfo_close() {
	setTimeout(function(){ mboxRadio_load(); }, 2000);
        appMsg.hide();        
        }

//----------------------------------------

function mboxRadioEdit_load(uuid)	{ mboxApp.requestAPI("GET",["data",uuid,"uuid,title,description,stream_info,stream_url,stream_url2"],"", mboxRadioEdit ); }
function mboxRadioEdit(data) 		{ mboxDataEdit(data); }
// -> mbox-data.js

// delete playlist (dialog to confirm)
//---------------------------
      
function mboxStreamDelete(uuid,title) {
	text    = lang("STREAM_DELETE_ASK") + ": <b>"+title+"</b>?";
	cmd     = "mboxStreamDelete_exec('"+uuid+"','"+title+"');";
	appMsg.confirm(text,cmd,150,true);
	}
	
function mboxStreamDelete_exec(uuid,title) {
	mboxApp.requestAPI('DELETE',['data',uuid],'',[mboxPlaylistDelete_msg,title]);
	}

function mboxStreamDelete_msg(data,title) {
	mboxReturnMsg(data,lang("STREAM_DELETED")+"<br/><b>"+title,lang("STREAM_DELETE_ERROR")+"<br/><b>"+title);
        mboxPlaylistAll_load();
        }

//----------------------------------------------------------------

function mboxRadioAdd() {
	var fields = ["stream_description","stream_radio_url","stream_stream_url","stream_image_url"];
	var param  = "";
	var title = document.getElementById("stream_title").value;

	for (var i=0;i<fields.length;i++) {
		param += document.getElementById(fields[i]).value + "||";
		}

        document.getElementById("mboxRadioAdd").disabled = true;
        document.getElementById("mboxRadioAdd").innerHTML = "Please wait ...";

        mboxApp.requestAPI('POST',['data','radio',encodeURIComponent(title+'||'+param)],'', mboxRadioAdd_msg);
        }

function mboxRadioAdd_dialog(i) {
        var onclick2 = "document.getElementById('album_"+(i)+"').style.display='none';";
        var text     = "<b>"+lang("ADD_STREAM")+":</b><br/><br/><table>";
        text += "<tr><td>"+lang("TITLE")+":</td>		<td><input id=\"stream_title\" style=\"width:150px\"></input></td></tr>";
        text += "<tr><td>"+lang("DESCRIPTION")+":</td> 		<td><input id=\"stream_description\" style=\"width:150px\"></input></td></tr>";
        text += "<tr><td>"+lang("WEBSITE")+" URL:</td>  	<td><input id=\"stream_radio_url\" style=\"width:150px\"></input></td></tr>";
        text += "<tr><td>"+lang("STREAM")+" URL (m3u):</td>	<td><input id=\"stream_stream_url\" style=\"width:150px\"></input></td></tr>";
        text += "<tr><td>"+lang("LOGO")+" URL:</td>		<td><input id=\"stream_image_url\" style=\"width:150px\"></input></td></tr>";
        text += "</table><br/>";
        text += button("mboxRadioAdd();",lang("ADD"),"mboxRadioAdd");
        text += button(onclick2,lang("CLOSE"),"close_stream");
        setTextById("album_"+i,text);
        document.getElementById("album_"+i).style.display="block";
        }

function mboxRadioAdd_msg(data) {
        var text = "";
        if (data["REQUEST"]["status"] == "success")     { text += lang("STREAM_CREATED"); } 
        else                         		        { text += lang("STREAM_CREATED_ERROR"); } 
        appMsg.alert(text);
        mboxRadio_load()
        }

//----------------------------------------------------------------
// EOF
