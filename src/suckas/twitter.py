from datetime import datetime, timedelta
from config import settings
from TwitterAPI import TwitterAPI
from dateutil.parser import parse
from .data.twitter import lists, hashtags
import csv
import os

description = """ First-person accounts from regions affected by conflict and diaster. """

definition = {
    'internalID': 'b3bf1450-8768-4204-b82e-c14bd2de7bce',
    'sourceType': 'twitter',
    'uniqueName': 'twitter',
    'language': 'python',
    'frequency': 'repeats',
    'repeatsEvery': 'minute',
    'startDate': datetime.strptime('20140507', "%Y%m%d"),
    'endDate': datetime.now() + timedelta(days=365),
    'description': description
}

def remove_non_ascii(s): return "".join(i for i in s if ord(i)<128)

def suck(save_item, handle_error, source):
    api = TwitterAPI(settings.TWITTER['consumer_key'], 
            settings.TWITTER['consumer_secret'], 
            settings.TWITTER['access_token'], 
            settings.TWITTER['access_token_secret'])
    
    
    if 'lastRetrieved' not in source:
        source['lastRetrieved'] = {}


    def get_and_save(endpoint, request_filters, lr_key, admin1, admin2=None, admin3=None, tags=None):
        if lr_key in source['lastRetrieved']:
            request_filters['since_id'] = source['lastRetrieved'][lr_key]

        r = api.request(endpoint, request_filters)
        
        new_since_id = None

        if r.status_code == 200:
            for record in r.get_iterator():
                if not new_since_id:
                    new_since_id = record['id_str']
                    source['lastRetrieved'][lr_key] = new_since_id

                item = transform(record, admin1, admin3=admin3, tags=tags)
                save_item(item)


    for l in lists.items:
        lr_key = l['owner_screen_name'] + '|' + l['slug']

        request_filters = {
            'slug':l['slug'], 
            'owner_screen_name':l['owner_screen_name'],
            'per_page': 100
        }

        get_and_save('lists/statuses', request_filters, lr_key, l['slug'].capitalize())


    for h in hashtags.items:
        lr_key = remove_non_ascii(h['hashtag'])

        request_filters = {
            'q': h['hashtag']
        }

        admin3 = None
        tags = None

        if 'state' in h:
            admin3 = h['state']

        if 'tags' in h:
            tags = h['tags']

        get_and_save('search/tweets', request_filters, lr_key, h['country'], admin3=admin3, tags=tags)
        

    
    return source['lastRetrieved']


def transform(record, admin1, admin2=None, admin3=None, tags=None):
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
            'addressComponents': {
                'adminArea1': admin1
            },
            'locationIdentifiers': {
                'authorLocationName': record['user']['location'],
                'authorTimeZone': record['user']['time_zone']
            }
        },
        'language': {
            'code': record['lang']
        },
        'source': 'twitter',
        'lifespan': 'temporary',
        'license': 'twitter'
    }

    if tags:
        data['tags'] = [{'name': tag, 'confidence': 1} for tag in tags]

    if admin3:
        data['geo']['addressComponents']['adminArea3'] = admin3

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
    

