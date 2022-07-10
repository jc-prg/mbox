# jc://music-box/ - Release Notes

## Summary v1.0.x (in progress)

* Fix & optimize list view for albums, playlists and streams / podcasts
* Introduced automated unit testing for server

## Summary v0.9.x

* Add podcasts as streams -> URL .xml / .rss / .podcast in stream_url (itunes-format, instead of m3u)
* Optimized playback status display
* Optimized wiring for LED to create stable connectors

## Summary v0.8.x

* Create dark theme
* Integrate [jc://modules/](https://github.com/jc-prg/modules) as sub-module
* Move app functionality to the repository [jc://app-framework/](https://github.com/jc-prg/app-framework) and integrate as submodule
* Several bugfixes

## Summary v0.7.x

* restart playlist where switched off
* additional LED for Wi-Fi and playback status
* optimized autohotspot installation incl. encrypted Wi-Fi password
* Stabilized API calls
* Playlist editing optimized
* New volume slider
* Local playback via browser for playlists and streams
* Extended ID3 metadata
* Improved playlist editing
* Improved RFID card connection
* Introduced language configuration file (in progress)
* Automatic update via start script

## Summary till v0.6

The following list summarizes the main functionality of the jc://music-box/:

### Albums

* List albums, filter albums by category (first level of directories) or author from metadata
* Play albums and single files (*.mp3, *.m3a) remote
* Play albums and single music files locally in the browser
* Import music files (*.mp3, *.m3a) from albums including metadata and images
* Import images from album directories
* Upload pictures
* Connect RFID Cards
* Show details

### Playlists

* Create and edit playlists
* Upload pictures
* Add and delete single music files or complete albums
* Connect RFID Cards
* Show details

### WebStreams

* Play web-streams from URL (*.m3u file)
* Create and edit web-streams
* Upload pictures
* Connect RFID cards
* Show details

### Other Client

* List RFID cards, remove connection
* List cover images, to create screenshots for foto print out (9x13cm)

### Server

* Playback audio files with vlc
* Detect RFID cards
* Show volume and system status with LEDs
* Control playback via push buttons
* Connect to your Wi-Fi for internet connection and app control
* Create hotspot if your Wi-Fi is not available
* Support main errors with spoken messages 

