//--------------------------------------
// jc://music-box/, (c) Christoph Kloth
//--------------------------------------
// mbox configurations
//--------------------------------------

var mbox_music_dir     = "mbox_music/";
var mbox_cover_dir     = "mbox_img/cover/";
var mbox_cover_upl_dir = "mbox_img/cover_upload/";
var mbox_mode          = "album";
var mbox_last_uuid     = "";
var mbox_settings      = false;
var mbox_filter        = true;
var mbox_lastshow      = "";
var mbox_lastshow_song = "";
var mbox_cover_list    = [];
var mbox_icon_dir	= "mbox_img/icon/";		// -> see "function app_theme_changed(theme)" in config_main.js
var mbox_icons     = {
	"album"	: "cd.png",
	"playlist"	: "list.png",
	"stream"	: "stream.png",
        "playing"	: "playing_25x25.gif",
        "radio"	: "radio.jpg",
        "album_bw"	: "album.png",
        "radio_bw"	: "stream.png",
        "playlist_bw"	: "list.png",
	}
var mbox_track_color = [ "",
	"lightseagreen","turquoise",
	"indianred","darksalmon"
	];
	
var mbox_color = {
	"dark"    : {
		"warning" : "yellow"
		},
	"default" : {
		"warning" : "red"
		}
	}	

var mbox_playlist       = {};
var mbox_playlist_queue = {};
var mbox_device         = "remote";
var mbox_show_char      = true;

//--------------------------------------
// EOF
