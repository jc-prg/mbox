# jc://music-box/start/ (in progress)

The box is ready and now? A description for people who get this box as a gift ...

1. Start the box
2. Connect to the Hotspot of the box, default SSID is "JCmbox"
3. Connect to the box via ssh, default is:

```bash
$ ssh pi@10.0.0.5                 # default pwd: raspberry
```

4. Change the default password

```bash
$ passwd pi
```

5. Change the wifi settings to your home network:

```bash
$ nano /etc/wpa_supplicant/wpa_supplicant.conf
```

6. Reboot the box

```bash
$ sudo reboot now
```

7. Search / define the IP of the box in your network. This step depends on your router. It's recommended to define a static IP for your box. 

8. Open your browser: http://&lt;your-ip&gt;/

9. Add data and configure your box:

   * Copy data to the USB stick ...
   * Reload music data ...
   * Add web-streams ...
   * Create Playlists ...
   * Connect RFID cards ...
   * Print covers ...
   
10. Enjoy
