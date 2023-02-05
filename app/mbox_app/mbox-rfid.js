//--------------------------------------
// jc://music-box/, (c) Christoph Kloth
//--------------------------------------
// list and edit rfid card infos
//--------------------------------------

mboxCardUUID     = "";
mboxCardCID      = "";
mboxCardDetected = "";
mboxCardConnect_lists = {};


function mboxCardSimulate(card_uuid) {
	if (card_uuid.indexOf(",") < 0) { card_uuid = "test-card,"+card_uuid; }
	
	appFW.requestAPI('PUT',['set-card',card_uuid],'','');
	setTimeout(function() {appFW.requestAPI('PUT',['set-card','no_card'],'','');}, 5000);
	}

function mboxCardWriteRFID(data,known="",list={}) {
	var text = "";
	var rfid = data;

	if (!data) { return ""; }
	if (rfid && rfid != "") {
		text += "<br/>Karte erkannt: " + rfid;
		
		if (known == "unknown" && mboxCardDetected != rfid) { mboxCardConnect(rfid,list); }
		
		if (document.getElementById("edit_card")) { document.getElementById("edit_card").style.display = "block"; }
		if (document.getElementById("show_card")) { document.getElementById("show_card").style.display = "none"; }

		mboxControlSetStatus("blue");
		mboxCardDetected = rfid;
		}
	else {
		if (document.getElementById("edit_card")) { document.getElementById("edit_card").style.display = "note"; }
		if (document.getElementById("show_card")) { document.getElementById("show_card").style.display = "block"; }

		mboxControlSetStatus("gray");
		}

	return text;
	}

function mboxCardConnect(card,list={}) {
	var dialog   = "<b>"+lang("RFID_NEW_CARD") +":</b> " + card + "<br/>";
	dialog	    += lang("CARD_SELECT_TO_CONNECT") + "<br/>&nbsp;";
	dialog      += "<input id='mbox_select_connect' style='display:none' value='album_info'>";

	var cmd      = "mboxCardConnect_exe('"+card+"');";
	var select = {};
	for (var key in list) { select = { "album_info" : lang("ALBUMS")+" (Album)", "album_info_2" : lang("ALBUMS")+" (Artist)",
	                        "radio" : lang("STREAMS"), "playlists" : lang("PLAYLISTS") }; }

	list["select"] = select;
	mboxCardConnect_lists  = list;

    dialog += mboxCardConnect_fields();
	appMsg.confirm(dialog,cmd,250);
	}

function mboxCardConnect_fields(filter="", update="") {
    console.log("mboxCardConnect_fields: '"+filter+"', '"+update+"'");
    var dialog = "";
    if (filter == "") {
        var onchange   = "select_x=document.getElementById(\"mbox_select_type\").value;";
        onchange      += "mboxCardConnect_selectVisible(select_x);";
        onchange      += "document.getElementById(\"mbox_select_filter\").value = \"\";";
        onchange      += "mboxCardConnect_fields(\"-------\");";
        var onchange_2 = "select_x=document.getElementById(\"mbox_select_type\").value;";
        onchange_2    += "select_y=document.getElementById(\"mbox_select_filter\").value;";
        onchange_2    += "mboxCardConnect_fields(select_y, select_x);";
	    dialog += mboxCardConnect_select("mbox_select_type",     "select",       "block", onchange);
	    dialog += mboxCardConnect_filter("mbox_select_filter",   "block",        onchange_2);
	    }
	if (filter == "-------") { filter = ""; }
    dialog += mboxCardConnect_select("mbox_select_album_info",   "album_info",   "block", "", filter);
    dialog += mboxCardConnect_select("mbox_select_album_info_2", "album_info_2", "none",  "", filter);
    dialog += mboxCardConnect_select("mbox_select_playlists",    "playlists",	 "none",  "", filter);
    dialog += mboxCardConnect_select("mbox_select_radio",        "radio",		 "none",  "", filter);
    if (filter == "") {
    	return dialog;
    	}
    }
	
function mboxCardConnect_exe(rfid) {
	type = getValueById('mbox_select_connect');
	uuid = getValueById('mbox_select_'+type);
	appFW.requestAPI('PUT', ['cards', uuid, rfid ],'', mboxDataReturnMsg )
	}

function mboxCardConnect_filter(id, visible, onchange) {
	var text = "<input id='"+id+"' style='width:200px;margin:5px;' onKeyUp='"+onchange+"'></br>";
    var container = "<div id='"+id+"_div' style='display:"+visible+"'>";
    container += text;
    container += "</div>";
    return container;
    }

