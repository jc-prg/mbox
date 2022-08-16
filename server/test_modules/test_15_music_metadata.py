from unittest import TestCase
import modules.music_metadata as music_metadata
import modules.config_mbox as mbox
import os

music_dir = os.path.join(os.getcwd(), "../test_data/music")
mbox.music_cover = os.path.join(os.getcwd(), "../test_data/cover_upload")
music_testfile_1 = "/01_Music/Goethe, Der Zauberlehrling/Goethe, Der Zauberlehrling_001.mp3"
music_testfile_2 = "/01_Music/Goethe, Der Zauberlehrling/Goethe, Der Zauberlehrling_004.mp3"
music_testfile_3 = "/01_Music/Goethe, Der Erlkoenig/Goethe, Der Erlkoenig_003.mp3"
music_testfile_4 = "/01_Music/Goethe, Der Erlkoenig (mp4)/Goethe, Der Erlkoenig_003.mp4"


class TestExtractMetadata(TestCase):

    def test_md5_hash(self):
        self.assertEqual(
            music_metadata.md5_hash(music_dir + "/01_Music/Goethe, Der Erlkoenig/Goethe, Der Erlkoenig_001.mp3"),
            "68ce74b5117852548bd29d4cb11b858b")
        self.assertEqual(
            music_metadata.md5_hash(music_dir + "/01_Music/Goethe, Der Zauberlehrling/Goethe, Der Zauberlehrling_001.mp3"),
            "2cf80edaf12d221399807329f840a6b4")

    def test_set_metadata_error(self):
        result = music_metadata.set_metadata_error(error="test-error", filename="music/test-error.mp3",
                                                   error_msg="test-error-msg", decoder="test-decoder")
        self.assertEqual(result["filesize"], 0)
        self.assertEqual(result["album"], "test-error")
        self.assertEqual(result["error"], "test-error-msg")
        self.assertTrue("music/test-error.mp3" in result["file"])
        self.assertTrue(result["uuid"].startswith("t_"))
        self.assertTrue("test-error" in result["title"])
        self.assertTrue("test-decoder" in result["title"])
        self.assertTrue(result["sort"].startswith("00000"))

    def test_read_metadata(self):
        filename = music_dir + music_testfile_1
        result = music_metadata.read_metadata(path_to_file=filename)
        print(result)
        self.assertEqual(result["album_artist"], "")
        self.assertEqual(int(result["track_num"]), 1)
        self.assertEqual(result["filesize"], 16261)
        self.assertEqual(result["length"], 3.752)
        self.assertEqual(result["title"], "Der Zauberlehrling 001")
        self.assertEqual(result["artist"], "Johann Wolfgang Goethe")

        filename = music_dir + music_testfile_3
        result = music_metadata.read_metadata(path_to_file=filename)
        print(result)
        self.assertEqual(int(result["track_num"]), 3)
        self.assertEqual(result["filesize"], 355127)
        self.assertEqual(result["length"], 20.208)
        self.assertEqual(result["title"], "Der Erlkoenig 003")
        self.assertEqual(result["album"], "Der Erlkönig")
        self.assertEqual(result["artist"], "Johann Wolfgang Goethe")
        self.assertEqual(result["decoder"], "eyed3")
        self.assertEqual(result["cover_image"], 1)

        filename = music_dir + music_testfile_4
        result = music_metadata.read_metadata(path_to_file=filename)
        print(result)
        self.assertEqual(result["filesize"], 243154)
        self.assertEqual(result["length"], 20.250666666666667)
        self.assertEqual(result["title"], "Der Erlkoenig 003")
        self.assertEqual(result["artist"], "Johann Wolfgang Goethe")
        self.assertEqual(result["album"], "Goethe, Der Erlkoenig (mp4)")
        self.assertEqual(result["decoder"], "mutagen::mp4")
        self.assertEqual(result["album_artist"], "")
        self.assertEqual(result["track_num"], ['1', ' 0'])  # track_no ????

    def test_read_metadata_mutagen(self):
        filename = music_dir + music_testfile_4
        result = music_metadata.read_metadata_mutagen(filename=filename, file_type="mp4")
        print(result)
        self.assertEqual(result["filesize"], 243154)
        self.assertEqual(result["length"], 20.250666666666667)
        self.assertEqual(result["title"], "Der Erlkoenig 003")
        self.assertEqual(result["artist"], "Johann Wolfgang Goethe")
        self.assertEqual(result["album"], "Goethe, Der Erlkoenig (mp4)")
        self.assertEqual(result["decoder"], "mutagen::mp4")
        self.assertEqual(result["album_artist"], "")
        self.assertEqual(result["track_num"], ['1', ' 0'])  # track_no ????

        filename = music_dir + music_testfile_1
        result = music_metadata.read_metadata_mutagen(filename=filename, file_type="mp3")
        print(result)
        self.assertEqual(result["filesize"], 16261)
        self.assertEqual(result["length"], 3.752)
        self.assertEqual(result["title"], "Der Zauberlehrling 001")
        self.assertEqual(result["artist"], "Johann Wolfgang Goethe")
        self.assertEqual(result["decoder"], "mutagen::mp3")
        self.assertEqual(result["album_artist"], None)
        self.assertEqual(result["track_num"], ['1'])  # track_no ????

    def test_read_metadata_id3(self):
        filename = music_dir + music_testfile_1
        result = music_metadata.read_metadata_id3(filename=filename, album_id="", album_nr="")
        print(result)
        self.assertEqual(result["album_artist"], "")
        self.assertEqual(int(result["track_num"]), 1)
        self.assertEqual(result["filesize"], 16261)
        self.assertEqual(result["length"], 3.752)
        self.assertEqual(result["title"], "Der Zauberlehrling 001")
        self.assertEqual(result["artist"], "Johann Wolfgang Goethe")
        self.assertEqual(result["decoder"], "eyed3")
        self.assertEqual(result["cover_image"], 0)

        filename = music_dir + music_testfile_2
        result = music_metadata.read_metadata_id3(filename=filename, album_id="", album_nr="")
        print(result)
        self.assertEqual(result["album_artist"], "")
        self.assertEqual(int(result["track_num"]), 4)
        self.assertEqual(result["filesize"], 81732)
        self.assertEqual(result["length"], 20.12)
        self.assertEqual(result["title"], "Der Zauberlehrling 004")
        self.assertEqual(result["artist"], "Johann Wolfgang Goethe")
        self.assertEqual(result["decoder"], "eyed3")
        self.assertEqual(result["cover_image"], 0)

        filename = music_dir + music_testfile_3
        result = music_metadata.read_metadata_id3(filename=filename, album_id="", album_nr="")
        print(result)
        self.assertEqual(result["album_artist"], None)
        self.assertEqual(int(result["track_num"]), 3)
        self.assertEqual(result["filesize"], 355127)
        self.assertEqual(result["length"], 20.208)
        self.assertEqual(result["title"], "Der Erlkoenig 003")
        self.assertEqual(result["artist"], "Johann Wolfgang Goethe")
        self.assertEqual(result["decoder"], "eyed3")
        self.assertEqual(result["cover_image"], 1)

    def test_save_image_as_file(self):
        filename = music_dir + music_testfile_3
        result = music_metadata.read_metadata_id3(filename=filename, album_id="", album_nr="")
        print(result)
        self.assertEqual(result["album_artist"], None)
        self.assertEqual(int(result["track_num"]), 3)
        self.assertEqual(result["filesize"], 355127)
        self.assertEqual(result["title"], "Der Erlkoenig 003")
        self.assertEqual(result["decoder"], "eyed3")
        self.assertEqual(result["cover_image"], 1)
        image = mbox.music_cover + result["cover_images"]["track"][0]
        print(image)
        self.assertTrue(os.path.isfile(image))
        self.assertTrue(os.path.getsize(image) > 0)

    def test_save_mp4_image_as_file(self):
        filename = music_dir + music_testfile_4
        result = music_metadata.read_metadata_mutagen(filename=filename, file_type="mp4")
        print(result)
        self.assertEqual(result["filesize"], 243154)
        self.assertEqual(result["title"], "Der Erlkoenig 003")
        self.assertEqual(result["decoder"], "mutagen::mp4")
        self.assertEqual(result["cover_image"], 1)
        image = mbox.music_cover + result["cover_images"]["track"][0]
        print(image)
        self.assertTrue(os.path.isfile(image))
        self.assertTrue(os.path.getsize(image) > 0)

