import logging
import os.path
import threading
import vlc
import time
import modules.config_mbox as mbox
import modules.config_stage as stage


class VlcThread(threading.Thread):

    def __init__(self, start_time):
        """
        set initial values to vars and start pygame.mixer
        """
        threading.Thread.__init__(self)
        self.running = True
        self.start_time = start_time
        self.volume = 0.5

        param = ""
        if stage.rollout == "prod":
            param = "--quiet"
        self.instance = vlc.Instance(param)
        self.player = self.instance.media_player_new()

        self.logging = logging.getLogger("vlc")
        self.logging.setLevel = stage.logging_level

        self.player_status = None
        self.play_status = None
        self.media = None

    def run(self):
        """
        run, get state
        """
        self.logging.info("Start VLC control ... "+self.start_time)
        while self.running:
            self.player_status = self.player.get_state()
            if self.player_status == "State.Playing":
                self.play_status = 1
            else:
                self.play_status = 0
        self.player.stop()
        self.logging.info("Stopped VLC control.")

    def stop(self):
        """
        stop thread
        """
        self.running = False

    def play(self, filename, wait=False):
        """
        play file using VLC
        """
        self.logging.info("Load file '" + filename + "' ...")
        if not os.path.isfile(filename):
            self.logging.error("Didn't find file  " + filename)
            return "error"
        try:
            self.media = self.instance.media_new(filename)  # str(file.encode('utf-8')) )
            self.player.set_media(self.media)
            #self.player.audio_set_volume(self.volume)
            self.player.play()
        except Exception as e:
            self.logging.error("Could not start playback - " + filename + " (" + str(e) + ")")
            return "error"

        time.sleep(1)
        if wait:
            state = ""
            while state == "State.Playing":
                if self.player_status != "State.Ended" and self.player_status != "State.Playing":
                    self.logging.error("Error during playback - " + filename + " (" + state + ")")
                    return "error"
            return "ended"
        else:
            return "play"

    def stop_play(self):
        """
        stop playback
        """
        self.player.stop()
        self.play_status = 0

    def pause_play(self):
        """
        pause / unpause running song
        """
        if self.player_status == "State.Playing":
            self.player.pause()
        if self.player_status == "State.Paused":
            self.player.play()

    def set_volume(self, volume):
        """
        set volume
        """
        self.player.audio_set_volume(volume)

    def mute(self, set_mute=True):
        """
        set volume
        """
        self.player.audio_set_mute(set_mute)