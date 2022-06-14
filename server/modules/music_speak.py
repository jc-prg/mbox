import logging
import os
import os.path
import threading
import time
import gtts
import modules.config_mbox as mbox
import modules.config_stage as stage


class SpeakThread(threading.Thread):

    def __init__(self, vlc_player, start_time):
        """
        set initial values to vars and start pygame.mixer
        """
        threading.Thread.__init__(self)
        self.stopProcess = False
        self.volume = 70
        self.running = True
        self.language = stage.language
        self.speak_msg = stage.speak_msg

        self.start_time = start_time
        self.vlc_player = vlc_player

        self.logging = logging.getLogger("speak")
        self.logging.setLevel = stage.logging_level

    def run(self):
        """        except Exception as e:
        run, get state
        """
        self.logging.info("Start SpeakMsg ... " + self.start_time)
        while self.running:
            time.sleep(1)
        self.logging.info("Stopped SpeakMsg.")

    def stop(self):
        """
        stop thread
        """
        self.running = False

    def speak_text(self, text, volume=None, filename=None, create_only=False):
        """
        Use Google API to speech from text
        """
        self.logging.debug("speak_text // " + text)
        if filename is None:
            filename = "/tmp/music-box-speech.mp3"
        language = self.language.lower()
        duration = 0

        try:
            tts = gtts.gTTS(text=text, lang=language)
            tts.save(filename)
        except Exception as e:
            self.logging.error("Could not create message to speak (" + text + "::" + filename + ").")
            self.logging.error(" -> gtts error: " + str(e))
            return "error"

        if not create_only:
            try:
                current_volume = self.vlc_player.volume
                self.vlc_player.mute(False)
                if volume is None:
                    self.vlc_player.set_volume(self.volume)
                else:
                    self.vlc_player.set_volume(volume)
                self.vlc_player.play(filename, wait=False)
                duration = self.vlc_player.media.get_duration() / 1000
                time.sleep(duration)
                self.vlc_player.set_volume(current_volume)
            except Exception as e:
                self.logging.error("Could not speak message (" + text + ").")
                self.logging.error(" -> player error: " + str(e))
                return "error"

            self.logging.info(" - Speak_text: " + str(text) + " (" + str(duration) + ")")

        return "ok"

    def speak_message(self, message):
        """
        play spoken messages from prerecorded files
        """
        if self.speak_msg.lower() != "yes":
            return "off"

        self.logging.debug("speak_message // " + message)
        current_volume = self.vlc_player.volume
        self.vlc_player.mute(False)
        self.vlc_player.set_volume(self.volume)

        directory_path = os.getcwd()
        filename = os.path.join(directory_path, mbox.error_msg_dir + self.language + "_" + message + ".mp3")
        filename_EN = os.path.join(directory_path, mbox.error_msg_dir + "EN_" + message + ".mp3")
        filename_UE = os.path.join(directory_path, mbox.error_msg_dir + self.language + "_UNKNOWN-ERROR.mp3")
        filename_UE_EN = os.path.join(directory_path, mbox.error_msg_dir + "EN_UNKNOWN-ERROR.mp3")

        if os.path.isfile(filename):
            self.vlc_player.play(filename, True)
            self.vlc_player.set_volume(current_volume)
        elif os.path.isfile(filename_EN):
            self.vlc_player.play(filename_EN, True)
            self.vlc_player.set_volume(current_volume)
        elif os.path.isfile(filename_UE):
            self.vlc_player.play(filename_UE, True)
            self.vlc_player.set_volume(current_volume)
            return self.language.upper()+"_UNKNOWN-ERROR"
        elif filename_UE_EN:
            self.vlc_player.play(filename_UE_EN, True)
            self.vlc_player.set_volume(current_volume)
            return "EN_UNKNOWN-ERROR"
        else:
            self.vlc_player.set_volume(current_volume)
            return "error"

        # duration = self.vlc_player.player.get_length() / 1000
        # time.sleep(duration - 0.3)
        return self.language.upper()+"_"+message
