from bs4 import BeautifulSoup
import requests
from datetime import datetime, timedelta
import re
from dateutil.parser import parse
import string

description = """ This Daily Live Nigerian election reporting """

definition = {
    'internalID': 'b49cf638-3dd2-4ab1-82e9-016ff5d502f3',
    'sourceType': 'thisdailylive',
    'uniqueName': 'nigeria_tdl',
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
        links = soup.find_all('a', text='Read more...')

        for link in links:
            url = 'http://www.thisdaylive.com' + link['href']
            r_sub = requests.get(url)

            if r_sub.status_code != 200:
                return
            
            soup_sub = BeautifulSoup(r_sub.text)
            h2 = soup_sub.find('h2', id='page_content_Content9_oModuleContent_2_h2_TitleAlt')
            title = h2.contents[0].strip()
            
            pub_date = parse(soup_sub.find('p', {'class':'date'}).contents[0].strip())
            tags = ['election']

            contents = soup_sub.find('div', id='page_content_Content9_oModuleContent_2_div_Body')
            text = ' '.join([p.contents[0].strip() for p in contents if p.name == 'p'])

            record = {
                'country': 'Nigeria',
                'publishedAt': pub_date,
                'tags': tags,
                'fromURL': url,
                'content': text,
                'summary': title
            }

            item = transform(record)
            save_item(item)
     

    r = requests.get('http://www.thisdaylive.com/politicsthisday-articles?page=1&items=24')
    handle_response(r)


def transform(record):
    def make_id():
        exclude = set(string.punctuation)
        slugified = ''.join(ch for ch in record['summary'].lower() if ch not in exclude).replace(' ','-')
        return 'thisdailylive_' + record['publishedAt'].strftime('%s') + '_' + slugified

    data = {
        'remoteID': make_id(),
        'content': record['content'],
        'publishedAt': record['publishedAt'],
        'geo': {
            'addressComponents': {
                'adminArea1': record['country']
            }
        },
        'source': 'thisdailylive',
        'lifespan': 'temporary',
        'license': 'unknown',
        'fromURL': record['fromURL'],
        'summary': record['summary'],
        'tags': [{'confidence': 1, 'name': tag} for tag in record['tags']]
    }

    return data