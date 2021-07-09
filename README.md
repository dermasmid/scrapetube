# List Yuotube channel
This module was originally made to get a list of all the videos from a Yuotube channle, but was then extended to include some other functionality.

With this module you can:


* Get all videos from a Youtube channel.
* Get all videos from a playlist.
* Search youtube.

# Installation

```bash
pip3 install list_youtube_channel
```

# Usage
Here a few short code examples.

## Get all videos for a channel
```python
import list_youtube_channel

videos = list_youtube_channel.get_channel("UCCezIgC97PvUuR4_gbFUs5g")

for video in videos:
    print(video['videoId'])
```

## Get all videos for a playlist
```python
import list_youtube_channel

videos = list_youtube_channel.get_playlist("PL-osiE80TeTt2d9bfVyTiXJA-UTHn6WwU")

for video in videos:
    print(video['videoId'])
```

## Make a search
```python
import list_youtube_channel

videos = list_youtube_channel.get_search("python")

for video in videos:
    print(video['videoId'])
```

# Full Documentation

[https://list-youtube-channel.readthedocs.io/en/latest/](https://list-youtube-channel.readthedocs.io/en/latest/)
