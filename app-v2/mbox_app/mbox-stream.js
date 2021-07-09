//--------------------------------------
// jc://music-box/, (c) Christoph Kloth
//--------------------------------------
// List radio channels
//--------------------------------------
/* INDEX:
function mboxStreams_load(stream_uuid="-")
function mboxStreams_reload()
function mboxStreams(data, uuid="")
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


// Load stream views
//--------------------------------------

function mboxStreams_load(stream_uuid="-")  { appFW.requestAPI("GET",["db","radio",stream_uuid],"", [mboxStreams,stream_uuid]); scrollToTop(); }
function mboxStreams_reload() { mboxStreams(data=mbox_list_data); }
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
                cover += mboxCoverAlbumInfo(4, album["cover_images"]["url"],    album["cover_images"]["active"], uuid);
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
        text += mboxHtmlTableNew(["<i>"+lang("STREAM")+" URL2:",	"<a href=\"" + album["stream_url2"] + "\" target=\"_blank\">" + album["stream_url2"] + "</a>" ] );
        text += mboxHtmlTableNew(["<i>"+lang("STREAM")+" UUID:",	"<a href='" + url + "/' target='_blank'>" + uuid + "</a>" ] );
        text += mboxHtmlTableNew(["<i>"+lang("CARD_ID")+":",		"<a style='cursor:pointer;' onclick='mboxCardList_load(\""+cardid+"\");'>"    + cardid + "</a>" ] );
        
        if (album["podcast"] && album["podcast"]["title"]) {
		text += "<tr><td colspan='2'><center><i><hr/>Podcast Info<hr/></i></center></td></tr>";
		text += mboxHtmlTableNew(["<i>"+lang("TITLE")+":",           album["podcast"]["title"] ] );
		text += mboxHtmlTableNew(["<i>"+lang("DESCRIPTION")+":",     album["podcast"]["description"] ] );        	        
		text += mboxHtmlTableNew(["<i>"+lang("TRACKS")+":",	       album["podcast"]["track_count"]+" Tracks" ] );        	        
		text += mboxHtmlTableNew(["<i>"+lang("PUBLICATION")+":",     album["podcast"]["publication"] ] );
		text += mboxHtmlTableNew(["<i>"+lang("UPDATE")+":",	       album["podcast"]["update_date"] ] );
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
	setTimeout(function(){ mboxStreams_load(); }, 2000);
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
        mboxStreams_load();
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
        var text     = "<b>"+lang("ADD_STREAM")+":</b><br/><hr/>";
        var width    = 150;
        
	text += mboxHtmlTableNew("start");
	text += mboxHtmlTableNew([lang("TITLE")+":",		"<input id=\"stream_title\" style=\"width:"+width+"px\"/>"]);
	text += mboxHtmlTableNew([lang("DESCRIPTION")+":",	"<input id=\"stream_description\" style=\"width:"+width+"px\"/>"]);
	text += mboxHtmlTableNew([lang("WEBSITE")+":",	"<input id=\"stream_radio_url\" style=\"width:"+width+"px\"/>"]);
	text += mboxHtmlTableNew([lang("STREAM")+":",		"<input id=\"stream_stream_url\" style=\"width:"+width+"px\"/>"]);
	text += mboxHtmlTableNew([lang("LOGO")+" URL:",	"<input id=\"stream_image_url\" style=\"width:"+width+"px\"/>"]);        
	text += "<tr><td colspan='2'><hr/>";
	text += button("mboxStreamAdd();",lang("ADD"),"mboxStreamAdd");
	text += button(onclick2,lang("CLOSE"),"close_stream");
	text += "</td></tr>";
	text += mboxHtmlTableNew("end");

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

//----------------------------------------------------------------
// EOF
