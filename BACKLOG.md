# jc://mbox/backlog/

Here you'll find a history of features implemented into hardware and software as well as ideas what else to implement.

## ToDo

### IN PROGRESS

- ...

### KNOWN BUGS

- State Stopped -> not resetted?
- On the box the type in some cases isn't set correctly which leads to errors
- 
- ....
- BUG srv: looses internet connection from time to time; -> check if internet connect exists first
- BUG server -> after connecting card to album, the server has to be reload <-> the message "invalid entry connected" is spoken -> move all data to cache directly?
- BUG server - Start with STREAM and card laying on the RFID sensor leads to an error -> remove card_id, until connection is OK
- BUG app/server - if playlist with the same title already exists, two lists with the same tracks, id, and image are displayed => check server side?
- BUG check if audio device is connected -> show visible error message in client (restart of computer usually works)

- UNSTABLE app/server - Delete RFID Cards doesn't work the 2nd time {Error: mbox - GET / http://music-box:5005/api/cards/-/ (not available/4/500).}

### FEATURE IDEAS

- app/srv: check internet connection -> error message for streams, if no connection
- jc-player: +5 / -5 ; jump to position (like in remote player)
- app: Delete reference to picture / delete picture (if uploaded)
- app: track view (with out albums) -> preparation for additional filters
- app: filter with full text search ...
- app: filter for genres (or other metadata ...)

- app: volume doesn't work with iOS / Safari yet -> HTML5 audio processing?

- server: if data dir is not available ... error message (from LED / RFI / BUTTONS server ...)
- server: understandable return message in API response (even if successful)
- server: save presets in database and e.g. prefered device
- server: run mboxDB and mboxServer outside of a container (? faster start up)
- server: check and show voltage for RPi... "vcgencmd measure_volts core" ... sdram_i, sdram_p, sdram_c (problem, when recharging the battery)

## DONE

### BOX BASICS

* OK - Pi, Battery & Speaker in Box are installed
* OK - Wifi connected to JC-WIFI
* OK - Raspberry installed incl. basics (docker ...)
* OK - Container for mbox running
* OK - BUG - exchange speaker / noise reduction (different speakers: Hama)
* OK - BUG - speaker not not load enough ($ amixer set PCM -- 100%)
* OK - Backup is working
* OK - protection for speaker
* OK - fixing electronic parts in the box
* OK - Container for intranet running
* OK - prod stage ... rollout script is working
* OK - server in docker container working
* OK - BUG box - blue LED doesn't work correctly
* OK - Autohotspot

### BOX ENHANCEMENTS

* OK - RFID Reader to trigger playback of a playlist
* OK - detect "other cards" ... (13,56 MHz required)
* OK - 10 LED to display volume (4 green, 2 yellow, 2 red)
* OK - Power Button with LED (between powerbank and raspberry)
* OK - Buttons for Volume: Up, Down, Mute (as a microservice)
* OK - Cover for power bank and speakers
* OK - Storage for cards
* OK - Buttons for "Play Next", "Play last", "Pause/Play"
* OK - LED for server status (Docker is running, server is running, microservices are running, ...)
* OK - LED for "card detected"
* OK - LED for WiFi connection & Playback status
* OK - 3 stable connectors for LED, RFID and buttons

- cover for "deckel" inside

* DECLINED - Display for status (connection)
* DECLINED - ...     for track title ....
* DECLINED - server: check if connected to the internet in the background (in a thread) - optimized autohotspot configuration + bugfix dns-server

### SERVER

* OK - Install PYGAME to play audio
* OK - Play single audio file by REST-Request
* OK - add UUID to album incl. track list (for requests)
* OK - add image from jpg/png file in folder to album (if no image in mp3-file)
* OK - wait for RFID input (and push data to app)
* OK - increase / decrease volume
* OK - Play list of audio files by REST-Request
* OK - Play list in correct order
* OK - handle files in play list with index - not .pop()
* OK - optimize handling with image path (hard coded at the moment)
* OK - Reload data -> remove all cover-files
* OK - Reload data -> update existing entries (not overwrite)
* OK - Load Playlist ... list loaded with correct uuid, but 
  "UnicodeEncodeError: 'ascii' codec can't encode character u'\xf6' in position 44: ordinal not in range(128)"
  -> or just don't start playing?!
