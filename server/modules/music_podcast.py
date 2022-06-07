import time
import datetime
import logging
import requests
import uuid
import threading

from xml.etree import cElementTree as ET
from collections import defaultdict

import modules.config_stage as stage
import modules.run_cmd as run_cmd


class PodcastThread(threading.Thread):

    def __init__(self, thread_database, thread_speak, start_time):
        """
        set initial values to vars and start VLC
        """
        threading.Thread.__init__(self)
        self.database = thread_database
        self.speak = thread_speak
        self.running = True
        self.temp_podcasts = {}
        self.update_interval = 60 * 60
        self.playing = 0
        self.playing_uuid = ""
        self.podcast_ending = [".xml", ".podcast", ".rss", "feed/mp3"]

        self.logging = logging.getLogger("podcast")
        self.logging.setLevel = stage.logging_level

    def run(self):
        """
        run thread (nothing special at the moment)
        """
        self.logging.info("Start PodCasts ... ")

        count_error = 0
        time.sleep(2)

        while self.running:
            streams = self.database.read_cache("radio")

            ######## DOESN'T WORK
            for stream_uuid in streams:

                if stream_uuid != self.playing_uuid:
                    stream = streams[stream_uuid]
                    if "stream_url" in stream:
                        stream_url = stream["stream_url"]

                        for end in self.podcast_ending:
                            if stream_url.endswith(end):
                                if stream_uuid not in self.temp_podcasts:
                                    podcast = self.get_tracks_rss(rss_url=stream_url, playlist_uuid=stream_uuid)
                                    self.temp_podcasts[stream_uuid] = podcast

                                elif self.temp_podcasts[stream_uuid] == "":
                                    count_error += 1
                                    if count_error == 15:
                                        count_error = 0
                                        podcast = self.get_tracks_rss(rss_url=stream_url, playlist_uuid=stream_uuid)
                                        self.temp_podcasts[stream_uuid] = podcast

                                elif self.temp_podcasts[stream_uuid]["update"] + self.update_interval < time.time():
                                    podcast = self.get_tracks_rss(rss_url=stream_url, playlist_uuid=stream_uuid)
                                    self.temp_podcasts[stream_uuid] = podcast

                    else:
                        self.logging.warning("No Stream_URL for " + stream_uuid)

            time.sleep(1)

        self.logging.info("Stopped PodCasts.")

    def stop(self):
        """
        Stop thread
        """
        self.running = False

    def check_playing_podcast(self, playing, playing_data):
        """
        check if a podcast is playing
        """
        playing_song = playing_data["song"]
        if "album_uuid" in playing_song and playing_song["album_uuid"].startswith("r_"):
            self.playing = playing
            self.playing_uuid = playing_song["album_uuid"]
            if "podcast" in playing_data:
                playing_podcast = playing_data["podcast"]
                self.temp_podcasts[self.playing_uuid] = playing_podcast
        else:
            self.playing = 0
            self.playing_uuid = ""

    def get_podcasts(self, playlist_uuid, stream_url=""):
        """
        return info from cache
        """
        self.logging.info("Load Podcast " + playlist_uuid + "/" + stream_url)
        if playlist_uuid in self.temp_podcasts:
            if "title" in self.temp_podcasts:
                self.logging.info(self.temp_podcasts[playlist_uuid]["title"])
            else:
                self.logging.info(str(self.temp_podcasts[playlist_uuid]))
            return self.temp_podcasts[playlist_uuid].copy()

        elif stream_url != "":
            for end in self.podcast_ending:
                if stream_url.endswith(end):
                    get_rss = self.get_tracks_rss(stream_url, playlist_uuid)
                    if get_rss != "":
                        return get_rss
                    else:
                        return {}
        return {}

    def get_tracks_rss(self, rss_url, playlist_uuid):
        """
        get tracks from rrs feed (itunes-format)
        """
        if not self.internet_connection():
            return

        try:
            self.logging.info("Read podcast:" + rss_url)
            response = requests.get(rss_url)
            response.encoding = response.apparent_encoding
            # self.logging.info(response.encoding)
            playlist = response.text  #### -> UTF-8 ???
            playlist = playlist.encode('utf-8')

        except requests.exceptions.RequestException as e:
            self.logging.error("Can't open the podcast info from RSS/XML: " + str(e))
            self.speak.speak_message("CANT-OPEN-STREAM")
            return ""

        e = ET.XML(playlist)
        data_all = etree_to_dict(e)["rss"]["channel"]
        data_items = data_all["item"]

        itunes_sub = "{http://www.itunes.com/dtds/podcast-1.0.dtd}"

        #      self.logging.info(".")
        #      self.logging.info(str(data_all))

        update_date = datetime.datetime.now()
        podcast = {
            "title": data_all["title"],
            "album": data_all["title"],
            "uuid": playlist_uuid,
            "artist": data_all[itunes_sub + "author"],
            "cover_images": {"active": "track", "active_pos": 0, "url": [], "track": [], "dir": [], "upload": []},
            "stream_info": data_all["link"],
            "stream_link": rss_url,
            "tracks": {},
            "track_count": 0,
            "track_list": [],
            "track_url": {},
            "publication": "",
            "description": "",
            "update": time.time(),
            "update_date": update_date.strftime('%d.%m.%Y %H:%M')
        }

        if "pubDate" in data_all: podcast["publication"] = data_all["pubDate"]
        if "description" in data_all: podcast["description"] = data_all["description"]

        if itunes_sub + "image" in data_all and "@href" in data_all[itunes_sub + "image"]:
            data_all["image"] = {}
            data_all["image"]["url"] = data_all[itunes_sub + "image"]["@href"]

        if "image" in data_all and "url" in data_all["image"]:
            podcast["cover_images"]["url"] = [data_all["image"]["url"]]
            podcast["cover_images"]["active"] = "url"

        podcast_sort = {}
        item_count = 0
        for item in data_items:
            item_uuid = "t_" + str(uuid.uuid1())
            item_count += 1
            podcast["tracks"][item_uuid] = {
                "decoder": "jc:music:podcast",
                "description": item["description"],
                "album": podcast["title"],
                "album_uuid": playlist_uuid,
                "file": item["enclosure"]["@url"],
                "filesize": float(item["enclosure"]["@length"]) / 1000,
                "image": "",
                "title": item["title"],
                "track_num": [],
                "type": item["enclosure"]["@type"],
                "url": item["enclosure"]["@url"],
                "uuid": item_uuid
            }

            podcast["track_url"][item["enclosure"]["@url"]] = item_uuid

            if "pubDate" in item:
                podcast["tracks"][item_uuid]["publication"] = item["pubDate"]

                if "+" in item["pubDate"] or "-" in item["pubDate"]:
                    time_format = "%a, %d %b %Y %H:%M:%S %z"
                else:
                    time_format = "%a, %d %b %Y %H:%M:%S %Z"
                time_input = item["pubDate"]
                time_stamp = time.mktime(datetime.datetime.strptime(time_input, time_format).timetuple())
                podcast_sort[time_stamp] = item_uuid

                podcast["tracks"][item_uuid]["publication"] = datetime.datetime.fromtimestamp(time_stamp).strftime(
                    "%d.%m.%Y %H:%M")

            if itunes_sub + "duration" in item:
                length_format = "%H:%M:%S"
                podcast["tracks"][item_uuid]["duration"] = item[itunes_sub + "duration"]
                if ":" in item[itunes_sub + "duration"]:
                    hour, minute, second = podcast["tracks"][item_uuid]["duration"].split(":")
                    podcast["tracks"][item_uuid]["length"] = float(hour) * 3600 + float(minute) * 60 + float(second)
                else:
                    podcast["tracks"][item_uuid]["length"] = float(item[itunes_sub + "duration"])

            if itunes_sub + "image" in item:
                podcast["tracks"][item_uuid]["image"] = item[itunes_sub + "image"]["@href"]
                if podcast["track_count"] == 1:
                    podcast["cover_images"]["track"].append(item[itunes_sub + "image"]["@href"])

        track_position = len(podcast_sort)
        for key in sorted(podcast_sort):
            podcast["track_list"].append(podcast_sort[key])
            podcast["track_count"] += 1
            podcast["tracks"][podcast_sort[key]]["track_num"] = [track_position, len(podcast_sort)]
            track_position -= 1

        podcast["track_list"] = podcast["track_list"][::-1]

        self.logging.debug(str(podcast))
        return podcast

    def internet_connection(self):
        """
        check if connection to internet exists
        """
        error_msg = run_cmd.check_internet_connect()

        if error_msg == "DNS-ERROR":
            self.logging.error("Could not connect to INTERNET!")
            self.speak.speak_message("CONNECTION-ERROR-RESTART-SHORTLY")
            time.sleep(20)
            return False

        elif error_msg != "CONNECTED":
            self.logging.error("Could not connect to INTERNET!")
            self.speak.speak_message("NO-INTERNET-CONNECTION")
            time.sleep(0.5)
            self.speak.speak_message("TRY-AGAIN-IN-A-MINUTE")
            time.sleep(20)
            self.music_ctrl["LastCard"] = ""
            return False

        return True


def etree_to_dict(t):
    """
    convert XML structure to dict
    """
    d = {t.tag: {} if t.attrib else None}
    children = list(t)
    if children:
        dd = defaultdict(list)
        for dc in map(etree_to_dict, children):
            for k, v in dc.items():
                dd[k].append(v)
        d = {t.tag: {k: v[0] if len(v) == 1 else v for k, v in dd.items()}}
    if t.attrib:
        d[t.tag].update(('@' + k, v) for k, v in t.attrib.items())
    if t.text:
        text = t.text.strip()
        if children or t.attrib:
            if text:
                d[t.tag]['#text'] = text
        else:
            d[t.tag] = text
    return d
