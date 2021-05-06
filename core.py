import praw
import json
import os
from psaw import PushshiftAPI

class Api:
    def __init__(self):
        self._praw = praw.Reddit(client_secret=None, **self._get_auth())
        self._psaw = PushshiftAPI(self._praw)

    def _get_auth(self):
        with open("auth.json", "r") as f:
            return json.load(f)

    def search(self, subreddit, flair):
        for submission in self._psaw.search_submissions(subreddit=subreddit):
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
