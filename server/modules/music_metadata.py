import os
import uuid
import logging
import hashlib

import eyed3
from mutagen.id3 import ID3
from mutagen.mp3 import MP3
from mutagen.mp4 import MP4, MP4Cover

import modules.config_mbox as mbox
import modules.config_stage as stage
import modules.run_cmd as run_cmd


md_logging = logging.getLogger("metadata")
md_logging.setLevel(stage.logging_level_data)

if stage.logging_level != logging.DEBUG:
    id3_logging = logging.getLogger("eyed3.id3")
    id3_logging.setLevel(logging.ERROR)
    id3_logging = logging.getLogger("eyed3.mp3")
    id3_logging.setLevel(logging.ERROR)
    id3_logging = logging.getLogger("eyed3.core")
    id3_logging.setLevel(logging.ERROR)
    id3_logging = logging.getLogger("eyed3.mp3.headers")
    id3_logging.setLevel(logging.ERROR)


class ExtractMetadata:

    def __init__(self):
        return


def md5_hash(filename):
    """
    create MD5 hash of filename
    """
    hash_md5 = hashlib.md5()
    with open(filename, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def set_metadata_error(error, filename, error_msg="", decoder=""):
    """
    create tags if an error occurred during file detection and metadata extraction
    """
    temp = filename.split("/")
    directory = filename.replace(temp[len(temp) - 1], "")
    directory = directory.replace(mbox.music_dir, "")
    filename = temp[len(temp) - 1]

    tags = {
        "uuid": "t_" + str(uuid.uuid1()),
        "file": directory + filename,
        "filesize": 0,
        "artist": "#error: " + directory,
        "album": error,
        "albumsize": 0,
        "title": filename + " (error: " + error + ")",
        "error": error,
        "sort": "00000" + filename
    }

    if decoder != "":
        md_logging.warning(" ... ERROR: " + error + ": " + filename + " (decoder: " + decoder + ")")
        tags["decoder"] = decoder
    else:
        md_logging.warning(" ... ERROR: " + error + ": " + filename)

    if error_msg != "":
        tags["error"] = error_msg

    return tags.copy()


def read_metadata(path_to_file):
    """
    get metadata from music file, return as standardized dict
    """

    tags = {}
    temp = path_to_file.split("/")
    filename = temp[len(temp) - 1]
    filepath = path_to_file.replace(stage.data_dir, "")

    md_logging.debug(" .. Read: " + filepath)
    run_cmd.file_logging(" .. Read: " + filepath)

    # check if file is empty
    file_stats = os.stat(path_to_file)
    if file_stats.st_size == 0:
        tags = set_metadata_error(error="Empty file", filename=path_to_file)
        return tags

    # check file type and read metadata
    if ".mp3" in filename.lower():
        tags = read_metadata_id3(path_to_file)
        if tags["filesize"] == 0:
            return tags

        # logging.info(tags)
        if "artist" not in tags and "album" not in tags:
            tags = read_metadata_mutagen(path_to_file, "mp3")
        elif tags["artist"] == "" and tags["album"] == "":
            tags = read_metadata_mutagen(path_to_file, "mp3")

    elif ".m4a" in filename.lower():
        tags = read_metadata_mutagen(path_to_file, "mp4")

    elif ".mp4" in filename.lower():
        tags = read_metadata_mutagen(path_to_file, "mp4")

    else:
        tags = set_metadata_error(error="file format not supported", filename=path_to_file)
        return tags

    if "artist" not in tags or tags["artist"] == "":
        tags["artist"] = "Unknown Artist"
    elif tags["artist"] is None:
        tags["artist"] = "Unknown Artist"
    if "album" not in tags or tags["album"] == "":
        tags["album"] = "Unknown Album"
    elif tags["album"] is None:
        tags["album"] = "Unknown Album"
    if "title" not in tags or tags["title"] == "":
        tags["title"] = filename
    elif tags["title"] is None:
        tags["title"] = filename

    if tags["album"] == "Unbekanntes Album":          tags["album"] = "Unknown Album"
    if tags["artist"] == "Unbekannte Künstler":       tags["album"] = "Unknown Artist"

    tags["MD5"] = md5_hash(path_to_file)

    if "track_no" in tags:
        del tags["track_no"]
    if "disc_no" in tags:
        del tags["disc_no"]

    md_logging.debug(" ..... Album/Artist: " + tags["album"] + " / " + tags["artist"])
    run_cmd.file_logging(" ..... Album/Artist: " + tags["album"] + " / " + tags["artist"])
    md_logging.debug(" ..... MD5: " + tags["MD5"])
    return tags


def read_metadata_mutagen(filename, file_type="mp4"):
    """
    read metadata from mp4 file
    """

    md_logging.debug(" ... Read metadata (Mutagen::" + file_type + ")")

    relevant_tags = {}
    data = {}

    if file_type == "mp4":
        relevant_tags = {  # https://mutagen.readthedocs.io/en/latest/api/mp4.html
            "album": "\xa9alb",
            "title": "\xa9nam",
            "genre": "\xa9gen",
            "artist": "\xa9ART",
            "album artist": "aART",
            "composer": "\xa9wrt",
            "disk_no": "disk",
            "track_no": "trkn"
        }
        # img = "covr"
        try:
            tags = MP4(filename).tags
        except Exception as e:
            tags = set_metadata_error(error="Not a correct MP4 file: ", filename=filename, error_msg=str(e),
                                      decoder="mutagen::" + file_type)
            return tags

    elif file_type == "mp3":  # https://en.wikipedia.org/wiki/ID3
        relevant_tags = {  # https://mutagen.readthedocs.io/en/latest/api/id3.html
            "album": "TALB",
            "title": "TIT2",
            "genre": "TCON",
            "artist": "TPE1",
            "album artist": "TPE2",
            "composer": "TCOM",
            "length": "TLEN",
            "track_no": "TRCK",
            "disc_no": "TPOS",
            "album_no": "TSOA"
        }

        try:
            tags = ID3(filename)  # .tags
        except Exception as e:
            tags = set_metadata_error(error="Not a correct MP3 file", filename=filename, error_msg=str(e),
                                      decoder="mutagen::" + file_type)
            return tags

    for r_tag in relevant_tags:
        for f_tag in tags:
            if relevant_tags[r_tag] in f_tag:
                value = tags[f_tag]
                data[r_tag] = value[0]

    if file_type == "mp3":
        try:
            data["length"] = MP3(filename).info.length
        except Exception as e:
            data = set_metadata_error(error="Can't get file length", filename=filename, error_msg=str(e),
                                      decoder="mutagen::" + file_type)
            return data

    elif file_type == "mp4":
        try:
            data["length"] = MP4(filename).info.length
        except Exception as e:
            data = set_metadata_error(error="Can't get file length", filename=filename, error_msg=str(e),
                                      decoder="mutagen::" + file_type)
            return data

    if file_type == "mp4" and "track_no" in data:
        track_no = str(data["track_no"])
        track_no = track_no.replace("(", "")
        track_no = track_no.replace(")", "")
        data["track_num"] = track_no.split(",")

    if file_type == "mp3" and "track_no" in data:
        if "/" in data["track_no"]:
            data["track_num"] = data["track_no"].split("/")
        elif "," in data["track_no"]:
            data["track_num"] = data["track_no"].split(",")
        else:
            data["track_num"] = [data["track_no"]]
        if "disc_no" in data and "/" in data["disc_no"]:
            data["disc_num"] = data["disc_no"].split("/")[0]
        elif "disc_no" in data:
            data["disc_num"] = data["disc_no"]

    data["file"] = filename.replace(mbox.music_dir, "")
    data["uuid"] = "t_" + str(uuid.uuid1())
    data["compliation"] = 0
    data["filesize"] = os.path.getsize(filename)
    data["cover_images"] = {}
    data["cover_images"]["track"] = []

    data["sort"] = 0
    if "track_num" in data and int(data["track_num"][0]) > 0: data["sort"] += int(data["track_num"][0])
    if "disc_num" in data and int(data["disc_num"]) > 0:      data["sort"] += int(data["disc_num"]) * 1000
    data["sort"] = str(data["sort"]).zfill(5) + data["file"]

    for tag in tags:
        if "covr" in tag:
            data["cover_images"]["track"] = [save_image_as_file(data["uuid"] + "_0", tags[tag]).replace(mbox.music_cover, "")]
            data["cover_images"]["active"] = "track"

        if "APIC" in tag:
            data["cover_images"]["track"] = [save_image_as_file(data["uuid"] + "_0", tags[tag]).replace(mbox.music_cover, "")]
            data["cover_images"]["active"] = "track"

    data["decoder"] = "mutagen::" + file_type
    return data.copy()


def read_metadata_id3(filename, album_id="", album_nr=""):
    """
    read metadata from mp3 file, for available tags see https://eyed3.readthedocs.io/en/latest/eyed3.id3.html?highlight=images#eyed3.id3.tag.Tag.images
    """
    md_logging.debug(" ... Read ID3 (eyed3::mp3)")
    run_cmd.file_logging(" ... Read ID3 (eyed3::mp3)")
    found = True

    # load data from audio file
    audiofile = eyed3.load(filename)
    albumdirs = filename.split("/")
    albumdir = albumdirs[len(albumdirs) - 1]
    filesize = os.path.getsize(filename)
    try:
        a = MP3(filename.encode('utf-8'))
        filelength = a.info.length
    except Exception as e:
        tags = set_metadata_error(error="Not a correct MP3 file", filename=filename, error_msg=str(e),
                                  decoder="eyed3::mp3")
        return tags

    # read tags from audio file
    tags = {}

    try:
        test = audiofile.tag.title
        tags_available = True
    except:
        tags_available = False

    if tags_available and audiofile.tag.title is not None:
        tags["artist"] = audiofile.tag.artist  # .encode('utf-8')
        tags["title"] = audiofile.tag.title  # .encode('utf-8')
        tags["album"] = audiofile.tag.album
        tags["album_dir"] = albumdir
        tags["album_artist"] = audiofile.tag.album_artist
        tags["track_num"] = str(audiofile.tag.track_num)
        tags["compilation"] = 0
        tags["filesize"] = filesize
        tags["length"] = filelength

        try:
            tags["track_total"] = audiofile.tag.track_total
        except Exception as e:
            tags["track_total"] = ""
            md_logging.debug(" ... Error in 'track_total': " + str(e))
            run_cmd.file_logging(" ... Error in 'track_total': " + str(e))

        try:
            if "," in tags["track_num"]:
                tags["track_num"] = tags["track_num"].replace("(", "")
                tags["track_num"] = tags["track_num"].replace(")", "")
                temp = tags["track_num"].split(",")
                tags["track_num"] = temp[0]
                if tags["track_total"] == "":
                    tags["track_total"] = temp[1]
        except Exception as e:
            md_logging.debug(" ... Error decoding 'track_num': " + str(e))
            run_cmd.file_logging(" ... Error decoding 'track_num': " + str(e))

        try:
            tags["disc_num"] = audiofile.tag.disc  # disc number
            tags["disc_total"] = audiofile.tag.disc_total  # the total number of discs
        except Exception as e:
            tags["disc_num"] = "0"
            tags["disc_total"] = "0"
            md_logging.debug(" ... Error in 'disc_num' or 'disc_total': " + str(e))
            run_cmd.file_logging(" ... Error in 'disc_num' or 'disc_total': " + str(e))

        try:
            tags["genre"] = str(audiofile.tag.genre)
            tags["genre"] = tags["genre"]  # .encode('utf-8')
        except Exception as e:
            tags["genre"] = ""
            md_logging.debug(" ... Error in 'genre': " + str(e))
            run_cmd.file_logging(" ... Error in 'genre': " + str(e))

        tags["file"] = filename.replace(mbox.music_dir, "")
        tags["uuid"] = "t_" + str(uuid.uuid1())
        # tags["duration"]     = audiofile.tag.duration

        tags["sort"] = 0

        try:
            if "track_num" in tags and tags["track_num"] is not None and int(tags["track_num"]) > 0:
                tags["sort"] += int(tags["track_num"])
        except Exception as e:
            md_logging.debug(" ... Error in 'track_num' (" + str(tags["track_num"]) + "): " + str(e))
            run_cmd.file_logging(" ... Error in 'track_num' (" + str(tags["track_num"]) + "): " + str(e))

        try:
            if "disc_num" in tags and tags["disc_num"] is not None and int(tags["disc_num"]) > 0:
                tags["sort"] += int(tags["disc_num"]) * 1000
        except Exception as e:
            md_logging.debug(" ... Error in 'disc_num' (" + str(tags["disc_num"]) + "): " + str(e))
            run_cmd.file_logging(" ... Error in 'disc_num' (" + str(tags["disc_num"]) + "): " + str(e))

        tags["sort"] = str(tags["sort"]).zfill(5) + tags["file"]

        # check for images and write to file
        tags["cover_images"] = {}
        tags["cover_images"]["track"] = []

        if len(audiofile.tag.images) > 0:
            # tags["cover_image"]  = 1 #audiofile.tag.images
            images = audiofile.tag.images
            count = 0
            for IMAGE in images:
                count += 1
                try:
                    image_url = save_image_as_file(tags["uuid"] + "_" + str(count),
                                                   IMAGE.image_data).replace(mbox.music_cover, "")
                    if image_url:
                        tags["cover_images"]["track"].append(image_url)
                        tags["cover_images"]["active"] = "track"
                        tags["cover_image"] = 1
                except Exception as e:
                    md_logging.debug(" ... Error writing 'cover_images': " + str(e))
                    run_cmd.file_logging(" ... Error writing 'cover_images': " + str(e))

        else:
            tags["cover_image"] = 0

    else:
        found = False

    if not found:
        filename_log = filename.replace(stage.data_dir, "")
        # ###md_logging.info("test// ...  " + filename_log)

        tags["artist"] = ""
        tags["title"] = filename.replace(mbox.music_dir, "")
        tags["album"] = ""
        tags["album_artist"] = ""
        tags["track_num"] = [0, 0]
        tags["file"] = filename.replace(mbox.music_dir, "")
        tags["uuid"] = "t_" + str(uuid.uuid1())
        tags["compliation"] = 0
        tags["filesize"] = filesize
        tags["length"] = filelength

    tags["decoder"] = "eyed3"
    return tags.copy()


def save_image_as_file(name, idata):
    """ write image data to file """

    dtype = type(idata)
    md_logging.debug(" ... Write Image: " + name + " (" + str(dtype) + ")")
    run_cmd.file_logging(" ... Write Image: " + name + " (" + str(dtype) + ")")

    if "id3.APIC" in str(dtype):  # <class 'mutagen.id3.APIC'>
        data = idata.data
    elif "bytes" in str(dtype):  # <class 'bytes'>
        data = idata
    else:  # byte object in array
        data = idata[0]

    filename = mbox.music_cover + name + ".jpg"
    file = open(filename, "wb")
    file.write(data)
    file.close()
    return filename


def save_mp4_image_as_file(uuid, target_file):
    """ write image data from mp4-file to file """

    filename = mbox.music_cover + uuid + ".jpg"
    return filename.copy()

