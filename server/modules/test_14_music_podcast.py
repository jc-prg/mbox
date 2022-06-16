import time
from unittest import TestCase
import os
import modules.config_stage as stage
import modules.config_mbox as mbox
import modules.couch_db as couch_db
import modules.music_vlc as music_vlc
import modules.music_speak as music_speak
import modules.music_podcast as music_podcast

working_dir = os.getcwd()
mbox.log_connection = os.path.join(working_dir, "../test_data/log/internet_connection")
test_podcast_url = "https://raw.githubusercontent.com/jc-prg/mbox/dev/test_data/test_podcast/test_podcast.xml"
test_podcast_url_error = "https://this.is.not.a.valid.domain/test_podcast.xml"
test_podcast_uuid = 'r_01234-56789-abcdef'
test_podcast_title = 'Test Podcast jc://music-box/'
test_podcast_entry = {
    "uuid": test_podcast_uuid,
    "title": test_podcast_title,
    "description": "",
    "stream_info": "",
    "stream_url": test_podcast_url,
    "stream_url2": "",
    "cover_images": {
        "active": "none",
        "upload": [],
        "url": ""
    }
}

class TestPodcastThread(TestCase):
    def start_threads(self):
        self.vlc = music_vlc.VlcThread("test")
        self.vlc.start()
        self.speak = music_speak.SpeakThread(self.vlc, "test")
        self.speak.start()
        self.couch = couch_db.CouchDB(stage.data_db, self.speak, "test")

    def stop_threads(self):
        self.vlc.stop()
        self.speak.stop()

    def test_run(self):
        self.start_threads()
        self.podcast = music_podcast.PodcastThread(self.couch, self.speak, "test")
        self.podcast.start()
        self.assertEqual(self.podcast.running, True)
        self.podcast.stop()
        self.stop_threads()

    def test_stop(self):
        self.start_threads()
        self.podcast = music_podcast.PodcastThread(self.couch, self.speak, "test")
        self.podcast.start()
        self.assertEqual(self.podcast.running, True)
        self.podcast.stop()
        self.assertEqual(self.podcast.running, False)
        self.stop_threads()

    def test_get_podcasts(self):
        self.start_threads()
        self.podcast = music_podcast.PodcastThread(self.couch, self.speak, "test")
        self.podcast.start()

        podcast_data = self.couch.read("radio")
        podcast_data[test_podcast_uuid] = test_podcast_entry
        self.couch.write("radio", podcast_data)
        time.sleep(5)
        podcast_data = self.podcast.get_podcasts(playlist_uuid=test_podcast_uuid)
        self.assertEqual(podcast_data["title"], test_podcast_title)
        self.assertEqual(podcast_data["uuid"], test_podcast_uuid)
        self.assertEqual(len(podcast_data["tracks"]), 4)

    def test_get_tracks_rss(self):
        self.start_threads()
        self.podcast = music_podcast.PodcastThread(self.couch, self.speak, "test")
        self.podcast.start()

        podcast_data = self.podcast.get_tracks_rss(rss_url=test_podcast_url, playlist_uuid="r_01234-56789-abcdef")
        self.assertEqual(podcast_data["title"], test_podcast_title)
        self.assertEqual(podcast_data["uuid"], test_podcast_uuid)
        self.assertEqual(len(podcast_data["tracks"]), 4)
        print(str(podcast_data))

        self.podcast.stop()
        self.stop_threads()

    def test_internet_connection(self):
        self.start_threads()
        self.podcast = music_podcast.PodcastThread(self.couch, self.speak, "test")
        self.podcast.start()
        self.assertEqual(self.podcast.internet_connection(), True)
        self.podcast.stop()
        self.stop_threads()
