import sys
import os
import platform

if platform.system() == 'Windows':
    separator = '\\'
else:
    separator = '/'

sys.path.insert(0, '/'.join(os.path.dirname(os.path.realpath(__file__)).split(separator)[:-1]))

import list_youtube_channel


videos = list_youtube_channel.get_channel("UC9-y-6csu5WGm29I7JiwpnA", sort_by=list_youtube_channel.SORT_BY_POPULAR)

for video in videos:
    print(video['videoId'])
