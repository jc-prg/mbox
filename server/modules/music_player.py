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
        self.is_playing = 0
        self.play_uuid = ""
        self.play_url = ""
        self.play_position = 0
        self.player_status = ""
        self.volume_factor = 1  # default factor to limit audio level (max = 1.0)
        self.volume_start = 40  # initial volume
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
            self.is_playing = self.playing()

        self.logging.info("Stopped Player.")
        return

    def stop(self):
        """
        stop playback
        """
        self.running = False

    def set_volume(self, vol):
        """
        set volume
        """
        self.logging.debug("Set volume to " + str(vol))
        self.vlc.set_volume(vol)
        self.volume = vol
        self.volume_mute = False

    def get_volume(self):
        """ get volume level"""
        return self.vlc.get_volume()

    def volume_up(self, up):
        """
         set volume - step up or down
        """
        vol = self.vlc.normalize_volume(self.volume)

        if up == "up" and vol < 95:
            vol = vol + 5
        elif up == "up" and vol < 100:
            vol = 100
        elif up == "down" and vol > 5:
            vol = vol - 5
        elif up == "down" and vol > 0:
            vol = 0
        elif isinstance(up, int):
            vol = self.vlc.normalize_volume(up)

        self.volume_mute = False
        self.set_volume(vol)

    def pause(self):
        """
        pause / unpause running song
        """
        if self.player_status == "State.Playing":
            self.player.pause()

        if self.player_status == "State.Paused":
            self.player.play()

    def mute(self, value=False):
        """
        mute / un-mute player
        """
        self.logging.debug("Mute ... " + str(value) + " / " + str(self.volume_mute) + " / " + str(self.volume))
        if self.volume_mute is False or value is True:
            self.volume = self.get_volume()
            self.vlc.set_volume(0)
            self.volume_mute = True
        else:
            self.volume_mute = False
            self.vlc.set_volume(self.volume)

    def play_file(self, path, wait=True):
        """
        play audio file, react on position var
        """
        # self.vlc.stop()

        if not os.path.exists(path.encode('utf-8')) and not path.startswith("http"):
            self.speak.speak_message("FILE-NOT-FOUND")
            return "Error"

        self.vlc.set_volume(self.volume)
        msg = self.vlc.play(path, wait)
        if msg != "error":
            self.play_url = path
            return "Play"

        else:
            self.speak.speak_message("COULD-NOT-START-PLAYBACK")
            return "Error"

    def play_stream(self, url, wait=True, check_internet=True):
        """
        play audio stream, react on position var
        """
        if check_internet and not self.internet_connection():
            return "Error"

        if url.endswith(".m3u"):
            url = self.get_stream_m3u(url)
            if url == "":
                self.speak.speak_message("CANT-OPEN-STREAM")
                return "error"
            else:
                return self.play_file(url, wait)
        else:
            return self.play_file(url, wait)

    def playing(self):
        """
        translate playback status to 0/1
        # Status description: https://www.olivieraubert.net/vlc/python-ctypes/doc/vlc.State-class.html
        """
        old_state = self.player_status
        self.player_status = str(self.player.get_state())

        if self.player_status == "State.Stopped" or \
                self.player_status == "State.NothingSpecial" or \
                self.player_status == "State.Ended" or \
                self.player_status == "":
            is_playing = 0
            self.logging.debug("Playing:" + self.play_url + "..." + str(self.is_playing))
        else:
            is_playing = 1

        self.logging.debug("Playing:" + old_state + " -> " + self.player_status + " (" + str(self.is_playing) + ")")
        return is_playing

    def set_position(self, percentage):
        """
        set position in current stream or file
        """
        self.logging.info(" ...... " + str(percentage))
        percentage = float(percentage)
        if 1 <= percentage <= 100:
            self.player.set_position(percentage / 100)
        elif 0 <= percentage < 1:
            self.player.set_position(percentage)

    def get_position(self):
        """
        get position in current playing or pause file -> 1000 / seconds
        """
        if self.player_status == "State.Playing" or self.player_status == "State.Paused":
            position = float(self.player.get_time())
        else:
            position = 0
        if position == -1:
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

    def stop_playback(self):
        """
        stop playback
        """
        self.player.stop()

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
            return False

        return True