* OK - read playlists from db and return
* OK - create new playlist in db 
* OK - add entry of playlist in db
* OK - add/change RFID to album/playlist
* OK - ensure correct order in playlists
* OK - remove entry of playlist in db
* OK - start when known RFID detected (else stop, if unknown)
* OK - add function for mute
* OK - add function to request parts of the DB (list or element) ...  /mbox/list/<part>/ AND /mbox/list/<part>/<entry>/
* OK - volume LED initial sequence (each LED once)
* OK - display volume on LED
* OK - sample microservice (get volume via /mbox/list and display to LEDs)
* OK - delete card / RFID connection
* OK - Create class to control stream (incl. first json-file)
* OK - load/play/stop radio stream url 
* OK - list available streams from radio.json
* OK - BUG - set volume for streams also
* OK - BUG - stop radio if start album and return
* OK - music_ctrl -> different if radio!
* OK - add rfid card to radio channel
* OK - start radio channel if rfid card detected (stream_mpc.py)
* OK - used buttons for radio stream also (play/pause)
* OK - reduce volume of music box to adjust it to the stream volume a bit
* OK - display status of reload / write to music_ctrl (to show in web-interface) ... calculation and logging started
* OK - reload in background
* OK - separate prod/test data in different sub-directories of one main directory
* OK - separate prod/test hardware config (check config-file what stage should use hardware)
* OK - BUG - server_led.py doesn't work for 2 stages at the same time: switch on/off GPIO when active stage changes
* OK - BUG - last title should not be played in an endless loop
* OK - radio: read URL from m3u file and return for local playback
* OK - edit image for album
* OK - BUG - Buttons / LED error handling, if
* OK - read/load size of album (the check if loading via LTE is OK) - in bytes per track / album
* OK - transfer genre information from tracks to album (as list)
* OK - translate volume to pseudo logarithmic scale 
* OK - LED error / stage to status LEDs
* OK - BUG - set metadata if mp3-tags are empty & and set infos, if file format not supported
* OK - BUG - entry without album and artist name leads to wrong entry
* OK - Switch STREAM to vlc
* OK - move buttons to new API commands
* OK - move LED to new API command
* OK - create a representative set of test data
* OK - create data tracks by artists (to filter ...)
* OK - LED initialize & init when chip used (hard coded at the moment)
* OK - switch MP3 / M4A playback to vlc (supports other new formats as well)
* OK - radio: add/delete radio stream entry
* OK - CouchDB to store the data
  * OK - backup JSON files to CouchDB
  * OK - request data for /mbox/list_album/<uuid>/ from CouchDB 
  * OK - move functions into module
  * OK - more generic function to control music playback incl. switch to CouchDB
  * OK - ... functions to read data incl. switch to CouchDB
  * OK - ... functions to edit/delete playlists
  * OK - ... functions to delete albums
  * OK - ... more generic functions to edit / delete data incl. switch to CouchDB
  * OK - ... more generic functions to import metadata from files incl. switch to CouchDB
  * OK - reload leads to wrong data ... ?!
* OK - read metadata from mp4 files using MUTAGEN
* OK - read image data from mp4 filw
* OK - reduced data in couchDB["albums"] - track_uuid instead of full title information
* OK - optimized rea direct from DB vs. out of cache; refill cache in the background when change data in the database
* OK - calculate time left when reloading
* OK - connect usb device with songs (simple version ... mount & symbolic link)
* OK - BUG - when connected rfid card to album you've to switch on/off the box to used card
* OK - reload images
* OK - BUG - load new music files 
* OK - check if card already is connected when reloading music files (based on album and artist)
* OK - RFID module moved to separate service
* OK - transmit UUID when made operations with this UUID (to reload with focus on this element)
* OK - add file / albumpath as reference to tracks / albums in playlist (for recovery, to be implemented)
* OK - radio/playlist: edit entry metadata
* OK - OPTIMIZE ARCHITECTURE
  * OK  - PERFORMANCE optimization: decide, when to refresh cache, when to load direct from DB, and when to load from cache
  * OK - use swagger connexion[swagger-ui] to define API
  * OK - migrate python2 to python3 (no python3 module for RFID) - requires migration to swagger
  * OK - use PUT, DEL, GET ...
