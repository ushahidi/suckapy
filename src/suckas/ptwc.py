import requests
from datetime import datetime, timedelta
from dateutil.parser import parse
import string
import feedparser

description = """ NOAA's two Tsunami Warning Centers (PTWC and WC/ATWC) have separate areas of responsibility, which are the geographical areas within which each Center has the responsibility for the dissemination of messages and the provision of interpretive information to emergency managers and other officials, news media, and the public. """

definition = {
    'internalID': '4a8d4ee1-a175-4143-a108-35348a71601d',
    'sourceType': 'noaa',
    'uniqueName': 'ptwc',
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
            'url': 'http://ptwc.weather.gov/feeds/ptwc_rss_hawaii.xml',
            'tags': ['tsunami']
        },
        {
            'url': 'http://ptwc.weather.gov/feeds/ptwc_rss_pacific.xml',
            'tags': ['tsunami']
        }
    ]

    for feed in feeds:
        d = feedparser.parse(feed['url'])
    
        for entry in d.entries:
            print entry
            item = transform(entry, feed['tags'])
            save_item(item)


def transform(record, tags):
    tags = tags + ['weather']

    item = {
        'remoteID': make_id(record),
        'author': {
            'remoteID': record.author
        },
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

