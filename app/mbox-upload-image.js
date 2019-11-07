// Upload image for album, playlist ...
//----------------------------------------------------------------

function mboxUploadImage(uuid,category,name="") {
        var text = "<b>"+name+"</b> ("+category+")<br/>";
        text    += "Cover-Bild hinzuf&uuml;gen / &auml;ndern / l&ouml;schen:<br/>&nbsp;<br/>" + defaultForm();
	var cmd  = "fileUpload( mboxUploadImageWrite, '" + uuid + "xXx" + category + "' );";

        appMsg.confirm(text,cmd,280,false);					// create dialog
	UploadDateien = [];							// empty var with file data
        enableUpload();								// enable upload
        document.getElementById("uploadbutton").style.display = "none";		// hide upload button from default form
        }

//----------------------------------------------------------------

function mboxUploadImageWrite(params) {
        param = params.split("xXx");
	//console.log("uuid:"+uuid);

        filename = document.getElementById('fName').value;
	if (filename == "") { filename = "-"; }

	if (param[1] == "album") 	{ mboxApp.requestAPI('PUT', [ 'images', 'upload', param[0], filename ], '', mboxAlbumAllLoad); }
	if (param[1] == "playlist") 	{ mboxApp.requestAPI('PUT', [ 'images', 'upload', param[0], filename ], '', mboxPlaylistAllLoad); }
	if (param[1] == "radio") 	{ mboxApp.requestAPI('PUT', [ 'images', 'upload', param[0], filename ], '', mboxRadioLoad); }
	else 				{ mboxApp.requestAPI('PUT', [ 'images', 'upload', param[0], filename ], ''); }
	appMsg.hide();
	}

