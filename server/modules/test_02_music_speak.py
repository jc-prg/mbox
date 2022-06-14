from unittest import TestCase
import time
import modules.music_vlc as music_vlc
import modules.music_speak as music_speak


class TestSpeakThread(TestCase):

    def vlc_start(self):
        self.vlc = music_vlc.VlcThread("test")
        self.vlc.start()

    def vlc_end(self):
        self.vlc.stop()

    def test_run(self):
        self.vlc_start()
        self.speak = music_speak.SpeakThread(self.vlc, "test")
        self.speak.start()
        time.sleep(1)
        self.assertEqual(self.speak.running, True)
        self.speak.stop()
        self.vlc_end()

    def test_stop(self):
        self.vlc_start()
        self.speak = music_speak.SpeakThread(self.vlc, "test")
        self.speak.start()
        time.sleep(1)
        self.assertEqual(self.speak.running, True)
        self.speak.stop()
        time.sleep(1)
        self.assertEqual(self.speak.running, False)
        self.vlc_end()

    def test_speak_text(self):
        self.vlc_start()
        self.speak = music_speak.SpeakThread(self.vlc, "test")
        self.speak.start()
        self.speak.language = "EN"
        self.assertEqual(self.speak.speak_text("This is a text to speech test."), "ok")
        self.vlc_end()

    def test_speak_message(self):
        self.vlc_start()
        self.vlc.set_volume(50)
        self.speak = music_speak.SpeakThread(self.vlc, "test")
        self.speak.start()
        self.speak.speak_msg = "no"
        self.assertEqual(self.speak.speak_message("STARTING"), "off")
        self.speak.speak_msg = "yes"
        self.speak.language = "EN"
        self.assertEqual(self.speak.speak_message("STARTING"), "EN_STARTING")
        self.speak.language = "DE"
        self.assertEqual(self.speak.speak_message("STARTING"), "DE_STARTING")
        self.assertEqual(self.speak.speak_message("XYXYXYXYX"), "DE_UNKNOWN-ERROR")
        self.assertEqual(self.vlc.volume, 50)
        self.vlc_end()
