# ------------------------
# control music playback
# ------------------------

import threading
import time
import os
import logging
import requests

import modules.config_stage as stage
import modules.run_cmd as run_cmd


class MusicPlayer(threading.Thread):

    def __init__(self, thread_vlc, thread_speak, start_time):
        """
        create VLC player
        """
        threading.Thread.__init__(self)
        self.vlc = thread_vlc
        self.player = self.vlc.player
        self.instance = self.vlc.instance
        self.speak = thread_speak
        self.start_time = start_time
        self.running = True

        self.connected = False
        self.internet = False
        self.play_uuid = ""
        self.play_url = ""
        self.play_status = 0
        self.play_position = 0
        self.player_status = ""
        self.volume_factor = 1  # default factor to limit audio level (max = 1.0)
        self.volume_start = 0.4  # initial volume
        self.volume = self.volume_start
        self.volume_mute = False
        self.media = None

        self.logging = logging.getLogger("player")
        self.logging.setLevel = stage.logging_level

    def run(self):
        """
        run player
        """
        self.logging.info("Start Player ... " + self.start_time)
        while self.running:
            time.sleep(0.5)
            self.play_status = self.playing()

        self.logging.info("Stopped Player.")
        return

    def set_volume(self, vol):
        """
        set volume
        """
        self.logging.debug("Set volume to " + str(vol))
        self.vlc.set_volume(vol)
        self.volume_mute = False

    def volume_up(self, up):
        """
         set volume - step up or down
        """
        vol = float(self.volume)
        if up == "up" and vol < 1:
            vol = vol + 0.05
        elif up == "down" and vol > 0:
            vol = vol - 0.05
        elif isinstance(up, int) and 0 <= up <= 100:
            vol = up / 100

        self.vlc.set_volume(vol)
        self.volume_mute = False
        self.volume = vol

    def pause(self):
        """
        pause / unpause running song
        """
        if self.player_status == "State.Playing":
            self.player.pause()
            self.play_status = 0

        if self.player_status == "State.Paused":
            self.player.play()
            self.play_status = 1

    def set_position(self, percentage):
        """
        set position in current stream or file
        """
        percentage = float(percentage)
        if 0 <= percentage <= 100:
            self.player.set_position(percentage / 100)

    def get_position(self):
        """
        get position in current playing or pause file -> 1000 / seconds
        """
        if self.player_status == "State.Playing" or self.player_status == "State.Paused":
            position = float(self.player.get_time())
        else:
            position = 0
        return position

    def get_length(self):
        """
        get length of current playing or pause file ->  1000 / seconds
        """
        if self.player_status == "State.Playing" or self.player_status == "State.Paused":
            length = float(self.player.get_length())
        else:
            length = 0
        return length

    def stop(self):
        """
        stop playback
        """
        self.player.stop()
        self.play_status = 0

    def mute(self, value=False):
        """
        mute / un-mute player
        """
        self.logging.debug("Mute ... " + str(value) + " / " + str(self.volume_mute) + " / " + str(self.volume))
        if self.volume_mute is False or value is True:
            self.vlc.set_volume(0)
            self.volume_mute = True
        else:
            self.volume_mute = False
            self.set_volume(self.volume)

    def play_file(self, path):
        """
        play audio file, react on position var
        """
        # self.vlc.stop()

        if not os.path.exists(path.encode('utf-8')) and not path.startswith("http"):
            self.speak.speak_message("FILE-NOT-FOUND")
            return "Error"

        msg = self.vlc.play(path, True)
        if msg != "error":
            self.vlc.set_volume(self.volume)
            self.play_url = path
        else:
            self.speak.speak_message("COULD-NOT-START-PLAYBACK")
            return "Error"

        return "Play"

    def play_stream(self, url):
        """
        play audio stream, react on position var
        """
        if not self.internet_connection():
            return "Error"

        if url.endswith(".m3u"):
            url = self.get_stream_m3u(url)
            return self.play_file(url)
        else:
            return self.play_file(url)

    def playing(self):
        """
        translate playback status to 0/1
        # Status description: https://www.olivieraubert.net/vlc/python-ctypes/doc/vlc.State-class.html
        """
        old_state = self.player_status
        self.player_status = str(self.player.get_state())

        if self.player_status == "State.Stopped" or \
                self.player_status == "State.NothingSpecial" or \
                self.player_status == "State.Ended":
            self.play_status = 0
            self.logging.debug("Playing:" + self.play_url + "..." + str(self.play_status))
        else:
            self.play_status = 1

        self.logging.debug("Playing:" + old_state + " -> " + self.player_status + " (" + str(self.play_status) + ")")
        return self.play_status

    def get_stream_m3u(self, url):
        """
        get mp3 file from url with m3u
        """
        self.logging.info("Load playlist URL from m3u (" + url + ")")

        try:
            response = requests.get(url)
            playlist = response.text

        except Exception as e:
            self.logging.warning(" -> Can't open the playlist from m3u: " + str(e))
            #self.speak.speak_message("CANT-OPEN-STREAM")
            return ""

        streams = playlist.replace("\r", "")
        streams = streams.split("\n")
        return_url = ""

        i = 0
        for stream in streams:
            self.logging.debug("... line: " + stream)
            if "#" in stream:
                self.logging.debug("... comment: " + stream)

            elif "http" in stream and i == 0:
                self.logging.debug("... url: " + stream)
                return_url = stream
                i = 1

        if return_url == "":
            self.logging.warning(" -> No URL found in m3u-file:" + url)
            #self.speak.speak_message("CANT-OPEN-STREAM")
        else:
            self.logging.info(" -> " + return_url)

        return return_url

    def internet_connection(self):
        """
        check if connection to internet exists
        """
        error_msg = run_cmd.check_internet_connect()

        if error_msg == "DNS-ERROR":
            self.logging.error("Could not connect to INTERNET!")
            self.speak.speak_message("CONNECTION-ERROR-RESTART-SHORTLY")
            time.sleep(20)
            return False

        elif error_msg != "CONNECTED":
            self.logging.error("Could not connect to INTERNET!")
            self.speak.speak_message("NO-INTERNET-CONNECTION")
            time.sleep(0.5)
            self.speak.speak_message("TRY-AGAIN-IN-A-MINUTE")
            time.sleep(20)
            self.music_ctrl["LastCard"] = ""
            return False

        return True
