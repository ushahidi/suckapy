import requests
from datetime import datetime, timedelta
from dateutil.parser import parse
import string
import feedparser
from .data.noaa import feeds

description = """ The National Oceanic and Atmospheric Administration is a scientific agency within the United States Department of Commerce focused on the conditions of the oceans and the atmosphere. """

definition = {
    'internalID': '72a1be3f-5a07-4615-bd47-4dd0db564a60',
    'sourceType': 'noaa',
    'uniqueName': 'noaa',
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
    for feed in feeds.items:
        d = feedparser.parse(feed['url'])
    
        for entry in d.entries:
            if 'lastRetrieved' not in source or parse(record.published) > source['lastRetrieved']:
                item = transform(entry, feed['tags'])
                save_item(item)

    return datetime.now()


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

    return item

