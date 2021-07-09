from typing import Generator
import requests
import json
import time


def get_channel(channel_id: str, limit: int = None, sleep: int = 1, sort_by: str = 'newest') -> Generator:
    """Get videos for a channel.

    Parameters:
        channel_id (``str``):
            The channel id from the channel you want to get the videos for.
        limit (``int``, *optional*):
            Limit to number of videos you want to get.
        sleep (``int``, *optional*):
            Time to sleep between api calls to youtube in order to prevent getting blocked. Defaults to `1`.
        sort_by (``str``, *optional*):
            In what order to retrive to videos. Pass one of the following values.
            ``"newest"``: Get the new videos first.
            ``"oldest"``: Get the old videos first.
            ``"popular"``: Get the popular videos first.
            Defaults to ``"newest"``.
    """

    sort_by_map = {
        'newest': 'dd',
        'oldest': 'da',
        'popular': 'p'
    }
    url = f'https://www.youtube.com/channel/{channel_id}/videos?view=0&sort={sort_by_map[sort_by]}&flow=grid'
    api_endpoint = 'https://www.youtube.com/youtubei/v1/browse'
    videos = get_videos(url, api_endpoint, 'gridVideoRenderer', limit, sleep)
    for video in videos:
        yield video


def get_playlist(playlist_id: str, limit: int = None, sleep: int = 1):
    """Get videos for a playlist.

    Parameters:
        playlist_id (``str``):
            The playlist id from the playlist you want to get the videos for.
        limit (``int``, *optional*):
            Limit to number of videos you want to get.
        sleep (``int``, *optional*):
            Time to sleep between api calls to youtube in order to prevent getting blocked. Defaults to `1`.
    """

    url = f'https://www.youtube.com/playlist?list={playlist_id}'
    api_endpoint = 'https://www.youtube.com/youtubei/v1/browse'
    videos = get_videos(url, api_endpoint, 'playlistVideoRenderer', limit, sleep)
    for video in videos:
        yield video


def get_search(query: str, limit: int = None, sleep: int = 1, sort_by: str = 'relevance', results_type: str = 'video') -> Generator:
    """Search youtube and get videos.

    Parameters:
        query (``str``):
            The term you want to search for.
        limit (``int``, *optional*):
            Limit to number of videos you want to get.
        sleep (``int``, *optional*):
            Time to sleep between api calls to youtube in order to prevent getting blocked. Defaults to `1`.
        sort_by (``str``, *optional*):
            In what order to retrive to videos. Pass one of the following values.
            ``"relevance"``: Get the new videos in order of relevance.
            ``"upload_date"``: Get the new videos first.
            ``"view_count"``: Get the popular videos first.
            ``"rating"``: Get videos with more likes first.
            Defaults to ``"relevance"``.
        results_type (``str``, *optional*):
            What type you want to search for. Pass one of the following values.
            ``"video"``|``"channel"``|``"playlist"``|``"movie"``
            Defaults to `"video"`.
    """

    sort_by_map = {
        'relevance': 'A',
        'upload_date': 'I',
        'view_count': 'M',
        'rating': 'E'
    }

    results_type_map = {
        'video': ['B', 'videoRenderer'],
        'channel': ['C', 'channelRenderer'],
        'playlist': ['D', 'playlistRenderer'],
        'movie': ['E', 'videoRenderer']
    }

    param_string = f'CA{sort_by_map[sort_by]}SAhA{results_type_map[results_type][0]}'
    url = f'https://www.youtube.com/results?search_query={query}&sp={param_string}'
    api_endpoint = 'https://www.youtube.com/youtubei/v1/search'
    videos = get_videos(url, api_endpoint, results_type_map[results_type][1], limit, sleep)
    for video in videos:
        yield video


def get_videos(url: str, api_endpoint: str, selector: str, limit: int, sleep: int) -> Generator:
    session = requests.Session()
    session.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36'
    is_first = True
    count = 0
    while True:
        if is_first:
            html = get_initial_data(session, url)
            client = json.loads(get_json_from_html(
                html, 'INNERTUBE_CONTEXT', 2, '"}},') + '"}}')['client']
            api_key = get_json_from_html(html, 'innertubeApiKey', 3)
            session.headers['X-YouTube-Client-Name'] = '1'
            session.headers['X-YouTube-Client-Version'] = client['clientVersion']
            data = json.loads(get_json_from_html(
                html, 'var ytInitialData = ', 0, '};') + '}')
            next_data = get_next_data(data)
            is_first = False
        else:
            data = get_ajax_data(session, api_endpoint, api_key, next_data, client)
            next_data = get_next_data(data)
        for result in get_videos_items(data, selector):
            count += 1
            yield result
            if count == limit:
                break

        if not next_data or count == limit:
            break

        time.sleep(sleep)


def get_initial_data(session: requests.Session, url: str) -> str:
    response = session.get(url)
    if 'uxe=' in response.request.url:
        session.cookies.set('CONSENT', 'YES+cb', domain='.youtube.com')
        response = session.get(url)

    html = response.text
    return html


def get_ajax_data(session: requests.Session, api_endpoint: str, api_key: str, next_data: dict, client: dict) -> dict:
    data = {
        "context": {
            'clickTracking': next_data['click_params'],
            'client': client
        },
        'continuation': next_data['token']
    }
    response = session.post(api_endpoint, params={'key': api_key}, json=data)
    return response.json()


def get_json_from_html(html: str, key: str, num_chars: int = 2, stop: str = '"') -> str:
    pos_begin = html.find(key) + len(key) + num_chars
    pos_end = html.find(stop, pos_begin)
    return html[pos_begin: pos_end]


def get_next_data(data: dict) -> dict:
    raw_next_data = next(search_dict(data, 'continuationEndpoint'), None)
    if not raw_next_data:
        return None
    next_data = {'token': raw_next_data['continuationCommand']['token'], 'click_params': {
        "clickTrackingParams": raw_next_data['clickTrackingParams']}}

    return next_data


def search_dict(partial: dict, search_key: str) -> Generator:
    stack = [partial]
    while stack:
        current_item = stack.pop(0)
        if isinstance(current_item, dict):
            for key, value in current_item.items():
                if key == search_key:
                    yield value
                else:
                    stack.append(value)
        elif isinstance(current_item, list):
            for value in current_item:
                stack.append(value)


def get_videos_items(data: dict, selector: str) -> Generator:
    return search_dict(data, selector)
