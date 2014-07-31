import requests
from datetime import datetime, timedelta
from dateutil.parser import parse
import string
import feedparser

description = """ NWCG is an operational group designed to coordinate programs of the participating wildfire management agencies """

definition = {
    'internalID': '6c8fc99f-4279-4405-9340-6d95b8662b6d',
    'sourceType': 'nwcg',
    'uniqueName': 'nwcg',
    'language': 'python',
    'frequency': 'repeats',
    'repeatsEvery': 'hour',
    'startDate': datetime.strptime('20140507', "%Y%m%d"),
    'endDate': datetime.now() + timedelta(days=365),
    'description': description
}

def make_id(record):
    return "%s_%s" %(str(parse(record.published).strftime('%s')),''.join("{:02x}".format(ord(c)) for c in record.title))


def suck(save_item, handle_error, source):
    feeds = [
        {
            'url': 'http://inciweb.nwcg.gov/feeds/rss/incidents/',
            'tags': ['wildfire']
        }
    ]

    for feed in feeds:
        d = feedparser.parse(feed['url'])
    
        for entry in d.entries:
            if 'lastRetrieved' not in source or parse(record.published) > source['lastRetrieved']:
                if hasattr(entry, 'summary'):
                    item = transform(entry, feed['tags'])
                    save_item(item)

    return datetime.now()


def transform(record, tags):
    tags = tags + ['weather']

    item = {
        'remoteID': make_id(record),
        'source': 'noaa',
        'content': record.summary,
        'summary': record.title,
        'tags': [{'name':tag, 'confidence':1} for tag in tags],
        'geo': {
            'coords': [record.geo_long, record.geo_lat]
        },
        'publishedAt': parse(record.published),
        'license': 'unknown',
        'fromURL': record.link
    }

    return item