function mboxCardConnect_select(id, select, visible="block", onchange="", filter="") {
    var select = mboxCardConnect_lists[select];
	var order = sortDictByValue(select);
	var text = "<select id='"+id+"' style='width:200px;margin:5px;' onchange='"+onchange+"'>";
	for (var i=0;i<order.length;i++) {
	    var value = select[order[i]];
	    if (filter == "") {
	        text += "<option value='"+order[i]+"'>"+value+"</option>";
	        }
	    else if (value.toLowerCase().includes(filter.toLowerCase())) {
	        text += "<option value='"+order[i]+"'>"+value+"</option>";
	        }
	    }
	text += "</select><br/>";

    if (document.getElementById(id+"_div")) {
        document.getElementById(id+"_div").innerHTML = text;
//        document.getElementById(id+"_div").style.display = visible;
        }
    else {
        var container = "<div id='"+id+"_div' style='display:"+visible+"'>";
        container += text;
        container += "</div>";
        return container;
        }
	}
	
function mboxCardConnect_selectVisible(change) {
	var lists = ["album_info","album_info_2","playlists","radio"];
	for (var i=0;i<lists.length;i++) {
		if (lists[i] == change) {
		    elementVisible("mbox_select_"+change+"_div");  setValueById('mbox_select_connect',change);
		    }
		else {
		    elementHidden("mbox_select_"+lists[i]+"_div");
		    }
		}
	}

