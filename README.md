# RedditFlair
A Reddit image client which bypasses the 1000 post limit using the [pushshift API](https://github.com/pushshift/api ), and can filter by flair.<br>
Also supports the prefetching and lazy-loading of images for a more responsive experience.

Reddit has a global [1000 post limit on listings](https://www.reddit.com/8zhcmr ), which is reached especially quickly when filtering posts by a flair. 
The ability to natively query by timestamp was also recently dropped, meaning that the only way to search for submissions past the 1000 new/hot/top ones
is to use a 3rd party api, such as the [pushshift API](https://github.com/pushshift/api ).

While gallery browsers for Reddit do exist, I couldn't find any that were not subject to this limitation because they didn't use 3rd party APIs. Hence, RedditFlair

<center><img src="res/scrot.png"></center>

# Usage
### Downloading/Installing
`cd` into the directory where you want to put the program, then:

```
git clone https://github.com/pixelzery/RedditFlair.git
cd RedditFlair
python3 -m pip install -r requirements.txt
```

### Launch
```
python3 main.py
```