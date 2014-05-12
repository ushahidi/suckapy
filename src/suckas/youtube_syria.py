from apiclient.discovery import build
from apiclient.errors import HttpError
from dateutil.parser import parse
from config import settings
from .data.google import youtube_syria_channel_ids
from datetime import datetime, timedelta

description = """ About 1k YouTube channels relevant to ongoing conflict in Syria, 
courtesy of Eliot Higgins (aka Brown Moses) """

definition = {
    'internalID': '79fc92b8-c834-4bc7-b58a-6f12b1d4075e',
    'sourceType': 'youtube_syria',
    'language': 'python',
    'frequency': 'repeats',
    'repeatsEvery': 'hour',
    'startDate': datetime.strptime('20140507', "%Y%m%d"),
    'endDate': datetime.now() + timedelta(days=365),
    'description': description
}

def suck(save_item, handle_error, source):
    DEVELOPER_KEY = settings.GOOGLE_DEV_KEY
    YOUTUBE_API_SERVICE_NAME = "youtube"
    YOUTUBE_API_VERSION = "v3"

    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
        developerKey=DEVELOPER_KEY)

    kwargs = {
        'part': 'id,snippet',
        'maxResults': 25,
        'order': 'date'
    }

    if not 'lastRetrieved' in source:
        source['lastRetrieved'] = {}

    for i in youtube_syria_channel_ids.ids:
        kwargs['channelId'] = i
        
        if i in source['lastRetrieved']:
            kwargs['publishedAfter'] = source['lastRetrieved'][i].strftime("%Y-%m-%dT%H:%M:%SZ")

        search_response = youtube.search().list(**kwargs).execute()

        for search_result in search_response.get("items", []):
            #print search_result
            item = transform(search_result)
            if item:
                save_item(item)

        source['lastRetrieved'][i] = datetime.now()


def transform(record):
    if record['id']['kind'] != 'youtube#video':
        return None

    item = {
        'remoteID': record['id']['videoId'],
        'source': 'youtube_syria',
        'publishedAt': parse(record['snippet']['publishedAt'].replace(' ','')),
        'image': record['snippet']['thumbnails']['high']['url'].replace(' ',''),
        'summary': record['snippet']['title'],
        'content': record['snippet']['description'],
        'video': 'https://www.youtube.com/watch?v=' + record['id']['videoId'],
        'geo': {
            'addressComponents': {
                'adminArea1': 'Syria'
            }
        } 
    }

    return item
