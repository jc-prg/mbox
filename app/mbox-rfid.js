//--------------------------------------
// jc://music-box/, (c) Christoph Kloth
//--------------------------------------
// list and edit rfid card infos
//--------------------------------------

mboxCardUUID = "";
mboxCardCID = "";

// show / hide info in <div id="edit_card">
//---------------------------------

function writeRFID(data) {
	var text = "";
	if (!data) { return ""; }
	var rfid = data;

	if (rfid && rfid != "") {
		text += "<br/>Karte erkannt: " + rfid;
		if (document.getElementById("edit_card")) { document.getElementById("edit_card").style.display = "block"; }
		if (document.getElementById("show_card")) { document.getElementById("show_card").style.display = "none"; }
		}
	else {
		if (document.getElementById("edit_card")) { document.getElementById("edit_card").style.display = "note"; }
		if (document.getElementById("show_card")) { document.getElementById("show_card").style.display = "block"; }
		}

	return text;
	}

// function for cards ....
//--------------------------------------

function CardID(uuid) {
        var text  = "";

        // visibility controlled in mbox_rfid.js (if card detected)
        var editCard = "editCardDialogLoad1('"+uuid+"')";	//\""+card_id+"\",\""+uuid+"\",\""+uuid+"\",\"\");";
        text += "<div id=\"edit_card\" style=\"display:none\">" + mboxButton("card_edit", editCard, "red", "") + "</div>";

        return text;
        }

// edit dialog ... // OFFEN -> RADIO
//---------------------------------

function editCardDialogLoad1(uuid) 	{ mboxCardUUID = uuid; 			mboxApp.requestAPI("GET",["status"],                "", editCardDialogLoad2); }
function editCardDialogLoad2(data)	{ mboxCardCID = data["LOAD"]["RFID"]; 	mboxApp.requestAPI("GET",["cards", mboxCardUUID],   "", editCardDialog); }
function editCardDialog(data) {

	var exist1 = "";
	var exist2 = "";
	var rfid   = mboxCardCID;
	var uuid   = mboxCardUUID;

        var cards     = data["DATA"]["cards"];
        var radio     = data["DATA"]["radio"];
	var albums    = data["DATA"]["album_info"];
	var playlists = data["DATA"]["playlists"];

	var dialog = "";
	var cmd = "mboxApp.requestAPI('PUT', ['cards','" + uuid + "','" + rfid + "'],'', editCard_save );";

	// check, if card detected ...
	if (rfid == "") { return; }
	console.log("Edit Dialog: " + rfid + "/" + uuid);

        // add rfid to album
	if (uuid.indexOf("a_") >= 0) {

	        var album   = {};;
		var cardID  = "";

		if (albums[uuid]) {
			album  = albums[uuid];
			if (album["card_id"]) 	{ cardID = album["card_id"]; }
			}

		// check if already connected
		if (cardID != rfid) {
			if (cardID.length > 0)  {
				exist1 += "<u>" + lang("NEW") + "</u> ";
				exist2 += lang("ALBUM_CONNECTED_WITH") + " " + cardID + "<br/>";
				}
			if (cards[rfid]) {
				exist2 += lang("CARD_CONNECTED_WITH") + "<br/>"+ cards[rfid][1];
				cmd = "";
				}
			}
		else {	exist2 += lang("CARD_CONNECTED");
			cmd = "";
			}

		// write message
		dialog += "<br/><b>Album und Karte "+exist1+"verknüpfen ...</b><br/>&nbsp;<br/>";
		dialog += "Album: "  + album["artist"] + " / " + album["album"] + "<br/>";
		dialog += "CardID: " + rfid + "<br/>";
		dialog += "<br/><i>" + exist2 + "</i>";
		}

	// add rfid to playlist
	if (uuid.indexOf("p_") >= 0) {

	        var album  = playlists[uuid];
		if (album["card_id"]) 	{ cardID = album["card_id"]; }
		else			{ cardID = ""; }

		// check if already connected
		if (cardID != rfid) {
			if (cardID.length > 0)  {
				exist1 += "<u>" + lang("NEW") + "</u> ";
				exist2 += lang("LIST_CONNECTED_WITH") + " " + cardID + "<br/>"; 
				}
			if (cards[rfid]) {
				exist2 += lang("CARD_CONNECTED_WITH") + " "+ cards[rfid][1];
				cmd = "";
			}	}
		else {	exist2 += lang("CARD_CONNECTED");
			cmd = "";
			}

		// write message
		dialog += "<br/><b>Playlist und Karte "+exist1+"verknüpfen ...</b><br/>&nbsp;<br/>";
		dialog += "Album: "  + album["title"] + " (" + album["description"] + ")<br/>";
		dialog += "CardID: " + rfid + "<br/>";
		dialog += "<br/><i>" + exist2 + "</i>";
		}

        // add rfid to radio channel
        if (uuid.indexOf("r_") >= 0) {

                var channel  = radio[uuid];
                if (channel["card_id"])   { cardID = channel["card_id"]; }
                else                      { cardID = ""; }

                // check if already connected
                if (cardID != rfid) {
                        if (cardID.length > 0)  {
				exist1 += "<u>" + lang("NEW") + "</u> ";
                                exist2 += "Channel bereits verknüpft mit: " + cardID + "<br/>"; 
                                }
                        if (cards[rfid]) {
                                exist2 += "Karte bereits verknüpft mit: "+ cards[rfid][1];
                                cmd = "";
                        }       }
                else {  exist2 += "Karte ist bereits mit Album verknüpft.";
                        cmd = "";
                        }

                // write message
                dialog += "<br/><b>Channel und Karte "+exist1+" verknüpfen ...</b><br/>&nbsp;<br/>";
                dialog += "Channel: " + channel["title"] + " (" + channel["description"] + ")<br/>";
                dialog += "CardID: " + rfid + "<br/>";
                dialog += "<br/><i>" + exist2 + "</i>";
                }

	appMsg.confirm(dialog, cmd, 250);
	}

