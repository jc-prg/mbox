from unittest import TestCase

import modules.music_load as music_load
import modules.music_control as music_ctrl
import modules.config_mbox as mbox
import modules.config_stage as stage
import modules.server_init as server_init
import modules.server_cmd as server_cmd

stage.log_filename_data = "/tmp/load_metadata.log"
mbox.log_connection = "/tmp/log_connection.log"
backup_dir = "../test_data/couchdb_backup/"


class TestMusicLoadMetadata(TestCase):
    def test_reload_music(self):
        self.fail()

    def test_reload_covers(self):
        self.fail()

    def test_get_files_in_directory(self):
        self.fail()

    def test_get_album_from_path(self):
        self.fail()

    def test_get_current_without_errors(self):
        self.fail()

    def test_set_progress_information(self):
        self.fail()

    def test_create_album_information(self):
        self.fail()

    def test_check_if_entry_in_playlist(self):
        self.fail()

    def test_check_if_card_exists(self):
        self.fail()

    def test_check_if_format_supported(self):
        self.fail()


class TestMusicLoadingThread(TestCase):
    def start_threads(self):
        # init all required threads
        server_init.start_modules(speak_msg=False)
        self.vlc = server_init.thread_vlc
        self.player = server_init.thread_player
        self.couch = server_init.thread_couch
        self.speak = server_init.thread_speak
        self.podcast = server_init.thread_podcast
        self.music_load = server_init.thread_music_load
        self.music_control = music_ctrl.MusicControlThread("music_box", self.couch, self.player, self.speak,
                                                           self.podcast, "time_since_start")
        self.music_control.wait_for_other_services = False
        self.mbox_music_dir = mbox.music_dir
        self.mbox_music_cover = mbox.music_cover
        self.mbox_music_cover_upload = mbox.music_cover_upload
        self.mbox_log_connection = mbox.log_connection

    def end_threads(self):
        pass

    def test_run(self):
        self.load = music_load.MusicLoadingThread(self.couch, "time_since_start")
        self.load.start()
        self.assertEqual(self.load.stopProcess, False)

    def test_stop(self):
        self.fail()
