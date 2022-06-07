//--------------------------------------
// jc://music-box/, (c) Christoph Kloth
//--------------------------------------
// List radio channels and podcasts
//--------------------------------------


function mboxStreams_load(stream_uuid="-")  {

    appFW.requestAPI("GET",["db","radio",stream_uuid],"", [mboxStreams,stream_uuid]);
    scrollToTop();
    }

function mboxStreams_reload() {

    mboxStreams(data=mbox_list_data);
    }

function mboxStreams(data, uuid="") {

	mbox_list_data   = data;
	var entries_info = data["DATA"]["radio"];

	// create filter
	var filter     = "";
	var the_filter = [""];
	
	// info if no internet connect
	if (!internetConnect) {
		filter = "<center><font color='red'>"+lang("NO-INTERNET-STREAMS")+"</font></center>";
		}
	
	// create sort keys
	var sort_keys = ["title","description"];

	// create list view
	mboxViewsList(type="radio", data=entries_info, selected_uuid=uuid, filter_key=the_filter, filter_text=filter, sort_keys=sort_keys, callTrackList="mboxViewsTrackList", chapter_rows=false);
	}
	
function mboxStreamWriteAudioPlayer(title,file,divid) {

        var text = "";
        text += title + "<hr/>";
        text += "<audio controls style=\"width:100%\">";
        text += "<source src=\"" + file + "\" type=\"audio/mpeg\">";
        text += "</audio>";
        //text += file;

        setTextById(divid,text);
        }

function mboxStreamInfo_load(uuid) {

    appFW.requestAPI("GET",["data",uuid,"-"],"", mboxStreamInfo );
    }

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
                cover += mboxCoverAlbumInfo(4, album["cover_images"]["url"],    album["cover_images"]["active"], uuid);
                }
        else {
                cover += lang("DATA_OLD_FORMAT");
                }

	var edit = "";
        edit += mboxHtmlButton("image_add",	"mboxUploadImage('"+uuid+"','radio','"+album["title"]+"');",                     "red");
        edit += mboxHtmlButton("edit",  	"mboxStreamEdit_load('"+uuid+"');",                                                "red");
        edit += mboxHtmlButton("delete",  	"mboxAlbumDelete('"+album["title"]+": "+album["description"]+"','"+uuid+"');",   "red");

        var info_data = [
        	[ lang("TITLE"),		album["title"] ],
        	[ lang("DESCRIPTION"),		album["description"] ],
        	[ lang("INFORMATION"),		"<a href=\"" + album["stream_info"] + "\" target=\"_blank\">" + album["stream_info"] + "</a>" ],
		[ lang("STREAM")+" URL",	"<a href=\"" + album["stream_url"] + "\" target=\"_blank\">" + album["stream_url"] + "</a>" ],
		[ lang("STREAM")+" URL2",	"<a href=\"" + album["stream_url2"] + "\" target=\"_blank\">" + album["stream_url2"] + "</a>" ],
		[ lang("STREAM")+" UUID",	"<a href='" + url + "/' target='_blank'>" + uuid + "</a>" ],
		[ lang("CARD_ID"),		"<a style='cursor:pointer;' onclick='mboxCardList_load(\""+cardid+"\");'>"    + cardid + "</a>" ],
		];
        
        if (album["podcast"] && album["podcast"]["title"]) { var info_data_podcast = [
        	[ "LINE" ],
        	[ lang("TITLE"), 		album["podcast"]["title"] ],
        	[ lang("DESCRIPTION"),		album["podcast"]["description"] ],
        	[ lang("TRACKS"),		album["podcast"]["track_count"]+" Tracks" ],
        	[ lang("PUBLICATION"),		album["podcast"]["publication"] ],
        	[ lang("UPDATE"),		album["podcast"]["update_date"] ],
        	[ lang("INFORMATION"),		"<a href=\"" + album["podcast"]["stream_info"] + "\" target=\"_blank\">" + album["podcast"]["stream_info"] + "</a>" ],
        	[ "LINE" ] ]; 
        	Array.prototype.push.apply( info_data, info_data_podcast );
        	}

	info_data.push( [ lang("COVER_AVAILABLE"),	cover ] );
	info_data.push( [ "LINE" ] );
	info_data.push( [ lang("EDIT"), 		edit ] );

	mboxViews_InfoTable(title=lang("STREAM_INFORMATION"), info_data=info_data, height=450);
	}

