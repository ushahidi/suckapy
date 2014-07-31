import requests
from datetime import datetime, timedelta
from dateutil.parser import parse
import string
import feedparser

description = """ Pacific Disaster Center uses information, science, and technology to enable effective evidence-based decision making and to promote disaster risk reduction (DRR) concepts and strategies. """

definition = {
    'internalID': 'b8f390d6-b6a8-4e82-9152-94a0500b56cf',
    'sourceType': 'pdc',
    'uniqueName': 'pdc',
    'language': 'python',
    'frequency': 'repeats',
    'repeatsEvery': 'hour',
    'startDate': datetime.strptime('20140507', "%Y%m%d"),
    'endDate': datetime.now() + timedelta(days=365),
    'status': 'active',
    'description': description
}

def make_id(record):
    return "%s_%s" %(str(parse(record.updated).strftime('%s')),''.join("{:02x}".format(ord(c)) for c in record.summary))


def suck(save_item, handle_error, source):
    feeds = [
        {
            'url': 'http://d2mxabrykbl1km.cloudfront.net/feed.xml',
            'tags': ['disaster']
        }
    ]

    for feed in feeds:
        d = feedparser.parse(feed['url'])
    
        for entry in d.entries:
            if 'lastRetrieved' not in source or parse(record.updated) > source['lastRetrieved']:
                item = transform(entry, feed['tags'])
                save_item(item)

    return datetime.now()


def transform(record, tags):
    tags = tags + ['weather']

    item = {
        'remoteID': make_id(record),
        'source': 'pdc',
        'content': record.title,
        'summary': record.summary,
        'tags': [{'name':tag, 'confidence':1} for tag in tags],
        'publishedAt': parse(record.updated),
        'license': 'unknown',
        'fromURL': record.link
    }

    if record.georss_point and len(record.georss_point) > 0:
        item['geo'] = {
            'coords': [float(p) for p in record.georss_point.split(' ')[::-1]]
        }

    return item

