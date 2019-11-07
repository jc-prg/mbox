//--------------------------------------
// List radio channels
//--------------------------------------

// Load data albums and list ...
//--------------------------------------

function mboxRadioLoadChannel(i,uuid) {
        var count = 3;
        var width = document.body.clientWidth;
        if (width > 1250) { mbox_list_count = 6; }

        mbox_list_pos = ((Math.floor((i-1)/mbox_list_count)+1) * mbox_list_count );
        if (mbox_list_pos > mbox_list_amount) { mbox_list_pos = mbox_list_amount; }

        //mboxEmptyAlbum();
        mboxApp.requestAPI("GET",["data",uuid,"-"],"", mboxRadioChannel );
        }


//--------------------------------------

function mboxRadioLoad()             { mboxApp.requestAPI("GET",["db","radio","-"],"", mboxRadio); }
function mboxRadio(data) {
        var text          = "";
	var print 	  = listCoverStart();
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
             var cmd_open = "mboxEmptyAlbum();mboxRadioLoadChannel('"+(i+1)+"','" + uuid + "');"; 
	     var cmd_play = "mboxApp.requestAPI('GET',['play', '" + uuid + "'],'',mboxControl);";
             var cover    = default_cover;

             // check cover
             cover = mboxAlbumCover2(uuid,radio_data);

             // print playlist cover
             text += mboxScrollTo( "start", uuid );
             text += mboxToolTip( "start" );

             // write cover
             text += mboxCoverList( uuid, cover, "<b>" + key + "</b><br/>WebRadio", cmd_open, cmd_play );
             if (cover != "") { print += listCoverEntry( uuid, cover ); }

             // write tooltip
             text += mboxToolTip( "end", i+1, "<b>" + key + "</b>" );
             text += mboxScrollTo( "end" );
             text += mboxAlbumDetail( i+1 );

	     a = i+1;
             }

        var onclick = "mboxAddListDialog_Radio("+(a+1)+");";
	text += mboxCoverSeparator( "+", onclick );
	text += mboxAlbumDetail( a+1 );

        mbox_list_amount = sorted_r.length+1;
	print += listCoverEnd();

	setTextById("remote4", ""); // no filter defined yet
        setTextById("remote2", text);
        setTextById("ontop",   print);
        }


function mboxAddListDialog_Radio(i) {
        var onclick2 = "document.getElementById('album_"+(i)+"').style.display='none';";
        var text     = "<b>Web-Stream / Radio hinzufügen:</b><br/><br/><table>";
        text += "<tr><td>Radio:</td>           <td><input id=\"stream_title\" style=\"width:150px\"></input></td></tr>";
        text += "<tr><td>Beschreibung:</td>    <td><input id=\"stream_description\" style=\"width:150px\"></input></td></tr>";
        text += "<tr><td>Radio URL:</td>       <td><input id=\"stream_radio_url\" style=\"width:150px\"></input></td></tr>";
        text += "<tr><td>Stream URL (m3u):</td><td><input id=\"stream_stream_url\" style=\"width:150px\"></input></td></tr>";
        text += "<tr><td>Logo URL:</td>        <td><input id=\"stream_image_url\" style=\"width:150px\"></input></td></tr>";
        text += "</table><br/>";
        text += button("add_stream();","Hinzufügen","add_stream");
        text += button(onclick2,"Schließen","close_stream");
        setTextById("album_"+i,text);
        document.getElementById("album_"+i).style.display="block";
        }




// List albums tracks of an album
//--------------------------------------

function mboxRadioChannel(data) {

        var text          = "";
        var uuid          = data["DATA"]["_selected_uuid"];
        var radio_data    = data["DATA"]["_selected"];
        var default_cover = mbox_icons["radio"];

        // log ...
        console.debug("Show Radio Channel: " + uuid + "/" + radio_data["title"]);

        // Check if Cover exists
        cover = mboxAlbumCover2(uuid,radio_data);
        if (!cover) { cover = default_cover; }

        // Write album cover
        text += "<div class=\"album_cover\" style=\"background:url("+cover+");background-size:contain;background-position:center;background-repeat:no-repeat;\" onclick='" + onclick + "'>";
        text += "</div>";

        // write album infos
        text += "<div class=\"album_infos new\">";
        text +=   "<b>" + radio_data["title"] + "</b><br/><i>" + radio_data["description"] + "</i><br/>";
        text += "</div>";
        text += mboxButton("exit",  "mboxEmptyBelow();", "opac",   "small small2");

        // player control (in box)
        text += "<div class=\"album_control new\">";
        text += "<div class=\"player_active big\" id=\"playing_"+uuid+"\" style=\"display:none;\"><img src=\""+mbox_icons["playing"]+"\" style=\"height:20px;width:24px\"></div>";
	if (mbox_device != "local") {
      		text += mboxButton("play",  "mboxApp.requestAPI('GET',['play', '" + uuid + "'],'',mboxControl);", "blue");
        	text += mboxButton("stop",  "mboxApp.requestAPI('GET',['stop'],'',mboxControl);", "blue");
        	text += mboxButton("empty");
		}

        text += mboxButton("info",  "mboxRadioInfoLoad('"+uuid+"');",  "red");

        // show and edit rfid card
        if ("card_id" in radio_data)        {
                text += "<div id=\"show_card\">";
                text += mboxButton("rfid",  "", "green");
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
	        writeAudioPlayerStream(radio_data["title"],radio_data["stream_url2"],"audioPlayer");
		}
        }


