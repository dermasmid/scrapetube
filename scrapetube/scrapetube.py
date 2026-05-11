import json
import time
from typing import Generator, Optional

import requests
from typing_extensions import Literal

type_property_map = {
    "videos": "videoRenderer",
    "streams": "videoRenderer",
    "shorts": "reelWatchEndpoint"
}

def get_channel(
    channel_id: str = None,
    channel_url: str = None,
    channel_username: str = None,
    limit: int = None,
    sleep: float = 1,
    proxies: dict = None,
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

        proxies (``dict``, *optional*):
            A dictionary with the proxies you want to use. Ex:
            ``{'https': 'http://username:password@101.102.103.104:3128'}``
        
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
    videos = get_videos(url, api_endpoint, "contents", type_property_map[content_type], limit, sleep, proxies, sort_by)
    for video in videos:
        yield video


def get_playlist(
    playlist_id: str, limit: int = None, sleep: int = 1, proxies: dict = None
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
        
        proxies (``dict``, *optional*):
            A dictionary with the proxies you want to use. Ex:
            ``{'https': 'http://username:password@101.102.103.104:3128'}``
    """

    url = f"https://www.youtube.com/playlist?list={playlist_id}"
    api_endpoint = "https://www.youtube.com/youtubei/v1/browse"
    videos = get_videos(url, api_endpoint, "playlistVideoListRenderer", "playlistVideoRenderer", limit, sleep, proxies)
    for video in videos:
        yield video


def get_search(
    query: str,
    limit: int = None,
    sleep: int = 1,
    sort_by: Literal["relevance", "upload_date", "view_count", "rating"] = "relevance",
    results_type: Literal["video", "channel", "playlist", "movie"] = "video",
    proxies: dict = None,
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
        
        proxies (``dict``, *optional*):
            A dictionary with the proxies you want to use. Ex:
            ``{'https': 'http://username:password@101.102.103.104:3128'}``

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
        url, api_endpoint, "contents", results_type_map[results_type][1], limit, sleep, proxies
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
    url: str, api_endpoint: str, selector_list: str, selector_item: str, limit: int, sleep: float, proxies: dict = None, sort_by: str = None
) -> Generator[dict, None, None]:
    session = get_session(proxies)
    is_first = True
    quit_it = False
    count = 0
    page_context = None
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
            page_context = get_page_context(data)
            data = next(search_dict(data, selector_list), None)
            next_data = get_next_data(data, sort_by)
            is_first = False
            if sort_by and sort_by != "newest": 
                continue
        else:
            data = get_ajax_data(session, api_endpoint, api_key, next_data, client)
            next_data = get_next_data(data)
        for result in get_videos_items(data, selector_item, page_context):
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


def get_session(proxies: dict = None) -> requests.Session:
    session = requests.Session()
    if proxies:
        session.proxies.update(proxies)
    session.headers[
        "User-Agent"
    ] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    session.headers["Accept-Language"] = "en"
    return session

def get_initial_data(session: requests.Session, url: str) -> str:
    session.cookies.set("CONSENT", "YES+cb", domain=".youtube.com")
    response = session.get(url, params={"ucbcb":1})

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


def get_page_context(data: dict) -> Optional[dict]:
    metadata = next(search_dict(data, "channelMetadataRenderer"), None)
    if not isinstance(metadata, dict):
        return None

    owner_url = None
    owner_urls = metadata.get("ownerUrls")
    if isinstance(owner_urls, list) and owner_urls:
        owner_url = owner_urls[0]

    canonical_base_url = None
    if isinstance(owner_url, str) and owner_url.startswith("https://www.youtube.com"):
        canonical_base_url = owner_url.replace("https://www.youtube.com", "", 1)

    return {
        "channel_id": metadata.get("externalId"),
        "channel_title": metadata.get("title"),
        "canonical_base_url": canonical_base_url,
    }


def _make_text_runs(text: str) -> dict:
    if not text:
        return {"runs": []}
    return {"runs": [{"text": text}]}


def _make_byline_text(channel_title: str, channel_id: str = None, canonical_base_url: str = None) -> dict:
    if not channel_title:
        return {"runs": []}

    navigation_endpoint = {}
    if channel_id:
        navigation_endpoint = {
            "commandMetadata": {
                "webCommandMetadata": {
                    "url": canonical_base_url or f"/channel/{channel_id}",
                    "webPageType": "WEB_PAGE_TYPE_CHANNEL",
                    "rootVe": 9662,
                }
            },
            "browseEndpoint": {
                "browseId": channel_id,
            },
        }
        if canonical_base_url:
            navigation_endpoint["browseEndpoint"]["canonicalBaseUrl"] = canonical_base_url

    run = {"text": channel_title}
    if navigation_endpoint:
        run["navigationEndpoint"] = navigation_endpoint
    return {"runs": [run]}


def _lockup_metadata_parts(lockup: dict) -> list:
    try:
        rows = (
            lockup.get("metadata", {})
            .get("lockupMetadataViewModel", {})
            .get("metadata", {})
            .get("contentMetadataViewModel", {})
            .get("metadataRows", [])
        )
        parts = []
        for row in rows:
            for part in row.get("metadataParts", []):
                text = part.get("text", {}).get("content")
                if text:
                    parts.append(text)
        return parts
    except (TypeError, KeyError, AttributeError):
        return []


def _lockup_duration_text(lockup: dict) -> str:
    try:
        overlays = (
            lockup.get("contentImage", {})
            .get("thumbnailViewModel", {})
            .get("overlays", [])
        )
        for overlay in overlays:
            bottom_overlay = overlay.get("thumbnailBottomOverlayViewModel")
            if not bottom_overlay:
                continue
            for badge in bottom_overlay.get("badges", []):
                badge_view_model = badge.get("thumbnailBadgeViewModel")
                if badge_view_model and badge_view_model.get("text"):
                    return badge_view_model["text"]
    except (TypeError, KeyError, AttributeError):
        pass
    return ""


def _lockup_view_count_text(lockup: dict) -> str:
    parts = _lockup_metadata_parts(lockup)
    return parts[0] if parts else ""


def _lockup_published_time_text(lockup: dict) -> str:
    parts = _lockup_metadata_parts(lockup)
    return parts[1] if len(parts) > 1 else ""


def _lockup_thumbnail(lockup: dict) -> dict:
    sources = (
        lockup.get("contentImage", {})
        .get("thumbnailViewModel", {})
        .get("image", {})
        .get("sources", [])
    )
    thumbnails = []
    for source in sources:
        if not isinstance(source, dict):
            continue
        url = source.get("url")
        if not url:
            continue
        thumbnails.append(
            {
                "url": url,
                "width": source.get("width"),
                "height": source.get("height"),
            }
        )
    return {"thumbnails": thumbnails}


def _lockup_navigation_endpoint(lockup: dict) -> dict:
    return (
        lockup.get("rendererContext", {})
        .get("commandContext", {})
        .get("onTap", {})
        .get("innertubeCommand", {})
    )


def _lockup_to_video_renderer(lockup: dict, page_context: Optional[dict] = None) -> Optional[dict]:
    if not isinstance(lockup, dict):
        return None

    content_type = lockup.get("contentType") or ""
    if "VIDEO" not in content_type:
        return None

    video_id = lockup.get("contentId")
    if not video_id:
        return None

    title_content = (
        lockup.get("metadata", {})
        .get("lockupMetadataViewModel", {})
        .get("title", {})
        .get("content")
    )
    title = _make_text_runs(title_content)

    view_count_text = _lockup_view_count_text(lockup)
    published_time_text = _lockup_published_time_text(lockup)
    duration_text = _lockup_duration_text(lockup)
    navigation_endpoint = _lockup_navigation_endpoint(lockup)

    channel_title = None
    channel_id = None
    canonical_base_url = None
    if page_context:
        channel_title = page_context.get("channel_title")
        channel_id = page_context.get("channel_id")
        canonical_base_url = page_context.get("canonical_base_url")

    byline = _make_byline_text(channel_title, channel_id, canonical_base_url)

    video = {
        "videoId": video_id,
        "title": title,
        "thumbnail": _lockup_thumbnail(lockup),
    }
    if navigation_endpoint:
        video["navigationEndpoint"] = navigation_endpoint
    if view_count_text:
        video["viewCountText"] = {"simpleText": view_count_text}
    if published_time_text:
        video["publishedTimeText"] = {"simpleText": published_time_text}
    if duration_text:
        video["lengthText"] = {"simpleText": duration_text}
    if byline.get("runs"):
        video["longBylineText"] = byline
        video["shortBylineText"] = byline
        video["ownerText"] = byline
    return video


def get_videos_items(data: dict, selector: str, page_context: Optional[dict] = None) -> Generator[dict, None, None]:
    if selector != "videoRenderer":
        yield from search_dict(data, selector)
        return

    seen = set()
    for item in search_dict(data, "videoRenderer"):
        video_id = item.get("videoId") if isinstance(item, dict) else None
        if video_id and video_id not in seen:
            seen.add(video_id)
            yield item

    for lockup in search_dict(data, "lockupViewModel"):
        converted = _lockup_to_video_renderer(lockup, page_context)
        if not converted:
            continue
        video_id = converted["videoId"]
        if video_id not in seen:
            seen.add(video_id)
            yield converted
