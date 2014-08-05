from datetime import datetime, timedelta
from config import settings
from dateutil.parser import parse
import requests
import os
import logging

logger = logging.getLogger('suckapy')

description = """ Public instances of the Ushahidi crowdsourced mapping platform. """

definition = {
    'internalID': 'd0274b3c-657e-48ea-9efa-c2d16827ea7b',
    'sourceType': 'ushahidi',
    'uniqueName': 'ushahidi_v2',
    'language': 'python',
    'frequency': 'repeats',
    'repeatsEvery': 'day',
    'status': 'active',
    'startDate': datetime.strptime('20140507', "%Y%m%d"),
    'endDate': datetime.now() + timedelta(days=365),
    'description': description
}

def remove_non_ascii(s): return "".join(i for i in s if ord(i)<128)

def suck(save_item, handle_error, source):
    url = 'http://tracker.ushahidi.com/list?return_vars=url,name&limit=0,5000'

    if 'lastRetrieved' not in source:
        source['lastRetrieved'] = {}

    r = requests.get(url)
    if r.status_code != 200:
        logger.error('Failed to retrieve list of URLs from Ushahidi tracker')
        return source['lastRetrieved']
    
    json_data = r.json()
    for key,val in json_data.iteritems():
        api_url = val['url'] + 'api'
        api_url += '?task=incidents&limit=100'

        if key in source['lastRetrieved']:
            api_url += '&since_id=' + source['lastRetrieved'][key]

        rr = requests.get(api_url)
        if rr.status_code != 200:
            continue
        
        report_data = rr.json()
        if 'payload' not in report_data or 'incidents' not in report_data['payload']:
            logger.warn("No payload incidents for Ushahidi " + str(key) + "|" + val['name'] + "|" + api_url)
            continue

        for report in report_data['payload']['incidents']:
            logger.info("Processing records for " + str(key) + "|" + val['name'] + "|" + api_url)
            item = transform(report, key, val['name'])
            save_item(item)

            ids = [i['incident']['incidentid'] for i in report_data['payload']['incidents']]
            source['lastRetrieved'][key] = max(ids)
        
    return source['lastRetrieved']


def transform(record, instance_id, name):
    incident = record['incident']

    data = {
        'remoteID': str(instance_id) + "-" + str(incident['incidentid']),
        'author': {
            'name': name,
            'remoteID': str(instance_id)
        },
        'content': incident['incidentdescription'],
        'summary': incident['incidenttitle'],
        'publishedAt': parse(incident['incidentdate']),
        'geo': {
            'addressComponents': {
                'formattedAddress': incident['locationname']
            }
        },
        'source': 'ushahidi_v2',
        'lifespan': 'temporary',
        'license': 'unknown',
        'tags': [{'name':cat['category']['title'], 'confidence': 1} for cat in record['categories']]
    }

    if 'locationlongitude' in record and 'locationlatitude' in record:
        data['geo']['coords'] = [
            float(record['locationlongitude']), 
            float(record['locationlatitude'])
        ]
    
    return data
    