# jc://music-box/hardware

## Table of Contents

- [Impressions](#impressions)
  - [The Wooden Box](#the-wooden-box)
  - [The Lid from Outside](#the-lid-from-outside)
  - [The Lid from Inside](#the-lid-from-inside)
  - [The Inner Box](#the-inner-box)
  - [The Client (on an iPhone)](#the-client-on-an-iphone)
- [Required Components](#required-components)
  - [Prepare the Front for the Speakers](#prepare-the-front-for-the-speakers)
  - [Prepare the Lid and Add Buttons](#prepare-the-lid-and-add-buttons)
- [Building the Hardware](#building-the-hardware)

## Impressions

### The Wooden Box v1.0
![the wooden box](images/mbox.jpg)
![the wooden box](images/mbox_screen.JPG)

### The Lid from Outside
![lid of the box - outside](images/mbox_detail_0.jpg)

### The Lid from Inside
![lid of the box - inside](images/mbox_detail_1.jpg)

### The Inner Box
![inner box with covered battery pack and speakers](images/mbox_detail_2.jpg)

### The Client (on an iPhone)
![the software 1](images/mbox_client_01.jpg)
![the software 2](images/mbox_client_02.jpg)

## Required Components

*Box:*
* 1x Wooden box (30cm x 20cm x 14cm)
* Wire mesh
* Plastic plates (~5mm thick)

*Computer:*
* 1x Raspberry Pi 3B+
* 1x 16GB microSDHC Card
* 1x 32GB USB Stick (e.g. Intenseo Micro Line)* 1x Transparent case for the Raspberry Pi
* 1x USB Speaker (e.g. Hama PC Speaker Sonic Mobil 181)
* 1x USB Power bank (recommended with 20.000 mAh)
* 2x USB Power extension cable (Type A Male / Micro USB Male)

*Peripheral equipment:*
* Several jumper wires (male-female)
* Several breakaway connector bridges (female)
* 5x perforated grid board (Lochrasterplatte)
* 2x 74HC595 8-bit shift register
* Several LED (e.g. 6x green, 2x yellow, 3x red, 1x white, 1x blue)
* Several electrical resistors (e.g. 1 kOhm)
* 6x colored push-buttons
* 1x LED Power Switch
* 5x double screw terminal blocks (wire to board connector)
* 1x RFID Reader: RFID Kit RC522
* Several RFID key cards 13,56 Mhz

## Building the Hardware

![parts](images/mbox_parts.JPG)
![tools](images/mbox_tools.JPG)

### Prepare the Front for the Speakers

![prepare the front 01](images/mbox_front01.JPG)
![prepare the front 02](images/mbox_front02.JPG)
![prepare the front 03](images/mbox_front03.JPG)

### Prepare the Lid and Add Buttons

![prepare the lid 01](images/mbox_lid01.JPG)
![prepare the lid 02](images/mbox_lid02.JPG)
![prepare the lid 03](images/mbox_lid03.JPG)

*further images will follow ...*

## Integrate IT Components

The IT components are connected via GPIO with the Raspberry Pi. A documentation can be found here: [https://www.raspberrypi.org/documentation/usage/gpio/](https://www.raspberrypi.org/documentation/usage/gpio/).
The GPIO pins are define in the file: [./server/modules_gpio/config.py](../server/modules_gpio/config.py).

### Integrate Raspberry Pi, Speakers and PowerBank

For the integration of the Raspberry Pi I've used a transparent case which I glued into the box with a small sheet of plastic between the case and the wooden box. The PowerBank can be fixed using velcro tape. The speakers I also fixed using velcro tape.

![Raspberry, Speaker and Powerbank](images/mbox_inside01.JPG)

### Integrate Power-Switch

To integrate a power switch I used a LED Power Switch. Additionally you need a grid board, the screw terminal blocks, several jumper cables and a USB extension cable. How to connect this depends on the switch you've choosen. In the end it could look like this:

![integrate the power-sitch](images/mbox_power-switch.JPG)

### Integrate RFID Kit RC533

The integration of the RFID Kit RC522 is relatively easy. The cabling is described here: [https://tutorial.cytron.io/2018/08/15/reading-rfid-tag-using-mifare-rc522-raspberry-pi/](https://tutorial.cytron.io/2018/08/15/reading-rfid-tag-using-mifare-rc522-raspberry-pi/).
Additionally the cabeling is documented (not configured) in the file [./server/modules_gpio/config.py](../server/modules_gpio/config.py).
The required software modules SPI and MRFC522 are installed within the docker containers, you only have to active SPI on your Raspberry PI:

```bash
# activate SPI for your Raspberry Pi: "Advanced Options" > "SPI"
$ sudo raspi-config
```

![connect rfid](images/mbox_rfid.JPG)
![wiring rfid](mbox-wiring-02.png)

### Integrate Buttons

The push buttons are easy to integrate also. Connect ground of all buttons and the other connect to an GPIO per button. For the default configuration see [./server/modules_gpio/config.py](../server/modules_gpio/config.py).

![prepare the lid 04](images/mbox_lid04.JPG)
![prepare the lid 05](images/mbox_lid05.JPG)
![wiring buttons](mbox-wiring-04.png)

### Create and integrate LED bars

This part is (at least for me) the most difficult part as you've to solder a lot. For this step you need 4 grid boards, 13 LEDs und 13 electrical resistors (e.g. 1 kOhm), 2 shift registers, several connector bridges and several jumper wires.

![led bar for volume visualization](images/mbox_led-bar.JPG)
![led shift register](images/mbox_register.JPG)
![prepare the lid 06](images/mbox_lid06.JPG)
![wiring led](mbox-wiring-03.png)

### Overview all wiring diagrams

![wiring overview](mbox-wiring-01.png)
