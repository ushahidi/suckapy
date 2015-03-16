from bs4 import BeautifulSoup
import requests
from datetime import datetime, timedelta
import re
from dateutil.parser import parse
import string

description = """ Premium Times Nigerian election reporting """

definition = {
    'internalID': 'f3793484-14ae-41b8-bb97-aa31d868e246',
    'sourceType': 'premiumtimes',
    'uniqueName': 'nigeria_premiumtimes',
    'language': 'python',
    'frequency': 'repeats',
    'repeatsEvery': 'hour',
    'startDate': datetime.strptime('20150307', "%Y%m%d"),
    'endDate': datetime.now() + timedelta(days=365),
    'description': description,
    'status': 'active'
}


def suck(save_item, handle_error, source):
    def handle_response(r):
        if r.status_code != 200:
            print r.status_code
            return None

        soup = BeautifulSoup(r.text)
        stories = soup.find_all('div', {'class': 'a-story'})

        for story in stories:            

            story_soup = BeautifulSoup(str(story))
            summary = story_soup.find('h3').contents[0].strip()

            story_content = story_soup.find('div', {'class': 'a-story-content'})
            content = story_content.contents[1].string

            url = story_soup.find_all('a')[0]['href']
            pub_date = datetime.now()
            
            record = {
                'country': 'Nigeria',
                'publishedAt': pub_date,
                'tags': ['election'],
                'fromURL': url,
                'content': content,
                'summary': summary
            }

            item = transform(record)
            save_item(item)
     

    headers = {'user-agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'}
    r = requests.get('http://www.premiumtimesng.com/category/news/top-news', headers=headers)
    handle_response(r)


def transform(record):
    def make_id():
        exclude = set(string.punctuation)
        slugified = ''.join(ch for ch in record['summary'].lower() if ch not in exclude).replace(' ','-')
        return 'premiumtimes_' + record['publishedAt'].strftime('%s') + '_' + slugified

    data = {
        'remoteID': make_id(),
        'content': record['content'],
        'publishedAt': record['publishedAt'],
        'geo': {
            'addressComponents': {
                'adminArea1': record['country']
            }
        },
        'source': 'premiumtimes',
        'lifespan': 'temporary',
        'license': 'unknown',
        'fromURL': record['fromURL'],
        'summary': record['summary'],
        'tags': [{'confidence': 1, 'name': tag} for tag in record['tags']]
    }

    return data