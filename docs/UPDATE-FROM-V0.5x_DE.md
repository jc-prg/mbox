# jc://music-box

Mit der Version v0.5.x gestartet? Aktuell ist die Version v0.7.x. Es wird Zeit für ein größeres Update in dem sich vor 
allem in Punkte Stabilität und Wartbarkeit aber auch ein wenig in der Funktionalität getan hat.
Dazu sind ein paar mehr Handgriffe nötig, damit im Anschluss auch Updates einfacher werden:

1. Einloggen und Software stoppen:

```bash
# Login
$ ssh pi@music-box
$ sudo -i
$ cd /project/prod/mbox

# Stop Software
$ docker-compose stop
$ docker-compose -f docker-compose-rpi.yml stop
```

2. Update laden:

```bash
$ git pull

# if error occurs stash changes and pull update again
$ git stash
$ git pull
```

3. Neue Konfiguartionsdatei erzeugen:

```bash
$ cd config/
$ mv config_prod config_prod-backup
$ cp config_prod.sample config_prod
$ nano config_prod
```

4. Konfigurationsdatei bearbeiten: Die Standard-Konfiguration tut meist direkt ihren Dienst. Geändert werden sollte:

   * Sprache (MBOX_LANGUAGE)
   * ID der Demokarte / des blauen Chips (MBOX_RFID_DEMOCARD)
   
5. Konfiguration aktivieren und Software starten (hier können künftig auch Updates gestartet werden):

```bash
# create configuration
$ create prod

# start software
$ cd ..
$ ./start
```

6. Systemkonfiguration anpassen:

* Update crontab
```bash
$ crontab -e
```

* Füge folgende Zeilen hin bzw. ersetze die vorhandenen:
```bash
* * * * * sudo /usr/bin/autohotspot >/dev/null 2>&1
* * * * * /projects/prod/mbox/start check-dns >/dev/null 2>&1
```

* Update rc.local (autostart)
```bash
$ nano /etc/rc.local
```

* Füge folgende Zeilen hin bzw. ersetze die vorhandenen:
```bash
/usr/bin/autohotspot 1
/projects/prod/mbox/start docker
```

* Update autohotspot
```bash
$ cd /project/prod/mbox/config/autohotspot
$ ./install-wifi
```


*Geschafft. Viel Spaß!*
