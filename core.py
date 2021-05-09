import praw
import json
import math
import os
from psaw import PushshiftAPI

class Api:
    def __init__(self):
        self._praw = praw.Reddit(client_secret=None, **self._get_auth())
        self._psaw = PushshiftAPI(self._praw)

    def _get_auth(self):
        with open("auth.json", "r") as f:
            return json.load(f)

    def search(self, subreddit, flair, **kwargs):
        for submission in self._psaw.search_submissions(subreddit=subreddit, **kwargs):
            if flair is not None and len(flair.strip()) > 0:
                if submission.link_flair_text == flair:
                    yield submission
            else:
                yield submission

class Config:
    def __init__(self, path):
        self._path = path
        self._data = {}
        self._load()

    def _load(self):
        if not os.path.isfile(self._path):
            return

        with open(self._path, 'r') as f:
            self._data = json.load(f)

    def _save(self):
        with open(self._path, 'w') as f:
            json.dump(self._data, f, indent=4)

    def __getitem__(self, key):
        return self._data[key]

    def __setitem__(self, key, value):
        self._data[key] = value
        self._save()

    def get(self, key, default=None):
        return self._data.get(key, default)

    def set(self, key, value):
        self[key] = value

config: Config = Config("config.json")


def human_number(num):
    """
    return human-readable version of number. E.g: 30.4k
    """
    # https://gist.github.com/pixelzery/eace0b100a381e7cf724612b7309a9d2
    if num == 0:
        return "0"
    elif num < 0:
        return "-" + human_number(-num)

    suffixes = ['', 'k', 'm', 'b', 't']
    suf_index = math.floor(math.log(num, 1000))
    big = (1000 ** suf_index)

    ret = ''
    ret += str(num // big)
    decimal_part = round((num % big) / (big / 10))
    if decimal_part > 0:
        ret += '.' + str(decimal_part)
    ret += suffixes[suf_index] if suf_index < len(suffixes) else ''
    return ret
