//----------------------------

var mbox_music_dir     = "./mbox_music/";
var mbox_cover_dir     = "./cover/";
var mbox_cover_upl_dir = "./cover_upload/";
var mbox_mode          = "Album";
var mbox_settings      = false;
var mbox_filter        = false;
var mbox_lastshow      = "";
var mbox_lastshow_song = "";
var mbox_cover_list    = [];
var mbox_icons     = {
	"album"       : "img/cd2.png",
	"playlist"    : "img/playlist.png",
	"stream"      : "img/stream.png",
        "playing"     : "img/playing.gif",
        "radio"       : "img/radio.jpg",
        "album_bw"    : "img/cd_bw.png",
        "radio_bw"    : "img/radio_bw.png",
        "playlist_bw" : "img/playlist_bw.png",
	}

var mbox_playlist       = {};
var mbox_playlist_queue = {};
var mbox_device         = "remote";
var mbox_show_char      = true;

//----------------------------

function mboxToggleMode() {
	if (mbox_mode == "Album")         { mbox_mode = "Playlist"; }
	else if (mbox_mode == "Playlist") { mbox_mode = "Radio"; }
	else                              { mbox_mode = "Album"; }

	//appMenu.set_title( appTitle + "/" + mbox_mode );
	}


//----------------------------

function mboxTooltipLeft(i) {
        var count = 3;
        var width = document.body.clientWidth;
        if (width > 705) { mbox_list_count = 6; }
        else             { mbox_list_count = 3; }

        // calculate if last album in row, than tooltip should show to the left
        var pos = i-(Math.floor(i/mbox_list_count) * mbox_list_count);
        if (pos == 0) { return " left"; }
        }