function mboxStreamTrackInfo_load(stream_uuid, track_uuid) {

    appFW.requestAPI("GET",["data",stream_uuid,"-"],"", [ mboxStreamTrackInfo, track_uuid ] );
    }

function mboxStreamTrackInfo(data, track_uuid) {
        var text   = "";
        var stream = data["DATA"]["_selected"];
        var uuid   = data["DATA"]["_selected_uuid"];
        var track  = stream["podcast"]["tracks"][track_uuid];
        var url    = RESTurl + "api/data/"+uuid+"/--";

	var info_data = [
		[ lang("TITLE"), 		track["title"] ],
		[ lang("DESCRIPTION"), 	track["description"] ],
		[ lang("DURATION"), 		track["duration"] ],
		[ lang("PUBLICATION"),		track["publication"] ],
		[ lang("TRACK")+" URL",	"<a href=\"" + track["file"] + "\" target=\"_blank\">" + track["file"] + "</a>" ],
		[ lang("TRACK")+" UUID",	track_uuid ],
		[ lang("STREAM")+" UUID",	"<a href='" + url + "/' target='_blank'>" + uuid + "</a>" ],
		];
		
	if (track["image"]) {
		cover = "<img src='"+track["image"]+"' style='height:80px;border:solid 1px black;'/>";
		info_data.push( [ "LINE" ] );
		info_data.push( [ lang("COVER_AVAILABLE"), cover ] );
		}
		
	mboxViews_InfoTable(title=lang("TRACK_INFORMATION"), info_data=info_data, height=450);
	}

function mboxStreamInfo_close() {
	setTimeout(function(){ mboxStreams_load(); }, 2000);
        appMsg.hide();        
        }

function mboxStreamEdit_load(uuid)	{

    appFW.requestAPI("GET",["data",uuid,"uuid,title,description,stream_info,stream_url,stream_url2"],"", mboxStreamEdit );
    }

function mboxStreamEdit(data) 	{ mboxDataEdit(data); }

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
        mboxStreams_load();
        }

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
	var text		= "";
	var onclick		= "document.getElementById('album_"+(i)+"').style.display='none';";
	var width		= 150;        
	var table		= new jcTable("add_dialog");
	table.table_width	= "100%";
	table.columns 		= 2;
	table.cells_width	= ["120px",""];
        
	text += table.start();
	text += table.row_one( "<b>"+lang("ADD_STREAM")+":</b>" );
	text += table.row_one( "<hr/>" );
	text += table.row( [ lang("TITLE")+":",	"<input id=\"stream_title\" style=\"width:"+width+"px\"/>" ] );
	text += table.row( [ lang("DESCRIPTION")+":",	"<input id=\"stream_description\" style=\"width:"+width+"px\"/>" ] );
	text += table.row( [ lang("WEBSITE")+":",	"<input id=\"stream_radio_url\" style=\"width:"+width+"px\"/>" ] );
	text += table.row( [ lang("STREAM")+":",	"<input id=\"stream_stream_url\" style=\"width:"+width+"px\"/>"] );
	text += table.row( [ lang("LOGO")+" URL:",	"<input id=\"stream_image_url\" style=\"width:"+width+"px\"/>"] );
	text += table.row_one( "<hr/>" );
	text += table.row_one( button("mboxStreamAdd();",lang("ADD"),"mboxStreamAdd") + button(onclick,lang("CLOSE"),"close_stream") );
	text += table.end();
        
	setTextById("album_"+i,text);
	document.getElementById("album_"+i).style.display="block";
	}

function mboxStreamAdd_msg(data) {
        var text = "";
        if (data["REQUEST"]["status"] == "success")	{ text += lang("STREAM_CREATED"); } 
        else						{ text += lang("STREAM_CREATED_ERROR"); } 
        appMsg.alert(text);
        mboxStreams_load()
        }
