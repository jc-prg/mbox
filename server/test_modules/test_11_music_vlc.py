import os
from unittest import TestCase
import time
import os
import modules.music_vlc as music_vlc

working_dir = os.getcwd()
test_audio_local = os.path.join(working_dir, "audio/EN_READY-HAVE-FUN.mp3")
test_audio_https = "https://github.com/jc-prg/mbox/raw/master/server/audio/EN_READY-HAVE-FUN.mp3"


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
        self.vlc = music_vlc.VlcThread("test")
        self.vlc.start()

        self.vlc.play(filename=test_audio_local, wait=True)
        time.sleep(0.5)
        self.assertEqual(self.vlc.play_status, 0)
        self.assertEqual(self.vlc.player_status, "State.Ended")

        self.vlc.play(filename=test_audio_https, wait=True)
        time.sleep(0.5)
        self.assertEqual(self.vlc.play_status, 0)
        self.assertEqual(self.vlc.player_status, "State.Ended")

        self.vlc.play(filename=test_audio_local, wait=False)
        time.sleep(0.5)
        self.assertEqual(self.vlc.play_status, 1)
        self.assertEqual(self.vlc.player_status, "State.Playing")
        time.sleep(3)

        self.vlc.stop()

    def test_stop_play(self):
        self.vlc = music_vlc.VlcThread("test")
        self.vlc.start()
        self.vlc.play(filename=test_audio_local, wait=False)
        time.sleep(0.5)
        self.assertEqual(self.vlc.play_status, 1)
        self.vlc.stop_play()
        self.assertEqual(self.vlc.play_status, 0)
        self.vlc.stop()

    def test_pause_play(self):
        self.vlc = music_vlc.VlcThread("test")
        self.vlc.start()
        self.vlc.play(filename=test_audio_local, wait=False)
        time.sleep(0.5)
        self.assertEqual(self.vlc.play_status, 1)
        self.vlc.pause_play()
        time.sleep(0.5)
        self.assertEqual(self.vlc.play_status, 0)
        self.vlc.pause_play()
        time.sleep(0.5)
        self.assertEqual(self.vlc.play_status, 1)
        time.sleep(1)
        self.vlc.stop()

    def test_normalize_volume(self):
        self.vlc = music_vlc.VlcThread("test")
        self.vlc.start()
        self.assertEqual(self.vlc.normalize_volume(-1), 0)
        self.assertEqual(self.vlc.normalize_volume(110), 100)
        self.assertEqual(self.vlc.normalize_volume(0.1), 10)
        self.assertEqual(self.vlc.normalize_volume(0.5), 50)
        self.assertEqual(self.vlc.normalize_volume(1), 1)
        self.vlc.stop()

    def test_set_volume(self):
        self.vlc = music_vlc.VlcThread("test")
        self.vlc.start()
        self.vlc.set_volume(10)
        self.assertEqual(self.vlc.player.audio_get_volume(), (self.vlc.volume_factor * 10))
        self.vlc.set_volume(50)
        self.assertEqual(self.vlc.player.audio_get_volume(), (self.vlc.volume_factor * 50))
        self.vlc.set_volume(110)
        self.assertEqual(self.vlc.player.audio_get_volume(), (self.vlc.volume_factor * 100))
        self.vlc.volume_factor = 0.5
        self.vlc.set_volume(80)
        self.assertEqual(self.vlc.player.audio_get_volume(), 40)
        self.vlc.stop()

    def test_get_volume(self):
        self.vlc = music_vlc.VlcThread("test")
        self.vlc.start()
        self.vlc.set_volume(10)
        self.assertEqual(self.vlc.get_volume(), 10)
        self.vlc.volume_factor = 0.5
        self.vlc.set_volume(10)
        self.assertEqual(self.vlc.get_volume(), 10)
        self.assertEqual(self.vlc.player.audio_get_volume(), 5)
        self.vlc.stop()

    def test_mute(self):
        self.vlc = music_vlc.VlcThread("test")
        self.vlc.start()
        self.vlc.mute()
        self.assertEqual(self.vlc.player.audio_get_mute(), True)
        self.vlc.mute(True)
        self.assertEqual(self.vlc.player.audio_get_mute(), True)
        self.vlc.mute(False)
        self.assertEqual(self.vlc.player.audio_get_mute(), False)
        self.vlc.stop()
