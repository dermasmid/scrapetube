# Installation

```bash
pip3 install list_youtube_channel
```

# Usage

```python
import list_youtube_channel

videos = list_youtube_channel.get_channel("UC9-y-6csu5WGm29I7JiwpnA")

for video in videos:
    print(video['videoId'])
```
