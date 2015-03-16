from bs4 import BeautifulSoup
import requests
from datetime import datetime, timedelta
import re
from dateutil.parser import parse
import string

description = """ Premium Times Nigerian election reporting """

definition = {
    'internalID': 'dce152d6-49a6-4b1a-ae53-df574ff0fec9',
    'sourceType': 'nigeria_news24',
    'uniqueName': 'nigeria_news24',
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
            return None

        soup = BeautifulSoup(r.text)
        stories = soup.find_all('div', {'class': 'item'})

        for story in stories:            

            story_soup = BeautifulSoup(str(story))
            link = story_soup.find('a',id='ArticleTitle')

            if not link:
                link = story_soup.find('a', id='lnkTitle')

            if not link:
                continue

            summary = link.contents[0].strip()
            url = link['href']

            story_content = story_soup.find('p').contents[0]
            story_date = story_soup.find('span', {'class': 'datestamp'})

            if story_date:
                pub_date = parse(story_date.contents[0])
            else:
                pub_date = datetime.now()
            
            record = {
                'country': 'Nigeria',
                'publishedAt': pub_date,
                'tags': ['election'],
                'fromURL': url,
                'content': story_content,
                'summary': summary
            }

            item = transform(record)
            save_item(item)
     

    headers = {'user-agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'}
    r = requests.get('http://www.news24.com.ng/Tags/Topics/2015_elections', headers=headers)
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