* OK - show space left on ssd card / USB stick; space left on system disk
* OK - measure durations during start process
* OK - BUG - current version doesn't read "Reisemaus/Ostsee" ...? -> Error in music files
* OK - BUG - Start radio channel by card doesn't work for all channels (starting via UI works) -> reread mp3-url when ever loaded - ignore comments in m3u-files
* OK - BUG - connecting to cards doesn't work anymore
* OK - API command to re-read data to cache, periodic re-read (not only on specific data changes - or ensure, no data change is forgotten)
* OK - BUG server - if card is not connect (wrong connected/connected with album which cannot be found?) -> error; after that no card is loaded any more:
* OK - if card not connected or wrong connected, speak message!
* OK - restart mboxServer and start autohotspot, if internet connection changes (autohotspot)
* OK - BUG fix extract images (mutagen API changed?)
* OK - BUG server - reconnect Cards when reloading data doesn't work
* OK - start with last song played before switched off
* OK - create HASH from files to reconnect (? additionally to filename ?)
* OK - BUG - when reading media files that are not OK
* OK - BUG - errors with HTTP server & CouchDB
* OK - Ping only once, if OK
* OK - server: if error in media files, group them in an album / or name album "#error" -> well visible in album list
* OK - BUG loading new data doesn't work correctly
* OK - BUG when detecting defect media files -> check is missing if already part of existing data (doubled data)
* OK - Move track sort from client to server, stabilize and simplify code (-> music_load.py)
* OK - BUG Reload data ... reference to playlist are not restored
* OK - Refactor music\_ctrl and stream\_ctrl -> in one library
* OK - Import and process podcast data
* OK - Handle podcast data as a playlist
* OK - Text2Speech for podcast titles (to navigate on the box)
* OK - BUG Stream doesn't start any more after refactoring
* OK - BUG srv: text2speech isn't played completely on the RPi -> other docker image (in progress)
* OK - BUG if 1 file is ready, does the next start? -> resource busy?
* OK - BUG server - if playing and press play in a playlist, start with first song instead of actuall running song (PlaySong -> start file, not list without loading list again) - reduced the errors
* OK - More detailed podcast information
* OK - BUG Play stream in local mode
* OK - ensure UTF-8 in the Dockerfile for filenames with special characters

* DECLINED - Play the whole song, not only parts // not seen any more
* DECLINED - dont delete playlist when stop: don't unload playlist/title if stop - just rewind to first position, but display now reflects situation


### CLIENT

* OK - send request to play an audio file
* OK - send request to stop playback
* OK - show RFID detection
* OK - show song running at the moment
* OK - single songs use play as for playlists
* OK - send request to play playlist (album)
* OK - show volume level
* OK - control volume (up / down)
* OK - control for running playlist/song ... and buttons to control playback (in 3rd frame ?)
  -> play, stop, pause, next, last
