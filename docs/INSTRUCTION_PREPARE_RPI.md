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

### Download Image

Download an up-to-date raspbian image: [https://www.raspberrypi.org/downloads/raspbian/](https://www.raspberrypi.org/downloads/raspbian/). 
This software was tested with:

* 2018-11-13-raspbian-stretch-lite.img
* 2019-09-26-raspbian-buster-lite.img

Other images or linux distributions will work also, but the preparation may differ.

### Write image to SD-card

The installation is described here: [https://www.raspberrypi.org/documentation/installation/installing-images/linux.md](https://www.raspberrypi.org/documentation/installation/installing-images/linux.md).
Or just use "dd":

```bash
# sudo dd bs=4M if=<input-file> of=<output-file/device> conv=fsync
$ sudo dd bs=4M if=2019-09-26-raspbian-buster-lite.img of=/dev/mmcblk0 conv=fsync
```
### Configure the Raspberry

Connect a keyboard and a screen and start the raspberry, to do the initial configuration (default login: pi / raspberry).

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

From now on you can work remote via ssh. Maybe you have to configure your router, that the raspberry will get the same IP4 address all the time.

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

To install docker the following instructions worked for me: [https://www.marksei.com/docker-on-raspberry-pi-raspbian/](https://www.marksei.com/docker-on-raspberry-pi-raspbian/). 
To make it short, you can use *./config/install-docker* or follow the following instructions:

```bash
# install required software and aquire GPG key
$ sudo apt-get install \
         apt-transport-https \
         ca-certificates \
         curl \
         gnupg2 \
         software-properties-common \
         python3-pip
$ curl -fsSL https://download.docker.com/linux/debian/gpg | sudo apt-key add -
             
# add repository
$ echo "deb [arch=armhf] https://download.docker.com/linux/debian \
         $(lsb_release -cs) stable" | \
         sudo tee /etc/apt/sources.list.d/docker.list
         
# install docker
$ sudo apt-get install docker-ce
$ systemctl enable --now docker

# install docker-compose use PIP:
$ sudo pip3 install docker-compose
```

## Install Additional Tools (optional)

Usually I install the Midnight Commander to navigate on the system ...

```bash
$ sudo apt-get install mc
```


