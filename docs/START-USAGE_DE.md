# jc://music-box/start/ (in progress)

Ihr habt eine Musikbox geschenkt bekommen ... und nun?

**Startet the Musikbox.** Das Starten dauert in der Regel 1:30 min. Sie ist bereit, sobald nur noch die weiße LED und vier grüne LED leuchten. 
Nun kann Musik über ggf. vorbelegte RFID-Karten gestartet werden. Um weitere Karten zu belegen, sind ein paar weitere Schritte nötig:

1. Mit dem WLAN der Box verbinden, die Standard-SSID ist "JCmbox".
2. Mit der Box via ssh verbinden, Standard ist:

```bash
$ ssh pi@10.0.0.5                 # default pwd: raspberry
```

3. Es empfiehlt sich , das Standard-Passwort zu ändern:

```bash
$ passwd pi
```

4. Soll die Musikbox mit dem eigenen WLAN verbunden werden, können die Einstellungen in der Datei */etc/wpa_supplicant/wpa_supplicant.conf* entsprechend angepasst werden:

```bash
$ nano /etc/wpa_supplicant/wpa_supplicant.conf
```

5. Nach dem Neustart der Box verbindet sich mit dem eingestellten WLAN (falls nicht, zurück zu 1.).

```bash
$ sudo reboot now
```

6. Nun gilt es die IP4-Adresse der Musikbox in Deinem Netzwerk ausfindig zu machen. Am einfachsten geht dies in der Regel über den Router. Dort sollte auch die IP-Adresse fix vergeben werden. 
   Je nach Router ist die App der Musikbox aber auch über den Hostnamen erreichbar:
     * Variante 1: http://&lt;your-ip&gt;/
     * Variante 2: http://music-box/

7. Über das Menü und Einstellungen können die **Musik-Dateien neu geladen** werden (RELOAD DATA). In der empfohlenen Konfiguration handelt es sich dabei um die Musik-Dateien auf dem USB-Stick.
   Wurden nur weitere Musik-Dateien hinzugefügt, können die neuen Dateien geladen werden (LOAD NEW DATA).

8. Das Verknüpfen von **RFID-Karten** erfolgt, indem die Karten auf die Box gelegt wird (blaue LED leuchtet) und das dann erscheinende Symbol mit der Karte in der App.
   Um die Cover ausdrucken und auf die Karten zu kleben, gibt es im Menü den Punkt "Cover Bilder". Ein Screenshot von 6 Covern ausgedruck als Foto im Format 9 cm x 13 cm erzeugt Cover-Bilder in der richtigen Größe.
   
9. Das Hinzufügen von Web-Streams und Playlisten ist hoffentlich intuitiv genug ;-).
   
10. **Viel Spa&szlig;!**
