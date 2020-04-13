# jc://music-box/

Ihr habt eine Musikbox geschenkt bekommen ... und nun?

**Startet the Musikbox.** Das Starten dauert in der Regel 1:30 min. Sie ist bereit, sobald nur noch die weiße LED und vier grüne LED leuchten - oder die Box mit Euch spricht. 
Nun kann Musik über ggf. vorbelegte RFID-Karten gestartet werden. Um weitere Karten zu belegen und eine Internet-Verbindung für die Nutzung von Web-Streams herzustellen, 
sind ein paar weitere Schritte nötig:

1. Mit dem WLAN der Box verbinden, die Standard-SSID ist "JCmbox" (Standard-Passwort: "012345689").
2. Die App ist anschließend erreichbar über *http://music-box/* (http://10.0.0.5/) und kann als WebApp auf dem Smartphone verwendet werden. Die App ist derzeit auf iPhone 5c/SE und iPhone XS hin optimiert.
3. Für die weitere Konfiguration der Box via ssh verbinden, Standard ist:

```bash
$ ssh pi@10.0.0.5                 # default pwd: raspberry
```

4. Es empfiehlt sich , das Standard-Passwort zu ändern:

```bash
$ passwd pi
```

5. Soll die Musikbox mit dem eigenen WLAN verbunden werden, können die Einstellungen in der Datei */etc/wpa_supplicant/wpa_supplicant.conf* entsprechend angepasst werden:

```bash
$ nano /etc/wpa_supplicant/wpa_supplicant.conf
```

6. Nach dem Neustart der Box verbindet sich mit dem eingestellten WLAN (falls nicht, zurück zu 1.).

```bash
$ sudo reboot now
```

7. Abhängig vom Router kann die App über die IP-Adresse oder den Hostname erreicht werden:
     * **Variante 1: http://music-box/**, sofern der verwendete Router diese Variante unterstützt
     * **Variante 2: http://&lt;your-ip&gt;/**, falls nicht. Dazu gilt es die IP4-Adresse der Musikbox in Deinem Netzwerk ausfindig zu machen. Am einfachsten geht dies in der Regel über den Router. Dort sollte auch die IP-Adresse fix vergeben werden. 
     
8. Aktuell ist die Software noch nicht 100% ausgereift. Deshalb sollte zunächst noch ein **Software-Update** erfolgen.
   Dazu die Box mit dem Internet verbinden und einloggen:

```bash
# Dateien neu laden
$ cd /project/prod/modules
$ sudo git pull
$ cd /project/prod/mbox
$ sudo git pull

# Konfiguration neu erzeugen
$ sudo cd config/
$ sudo rm config_prod
$ sudo cp config_prod.sample config_prod
$ sudo nano config_prod         # MBOX_LANGUAGE in "DE" ändern und anschließend speichern, weitere Änderungen optional
$ sudo ./create prod

# Komponenten neu starten ... alternativ Box einfach aus und wieder einschalten
$ cd ../
$ sudo docker-compose stop
$ sudo docker-compose -f docker-compose-rpi.yml stop
$ sudo ./start_mbox docker
```

9. Über das Menü und Einstellungen können die **Musik-Dateien neu geladen** werden (RELOAD DATA). In der empfohlenen Konfiguration handelt es sich dabei um die Musik-Dateien auf dem USB-Stick.
   Wurden nur weitere Musik-Dateien hinzugefügt, können die neuen Dateien geladen werden (LOAD NEW DATA).

10. Das Verknüpfen von **RFID-Karten** erfolgt, indem die Karten auf die Box gelegt wird (blaue LED leuchtet) und das dann erscheinende Symbol mit der Karte in der App.
   Um die Cover ausdrucken und auf die Karten zu kleben, gibt es im Menü den Punkt "Cover Bilder". Ein Screenshot von 6 Covern ausgedruckt als Foto im Format 9 cm x 13 cm erzeugt Cover-Bilder in der richtigen Größe.
   
11. Das Hinzufügen von Web-Streams und Playlisten ist hoffentlich intuitiv genug ;-).
   
12. **Viel Spa&szlig;!**
