import requests
from datetime import datetime, timedelta
from dateutil.parser import parse
import json

description = """ SyriaTracker Ushahidi instance. syriatracker.crowdmap.com """

definition = {
    'internalID': 'fa08edfe-83f3-4a57-a968-e7d725a4325c',
    'sourceType': "syria_tracker",
    'language': "python",
    'frequency': "repeats",
    'repeatsEvery': "hour",
    'startDate': datetime.strptime('20140507', "%Y%m%d"),
    'endDate': datetime.now() + timedelta(days=365),
    'description': description
}


def suck(save_item, handle_error, source):
    last_retrieved = None

    url = 'http://syriatracker.crowdmap.com/api?task=incidents&limit=100'
    if 'lastRetrieved' in source:
        url += '&by=sinceid&id=' + source['lastRetrieved']
        last_retrieved = source['lastRetrieved']

    r = requests.get(url)
    if r.status_code == 200:
        res_json = r.json()
        if 'error' in res_json and res_json['error']['code'] == '007':
            return last_retrieved
        
        incidents = r.json()['payload']['incidents']

        last_retrieved = max([i['incident']['incidentid'] for i in incidents])
        for incident in incidents:
            item = transform(incident)
            save_item(item)

    return last_retrieved


def transform(record):
    item = {
        'remoteID': record['incident']['incidentid'],
        'publishedAt': parse(record['incident']['incidentdate']),
        'content': record['incident']['incidentdescription'],
        'summary': record['incident']['incidenttitle'],
        'lifespan': "temporary",
        'geo': {
            'addressComponents': {
                'formattedAddress': record['incident']['incidenttitle']
            }
        },
        'source': "syria_tracker",
        'tags': [{'name': cat['category']['title'], 'confidence': 1} for cat in record['categories']]
    }

    if 'locationlongitude' in record['incident'] and 'locationlatitude' in record['incident']:
        item['geo']['coords'] = [
            float(record['incident']['locationlongitude']),
            float(record['incident']['locationlatitude'])
        ]

    return item
  