// Show all defined RFID Cards ... later edit
//---------------------------------

function mboxListCardsLoad() { mboxApp.requestAPI("GET",["cards","-"], "", mboxListCards); console.log("Load list of RFID-Cards..."); }
function mboxListCards(data) {

	console.log("Load list of RFID-Cards... DATA LOADED");

	var title    = "";
        var cards    = data["DATA"]["cards"];
        var album    = data["DATA"]["album_info"];
        var playlist = data["DATA"]["playlists"];
        var radio    = data["DATA"]["radio"];

	var div0     = "<div class=\"rfid_list\">";
	var div1     = "<div class=\"rfid_entry\">";
	var div2     = "<div class=\"rfid_xxx\">";
	var divE     = "</div>";

        var text = "<center><b>Manage RIFD Cards:</b><hr/>";
        text += div0;

	if (! typeof cards) {
		console.log("test");
		console.log(data["DATA"]);
		//return;
		}


	if (typeof cards != "string" && Object.keys(cards).length > 0) {
           for (var card in cards) {
		text += div2; //"<div style=\"float:left;height:70px;\">";
                //text += "<div style=\"height:70px;width:30px;float:left;margin:2px;\">";
                //text += mboxButton("rfid","","yellow");
		//text += "</div>";

                var aa      = cards[card][0];
		var onclick = "";

                if (aa.indexOf("a_")>-1)   	{ //album
			text += div2 + "<img src=\""+mbox_icons["album_bw"]+"\" style=\"width:30px;height:30px;\"/>" + divE;
			}
                if (aa.indexOf("p_")>-1)   	{ //playlist
			text += div2 + "<img src=\""+mbox_icons["playlist_bw"]+"\" style=\"width:30px;height:30px;\"/>" + divE;
			}
                if (aa.indexOf("r_")>-1)   	{ //radio/webstream
			text += div2 + "<img src=\""+mbox_icons["radio_bw"]+"\" style=\"width:30px;height:30px;\"/>" + divE;
			}

		console.log(aa);

		text    += div1; //"<div style=\"float:left;height:70px;\">";
                text    += card + "<br/><b>";
		notfound = "<font color=\"red\">NOT FOUND ...</b></font><br/>("+aa+" / "+cards[card][1]+")";

                if (aa.indexOf("a_")>-1)   	{
			onclick = "mboxListLoad();setTimeout(function(){mboxAlbumLoad(1,\""+aa+"\");},1000);"
	                text += "<a style='cursor:pointer;' onclick='"+onclick+"'><small>";
			if (aa in album) {
				text += album[aa]["album"] + " / " + album[aa]["artist"] + "<br/>";
				title = album[aa]["album"];
				}
			else { text += notfound;  title = "";}
			}
                else if (aa.indexOf("p_")>-1 && aa in playlist) 	{
			onclick = "mboxPlaylistsLoad();setTimeout(function(){mboxPlaylistLoad(1,\""+aa+"\");},1000);"
	                text += "<a style='cursor:pointer;' onclick='"+onclick+"'><small>";
			if (aa in playlist) {
				text += playlist[aa]["title"] + "<br/>";
				title = playlist[aa]["title"];
				}
			else { text += notfound;  title = "";}
			}
		else if (aa.indexOf("r_")>-1) {
			onclick = "mboxRadioLoad();setTimeout(function(){mboxRadioLoadChannel(1,\""+aa+"\");},1000);"
	                text += "<a style='cursor:pointer;' onclick='"+onclick+"'><small>";
			if (aa in radio) {
				text += radio[aa]["title"] + " / " + radio[aa]["description"] + "<br/>";
				title = radio[aa]["title"];
				}
			else { text += notfound;  title = "";}
			//text += "Radio Channel"; 
			//title = "Radio";
			}

                text += "</small></a></b>" + divE;

		if (data["LOAD"]["RFID"] == card) 	{ color = "yellow"; }
		else					{ color = "red";    }

                text += div2; // + "<div style=\"margin:px;\">";
                text += mboxButton("delete","appMsg.confirm('<br/>Zuordnung zwischen Karte &quot;" + card  + "&quot; und Album &quot;" + title + "&quot; löschen?','mbox_delete_card(#" + card + "#,#" + cards[card][0] + "#)',150)",color);
		text += divE; // + divE;

		text += divE;
                }
	    }
	else if (Object.keys(cards).length == 0){
		text += "No card connected.<br/>";
		if (data["LOAD"]["RFID"]) { text += "Card detected: "+data["LOAD"]["RFID"]; }
		text
		}
	else {
		text += "ERROR in DB entry: &quot;"+cards+"&quot;";
		if (data["LOAD"]["RFID"]) { text += "Card detected: "+data["LOAD"]["RFID"]; }
		}
	text += divE + "</center>";
	//text += data["LOAD"]["RFID"];

	appMsg.confirm(text,"",400);
        //setTextById("remote1",text);
        }


function mbox_delete_card(card_id,uuid_pl) {

        //alert(card_id+"\n"+uuid_pl);
	//mboxApp.requestAPI("DELETE", ['cards', uuid_pl, card_id], "", editCard_save );
	mboxApp.requestAPI("DELETE", ['data', card_id], "", editCard_save );
	}


// save edit dialog ...
//---------------------------------

function editCard_save(data) {
        mboxListCardsLoad();
	}
