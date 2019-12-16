//--------------------------------------
// jc://music-box/, (c) Christoph Kloth
//--------------------------------------
// multi-language support (implementation just started)
//--------------------------------------
// language[LANG][<param>]
// lang(<param>);

var LANG     = "EN";
var language = {
	"DE" : {
		"ADD"			: "Hinzug&uuml;gen",
		"ADD_PLAYLIST"		: "Playliste hinzuf&uuml;gen",
		"ADD_STREAM"		: "Stream hinzuf&uuml;gen",
                "ALREADY_CONNECTED_WITH": "Bereits verknüpft mit:",
		"ALBUM_CONNECTED_WITH"	: "Album ist bereits verknüpft mit:",
		"CARD_CONNECTED"	: "Karte ist bereits mit Medium verknüpft.",
		"CARD_CONNECTED_WITH"   : "Karte ist bereits verknüpft mit:",
		"CLOSE"			: "Schlie&szlig;en",
		"COVER_AVAILABLE"	: "Verf&uuml;gbare Cover",
		"COVER_IMAGES"		: "Cover-Bilder",
		"COVER_PRINT_VIEW_1"	: "Album-Cover für den Ausdruck:",
		"COVER_PRINT_VIEW_2"	: "Klicke auf ein Cover, um es auszublenden (z.B. wenn schon gedruckt).",
		"COVER_PRINT_VIEW_3"	: "Klicke hier, um diese Ansicht zu schließen.",
		"DATA_OLD_FORMAT"	: "Altes Datenformat oder keine Bilder vorhanden, Titelinfos neu laden!",
		"DESCRIPTION"		: "Beschreibung",
		"DEVICE"		: "Gerät",
		"DEVICE_UNKNOWN"	: "Gerät unbekannt",
		"EDIT"                  : "Bearbeiten",
		"HERE"                  : "hier",
		"INFORMATION"		: "Informationen",
		"LOADING_APP"		: "Starte App",
		"LIST_CONNECTED"        : "Playliste ist bereits verknüpft.",
		"LIST_CONNECTED_WITH"   : "Playliste ist bereits verknüpft mit:",
		"NEW"			: "neu",
                "NODATA_RELOAD"         : "Bislang ist die Datenkbak leer. Bitte Musikdateien ins Verzeichnis kopieren und über Einstellungen Daten neu laden.",
		"NOINFO_CONNECTED"	: "Keine Infos zu verknüpftem Medium.",
		"RFID_CARDS"		: "RFID-Karten",
		"SELECT_MUSIC_ITEM" 	: "Wähle einen Sender, ein Album oder eine Playlist aus ...",
		"SETTINGS"		: "Einstellungen",
		"TITLE"			: "Titel",
		},
	"EN" : {
		"ADD"			: "Add",
		"ADD_PLAYLIST"		: "Add playlist",
		"ADD_STREAM"		: "Add stream",
		"ALBUM_CONNECTED_WITH"	: "Album is already connected with:",
                "ALREADY_CONNECTED_WITH": "Already connected with:",
		"CARD_CONNECTED"	: "Card is already connected.",
		"CARD_CONNECTED_WITH"   : "Card is already connected with:",
		"CLOSE"			: "Close",
		"COVER_AVAILABLE"	: "Available cover",
		"COVER_IMAGES"		: "Cover Images",
		"COVER_PRINT_VIEW_1"	: "Print view for album cover:",
		"COVER_PRINT_VIEW_2"	: "Click onto a cover to hide (e.g. of already printed).",
		"COVER_PRINT_VIEW_3"	: "Click here to close this view.",
		"DATA_OLD_FORMAT"	: "Old dataformat or no images available, please reload data in the settings.",
		"DESCRIPTION"		: "Description",
		"DEVICE"		: "Device",
		"DEVICE_UNKNOWN"	: "Device unknown",
		"EDIT"                  : "Edit",
		"HERE"                  : "here",
		"INFORMATION"		: "Information",
		"LOADING_APP"		: "Loading App",
		"LIST_CONNECTED"        : "Playlist is already connected.",
		"LIST_CONNECTED_WITH"   : "Playlist is already connected with:",
		"NEW"			: "new",
		"NOINFO_CONNECTED"	: "No info for connected media.",
                "NODATA_RELOAD"         : "No entries in the database yet. Please copy music files to the data directory and reload data in the settings.",
		"RFID_CARDS"		: "RFID Cards",
		"SELECT_MUSIC_ITEM" 	: "Select a stream, album or playlist ...",
		"SETTINGS"		: "Settings",
		"TITLE"			: "Title",
		}
	}


function lang( param ) {
	if (lanuage[LANG][param]) 	{ return lanuage[LANG][param]; }
        else if (lanuage["EN"][param])  { return lanuage["EN"][param]; }
        else if (lanuage["DE"][param])  { return lanuage["DE"][param]; }
	else { return "<font color='red'>Translation not found</font>"; }
	}
