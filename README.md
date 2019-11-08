# jc://mbox/

A friend has built a similar box based on an existing free software. As my children where faszinated by this box I decided to build such a box for my children, but to write the software on my own from the scratch. My intentions is to try out different development practices. So it's not my idea but my individual implementation of this idea ...

![mbox image](https://raw.githubusercontent.com/jc-prg/mbox/master/docs/mbox.jpg)

## Whats inside

This software is built to play music (MP3 / M4A files and web-streams) on a _Raspberry Pi 3B+_ in a wooden box with speakers. It consists of:

- *Client* to show and manage content and control playback (JavaScript/HTML5/CSS)
- *Server* to import and manage content and control playback (Python3)
- *LED Server* to show volume and status via LED (Python3)
- *Button Server* to read commands via push buttons and send to main server (Python3)
- *RFID Server* to detect RFID cards (Python2)

The jc://mbox/ uses VLC (https://www.videolan.org/) and several other sources and is written in PYTHON (server) and JAVASCRIPT (client).

## Prerequisites

In order to use mbox as it is you must have installed:

1. docker, docker-compose
2. python3, pip3, python2, pip

## How to build the hardware

An instruction will follow soon ...
... in the meanwhile here are some [pictures](docs/BUILD_HARDWARE.md).

## How to install, configure and run the software

The *server software* has been tested on a Raspberry Pi 3B+ with Raspbian (2018-11-13-raspbian-stretch-lite) and on an Ubuntu Desktop. RFID reader, LED and Buttons only tested on the Raspberry Pi.

The *client software* has been tested with Chrome 70.0, Firefox 68.0 and Safari on iOS 13 (iPhone XS, iPhone SE).

1. Clone this repository and the modules

```bash
$ git clone https://github.com/jc-prg/mbox.git
$ git clone https://github.com/jc-prg/modules.git
```

2. Install python modules (CouchDB, VLC, eye3D, Mutagen, Connexion/swagger-ui,...)

```bash
$ ./mbox/config/install/install-server
$ ./mbox/config/install/install-rfid
```
3. Activate SPI on your Raspberry via rasp-config to use RFID reader

```bash
$ rasp-config
```

4. Edit configuration files

Customize your configuration depending on your directory structure and needs:

```bash
$ nano ./mbox/config/config_prod  # configure prod environment
$ nano ./mbox/config/config_test  # configure test environment
```

The tested directory structure is:

```bash
# project directories
/projects/git/
/projects/git/mbox/
/projects/git/modules/

# data directories (e.g. on mounted USB drive)
/projects_data/
/projects_data/test/
/projects_data/prod/

# structure inside the data directories
./couchdb/
./cover/
./cover_upload/
./data/
./music/

# default structure of music directories
./music/<category>/<artist>/<album>/*.*
```

5. Create working configuration (test or prod)

```bash
$ cd mbox/config
$ ./create_test               # create test environment

$ cd install
$ ./install-datadir           # create required sub-directories in data-dir
```

6. Copy music files to directory *./music/* (see suggested structure above)

7. Start server and client

```bash
# start client in docker container
$ cd ..
$ sudo docker-compose up -d

# start server
$ ./server/server.py         &
$ ./server/server_rfid.py    &
$ ./server/server_led.py     &
$ ./server/server_button.py  &
```

8. Open client and start "Reload Data" in the settings (e.g. http://localhost:85/ for PROD environment)

9. Optional: enable auto-start - add the following to */etc/rc.local*

```bash
# jc://mbox/ Server (if Raspberry Pi)
/usr/bin/python3 /projects/git/mbox/server/server_led.py     > /dev/null &
/usr/bin/python3 /projects/git/mbox/server/server_buttons.py > /dev/null &
/usr/bin/python2 /projects/git/mbox/server/server_rfid.py    > /dev/null &

# jc://mbox/ Server
/usr/bin/python3 /projects/git/mbox/server/server.py         > /dev/null &

# jc://mbox/ Client
/usr/bin/docker-compose -f /projects/git/mbox/docker-compose.yml up -d &

```

## Disclaimer

I'm just starting to publish my code and to work with GitHub. So the projects are not complete at the moment but will grow.
The software can be used "as is". I'll give no warranty that it works for you and is free of bugs. Ideas and suggestions what and how to improve are welcome.
