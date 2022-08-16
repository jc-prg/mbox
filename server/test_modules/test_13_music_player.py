from unittest import TestCase
import time
import os
import modules.music_vlc as music_vlc
import modules.music_speak as music_speak
import modules.music_player as music_player
import modules.config_mbox as mbox

working_dir = os.getcwd()
test_audio_local1 = os.path.join(working_dir, "audio/EN_READY-HAVE-FUN.mp3")
test_audio_local2 = os.path.join(working_dir, "audio/DE_UNVALID-ENTRY-CONNECTED-TO-CARD.mp3")
test_audio_https = "https://github.com/jc-prg/mbox/raw/master/server/audio/EN_READY-HAVE-FUN.mp3"
test_audio_m3u = "https://raw.githubusercontent.com/jc-prg/mbox/dev/test_data/test_m3u/test.m3u"
test_audio_error = os.path.join(working_dir, "audio/EN_XYXYXYXYXY.mp3")
test_audio_m3u_error = "https://domain.does.not.exist.com/test.m3u"
mbox.log_connection = os.path.join(working_dir, "../test_data/log/internet_connection")


class TestMusicPlayer(TestCase):

    def vlc_start(self):
        self.vlc = music_vlc.VlcThread("test")
        self.vlc.start()
        self.speak = music_speak.SpeakThread(self.vlc, "test")
        self.speak.start()

    def vlc_stop(self):
        self.speak.stop()
        self.vlc.stop()

    def test_run(self):
        self.vlc_start()
        self.player = music_player.MusicPlayer(self.vlc, self.speak, "test")

        self.player.start()
        time.sleep(1)
        self.assertEqual(self.player.running, True)

        self.player.stop()
        self.vlc_stop()

    def test_stop(self):
        self.vlc_start()
        self.player = music_player.MusicPlayer(self.vlc, self.speak, "test")
        self.player.start()

        time.sleep(1)
        self.assertEqual(self.player.running, True)
        self.player.stop()
        time.sleep(1)
        self.assertEqual(self.player.running, False)

        self.vlc_stop()

    def test_set_volume(self):
        self.vlc_start()
        self.player = music_player.MusicPlayer(self.vlc, self.speak, "test")
        self.player.start()

        self.player.set_volume(10)
        self.assertEqual(self.vlc.player.audio_get_volume(), (self.vlc.volume_factor * 10))
        self.vlc.set_volume(50)
        self.assertEqual(self.vlc.player.audio_get_volume(), (self.vlc.volume_factor * 50))
        self.vlc.set_volume(110)
        self.assertEqual(self.vlc.player.audio_get_volume(), (self.vlc.volume_factor * 100))

        self.player.stop()
        self.vlc_stop()

    def test_get_volume(self):
        self.vlc_start()
        self.player = music_player.MusicPlayer(self.vlc, self.speak, "test")
        self.player.start()

        self.player.set_volume(50)
        self.assertEqual(self.player.get_volume(), 50)
        self.player.set_volume(0.64)
        self.assertEqual(self.player.get_volume(), 64)
        self.player.set_volume(110)
        self.assertEqual(self.player.get_volume(), 100)

        self.player.stop()
        self.vlc_stop()

    def test_mute(self):
        self.vlc_start()
        self.player = music_player.MusicPlayer(self.vlc, self.speak, "test")
        self.player.start()

        self.vlc.player.audio_set_mute(True)
        current_volume = self.vlc.player.audio_get_volume()
        self.player.mute()
        self.assertEqual(self.player.volume_mute, True)
        self.assertEqual(self.vlc.player.audio_get_volume(), 0)
        self.player.mute()
        self.assertEqual(self.player.volume_mute, False)
        self.assertEqual(self.vlc.player.audio_get_volume(), current_volume)

        self.player.stop()
        self.vlc_stop()

    def test_volume_up(self):
        self.vlc_start()
        self.player = music_player.MusicPlayer(self.vlc, self.speak, "test")
        self.player.start()

        self.player.set_volume(10)
        self.player.volume_up("up")
        self.assertEqual(self.player.get_volume(), 15)
        self.player.set_volume(97)
        self.player.volume_up("up")
        self.assertEqual(self.player.get_volume(), 100)

        self.player.set_volume(10)
        self.player.volume_up("down")
        self.assertEqual(self.player.get_volume(), 5)
        self.player.set_volume(4)
        self.player.volume_up("down")
        self.assertEqual(self.player.get_volume(), 0)

        self.player.volume_up(5)
        self.assertEqual(self.player.get_volume(), 5)
        self.player.volume_up(34)
        self.assertEqual(self.player.get_volume(), 34)
        self.player.volume_up(50)
        self.assertEqual(self.player.get_volume(), 50)
        self.player.volume_up(-2)
        self.assertEqual(self.player.get_volume(), 0)
        self.player.volume_up(105)
        self.assertEqual(self.player.get_volume(), 100)

        self.player.stop()
        self.vlc_stop()

    def test_play_file(self):
        self.vlc_start()
        self.player = music_player.MusicPlayer(self.vlc, self.speak, "test")
        self.player.start()

        self.assertEqual(self.player.play_file(path=test_audio_local1, wait=True), "Play")
        time.sleep(0.5)
        self.assertEqual(self.vlc.play_status, 0)
        self.assertEqual(self.vlc.player_status, "State.Ended")
        time.sleep(1)
        self.assertEqual(self.player.play_file(path=test_audio_https, wait=True), "Play")
        time.sleep(1)
        self.assertEqual(self.vlc.play_status, 0)
        self.assertEqual(self.vlc.player_status, "State.Ended")
        time.sleep(1)
        self.assertEqual(self.player.play_file(path=test_audio_local1, wait=False), "Play")
        time.sleep(0.5)
        self.assertEqual(self.vlc.play_status, 1)
        self.assertEqual(self.vlc.player_status, "State.Playing")
        time.sleep(1)
        self.assertEqual(self.player.play_file(path=test_audio_error, wait=False), "Error")
        time.sleep(0.5)
        self.assertEqual(self.vlc.play_status, 0)
        self.assertNotEqual(self.vlc.player_status, "State.Playing")

        self.player.stop()
        self.vlc_stop()

    def test_play_stream(self):
        self.vlc_start()
        self.player = music_player.MusicPlayer(self.vlc, self.speak, "test")
        self.player.start()

        self.assertEqual(self.player.play_stream(url=test_audio_m3u_error, wait=True, check_internet=False).lower(), "error")
        self.assertEqual(self.player.play_stream(url=test_audio_m3u, wait=True, check_internet=False).lower(), "play")
        time.sleep(0.5)
        self.assertEqual(self.player.player_status, "State.Ended")

        self.player.stop()
        self.vlc_stop()

    def test_playing(self):
        self.vlc_start()
        self.player = music_player.MusicPlayer(self.vlc, self.speak, "test")
        self.player.start()

        self.assertEqual(self.player.play_file(path=test_audio_local1, wait=False), "Play")
        time.sleep(0.5)
        self.assertEqual(self.vlc.play_status, 1)
        self.assertEqual(self.player.playing(), 1)

        self.player.stop_playback(), "Play"
        self.player.stop()
        self.vlc_stop()

    def test_pause_playback(self):
        self.vlc_start()
        self.player = music_player.MusicPlayer(self.vlc, self.speak, "test")
        self.player.start()

        self.assertEqual(self.player.play_file(path=test_audio_local1, wait=False), "Play")
        time.sleep(0.5)
        self.assertEqual(self.vlc.play_status, 1)
        self.player.pause()
        time.sleep(0.5)
        self.assertEqual(self.vlc.play_status, 0)
        self.player.pause()
        time.sleep(0.5)
        self.assertEqual(self.vlc.play_status, 1)

        self.player.stop()
        self.vlc_stop()

    def test_stop_playback(self):
        self.vlc_start()
        self.player = music_player.MusicPlayer(self.vlc, self.speak, "test")
        self.player.start()

        self.assertEqual(self.player.play_file(path=test_audio_local1, wait=False), "Play")
        time.sleep(0.5)
        self.assertEqual(self.vlc.play_status, 1)
        self.assertEqual(self.vlc.player_status, "State.Playing")
        time.sleep(0.5)
        self.player.stop_playback(), "Play"
        time.sleep(0.5)
        self.assertEqual(self.vlc.play_status, 0)
        self.assertEqual(self.vlc.player_status, "State.Stopped")

        self.player.stop()
        self.vlc_stop()

    def test_set_and_get_position(self):
        self.vlc_start()
        self.player = music_player.MusicPlayer(self.vlc, self.speak, "test")
        self.player.start()

        self.assertEqual(self.player.play_file(path=test_audio_local2, wait=False), "Play")
        time.sleep(0.5)
        self.assertEqual(self.player.get_length(), 3553)
        self.player.set_position(50)
        self.assertTrue(1750 < self.player.get_position() < 2000)
        self.player.stop_playback()
        self.assertEqual(self.player.get_position(), 0)

        self.player.stop()
        self.vlc_stop()

    def test_get_length(self):
        self.vlc_start()
        self.player = music_player.MusicPlayer(self.vlc, self.speak, "test")
        self.player.start()

        self.assertEqual(self.player.play_file(path=test_audio_local1, wait=False), "Play")
        time.sleep(0.5)
        self.assertEqual(self.player.get_length(), 1829)
        self.player.stop_playback()

        self.assertEqual(self.player.play_file(path=test_audio_local2, wait=False), "Play")
        time.sleep(0.5)
        self.assertEqual(self.player.get_length(), 3553)
        self.player.stop_playback()

        self.player.stop()
        self.vlc_stop()

    def test_get_stream_m3u(self):
        self.vlc_start()
        self.player = music_player.MusicPlayer(self.vlc, self.speak, "test")
        self.player.start()

        self.assertEqual(self.player.get_stream_m3u(test_audio_m3u), test_audio_https)
        self.assertEqual(self.player.get_stream_m3u(test_audio_m3u_error), "")

        self.player.stop()
        self.vlc_stop()

    def test_internet_connection(self):
        """
        important: requires root access at the moment
        """
        self.vlc_start()
        self.player = music_player.MusicPlayer(self.vlc, self.speak, "test")
        self.player.start()

        self.assertEqual(self.player.internet_connection(), True)

        self.player.stop()
        self.vlc_stop()
