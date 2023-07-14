import json
import time
from typing import Generator

import requests
from typing_extensions import Literal

type_property_map = {
    "videos": "videoRenderer",
    "streams": "videoRenderer",
    "shorts": "reelItemRenderer"
}

def get_channel(
    channel_id: str = None,
    channel_url: str = None,
    channel_username: str = None,
    limit: int = None,
    sleep: int = 1,
    sort_by: Literal["newest", "oldest", "popular"] = "newest",
    content_type: Literal["videos", "shorts", "streams"] = "videos",
) -> Generator[dict, None, None]:

    """Get videos for a channel.

    Parameters:
        channel_id (``str``, *optional*):
            The channel id from the channel you want to get the videos for.
            If you prefer to use the channel url instead, see ``channel_url`` below.

        channel_url (``str``, *optional*):
            The url to the channel you want to get the videos for.
            Since there is a few type's of channel url's, you can use the one you want
            by passing it here instead of using ``channel_id``.

        channel_username (``str``, *optional*):
            The username from the channel you want to get the videos for.
            Ex. ``LinusTechTips`` (without the @).
            If you prefer to use the channel url instead, see ``channel_url`` above.

        limit (``int``, *optional*):
            Limit the number of videos you want to get.

        sleep (``int``, *optional*):
            Seconds to sleep between API calls to youtube, in order to prevent getting blocked.
            Defaults to 1.

        sort_by (``str``, *optional*):
            In what order to retrieve to videos. Pass one of the following values.
            ``"newest"``: Get the new videos first.
            ``"oldest"``: Get the old videos first.
            ``"popular"``: Get the popular videos first. Defaults to "newest".

        content_type (``str``, *optional*):
            In order to get content type. Pass one of the following values.
            ``"videos"``: Videos
            ``"shorts"``: Shorts
            ``"streams"``: Streams
    """

    base_url = ""
    if channel_url:
        base_url = channel_url
    elif channel_id:
        base_url = f"https://www.youtube.com/channel/{channel_id}"
    elif channel_username:
        base_url = f"https://www.youtube.com/@{channel_username}"

    url = "{base_url}/{content_type}?view=0&flow=grid".format(
        base_url=base_url,
        content_type=content_type,
    )
    api_endpoint = "https://www.youtube.com/youtubei/v1/browse"
    videos = get_videos(url, api_endpoint, type_property_map[content_type], limit, sleep, sort_by)
    for video in videos:
        yield video


def get_playlist(
    playlist_id: str, limit: int = None, sleep: int = 1
) -> Generator[dict, None, None]:

    """Get videos for a playlist.

    Parameters:
        playlist_id (``str``):
            The playlist id from the playlist you want to get the videos for.

        limit (``int``, *optional*):
            Limit the number of videos you want to get.

        sleep (``int``, *optional*):
            Seconds to sleep between API calls to youtube, in order to prevent getting blocked.
            Defaults to 1.
    """

    url = f"https://www.youtube.com/playlist?list={playlist_id}"
    api_endpoint = "https://www.youtube.com/youtubei/v1/browse"
    videos = get_videos(url, api_endpoint, "playlistVideoRenderer", limit, sleep)
    for video in videos:
        yield video


def get_search(
    query: str,
    limit: int = None,
    sleep: int = 1,
    sort_by: Literal["relevance", "upload_date", "view_count", "rating"] = "relevance",
    results_type: Literal["video", "channel", "playlist", "movie"] = "video",
) -> Generator[dict, None, None]:

    """Search youtube and get videos.

    Parameters:
        query (``str``):
            The term you want to search for.

        limit (``int``, *optional*):
            Limit the number of videos you want to get.

        sleep (``int``, *optional*):
            Seconds to sleep between API calls to youtube, in order to prevent getting blocked.
            Defaults to 1.

        sort_by (``str``, *optional*):
            In what order to retrieve to videos. Pass one of the following values.
            ``"relevance"``: Get the new videos in order of relevance.
            ``"upload_date"``: Get the new videos first.
            ``"view_count"``: Get the popular videos first.
            ``"rating"``: Get videos with more likes first.
            Defaults to "relevance".

        results_type (``str``, *optional*):
            What type you want to search for. Pass one of the following values:
            ``"video"|"channel"|"playlist"|"movie"``. Defaults to "video".
    """

    sort_by_map = {
        "relevance": "A",
        "upload_date": "I",
        "view_count": "M",
        "rating": "E",
    }

    results_type_map = {
        "video": ["B", "videoRenderer"],
        "channel": ["C", "channelRenderer"],
        "playlist": ["D", "playlistRenderer"],
        "movie": ["E", "videoRenderer"],
    }

    param_string = f"CA{sort_by_map[sort_by]}SAhA{results_type_map[results_type][0]}"
    url = f"https://www.youtube.com/results?search_query={query}&sp={param_string}"
    api_endpoint = "https://www.youtube.com/youtubei/v1/search"
    videos = get_videos(
        url, api_endpoint, results_type_map[results_type][1], limit, sleep
    )
    for video in videos:
        yield video



