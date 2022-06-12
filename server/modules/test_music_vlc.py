from unittest import TestCase
import modules.music_vlc as music_vlc
import time


class TestVlcThread(TestCase):

    def test_run(self):
        self.vlc = music_vlc.VlcThread("test")
        self.vlc.start()
        self.assertEqual(self.vlc.running, True)
        self.vlc.stop()

    def test_stop(self):
        self.vlc = music_vlc.VlcThread("test")
        self.vlc.start()
        self.assertEqual(self.vlc.running, True)
        self.vlc.stop()
        self.assertEqual(self.vlc.running, False)

    def test_play(self):
        self.fail()

    def test_stop_play(self):
        self.fail()

    def test_pause_play(self):
        self.fail()

    def test_normalize_volume(self):
        self.fail()

    def test_set_volume(self):
        self.fail()

    def test_mute(self):
        self.fail()
