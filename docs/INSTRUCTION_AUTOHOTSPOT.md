# Autohotspot (by raspberryconnect.com)

## Install autohotspot

To make configuration easy I wrote a script based on the description and code I found here https://www.raspberryconnect.com/projects/65-raspberrypi-hotspot-accesspoints/158-raspberry-pi-auto-wifi-hotspot-switch-direct-connection.
The WIFI configuration can be done in the [config file](../config/config_prod.sample). Create an configuration for jc://music-box/ first.

```bash
$ cd config/autohotspot
$ ./install-wifi
```

## Activate autohotspot

Last step is to add the script to crontab (e.g. check every 5 minutes)...

```bash
*/5 * * * * sudo /usr/bin/autohotspot >/dev/null 2>&1
```

... and the to /etc/rc.local (check wifi during startup).


```bash
/usr/bin/autohotspot
```

## Back to README

[README.md](../README.md)