* OK - initial App-title
* OK - Load album details based on "album_info" and "tracks"
* OK - Load Playlists / single titles ... load with "undefined" as uuid (POTENTIALY FIXED)
* OK - Stop / Play for Playlist Control ... (stop, hold position, start position from the beginning, dont reload playlist)
* OK - load album details (incl. tracks) by sendCmd
* OK - mode "playlists"
* OK - show app title (change depending on function/mode -> all/playlists)
* OK - check if server and if update available (see jc://remote/)
* OK - setting page to reload db
* OK - setting page to show relevant data (summary)
* OK - create playlist
* OK - Reload mboxControl after every command
* OK - add/change RFID Key for albums
* OK - add/change RFID for playlist
* OK - ensure correct order in playlists
* OK - add/delete track from playlist
* OK - show list of rfid cards in db
* OK - UX design for control for playlist
* OK - show icon, if playing playlist or album
* OK - error handling if edding rfid connect
* OK - BUG - album image in album view if image2
* OK - add title to playlist:
  * OK -> appMsg.confirm: (1) Drop Down of Albums; 
  * OK ->              (2) Load Album titles after selection and list 
  * OK ->              (3) each title with a (+) and a (+) to add all titles
  * OK - BUG - appMsg.confirm -> place buttons dependend from height of msg-box
* OK - button for mute
* OK - album image in list mode if image2
* OK - delete RFID from album/playlist
* OK - edit rfid cards out of list ...
* OK - add function / button for mute (and set volume to 0, save old volume)
* OK - load list and show of web streams (radio)
* OK - control playback (play & load, stop) and show if playing (analog to albums)
* OK - radio - show if playing (analog to albums)
* OK - radio - mboxControl für Radio anpassen ... (ICON what is loaded, Title, Buttons ...)
* OK - set default icon radio
* OK - show if playing for playlists (analog to albums)
* OK - load album/playlist/radio info below the cover
* OK - buttons for album/playlist/radio in the top
* OK - connect radio to rfid card
* OK - 2 columns for mobile phone horizontal (css)
* OK - unpause if pressed play
* OK - BUG - performance issue: load only data that are required for next step
* OK - show radio channel information from mpc
* OK - BUG - stop radio/music if card detected
* OK - BUG - edit/show rfid cards after feature adding for radio ... and UX optimizing
* OK - check last loading -> show status if offline for a while (control and virtual LED)
* OK - show image for playlist (without upload)
* OK - show reload status (progress)
* OK - add image for playlist (Upload)
* OK - BUG - upload image -> change php.ini; set image size limit higher?!
* OK - sendCmd in "LED" top/right (see jc://remote/)
* OK - hide playing icon when disconnect
* OK - fullscreen view for 6 covers ... show page by page ... to create screenshots for print out
* OK - adaptive design for iPhone 5c
* OK - tooltip for albums (adaptive design)
* OK - connecting triangle between album cover and album details (opened)
* OK - Albums: separate when new character in album / artist name ...
* OK - Albums/Playlist: delete from data base -> to reload after editing with another software
* OK - enhanced player for playback via client (try to use freeware)
  * OK - BUG - right order of tracks
  * OK - buttons with icons as control
  * OK - show time infos while playing
  * OK - responsive and below the list
  * OK - show time left
  * OK - cover if in file or in mp3
  * OK - replace player for single tracks with this player
  * OK - optimize control (switch to hide control elements)
* OK - progressbar for music playing on mbox (remote)
* OK - show playing song in album
* OK - change playback commands to new server commands /mbox/ctrl/*/*/ (e.g. http://192.168.1.27:5006/mbox/ctrl/play/a_2605c8a6-de37-11e9-b8b8-b827eb13c62e/)
* OK - albums: (handle files without ID3 Tags ... Album/Arist name)
* OK - show chapter without cursor:pointer (CSS)
* OK - shorten track entries in playlists and albums
* OK - Check playlist functionality after changing backend / server (listing OK, editing and playback not yet tested)
* OK - add playlist out of list of playlists and optimized deletion / addition incl. an alert
* OK - add album image via upload (analog playlist) - show image is open (select if cover_image1,2,3)
* OK - detail info view for playlists and webstreams
* OK - add stream image via upload
* OK - local images for radio logo / default image for radio
* OK - BUG - show playing: not working when unloaded files ...?!
* OK - show playing: radio channel (mbox-radio.js / mbox-control.js => reuse div with ids ...)
* OK - show playing: playlist / song in playlist
* OK - BUG - detail view Playlist doesnt open if less than 6 tiles in the first row ... ?!
* OK - BUG - show playing album if only single title selected
* OK - show time left when reloading data
* OK - first filter based on directory (= category)
* OK - show blue light in APP when RFID card detected
* OK - show and scroll to album / playlist if done operation with this list
* OK - optimize playlist editing (reload is done automatically, optimized view of tracks to be added or deleted)
* OK - optimize RFID editing
* OK - BUG - if stop, no album/track info is shown any more?! -> OK, but mbox control and playing icon now reflect this
* OK - optimize CSS animation for mbox control
* OK - enable jcApp for PUSH, POST, DELETE ... and use XMLHttpRequest() 
* OK - filter for/group by artists
* OK - edit metadata for playlists and web-streams
* OK - show initial load time and running time in settings
* OK - new icon set, due to license reasons
* OK - several optimizations
* OK - enable multi-language support
* OK - BUG printAppStatusLoad not defined
* OK - BUG Settings displayed not correctly (on the box)
* OK - BUG hide menu when width of browser > XX Pixel (720?); see remote
* OK - BUG show filter from the beginning, if set "mbox_filter = true"
* OK - BUG app - jump to album doesnt work - no error detected 
* OK - BUG app - track delete from list (when not connected any more), doesn't work ... maybe, as used the same function as in edit dialog?
* OK - BUG app - create playlist -> missing translation ("pleases wait" on button)
* OK - new volume control
* OK - BUG app - edit playlist (if data is not connected correctly any more, e.g. due to reload)
* OK - cleaned code (readable functions, sorted into the right files)
* OK - BUG app - local player also for playlists (tracks & albums to be loaded)
* OK - BUG app - local player of streams doesn't work (plays last loaded album instead)
* OK - Button for filter
* OK - Queue for jcApp.requestAPI
* OK - BUG app - callback functions overwriten by second call?
* OK - timeout for API Request and reaction to the timeout (show error message) - required e.g. if parallel processes like a system update is running on the raspberry
* OK - BUG app - displayed order of tracks in playlist is not correct (playback order is OK)
* OK - app: jump +5 / -5 tracks
* OK - sort including disc numbers
* OK - if unknown card detect offer dialog to connect item
* OK - app: appMsg.confirm 
   * OK - place dialog in the middle depending on screen and dialog size (bit more above ...)
   * OK - if text bigger than box, scroll automatically
* OK - BUG app - deletion of card connection doesn't work (at least, if album not found ...)
* OK - BUG in jc://modules/ ... some API requests doesnt work (global var instead of locale)
* OK - app-framework as separate module -> submodule
* OK - include jc://modules/ as submodule
* OK - UNSTABLE app - loading albums and tracks to edit playlist doesnt work every time (on the box more often than on the computer)
* OK - BUG place triangle of album detail correctly
* OK - Smooth showing & hiding of the control panel (playing in formation)
* OK - BUG upload image -> alert("error 404") ... for playlist & stream also; upload php not found -> see ./modules/jc-upload/upload.js (upload.php fix defined)
* OK - optimize playlist view analogue to the album view (incl. 3 columns)
* OK - BUG Control Panel disappears from time to time when jumping to next song
* OK - BUG Control Panel disappears when playing stream (or playlist?)
* OK - BUG Deleting playlist entry with "not found" from list doesn't work
* OK - play in track of a playlist starts as part of the playlist (instead of single track)
* OK - BUG icons on local player buttons
* OK - simulate cardID in the settings
* OK - Handle podcasts as a specific type of streams -> playlist functionality
* OK - BUG jump in track
* OK - app: length of podcast (= x/1000?)
* OK - app: jump in a podcast (like in track)
* OK - BUG List of Cards doesn't work any more (only ID, no track infos) -> Dark Theme
* OK - BUG app: "empty album" isn't placed correctly for wider view incl. chapters
* OK - faster status reload if playing a song
* OK - Track Info for podcasts, more detailed podcast info, cover in list view
* OK - Last run for podcasts also -> last_run podcast (save / reload former data, intelligent reload ...)
* OK - Same list view for albums, playlists, streams - lists and tracks
* OK - BUG filter views, show details for the last row