// show audio player for one audio file
//--------------------------------------

function writeAudioPlayerStream(title,file,divid) {

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

function mboxRadioInfoLoad(uuid) { mboxApp.requestAPI("GET",["data",uuid,"-"],"", mboxRadioInfo ); }
function mboxRadioInfo(data) {
        var text   = "";
        var album  = data["DATA"]["_selected"];
        var uuid   = data["DATA"]["_selected_uuid"];

        var url    = RESTurl + "mbox/read/radio/"+uuid+"/";
        var size   = Math.round(album["albumsize"]/1024/1024*100)/100;
        var cardid = album["card_id"]; if (!cardid) { cardid = "Keine Karte verkn&uuml;pft."; }

	var cover  = "";
        if (album["cover_images"]) {
                cover += mboxAlbumInfoCover(1, album["cover_images"]["track"],  album["cover_images"]["active"], uuid);
                cover += mboxAlbumInfoCover(2, album["cover_images"]["dir"],    album["cover_images"]["active"], uuid);
                cover += mboxAlbumInfoCover(3, album["cover_images"]["upload"], album["cover_images"]["active"], uuid);
                cover += mboxAlbumInfoCover(4, album["cover_images"]["web"],    album["cover_images"]["active"], uuid);
                }
        else {
                cover += "Altes Datenformat oder keine Bilder vorhanden, Titelinfos neu laden!";
                }

	var edit = "";
        edit += mboxButton("cover", "mboxUploadImage('"+uuid+"','radio','"+album["title"]+"');",                     "red");
        edit += mboxButton("edit",  "mboxRadioEditLoad('"+uuid+"');",                                                "red");
        edit += mboxButton("exit",  "mboxAlbumDelete('"+album["title"]+": "+album["description"]+"','"+uuid+"');",   "red");

        text += "<b>Stream Informationen</b><br/><br/>";
        text += mboxTableNew("start");
        text += "<tr><td colspan='2'><hr></td></tr>";
        text += mboxTableNew(["<i>Title:",              album["title"] ] );
        text += mboxTableNew(["<i>Description:",        album["description"] ] );
        text += mboxTableNew(["<i>Info:",	        "<a href=\"" + album["stream_info"] + "\" target=\"_blank\">" + album["stream_info"] + "</a>" ] );
        text += mboxTableNew(["<i>Stream:",	        "<a href=\"" + album["stream_url"] + "\" target=\"_blank\">" + album["stream_url"] + "</a>" ] );
        text += mboxTableNew(["<i>UUID:",               "<a href='" + url + "/' target='_blank'>" + uuid + "</a>" ] );
        text += mboxTableNew(["<i>Card ID:",            "<a style='cursor:pointer;' onclick='mboxListCardsLoad();'>"    + cardid + "</a>" ] );
        text += mboxTableNew(["<i>Verf&uuml;gbare Cover:",      cover ] );
        text += "<tr><td colspan='2'><hr></td></tr>";
        text += mboxTableNew(["<i>Bearbeiten:",         edit ] );
        text += "<tr><td colspan='2'><hr></td></tr>";
        text += mboxTableNew("end");

        appMsg.confirm(text,"",450);
        }

//----------------------------------------

function mboxRadioEditLoad(uuid) { mboxApp.requestAPI("GET",["data",uuid,"uuid,title,description,stream_info,stream_url,stream_url2"],"", mboxDataEdit ); }
// -> mbox-data.js

//----------------------------------------

function mboxRadioInfoClose() {
	setTimeout(function(){ mboxRadioLoad(); }, 2000);
        appMsg.hide();        
        }

// delete playlist (dialog to confirm)
//---------------------------

function mboxDeleteRadio(uuid,title) {
        text    = "Webstream <b>"+title+"</b> wirklich l&ouml;schen?";
        cmd     = "mboxApp.requestAPI(#DELETE#,[#data#,#"+uuid+"#],##, mboxRadioLoad);";
        appMsg.confirm(text,cmd,150,true);
        }

//----------------------------------------------------------------

function add_stream() {
	var fields = ["stream_description","stream_radio_url","stream_stream_url","stream_image_url"];
	var param  = "";
	var title = document.getElementById("stream_title").value;

	for (var i=0;i<fields.length;i++) {
		param += document.getElementById(fields[i]).value + "||";
		}

        document.getElementById("add_stream").disabled = true;
        document.getElementById("add_stream").innerHTML = "Please wait ...";

        mboxApp.requestAPI('POST',['data','radio',encodeURIComponent(title+'||'+param)],'', add_stream_msg);
        }

function add_stream_msg(data) {
        var text = "";
        if (data["StatusMsg"] == "success")     { text += "Webradio / Stream angelegt."; }
        else                                    { text += "Beim Anlegen des Webradios ist ein Fehler aufgetreten."; }
        appMsg.alert(text);
        mboxRadioLoad()
        }


