from datetime import datetime, timedelta
from config import settings
from TwitterAPI import TwitterAPI
from dateutil.parser import parse
from .data.twitter import lists
import csv
import os

description = """ First-person accounts from regions affected by conflict and diaster. """

definition = {
    'internalID': 'b3bf1450-8768-4204-b82e-c14bd2de7bce',
    'sourceType': 'twitter',
    'language': 'python',
    'frequency': 'repeats',
    'repeatsEvery': 'hour',
    'startDate': datetime.strptime('20140507', "%Y%m%d"),
    'endDate': datetime.now() + timedelta(days=365),
    'description': description
}


def suck(save_item, handle_error, source):
    api = TwitterAPI(settings.TWITTER['consumer_key'], 
            settings.TWITTER['consumer_secret'], 
            settings.TWITTER['access_token'], 
            settings.TWITTER['access_token_secret'])
    
    
    if 'lastRetrieved' not in source:
        source['lastRetrieved'] = {}

    for l in lists.items:
        request_filters = {
            'slug':l['slug'], 
            'owner_screen_name':l['owner_screen_name'],
            'per_page': 100
        }

        if l['owner_screen_name'] in source['lastRetrieved']:
            request_filters['since_id'] = source['lastRetrieved'][l['owner_screen_name']]

        r = api.request('lists/statuses', request_filters)
        
        new_since_id = None

        if r.status_code == 200:
            for record in r.get_iterator():
                if not new_since_id:
                    new_since_id = record['id_str']
                    source['lastRetrieved'][l['owner_screen_name']] = new_since_id

                item = transform(record)
                save_item(item)

        return source['lastRetrieved']


def transform(record):
    data = {
        'remoteID': record['id_str'],
        'author': {
            'name': record['user']['name'],
            'username': record['user']['screen_name'],
            'remoteID': str(record['user']['id']),
            'image': record['user']['profile_image_url']
        },
        'content': record['text'],
        'publishedAt': parse(record['created_at']),
        'geo': {
            'locationIdentifiers': {
                'authorLocationName': record['user']['location'],
                'authorTimeZone': record['user']['time_zone']
            }
        },
        'language': {
            'code': record['lang']
        },
        'source': 'twitter',
        'lifespan': 'temporary'
    }

    if 'coords' in record and record['coords']:
        data['geo']['coords'] = record['coordinates']['coordinates']

    if 'media' in record['entities'] and len(record['entities']['media']) > 0:
        media = record['entities']['media'][0]
        if media['type'] is 'video':
            prop = 'video'
        else:
            prop = 'image'

        data[prop] = media['media_url']


    return data
    

