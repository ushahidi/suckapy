import requests
from datetime import datetime, timedelta
from dateutil.parser import parse
import string
import feedparser

description = """ Latest Weather News Headlines for the United States Issued by the National Weather Service """

definition = {
    'internalID': 'eecdca54-b960-4a0c-b7f5-f45df6075db9',
    'sourceType': 'noaa',
    'uniqueName': 'noaa_news',
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
            'url': 'http://www.weather.gov/rss_page.php?site_name=nws',
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
        'source': 'noaa_news',
        'content': record.summary,
        'summary': record.title,
        'tags': [{'name':tag, 'confidence':1} for tag in tags],
        'publishedAt': parse(record.published),
        'license': 'unknown',
        'fromURL': record.link
    }

    return item

