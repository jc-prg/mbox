# jc://music-box/image

## Table of Contents

- [Prepare your Raspberry Pi](#prepare-your-raspberry-pi)
  - [Download Image](#download-image)
  - [Write image to SD-card](#write-image-to-sd-card)
  - [Configure the Raspberry](#configure-the-raspberry)
- [Update Software and Prepare Project Directories](#update-software-and-prepare-project-directories)
  - [Update Software](#update-software)
  - [Create Directories](#create-directories)
  - [Install Docker and Docker-Compose](#install-docker-and-docker-Compose)
- [Install Additional Tools (optional)](#install-additional-tools-optional)

## Prepare your Raspberry Pi

For a faster starting and a better experience it's recommended to use a _Raspberry Pi 4_. Nevertheless Raspberry Pi 3B+ will do a good job also, but it will need more to to start.

### Install Image

Use Raspberry Pi Imager to install Raspberry OS Lite: [https://www.raspberrypi.com/software/](https://www.raspberrypi.com/software/).

### Configure the Raspberry

Connect a keyboard and a screen and start the raspberry, to do the initial configuration.

```bash
$ sudo raspi-config
```

Initial configuration:

* Set keyboard layout: *Localisation options* > *Change Keyboard Layout*
* Enable ssh server: *Boot options* > *SSH*
* Change password for user pi: *Change User Password*
* Connect to your wifi/network: *Network options* > *Wi-fi*
* Resize partition: *Advanced options* > *Expand filesystem* (requires reboot)
* Identify your IP4 address:

```bash
$ ipconfig
```

From now on you can work remote via ssh. Maybe you have to configure your router, that the raspberry will get the same 
IP4 address all the time. It's also recommended to change the hostname to "music-box"

```bash
$ sudo nano /etc/hostname
```

## Update Software and Prepare Project Directories

### Update Repositories and Software:

```bash
$ sudo apt-get update
$ sudo apt-get upgrade
```

### Install Git:

```bash
$ sudo apt-get install git
```

### Create directories:

```bash
$ sudo cd /
$ sudo mkdir projects
$ sudo chown pi.pi projects

$ sudo mkdir projects_data
$ sudo chown pi.pi projects_data

$ cd projects/
$ mkdir test
$ mkdir prod

$ cd ../projects_data/
$ mkdir test
$ mkdir prod
```

### Install Docker and Docker-Compose:

Use the following script to install [./config/install-docker](../config/install-docker):

```bash
$ cd /projects/prod/mbox/config
$ sudo install-docker
```

## Install Additional Tools (optional)

Usually I install the Midnight Commander to navigate on the system ...

```bash
$ sudo apt-get install mc
```

## Back to README

[README.md](../README.md)
