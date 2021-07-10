//--------------------------------------
// jc://music-box/, (c) Christoph Kloth
//--------------------------------------
// Upload image for album, playlist ...
//--------------------------------------
/* INDEX:
function mboxUploadImage(uuid,category,name="")
function mboxUploadImageWrite(params)
*/
//--------------------------------------

var mbox_upload_script = "modules/jc-upload/upload-0.2.0.php";   // jc://modules/jc-upload/
var mbox_upload_dir    = "../../mbox_img/cover_upload";    // dir relative to mbox_upload_script

//----------------------------------------------------------------

function mboxUploadImage(uuid,category,name="") {

	appUpload = undefined;
	appUpload = new jcUpload("appUpload", "");
	appUpload.uploadScript = mbox_upload_script;
	appUpload.callback     = mboxUploadImageWrite;
	appUpload.init(uploadPath=mbox_upload_dir, uploadType="", visibleValues=false, visibleButton=false);

	var form = appUpload.uploadForm(); 	
	var text = "<b>"+name+"</b> ("+category+")<br/>";
	text    += lang("COVER_ADD-CHANGE") + "<br/>&nbsp;<br/>" + form;
	var cmd  = "appUpload.fileUpload('" + uuid + "xXx" + category + "xXx" + "appUpload');";

	appMsg.confirm(text,cmd,280,false);					// create dialog
	}

//----------------------------------------------------------------

function mboxUploadImageWrite(params) {
        param = params.split("xXx");
	//console.log("uuid:"+uuid);

        filename = document.getElementById(param[2]+'_fName').value;
	if (filename == "") { filename = "-"; }
	
	appFW.requestAPI('PUT', [ 'images', 'upload', param[0], filename ], '', [mboxViewsList_load, param[1]]);
	appMsg.hide();
	}

//----------------------------------------------------------------
// EOF
