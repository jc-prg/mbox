//--------------------------------------
// jc://music-box/, (c) Christoph Kloth
//--------------------------------------
// Local Player -- ACTUAL
//--------------------------------------
/* INDEX:
function localPlayer(position=0, play=true)
function writeAudioPlayer(id,divid)
function myPlayer(id,divid)
*/
//--------------------------------------

var mboxPlayer;

function localPlayer(position=0, play=true) {
	//appMsg.confirm("<div id='localPlayer' style='width:100%;height:200px;'></div>","",280);

	if (!mboxPlayer) { mboxPlayer = new jcPlayer("mboxPlayer","audioPlayer", mbox_music_dir, mbox_cover_dir, "apps/"); }

	mboxPlayer.activeTrack              	  = position;
	//mboxPlayer.activeCtrl["buttons"]    	  = false;
	mboxPlayer.activeCtrl["info_cover"] 	  = false;
	mboxPlayer.activeCtrl["info_short"] 	  = true;
	mboxPlayer.activeCtrl["progress_padding"] = "0";

	mboxPlayer.init();

	//console.log(mbox_playlist_queue);

	if (play) {
		mboxPlayer.load(mbox_playlist_queue);
		mboxPlayer.play();
		}
	}

//--------------------------------------
// show audio player for one audio file -- OLD
//--------------------------------------

function writeAudioPlayer(id,divid) {
	var file = MusicDir + dataTracks[id]["file"];
	var text = "";
	text += dataTracks[id]["title"] + "<hr/>";
	text += "<audio controls style=\"width:100%\">";
	text += "<source src=\"" + file + "\" type=\"audio/mpeg\">";
	text += "</audio>";
	//text += file;

	setTextById(divid,text);
	}


function myPlayer(id,divid) {
	var file = "./mbox_music/" + dataTracks[id]["file"];
	var myaudio = new Audio(file);
	var text = "";
	text += dataTracks[id]["title"] + "<hr/>";
	text += "<button onclick=\"myaudio.play();\">play</button>";
	text += "<button onclick=\"myaudio.pause();\">pause</button>";
	text += myaudio.duration;

	setTextById(divid,text);
	}















