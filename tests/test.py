import sys
import os
import platform

if platform.system() == 'Windows':
    separator = '\\'
else:
    separator = '/'

sys.path.insert(0, '/'.join(os.path.dirname(os.path.realpath(__file__)).split(separator)[:-1]))

import scrapetube


videos = scrapetube.get_channel("UC9-y-6csu5WGm29I7JiwpnA", sort_by='popular')

for video in videos:
    print(video['videoId'])
