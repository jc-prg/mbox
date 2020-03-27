//--------------------------------------
// jc://music-box/, (c) Christoph Kloth
//--------------------------------------
// Local Player -- ACTUAL
//--------------------------------------
/* INDEX:
function mboxPlayerLocal(position=0, play=true)
*/
//--------------------------------------

var mboxPlayer;

function mboxPlayerLocal(position=0, play=true) {
	//appMsg.confirm("<div id='mboxPlayerLocal' style='width:100%;height:200px;'></div>","",280);

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
// EOF
