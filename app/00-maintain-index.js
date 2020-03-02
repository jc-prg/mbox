----------------------------
./mbox-upload-image.js (51)
----------------------------
function mboxUploadImage(uuid,category,name="")
function mboxUploadImageWrite(params)
----------------------------
./mbox-playlist.js (632)
----------------------------
function mboxPlaylistAllLoad(filter="",uuid="")
function mboxPlaylistAll(data)
function mboxAddListDialog(i)
function mboxPlaylistOneLoad2(uuid)
function mboxPlaylistOneLoad(i,uuid)
function mboxPlaylistOne(data)
function mboxPlaylistEditLoad(uuid)
function mboxPlaylistEdit(data)
function mboxPlaylistInfoLoad(uuid)
function mboxPlaylistInfo(data)
function mboxPlaylistInfoClose()
function mboxPlaylistEditEntryLoad(uuid)
function mboxReloadPlaylist(uuid)
function mboxDeletePlaylist(uuid,title)
function mboxPlaylistEditAlbumsLoad(uuid)
function mboxPlaylistEditAlbums(data)
function mboxPlaylistEditTracksLoad(uuid,source="")
function mboxPlaylistEditTracks(data)
function mboxTrackRowPL(data,uuid,split=false,uuid_pl="")
function mboxInfoDelete(data)
function mboxInfoAdd(data)
function add_playlist()
function add_playlist_msg(data)
----------------------------
./app-menu.js (108)
----------------------------
function jcMenu(name, menu, title)
	this.entry_link   = function (link,label)
	this.entry_script = function (script,label)
----------------------------
./mbox-settings.js (248)
----------------------------
function settingsToggle()
function settingsStatusLoad()
function settingsStatus (data)
function settingsStatus_PerformanceLoad()
function settingsStatus_Performance(data)
function mboxShowLoading(data)
function mboxShowJson(data)
function toggleCoverPrint()
function uploadImage()
function dict_size(d)
----------------------------
./mbox-html-elements.js (263)
----------------------------
function mboxCoverSeparator( content, cmd )
function mboxCoverList( uuid, cover="", description="", cmd_open="", cmd_play="", type="album" )
function mboxButton( button, cmd="", color="blue", small="", display="block" )
function mboxToolTip( type, count=0, input_text="" )
function mboxScrollTo( type, uuid="" )
function mboxAlbumDetail( count )
function show_data_object(data)
function mboxTableNew( cells=[], divide=false, width="100%", height="" )
function mboxTable(p1,p2="",p3="",p4="")
function input_element( name, data )
function button (onclick,label, id="")
function add_link(link, description="")
function clickMenu ()
function setNavTitle (title)
function setButtonConfig(data)
function image(file)
----------------------------
./00-maintain-index.js (-1)
----------------------------
----------------------------
./mbox-conf.js (-1)
----------------------------
----------------------------
./volume_slider.js (100)
----------------------------
function slider ( name, container, callOnChange )
----------------------------
./config_stage.js (-1)
----------------------------
----------------------------
./app-conf.js (-1)
----------------------------
----------------------------
./mbox-rfid.js (312)
----------------------------
function writeRFID(data)
function CardID(uuid)
function editCardDialogLoad1(uuid)
function editCardDialogLoad2(data)
function editCardDialog(data)
function mboxListCardsLoad()
function mboxListCards(data)
function mbox_delete_card(card_id,uuid_pl)
function editCard_save(data)
----------------------------
./mbox-control.js (558)
----------------------------
function mboxWriteGroups()
function mboxControlLoad()
function mboxControl (data)
function mboxControlChangePosition(e)
function mboxControlProgressPrint()
function mboxControlProgress()
function mboxControlProgressTime()
function mboxVolumeControl(volume, mute)
function mboxPlaylistControl(uuid)
function mboxShowUUID(uuid)
function mboxRadioControl(uuid)
function mboxShowPlaying(uuid,uuid_song,playing)
function mboxButton2( sendCmd, label )
function mboxControl_open()
function mboxCheckLoading(data)
function mboxCheckStatus ()
function mboxDeletePlaying ()
function mboxSetStatus (color)
function mboxToggleDevice ()
function mboxToggleFilter ()
----------------------------
./config_language.js (-1)
----------------------------
----------------------------
./mbox-data.js (88)
----------------------------
function showReturnMsg(data)
function mboxDataEdit(data)
function mboxDataEditExecute(uuid, key_list, type)
----------------------------
./mbox-album.js (661)
----------------------------
function mboxEmptyBelow()
function mboxWriteBelow(text)
function mboxAlbumAllLoad(filter="",uuid="")
function mboxAlbumAll(data)
function mboxAlbumAll_section(count,title,last_title)
function mboxAlbumAll_album(count,uuid,title,description,cover,cmd_open,cmd_play)
function mboxCreateAlbumFilter(data,selected)
function mboxCreateArtistFilter(data,selected)
function mboxAlbumLoad(i,uuid)
function mboxListAlbum(data)
function mboxTrackInfoLoad(uuid)
function mboxTrackInfo(data)
function mboxAlbumInfoLoad(uuid)
function mboxAlbumInfoClose()
function mboxAlbumInfo(data)
function mboxAlbumDelete(album,uuid)
function mboxAlbumTrackRow(id,dataTracks,album=true,artist=false,count=0)
function show_triangle(i)
function hide_triangle(i)
function mboxEmptyAlbum()
----------------------------
./mbox-player.js (78)
----------------------------
function localPlayer(position=0, play=true)
function writeAudioPlayer(id,divid)
function myPlayer(id,divid)
----------------------------
./app-main.js (149)
----------------------------
function appPrintMenu()
function appPrintStatus_load()
function appPrintStatus(data)
function appCheckUpdates_msg(data)
function appCheckUpdates()
----------------------------
./mbox-radio.js (316)
----------------------------
function mboxRadioLoadChannel(i,uuid)
function mboxRadioLoad()
function mboxRadio(data)
function mboxAddListDialog_Radio(i)
function mboxRadioChannel(data)
function writeAudioPlayerStream(title,file,divid)
function mboxRadioInfoLoad(uuid)
function mboxRadioInfo(data)
function mboxRadioEditLoad(uuid)
function mboxRadioInfoClose()
function mboxDeleteRadio(uuid,title)
function add_stream()
function add_stream_msg(data)
----------------------------
./mbox-cover.js (149)
----------------------------
function mboxAlbumInfoCover(nr,url_list,act,uuid)
function mboxAlbumCover(artist,album)
function mboxAlbumCover2(id,data)
function mboxAlbumCover_checkFile(image_url)
function listCoverStart()
function listCoverEnd()
function listCoverEntry(id,cover)
