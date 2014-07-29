import requests
from datetime import datetime, timedelta
from dateutil.parser import parse
import string
import feedparser

description = """ Current Watches, Warnings and Advisories for the United States Issued by the National Weather Service """

definition = {
    'internalID': '32ad9f25-d2e0-4ac1-8c21-fe9bb432f030',
    'sourceType': 'noaa',
    'uniqueName': 'noaa_alerts',
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
            'url': 'http://alerts.weather.gov/cap/us.php?x=0',
            'tags': ['severe-weather']
        }
    ]

    for feed in feeds:
        d = feedparser.parse(feed['url'])
    
        for entry in d.entries:
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
        'publishedAt': parse(record.published),
        'license': 'unknown',
        'fromURL': record.link
    }

    coord_str = record.cap_polygon.split(' ')[0].split(',')[::-1]
    if len(coord_str) > 1:
        item['geo'] = {
            'coords': [float(coord) for coord in coord_str]
        }

    return item

