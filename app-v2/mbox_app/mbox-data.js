//--------------------------------------
// jc://music-box/, (c) Christoph Kloth
//--------------------------------------
// Edit data (playlist and web-stream)
//--------------------------------------
/* INDEX:
function mboxDataReturnMsg(data={},success="",error="")
function mboxDataEdit(data,callback)
function mboxDataEditExecute(uuid, key_list, type)
*/
//--------------------------------------

//-----------------------------

function mboxDataReturnMsg(data={},success="",error="") {

	if (success == "") { success = "OK!"; }
	if (error   == "") { error   = "Error!"; }
	
	if (data["REQUEST"]["status"] == "success" && !data["REQUEST"]["error"]) {
		appMsg.alert(success);
		}
	else if (data["REQUEST"]["status"] == "success" && data["REQUEST"]["error"]) {
		appMsg.alert(error + "<br/>("+data["REQUEST"]["error"]+")");
		}
	else {
		appMsg.alert(error);
		console.warn("Unknown data returned.");
		}
	}

//--------------------------------------

function mboxDataEdit(data,callback) {

        var text        = "";
	var key_list    = "";
        var album       = data["DATA"]["_selected"];
        var uuid        = data["DATA"]["_selected_uuid"];
        var type        = data["DATA"]["_selected_db"];
	var sort_keys   = data["REQUEST"]["db_filter"];
	var sorted_keys = [];

	if (sort_keys.indexOf(",") >= 0) { sorted_keys = sort_keys.split(","); }

	text += "<div style='width:100%;height:350px;border:0px;overflow:auto'>";
        text += "<b>Edit " + type + "</b><br/><br/>";
	text += "<hr/>";
        text += mboxHtmlTableNew("start");

	if (sorted_keys.length == 0) { for (var key in album) {
		var star = "";
		if (typeof album[key] == "string") { key_list += key + ","; star = "*"; }
		text     += mboxHtmlTableNew(["<i>"+key+":</i>", mboxHtmlInputElement("edit_"+key, album[key]), star ]);
		} }
	else { for (var i=0;i<sorted_keys.length;i++) {
		if (typeof album[sorted_keys[i]] == "string") { key_list += sorted_keys[i] + ","; }
		text     += mboxHtmlTableNew(["<i>"+sorted_keys[i]+":</i>", mboxHtmlInputElement("edit_"+sorted_keys[i], album[sorted_keys[i]]) ]);
		} }

        text += mboxHtmlTableNew("end");
	text += "<hr/>";
	text += "</div>";

        appMsg.confirm(text,"mboxDataEditExecute('"+uuid+"','" + key_list + "','" + type + "');",400);
        }

//--------------------------------------

function mboxDataEditExecute(uuid, key_list, type) {
	var data     = {};
	var callback = "";
	var keys     = key_list.split(",");

	//alert(uuid + ", " + key_list);

	for (var i=0;i<keys.length;i++) { if (keys[i] != "") {
		if (document.getElementById('edit_'+keys[i])) {
			data[keys[i]] = document.getElementById('edit_'+keys[i]).value;
			}
		}}
	if (type == "radio")      	{ callback = mboxStreams_load; }
	else if (type == "playlists")	{ callback = mboxPlaylists_load; }
	else				{ callback = appMsg.hide; }
	
	console.error("EDIT EXECUTE"+type);

	appFW.requestAPI("PUT", ["data",uuid], data, callback );
	}

//--------------------------------------
// EOF
	
