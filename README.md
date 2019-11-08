# jc://mbox/

This software is built to play music (MP3 / M4A files and web-streams) on a _Raspberry Pi 3B+_ in a wooden box with speakers. It consists of:

- *Client* to show and manage content and control playback (JavaScript/HTML5/CSS)
- *Server* to import and manage content and control playback (Python3)
- *LED Server* to show volume and status via LED (Python3)
- *Button Server* to read commands via push buttons and send to main server (Python3)
- *RFID Server* to detect RFID cards (Python2)

The jc://mbox/ uses VLC (https://www.videolan.org/) and several other sources and is written in PYTHON (server) and JAVASCRIPT (client).

## Idea behind the box

A friend has built a similar box based on an existing free software. As my children where faszinated from this box I decided to build such a box for my children, but to write the software on my own from the scratch to try out different development practices. So it's not my idea but my individual implementation of this idea.

## Prerequisites

In order to use mbox as it is you must have installed:

1. docker (https://docs.docker.com/engine/installation/)
2. docker-compoye (https://docs.docker.com/compose/install/)
3. python3, python2, pip, pip3

## How to build the hardware

An instruction will follow soon ...

## How to install, configure and run the software

The software has been tested on a Raspberry Pi 3B+ with Raspbian (2018-11-13-raspbian-stretch-lite) and on an Ubuntu Desktop. RFID reader, LED and Buttons only tested on the Raspberry Pi.

1. Clone this repository and the modules

```bash
git clone https://github.com/jc-prg/mbox.git
git clone https://github.com/jc-prg/modules.git
```

2. Install python modules (CouchDB, VLC, eye3D, Mutagen, Connexion/swagger-ui,...)

```bash
cd mbox/config/install
./install-server
./install-rfid
```
3. Activate SPI on your Raspberry via rasp-config to use RFID reader

```bash
rasp-config
```

4. Edit configuration files
5. Create working configuration (test or prod)
6. Run server and client
7. optional: enable auto-start

## Disclaimer

I'm just starting to publish my code and to work with GitHub. So the projects are not complete at the moment but will grow.
The software can be used "as is". I'll give no warranty that it works for you and is free of bugs. Ideas and suggestions what and how to improve are welcome.
