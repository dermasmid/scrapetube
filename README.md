# Scrapetube
This module will help you scrape youtube without the official youtube api and without selenium.

With this module you can:


* Get all videos from a Youtube channel.
* Get all videos from a playlist.
* Search youtube.

# Installation

```bash
pip3 install scrapetube
```

# Usage
Here's a few short code examples.

## Get all videos for a channel
```python
import scrapetube

videos = scrapetube.get_channel("UCCezIgC97PvUuR4_gbFUs5g")

for video in videos:
    print(video['videoId'])
```

## Get all videos for a playlist
```python
import scrapetube

videos = scrapetube.get_playlist("PL-osiE80TeTt2d9bfVyTiXJA-UTHn6WwU")

for video in videos:
    print(video['videoId'])
```

## Make a search
```python
import scrapetube

videos = scrapetube.get_search("python")

for video in videos:
    print(video['videoId'])
```

# Full Documentation

[https://scrapetube.readthedocs.io/en/latest/](https://scrapetube.readthedocs.io/en/latest/)