def get_video(
    id: str,
) -> dict:

    """Get a single video.

    Parameters:
        id (``str``):
            The video id from the video you want to get.
    """

    session = get_session()
    url = f"https://www.youtube.com/watch?v={id}"
    html = get_initial_data(session, url)
    client = json.loads(
        get_json_from_html(html, "INNERTUBE_CONTEXT", 2, '"}},') + '"}}'
    )["client"]
    session.headers["X-YouTube-Client-Name"] = "1"
    session.headers["X-YouTube-Client-Version"] = client["clientVersion"]
    data = json.loads(
        get_json_from_html(html, "var ytInitialData = ", 0, "};") + "}"
    )
    return next(search_dict(data, "videoPrimaryInfoRenderer"))



def get_videos(
    url: str, api_endpoint: str, selector: str, limit: int, sleep: int, sort_by: str = None
) -> Generator[dict, None, None]:
    session = get_session()
    is_first = True
    quit_it = False
    count = 0
    while True:
        if is_first:
            html = get_initial_data(session, url)
            client = json.loads(
                get_json_from_html(html, "INNERTUBE_CONTEXT", 2, '"}},') + '"}}'
            )["client"]
            api_key = get_json_from_html(html, "innertubeApiKey", 3)
            session.headers["X-YouTube-Client-Name"] = "1"
            session.headers["X-YouTube-Client-Version"] = client["clientVersion"]
            data = json.loads(
                get_json_from_html(html, "var ytInitialData = ", 0, "};") + "}"
            )
            next_data = get_next_data(data, sort_by)
            is_first = False
            if sort_by and sort_by != "newest": 
                continue
        else:
            data = get_ajax_data(session, api_endpoint, api_key, next_data, client)
            next_data = get_next_data(data)
        for result in get_videos_items(data, selector):
            try:
                count += 1
                yield result
                if count == limit:
                    quit_it = True
                    break
            except GeneratorExit:
                quit_it = True
                break

        if not next_data or quit_it:
            break

        time.sleep(sleep)

    session.close()


def get_session() -> requests.Session:
    session = requests.Session()
    session.headers[
        "User-Agent"
    ] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    session.headers["Accept-Language"] = "en"
    return session

def get_initial_data(session: requests.Session, url: str) -> str:
    session.cookies.set("CONSENT", "YES+cb", domain=".youtube.com")
    response = session.get(url)

    html = response.text
    return html


def get_ajax_data(
    session: requests.Session,
    api_endpoint: str,
    api_key: str,
    next_data: dict,
    client: dict,
) -> dict:
    data = {
        "context": {"clickTracking": next_data["click_params"], "client": client},
        "continuation": next_data["token"],
    }
    response = session.post(api_endpoint, params={"key": api_key}, json=data)
    return response.json()


def get_json_from_html(html: str, key: str, num_chars: int = 2, stop: str = '"') -> str:
    pos_begin = html.find(key) + len(key) + num_chars
    pos_end = html.find(stop, pos_begin)
    return html[pos_begin:pos_end]


def get_next_data(data: dict, sort_by: str = None) -> dict:
    # Youtube, please don't change the order of these
    sort_by_map = {
        "newest": 0, 
        "popular": 1,
        "oldest": 2, 
    }
    if sort_by and sort_by != "newest":
        endpoint = next(
            search_dict(data, "feedFilterChipBarRenderer"), None)["contents"][sort_by_map[sort_by]]["chipCloudChipRenderer"]["navigationEndpoint"]
    else:
        endpoint = next(search_dict(data, "continuationEndpoint"), None)
    if not endpoint:
        return None
    next_data = {
        "token": endpoint["continuationCommand"]["token"],
        "click_params": {"clickTrackingParams": endpoint["clickTrackingParams"]},
    }

    return next_data


def search_dict(partial: dict, search_key: str) -> Generator[dict, None, None]:
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


def get_videos_items(data: dict, selector: str) -> Generator[dict, None, None]:
    return search_dict(data, selector)
