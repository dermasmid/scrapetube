from typing import Generator
import requests
import json
import time


SORT_BY_NEWEST = 'newest'
SORT_BY_OLDEST = 'oldest'
SORT_BY_POPULAR = 'popular'

def get_channel(channel_id: str, limit: int = None, sleep: int = 1, sort_by: str = SORT_BY_NEWEST) -> Generator:
    session = requests.Session()
    session.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36'
    is_first = True
    count = 0
    while True:
        if is_first:
            html = get_initial_data(session, channel_id, sort_by)
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
            data = get_ajax_data(session, api_key, next_data, client)
            next_data = get_next_data(data)

        for result in get_videos(data):
            count += 1
            yield result
            if count == limit:
                break

        if not next_data or count == limit:
            break

        time.sleep(sleep)


def get_initial_data(session: requests.Session, channel_id: str, sort_by: str) -> str:
    sort_by_map = {
        SORT_BY_NEWEST: 'dd',
        SORT_BY_OLDEST: 'da',
        SORT_BY_POPULAR: 'p'
    }
    url = f'https://www.youtube.com/channel/{channel_id}/videos?view=0&sort={sort_by_map[sort_by]}&flow=grid'
    response = session.get(url)
    if 'uxe=' in response.request.url:
        session.cookies.set('CONSENT', 'YES+cb', domain='.youtube.com')
        response = session.get(url)

    html = response.text
    return html


def get_ajax_data(session: requests.Session, api_key: str, next_data: dict, client: dict) -> dict:
    data = {
        "context": {
            'clickTracking': next_data['click_params'],
            'client': client
        },
        'continuation': next_data['token']
    }
    response = session.post(
        'https://www.youtube.com/youtubei/v1/browse', params={'key': api_key}, json=data)
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
        current_item = stack.pop()
        if isinstance(current_item, dict):
            for key, value in current_item.items():
                if key == search_key:
                    yield value
                else:
                    stack.append(value)
        elif isinstance(current_item, list):
            for value in current_item:
                stack.append(value)


def get_videos(data: dict) -> Generator:
    return search_dict(data, 'gridVideoRenderer')
