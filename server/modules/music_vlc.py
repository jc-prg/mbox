import logging
import os.path
import threading
import vlc
import time
import modules.config_stage as stage


class VlcThread(threading.Thread):

    def __init__(self, start_time):
        """
        set initial values to vars and start pygame.mixer
        """
        threading.Thread.__init__(self)
        self.running = True
        self.start_time = start_time
        self.volume = 60
        self.volume_factor = 1  # default factor to limit audio level (max = 1.0)

        param = ""
        if stage.rollout == "prod":
            param = "--quiet"
        self.instance = vlc.Instance(param)
        self.player = self.instance.media_player_new()
        self.player.audio_set_volume(self.volume)

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
            time.sleep(0.5)
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
        state = ""
        length = 0
        self.logging.info("Load file '" + filename + "' (wait="+str(wait)+",vol="+str(self.volume)+") ...")
        if "http" not in filename and not os.path.isfile(filename):
            self.logging.error("Didn't find file  " + filename)
            return "error"
        elif "http" not in filename and not os.access(filename, os.R_OK):
            self.logging.error("Couldn't access file  " + filename)
            return "error"

        # try:
        self.player.pause()
        self.media = self.instance.media_new(filename)  # str(file.encode('utf-8')) )
        self.media.parse_with_options(1, 0)
        start_time = time.time()
        while True:
            parsed = str(self.media.get_parsed_status())
            if "done" in parsed:
                break  # Might be a good idea to add a failsafe in here.
            elif time.time() > start_time + 5:
                self.logging.error("Could not read media file: "+filename)
                return "error"

            self.logging.debug(" ... " + parsed)
            time.sleep(0.1)

        length = self.media.get_duration()
        self.player.set_media(self.media)
        self.player.play()
        self.play_status = 1

        try:
            state = self.player_status
            self.logging.debug(" ... Parsed: " + str(parsed))
            self.logging.debug(" ... Length: " + str(length / 1000))
            self.logging.debug(" ... State:  " + str(self.player.get_state()))
            if "http" not in filename:
                self.logging.debug(" ... Access: " + str(os.access(filename, os.R_OK)))
                self.logging.debug(" ... Size:   " + str(os.path.getsize(filename)))
        except Exception as e:
            self.logging.warning("Could not get playing status: "+str(e))

        # IDEE: auf Länge aufsetzen; while-loop -> Stop: set playing status to end loop
        start_time = time.time()
        self.logging.debug(" ... " + str(start_time) + "-" + str(length))
        if wait:
            while True:
                state = str(self.play_status) + "-" + str(self.player.get_state())
                if self.play_status == 0:
                    break
                elif "Ended" in state:
                    break
                elif "Stopped" in state:
                    self.logging.info(" ... Stopped for some reason?!")
                    break
                elif time.time() > start_time + (length/1000):
                    break
                time.sleep(0.5)
                self.logging.debug(" ... "+state+"-"+str(start_time+length)+"/"+str(time.time()))
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

    @staticmethod
    def normalize_volume(volume):
        """
        normalize volume to range 0..100
        """
        if 0 < volume < 1:
            volume = volume * 100
        if volume > 100:
            volume = 100
        elif volume < 0:
            volume = 0
        return volume

    def set_volume(self, volume):
        """
        set volume
        """
        volume = self.normalize_volume(volume)
        self.logging.debug("Set volume to " + str(volume))
        self.volume = volume
        volume = volume * self.volume_factor
        self.player.audio_set_volume(int(volume))

    def mute(self, set_mute=True):
        """
        set volume
        """
        self.player.audio_set_mute(set_mute)
