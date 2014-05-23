from datetime import datetime, timedelta
from config import settings
from instagram.client import InstagramAPI
from dateutil.parser import parse
import csv
import os

description = """ Requests to photos tagged to places in Instagram. """

definition = {
    'internalID': 'b5583296-f0b3-496f-b090-bff59ff2b387',
    'sourceType': 'instagrammer',
    'language': 'python',
    'frequency': 'repeats',
    'repeatsEvery': 'minute',
    'status': 'active',
    'startDate': datetime.strptime('20140507', "%Y%m%d"),
    'endDate': datetime.now() + timedelta(days=365),
    'description': description
}


def suck(save_item, handle_error, source):
    api = InstagramAPI(client_id=settings.INSTAGRAM['client_id'], 
        client_secret=settings.INSTAGRAM['client_secret'])

    if 'lastRetrieved' not in source:
        source['lastRetrieved'] = {}

    if 'thaicoup' in source['lastRetrieved']:
        last_id = source['lastRetrieved']['thaicoup']

    else:
        last_id = 0
    
    tag_media, next = api.tag_recent_media(50, 0, 'thaicoup')
    
    source['lastRetrieved'] = {
        'thaicoup': 0
    }
    
    source['lastRetrieved']['thaicoup'] = str(tag_media[0].id)
    for media in tag_media:
        item = transform(media)
        save_item(item)

    """
    if 'lastRetrieved' not in source:
        source['lastRetrieved'] = {}

    for l in lists.items:
        lr_key = l['owner_screen_name'] + '|' + l['slug']

        request_filters = {
            'slug':l['slug'], 
            'owner_screen_name':l['owner_screen_name'],
            'per_page': 100
        }

        if lr_key in source['lastRetrieved']:
            request_filters['since_id'] = source['lastRetrieved'][lr_key]

        r = api.request('lists/statuses', request_filters)
        
        new_since_id = None

        if r.status_code == 200:
            for record in r.get_iterator():
                if not new_since_id:
                    new_since_id = record['id_str']
                    source['lastRetrieved'][lr_key] = new_since_id

                item = transform(record, l['slug'])
                save_item(item)
    """

    
    return source['lastRetrieved']


def transform(record):
    data = {
        'remoteID': str(record.id),
        'author': {
            'name': record.user.full_name,
            'username': record.user.username,
            'remoteID': str(record.user.id),
            'image': record.user.profile_picture
        },
        'content': record.caption.text,
        'publishedAt': record.created_time,
        'geo': {
            'addressComponents': {
                'adminArea1': 'Thailand'
            }
        },
        'source': 'instagram',
        'lifespan': 'temporary',
        'image': record.get_standard_resolution_url(),
        'fromURL': record.link
    }

    if hasattr(record, 'location'):
        data['geo']['coords'] = [record.location.point.longitude, record.location.point.latitude]


    return data
    

