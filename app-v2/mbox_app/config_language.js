//--------------------------------------
// jc://app-framework/, (c) Christoph Kloth
//--------------------------------------
// multi-language support (implementation just started)
//--------------------------------------
// language_app[LANG][<param>]
// add your app specific translations

var language_app = {
	"DE" : {
		"ADD"			: "Hinzuf&uuml;gen",
		"ADD_PLAYLIST"		: "Playliste hinzuf&uuml;gen",
		"ADD_STREAM"		: "Stream hinzuf&uuml;gen",
		"ADD_TRACK"		: "Track hinzufügen",
                "ALREADY_CONNECTED_WITH": "Bereits verknüpft mit:",
		"ALBUM"		: "Album",
		"ALBUMS"		: "Alben",
		"ALBUM_CONNECTED_WITH"	: "Album ist bereits verknüpft mit:",
		"ALBUM_COMPLETE"	: "Ganzes Album",
		"ALBUM_DELETED"	: "Album gelöscht.",
		"ALBUM_DELETE_ASK"	: "Album wirklich l&ouml;schen",
		"ALBUM_DELETE_ERROR"	: "Fehler beim Löschen des Albums aufgetreten.",
		"BAND_ARTIST"		: "Band / K&uuml;nstler",
		"CARD"			: "Karte",
		"CARD_CONNECTED"	: "Karte ist bereits mit Medium verknüpft.",
		"CARD_CONNECTED_WITH"	: "Karte ist bereits verknüpft mit:",
		"CARD_DELETED"		: "Karte gelöscht",
		"CARD_DELETE_ASK"	: "Karte wirklich löschen",
		"CARD_DELETE_ERROR"	: "Fehler beim Löschen der Karte aufgetreten.",
		"CARD_NOT_CONNECTED"	: "Keine Karte verknüpft.",
		"CARD_ID"		: "Karten-ID",
		"CARD_SELECT_TO_CONNECT": "Wähle ein Album, eine Playlist oder einen Webstream aus,<br/>der mit der Karte verlinkt werden soll:",
		"CARD_STARTED"		: "Karte gestartet.",
		"CATEGORY"		: "Kategorie",
		"CLOSE"		: "Schlie&szlig;en",
		"COVER_AVAILABLE"	: "Verf&uuml;gbare Cover",
		"COVER_IMAGES"		: "Cover-Bilder",
		"COVER_PRINT_VIEW_1"	: "Album-Cover für den Ausdruck:",
		"COVER_PRINT_VIEW_2"	: "Klicke auf ein Cover, um es auszublenden - z.B. wenn es schon gedruckt wurde.",
		"COVER_PRINT_VIEW_3"	: "Klicke hier, um diese Ansicht zu schließen.",
		"COVER_PRINT_VIEW_4"	: "Um Label für RFID-Karten zu erstellen, bitte einen Screenshot von 6 Bildern erzeugen und als 10x15 Photo ausdrucken lassen.",
		"DATA_OLD_FORMAT"	: "Altes Datenformat oder keine Bilder vorhanden, Titelinfos neu laden!",
		"DESCRIPTION"		: "Beschreibung",
		"DEVICE"		: "Gerät",
		"DEVICE_UNKNOWN"	: "Gerät unbekannt",
		"DISC_SPACE"		: "Speicherplatz",
		"DURATION"		: "Dauer",
		"EDIT"			: "Bearbeiten",
		"EMPTY_LIST"		: "Liste ist leer",
		"ERROR"		: "Fehler",
		"GENRE"		: "Genre",
		"HERE"			: "hier",
		"INFORMATION"		: "Informationen",
		"LIST_CONNECTED"	: "Playliste ist bereits verknüpft.",
		"LIST_CONNECTED_WITH"	: "Playliste ist bereits verknüpft mit:",
		"LOADING_APP"		: "Starte App",
		"LOADING_TIME"		: "Ladezeiten",
		"LOADING_DATA"		: "Lade Daten ...",
		"LOGO"			: "Logo",
		"NEW"			: "neu",
                "NODATA_RELOAD"	: "Bislang ist die Datenkbak leer. Bitte Musikdateien ins Verzeichnis kopieren und über Einstellungen Daten neu laden.",
		"NOINFO_CONNECTED"	: "Keine Infos zu verknüpftem Medium.",
		"NOT_FOUND"		: "nicht gefunden",
		"PLAYLIST"		: "Playliste",
		"PLAYLISTS"		: "Playlisten",
		"PLAYLIST_CREATED"	: "Playlist angelegt.",
		"PLAYLIST_CREATED_ERROR": "Fehler beim Anlegen der Playiste aufgetreten.",
		"PLAYLIST_EDIT"	: "Playliste bearbeiten",
		"PLAYLIST_EMPTY"	: "Leere Playliste",
		"PLAYLIST_DELETED"	: "Playliste gelöscht.",
		"PLAYLIST_DELETE_ASK"	: "Playliste wirklich l&ouml;schen",
		"PLAYLIST_DELETE_ERROR": "Fehler beim Löschen der Playliste aufgetreten.",
		"PLAYLIST_INFORMATION"	: "Information zu Playliste",
		"PLEASE_WAIT"		: "Bitte warten",
		"PUBLICATION"		: "Ver&ouml;ffentlichung",
		"PODCAST"		: "Podcast",
		"RELOAD"		: "neu laden",
		"RELOAD_DATA"		: "Daten neu laden",
		"RELOAD_STARTED"	: "Reload gestartet",
		"RESTORE_FINISHED"	: "Wiederherstellung JSON 2 DB abgeschlossen.",
		"RFID_CARDS"		: "RFID-Karten",
		"RFID_NEW_CARD"	: "Neue RFID Karte erkannt (nicht verlinkt)",
		"SELECT_MUSIC_ITEM" 	: "Starte ein Album, eine Playlist oder einen Stream aus ...",
		"SELECT_ARTIST"	: "Interpret/Band auswählen",
		"SETTINGS"		: "Einstellungen",
		"SIZE"			: "Gr&ouml;&szlig;e",
		"STREAM"		: "WebStream",
		"STREAM-PODCAST"	: "Stream / Podcast",
		"STREAMS"		: "WebStreams",
		"STREAM_CREATED"	: "WebStream angelegt.",
		"STREAM_CREATED_ERROR"	: "Fehler beim Anlegen des WebStreams aufgetreten.",
		"STREAM_EDIT"		: "WebStream bearbeiten",
		"STREAM_DELETED"	: "WebStream gelöscht.",
		"STREAM_DELETE_ASK"	: "WebStream wirklich löschen",
		"STREAM_DELETE_ERROR"	: "Fehler beim Löschen des WebStreams aufgetreten.",
		"STREAM_INFORMATION"	: "Information zum WebStream",
		"TITLE"		: "Titel",
		"TRACK"		: "Track",
		"TRACKS"		: "Tracks",
		"TRACK_INFORMATION"	: "Track Information",
		"TRACKS_INSIDE"	: "Enthaltene Tracks",
		"TRACK_DELETED"	: "Track gelöscht.",
		"TRACK_DELETE_ERROR"	: "Fehler beim Löschen der Playlist aufgetreten.",
		"QUESTION_RELOAD"	: "Files komplett neu in DB laden?<br/>Playlisten im Anschluss nicht mehr nutzbar und RFID-Cards müssen neu verknüpft werden.",
		"QUESTION_LOAD_NEW"	: "Neue Files in DB laden?",
		"QUESTION_LOAD_IMG"	: "Neue Bilder in DB laden?",
		"QUESTION_RESTORE_JSON": "Daten aus JSON-Backup wiederherstellen in die CouchDB?",
		"QUESTION_BACKUP2JSON"	: "Backup der CouchDB in JSON-Files erstellen?",
		"WEBSITE"		: "Webseite",
		},
	"EN" : {
		"ADD"			: "Add",
		"ADD_PLAYLIST"		: "Add playlist",
		"ADD_STREAM"		: "Add stream",
		"ADD_TRACK"		: "Add track",
		"ALBUM"		: "Album",
		"ALBUMS"		: "Albums",
		"ALBUM_CONNECTED_WITH"	: "Album is already connected with:",
		"ALBUM_COMPLETE"	: "Complete Album",
		"ALBUM_DELETED"	: "Album deleted.",
		"ALBUM_DELETE_ASK"	: "Delete album",
		"ALBUM_DELETE_ERROR"	: "Error while deleting album.",
                "ALREADY_CONNECTED_WITH": "Already connected with:",
		"BAND_ARTIST"		: "Band / Artist",
		"CARD"			: "Card",
		"CARD_CONNECTED"	: "Card is already connected.",
		"CARD_CONNECTED_WITH"	: "Card is already connected with:",
		"CARD_DELETED"		: "Card deleted.",
		"CARD_DELETE_ASK"	: "Delete card",
		"CARD_DELETE_ERROR"	: "Error while deleting card.",
		"CARD_ID"		: "Card ID",
		"CARD_NOT_CONNECTED"	: "No card connected.",
		"CARD_STARTED"		: "Card started.",
		"CARD_SELECT_TO_CONNECT": "Select an album, a playlist or a stream<br/>you want to connect to the card:",
		"CATEGORY"		: "Category",
		"CLOSE"		: "Close",
		"COVER_AVAILABLE"	: "Available cover",
		"COVER_IMAGES"		: "Cover Images",
		"COVER_PRINT_VIEW_1"	: "Print view for album cover:",
		"COVER_PRINT_VIEW_2"	: "Click onto a cover to hide it - e.g. if it already has been printed.",
		"COVER_PRINT_VIEW_3"	: "Click here to close this view.",
		"COVER_PRINT_VIEW_4"	: "To create labels that fit on a RFID card, create a screenshot of 6 covers and print it to a 10x15 photo.",
		"DATA_OLD_FORMAT"	: "Old dataformat or no images available, please reload data in the settings.",
		"DESCRIPTION"		: "Description",
		"DEVICE"		: "Device",
		"DEVICE_UNKNOWN"	: "Device unknown",
		"DISC_SPACE"		: "Disc space",
		"DURATION"		: "Duration",
		"EDIT"			: "Edit",
		"EMPTY_LIST"		: "List is empty",
		"ERROR"		: "Error",
		"GENRE"		: "Genre",
		"HERE"			: "here",
		"INFORMATION"		: "Information",
		"LIST_CONNECTED"	: "Playlist is already connected.",
		"LIST_CONNECTED_WITH"	: "Playlist is already connected with:",
		"LOADING_APP"		: "Loading App",
		"LOADING_TIME"		: "Loading Time",
		"LOADING_DATA"		: "Loading data ...",
		"LOGO"			: "Logo",
		"NEW"			: "new",
		"NOINFO_CONNECTED"	: "No info for connected media.",
		"NODATA_RELOAD"	: "No entries in the database yet. Please copy music files to the data directory and reload data in the settings.",
		"NOT_FOUND"		: "not found",
		"PLAYLIST"		: "Playlist",
		"PLAYLISTS"		: "Playlists",
		"PLAYLIST_CREATED"	: "Playlist created.",
		"PLAYLIST_CREATED_ERROR": "Error while creating playlist.",
		"PLAYLIST_DELETE_ASK"	: "Delete playlist",
		"PLAYLIST_DELETED"	: "Playlist deleted.",
		"PLAYLIST_DELETE_ERROR": "Error while deleting playlist.",
		"PLAYLIST_EDIT"	: "Edit playlist",
		"PLAYLIST_EMPTY"	: "Empty playlist",
		"PLAYLIST_INFORMATION"	: "Playlist Information",
		"PLEASE_WAIT"		: "Please wait",
		"PODCAST"		: "Podcast",
		"PUBLICATION"		: "Publication",
		"RELOAD"		: "reload",
		"RELOAD_DATA"		: "Reload data",
		"RELOAD_STARTED"	: "Reload started",
		"RESTORE_FINISHED"	: "Restore JSON 2 DB finished.",
		"RFID_CARDS"		: "RFID Cards",
		"RFID_NEW_CARD"	: "New RFID card detected (not connected)",
		"SELECT_MUSIC_ITEM" 	: "Start an album, a playlist or a stream ...",
		"SELECT_ARTIST"	: "Select artist",
		"SETTINGS"		: "Settings",
		"SIZE"			: "Size",
		"STREAM"		: "Stream",
		"STREAM-PODCAST"	: "Stream / Podcast",
		"STREAMS"		: "Streams",
		"STREAM_CREATED"	: "Stream created.",
		"STREAM_CREATED_ERROR"	: "Error while creating stream.",
		"STREAM_EDIT"		: "Edit stream",
		"STREAM_DELETED"	: "Stream deleted.",
		"STREAM_DELETE_ASK"	: "Delete stream",
		"STREAM_DELETE_ERROR"	: "Error while deleting stream.",
		"STREAM_INFORMATION"	: "Stream Information",
		"TITLE"		: "Title",
		"TRACK"		: "Track",
		"TRACKS"		: "Tracks",
		"TRACK_INFORMATION"	: "Track Information",
		"TRACKS_INSIDE"	: "Tracks inside",
		"TRACK_DELETED"	: "Track deleted.",
		"TRACK_DELETE_ERROR"	: "Error while deleting track.",
		"PLEASE_WAIT"		: "Please wait",
		"QUESTION_RELOAD"	: "Reload all music files into the database?<br/>Playlists and connected RFID cards may have to be reconnected.",
		"QUESTION_LOAD_NEW"	: "Load new files into database?",
		"QUESTION_LOAD_IMG"	: "Reload images form directories into the database?",
		"QUESTION_RESTORE_JSON": "Transfer data from JSON files to CouchDB?",
		"QUESTION_BACKUP2JSON"	: "Backup data from CouchDB to JSON files?",
		"WEBSITE"		: "Website",
		}
	}

