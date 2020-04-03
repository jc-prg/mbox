//--------------------------------------
// jc://music-box/, (c) Christoph Kloth
//--------------------------------------
// mbox configurations
//--------------------------------------

var mbox_music_dir     = "mbox_music/";
var mbox_cover_dir     = "cover/";
var mbox_cover_upl_dir = "cover_upload/";
var mbox_mode          = "Album";
var mbox_settings      = false;
var mbox_filter        = true;
var mbox_lastshow      = "";
var mbox_lastshow_song = "";
var mbox_cover_list    = [];
var mbox_icons     = {
	"album"       : "icon/cd.png",
	"playlist"    : "icon/list.png",
	"stream"      : "icon/stream.png",
        "playing"     : "icon/playing_25x25.gif",
        "radio"       : "icon/radio.jpg",
        "album_bw"    : "icon/album.png",
        "radio_bw"    : "icon/stream.png",
        "playlist_bw" : "icon/list.png",
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
