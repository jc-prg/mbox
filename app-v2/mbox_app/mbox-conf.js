//--------------------------------------
// jc://music-box/, (c) Christoph Kloth
//--------------------------------------
// mbox configurations
//--------------------------------------

var mbox_music_dir     = "mbox_music/";
var mbox_cover_dir     = "mbox_img/cover/";
var mbox_cover_upl_dir = "mbox_img/cover_upload/";
var mbox_mode          = "Album";
var mbox_settings      = false;
var mbox_filter        = true;
var mbox_lastshow      = "";
var mbox_lastshow_song = "";
var mbox_cover_list    = [];
var mbox_icon_dir	= "mbox_img/icon/";
var mbox_icons     = {
	"album"	: "mbox_img/icon/cd.png",
	"playlist"	: "mbox_img/icon/list.png",
	"stream"	: "mbox_img/icon/stream.png",
        "playing"	: "mbox_img/icon/playing_25x25.gif",
        "radio"	: "mbox_img/icon/radio.jpg",
        "album_bw"	: "mbox_img/icon/album.png",
        "radio_bw"	: "mbox_img/icon/stream.png",
        "playlist_bw"	: "mbox_img/icon/list.png",
	}
var mbox_track_color = [ "",
	"lightseagreen","turquoise",
	"indianred","darksalmon"
	]

var mbox_playlist       = {};
var mbox_playlist_queue = {};
var mbox_device         = "remote";
var mbox_show_char      = true;

//--------------------------------------
// EOF