function mboxCardInfoIcon(entry_data, uuid) {
        var text = "";
        
        if ("card_id" in entry_data && entry_data["card_id"] != "") {
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
                
	return text;
	}

function mboxCardEditLink(uuid) {
        var text  = "";

        // visibility controlled in mbox_rfid.js (if card detected)
        var editCard = "mboxCardEditDialog_load1('"+uuid+"')";	//\""+card_id+"\",\""+uuid+"\",\""+uuid+"\",\"\");";
        text += "<div id=\"edit_card\" style=\"display:none\">" + mboxHtmlButton("card_edit", editCard, "red", "") + "</div>";

        return text;
        }

function mboxCardEditDialog_load1(uuid) {
    mboxCardUUID = uuid;
    appFW.requestAPI("GET", ["status"], "", mboxCardEditDialog_load2);
    }

function mboxCardEditDialog_load2(data)	{
    mboxCardCID = data["LOAD"]["RFID"];
    appFW.requestAPI("GET",["cards", mboxCardUUID], "", mboxCardEditDialog);
    }

function mboxCardEditDialog(data) {

	var exist1 = "";
	var exist2 = "";
	var rfid   = mboxCardCID;
	var uuid   = mboxCardUUID;

        var cards     = data["DATA"]["cards"];
        var radio     = data["DATA"]["radio"];
	var albums    = data["DATA"]["album_info"];
	var playlists = data["DATA"]["playlists"];

	var dialog = "";
	var cmd = "appFW.requestAPI('PUT', ['cards','" + uuid + "','" + rfid + "'],'', mboxCardEdit_save );";

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

function mboxCardList_load(card_id="-") {
    appFW.requestAPI("GET",["cards",card_id], "", mboxCardList);
    console.log("Load list of RFID-Cards...");
    }

function mboxCardList(data) {

	console.log("Load list of RFID-Cards... DATA LOADED");

	var title    = "";
        var cards    = data["DATA"]["cards"];
        var album    = data["DATA"]["album_info"];
        var playlist = data["DATA"]["playlists"];
        var radio    = data["DATA"]["radio"];
        
        try { selected = data["DATA"]["_selected_uuid"]; }   catch(e) { selected = ""; }
        try { filter   = data["DATA"]["_selected_filter"]; } catch(e) { filter   = ""; }
        
	var div0     = "<div class=\"rfid_list\">";
	var div1     = "<div class=\"rfid_entry\">";
	var div2     = "<div class=\"rfid_line\">";
	var div3     = "<div class=\"rfid_xxx\">";
	var divE     = "</div>";
	
	if (selected != "" || filter != "")	{ var filter_txt = " &nbsp;(<a onclick='mboxCardList_load();'>delete filter</a>)"; }
	else					{ var filter_txt = ""; }


        var text = "<center><b>Manage RIFD Cards:</b>"+filter_txt+"<hr/>";
        text += div0;

	if (typeof cards != "string" && Object.keys(cards).length > 0) {
           for (var card in cards) {
		
		var aa      = cards[card][0];
		var title1  = cards[card][1];
		var onclick = "";
		var type    = "";

                if (aa.indexOf("a_")>-1)  { img = "<img src=\""+mbox_icon_dir+mbox_icons["album_bw"]+"\" style=\"width:30px;height:30px;\"/>"; 	type = "album"; } //album
                if (aa.indexOf("p_")>-1)  { img = "<img src=\""+mbox_icon_dir+mbox_icons["playlist_bw"]+"\" style=\"width:30px;height:30px;\"/>";	type = "playlist"; } //playlist
                if (aa.indexOf("r_")>-1)  { img = "<img src=\""+mbox_icon_dir+mbox_icons["radio_bw"]+"\" style=\"width:30px;height:30px;\"/>"; 	type = "radio"; } //radio/webstream

		if (selected && selected != "" && card != selected) { continue; }
//		if (filter   && filter != "" && filter != type)	  { continue; }

		text    += div2; 
		text    += div3 + img + divE;


		text    += div1; //"<div style=\"float:left;height:70px;\">";
		text    += "<a href='"+ RESTurl + "api/data/"+card+"/-/' target='_blank'>" +card + "</a><br/><b>";
		//text    += cards[card][1] + cards[card][2] + ".";
		notfound = "<font color=\""+mbox_color[appTheme]["warning"]+"\">NOT FOUND ...</b></font><br/>("+aa+" / "+cards[card][1]+")";

                if (aa.indexOf("a_")>-1)   	{
			onclick = "mboxListLoad();setTimeout(function(){mboxAlbumList_load(1,\""+aa+"\");},1000);"
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
			onclick = "mboxStream_load();setTimeout(function(){mboxStreamChannel_load(1,\""+aa+"\");},1000);"
	                text += "<a style='cursor:pointer;' onclick='"+onclick+"'><small>";
			if (aa in radio) {
				text += radio[aa]["title"] + " / " + radio[aa]["description"] + "<br/>";
				//text += title1 + "<br/>";
				title = radio[aa]["title"];
				}
			else { text += notfound;  title = "";}
			//text += "Radio Channel"; 
			}
			
		text += "</small></a></b>" + divE;

		if (data["LOAD"]["RFID"] == card) 	{ color = "yellow"; }
		else					{ color = "red";    }

		text += div3; // + "<div style=\"margin:px;\">";
		text += mboxHtmlButton("play",  "appMsg.confirm('<br/>Karte &quot;" + card  + "&quot; ausführen und Album &quot;" + title + "&quot; starten?','mboxCardPlay_exec(#" + card + "#,#" + cards[card][0] + "#)',150)","green");
		text += mboxHtmlButton("delete","appMsg.confirm('<br/>Karte &quot;" + card  + "&quot; vom Album &quot;" + title + "&quot; l&ouml;sen?','mboxCardDelete_exec(#" + card + "#,#" + cards[card][0] + "#)',150)",color);
//		text += mboxHtmlButton("delete","mboxCardDelete(#" + card + "#,#" + cards[card][0] + "#);",color);
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

	if (selected && selected != "") { appMsg.confirm(text,"mboxCardList_load();",400); }
	else				 { appMsg.confirm(text,"",400); }
        //setTextById("remote1",text);
        }

function mboxCardDelete(card_id,title) {
	text    = lang("CARD_DELETE_ASK") + "?<br/> "+lang("TITLE")+": <b>"+title+"</b><br/>ID: "+card_id;
	cmd     = "mboxCardDelete_exec('"+card_id+"','"+title+"');";
	appMsg.confirm(text,cmd,150,true);
	}
	
function mboxCardDelete_exec(card_id,uuid) {

	appFW.requestAPI('DELETE',['data',card_id],'',[mboxCardDelete_msg,[card_id,uuid]]);
	}

function mboxCardPlay_exec(card_id, uuid) {
	appFW.requestAPI('PUT',['set-card',card_id],'',[mboxCardPlay_msg,[card_id,uuid]]);
	setTimeout(function(){ appFW.requestAPI('PUT',['set-card','no_card']); }, 5000);
	}

function mboxCardDelete_msg(data,cardid_uuid) {
	var cardid = cardid_uuid[0];
	var uuid   = cardid_uuid[1];
	mboxDataReturnMsg(data,lang("CARD_DELETED")+"<br/><b>"+cardid,lang("CARD_DELETE_ERROR")+"<br/><b>"+cardid);	
	mboxControlShowUUID(uuid);
	}

function mboxCardPlay_msg(data,cardid_uuid) {
	var cardid = cardid_uuid[0];
	var uuid   = cardid_uuid[1];
	mboxDataReturnMsg(data,lang("CARD_STARTED")+"<br/><b>"+cardid,lang("CARD_START_ERROR")+"<br/><b>"+cardid);
	mboxControlShowUUID(uuid);
	}

function mboxCardEdit_save(data) {

        mboxCardList_load();
	}

