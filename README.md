# jc://music-box/

A friend has built a similar box based on an existing free software (which I've never seen myself). As my children where faszinated by this box I decided to build such a box for my children, but to write the software on my own from the scratch. My intentions is to try out different development practices. So it's not my idea but my individual implementation of this idea ...

![mbox image](https://raw.githubusercontent.com/jc-prg/mbox/master/docs/mbox.jpg)

## Table of Contents

- [What's inside](#whats-inside)
- [How to build the hardware](#how-to-build-the-hardware)
- [How to setup the software](#how-to-setup-the-software)
  - [Initial Raspberry Pi setup](#initial-raspberry-pi-setup)
  - [Prerequisites](#prerequisites)
  - [How to install, configure and run the software](#how-to-install-configure-and-run-the-software)
- [Disclaimer](#disclaimer)

## What's inside

This software is built to play music (MP3 / M4A files and web-streams) on a _Raspberry Pi 3B+_ in a wooden box with speakers. It consists of:

- *Client* to show and manage content and control playback (JavaScript/HTML5/CSS)
- *Server* to import and manage content and control playback (Python3)
- *LED Server* to show volume and status via LED (Python3)
- *Button Server* to read commands via push buttons and send to main server (Python3)
- *RFID Server* to detect RFID cards (Python2)

The jc://mbox/ uses VLC (https://www.videolan.org/) and several other sources and is written in PYTHON (server) and JAVASCRIPT (client).

## How to build the hardware

An instruction will follow soon ... in the meanwhile here are some [pictures](docs/INSTRUCTION_BUILD_HARDWARE.md).

## How to setup the software

### Initial Raspberry Pi setup

If you want to use a fresh Raspberry Pi image, additional guidance can be found [here](docs/INSTRUCTION_PREPARE_RPI.md).

### Prerequisites

In order to use jc://music-box/ as it is you must have installed:

1. git
2. docker, docker-compose
3. python3, pip3, python2, pip

The *server software* has been tested on a Raspberry Pi 3B+ with [Raspbian](docs/INSTRUCTION_PREPARE_RPI.md) and on an Ubuntu Desktop. RFID reader, LED and Buttons only tested on the Raspberry Pi.

The *client software* has been tested with Chrome 70.0, Firefox 68.0 and Safari on iOS 13 (iPhone XS, iPhone SE).

### How to install, configure and run the software

1. Clone this repository and the modules

```bash
$ git clone https://github.com/jc-prg/mbox.git
$ git clone https://github.com/jc-prg/modules.git
```

2. Install python modules (CouchDB, VLC, eye3D, Mutagen, Connexion/swagger-ui,...) - please note, that this part isn't fully tested at the moment.

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
$ cd mbox/config/
$ cp sample.config_prod config_prod     # create local configuration
$ nano config_prod                      # configure prod environment
```

   The tested directory structure is:

```bash
# project directories
/projects/prod/
/projects/prod/mbox/
/projects/prod/modules/

# data directories (e.g. on mounted USB drive)
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
$ ./create_prod               # create prod environment

$ cd install
$ ./install-datadir           # create required sub-directories in data-dir, chmod 777 for cover_upload
```

6. Copy music files to directory *./music/* (see suggested structure above) or see 10. to connect an USB device with the music files to your Raspberry. Using an USB device makes it easier to add or change the music files ...

7. Set the maximum loudness of the Raspberry to 100% (per default it's to low):

```bash
$ amixer set PCM -- 100%
```

8. Start server and client

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

9. Open client and start "Reload Data" in the settings (e.g. http://localhost:85/ for PROD environment)

```bash
# Default URL:
# - http://localhost:85/          - Client
# - http://localhost:5005/api/ui  - Swagger UI API description
# - http://localhost:5105/_utils  - Fauxton CouchDB access (default user:mbox; pwd:mbox)

```

10. Optional: enable auto-start - add the following to */etc/rc.local*

```bash
# jc://mbox/ server modules (if Raspberry Pi)
/usr/bin/python3 /projects/prod/mbox/server/server_led.py     > /dev/null &
/usr/bin/python3 /projects/prod/mbox/server/server_buttons.py > /dev/null &
/usr/bin/python2 /projects/prod/mbox/server/server_rfid.py    > /dev/null &

# jc://mbox/ main server, client and database
/usr/bin/docker-compose -f /projects/prod/mbox/docker-compose.yml up -d &
```

11. Optional: mount USB device for music data

```bash
# to mount a USB device once:
$ cd /media
$ mkdir usb
$ mount /dev/sda1 /media/usb/

# to mount a USB on start up add this line to the /etc/rc.local (alternatively you can add a line to /etc/fstab)
/dev/sda1 /media/usb auto nosuid,nodev,nofail 0 0

# create a symlink to the right directory on you USB stick
$ ln -s /media/usb/Music /projects_data/prod/music
```

## Disclaimer

I'm just starting to publish my code and to work with GitHub. So the projects are not complete at the moment but will grow.
The software can be used "as is". I'll give no warranty that it works for you and is free of bugs. Ideas and suggestions what and how to improve are welcome.

