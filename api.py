import praw
from psaw import PushshiftAPI

class Api:
    def __init__(self):
        self._praw = praw.Reddit()
        self._psaw = PushshiftAPI(self._praw)

    def search(self, subreddit, flair):
        for submission in self._psaw.search_submissions(subreddit=subreddit):
            print(submission)