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
		"DISC_SPACE"		: "Speicherplatz",
		"EDIT"                  : "Bearbeiten",
		"HERE"                  : "hier",
		"INFORMATION"		: "Informationen",
		"LIST_CONNECTED"        : "Playliste ist bereits verknüpft.",
		"LIST_CONNECTED_WITH"   : "Playliste ist bereits verknüpft mit:",
		"LOADING_APP"		: "Starte App",
		"LOADING_TIME"		: "Ladezeiten",
		"NEW"			: "neu",
                "NODATA_RELOAD"         : "Bislang ist die Datenkbak leer. Bitte Musikdateien ins Verzeichnis kopieren und über Einstellungen Daten neu laden.",
		"NOINFO_CONNECTED"	: "Keine Infos zu verknüpftem Medium.",
                "RELOAD_DATA"		: "Daten neu laden",
                "RELOAD_STARTED"	: "Reload gestartet",
                "RESTORE_FINISHED"	: "Wiederherstellung JSON 2 DB abgeschlossen.",
		"RFID_CARDS"		: "RFID-Karten",
		"SELECT_MUSIC_ITEM" 	: "Wähle einen Sender, ein Album oder eine Playlist aus ...",
		"SETTINGS"		: "Einstellungen",
		"TITLE"			: "Titel",
		"PLEASE_WAIT"		: "Bitte warten",
		"QUESTION_RELOAD"	: "Files komplett neu in DB laden?<br/>Playlisten im Anschluss nicht mehr nutzbar und RFID-Cards müssen neu verknüpft werden.",
		"QUESTION_LOAD_NEW"	: "Neue Files in DB laden?",
		"QUESTION_LOAD_IMG"	: "Neue Bilder in DB laden?",
		"QUESTION_RESTORE_JSON"	: "Daten aus JSON-Backup wiederherstellen in die CouchDB?",
		"QUESTION_BACKUP2JSON"	: "Backup der CouchDB in JSON-Files erstellen?",
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
		"DISC_SPACE"		: "Disc space",
		"EDIT"                  : "Edit",
		"HERE"                  : "here",
		"INFORMATION"		: "Information",
		"LIST_CONNECTED"        : "Playlist is already connected.",
		"LIST_CONNECTED_WITH"   : "Playlist is already connected with:",
		"LOADING_APP"		: "Loading App",
		"LOADING_TIME"		: "Loading Time",
		"NEW"			: "new",
		"NOINFO_CONNECTED"	: "No info for connected media.",
                "NODATA_RELOAD"         : "No entries in the database yet. Please copy music files to the data directory and reload data in the settings.",
                "RELOAD_DATA"		: "Reload data",
                "RELOAD_STARTED"	: "Reload started",
                "RESTORE_FINISHED"	: "Restore JSON 2 DB finished.",
		"RFID_CARDS"		: "RFID Cards",
		"SELECT_MUSIC_ITEM" 	: "Select a stream, album or playlist ...",
		"SETTINGS"		: "Settings",
		"TITLE"			: "Title",
		"PLEASE_WAIT"		: "Please wait",
		"QUESTION_RELOAD"	: "Reload all music files into the database?<br/>Playlists and connected RFID cards may have to be reconnected.",
		"QUESTION_LOAD_NEW"	: "Load new files into database?",
		"QUESTION_LOAD_IMG"	: "Reload images form directories into the database?",
		"QUESTION_RESTORE_JSON"	: "Transfer data from JSON files to CouchDB?",
		"QUESTION_BACKUP2JSON"	: "Backup data from CouchDB to JSON files?",
		}
	}


function lang( param ) {
	if (language[LANG][param]) 	 { return language[LANG][param]; }
        else if (language["EN"][param])  { return language["EN"][param]; }
        else if (language["DE"][param])  { return language["DE"][param]; }
	else { return "<font color='red'>Translation not found</font>"; }
	}
