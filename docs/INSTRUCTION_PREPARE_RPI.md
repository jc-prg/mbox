# jc://music-box/image

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
### Configure the raspberry

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

### Update software and prepare projects

#### Update Software:

```bash
$ sudo apt-get update
$ sudo apt-get upgrade
```

#### Install Git:

```bash
$ sudo apt-get install git
```

#### Create directories:

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

#### Additional tools

Usually I install the Midnight Commander to navigate on the system ...

```bash
$ sudo apt-get install mc
```
