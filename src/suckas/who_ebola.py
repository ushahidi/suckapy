from bs4 import BeautifulSoup
import requests
from datetime import datetime, timedelta
import re
from dateutil.parser import parse

description = """ WHO Ebola virus disease reports """

definition = {
    'internalID': 'abf592b2-98f3-4b53-83da-843148505fe6',
    'sourceType': 'who',
    'uniqueName': 'who_ebola',
    'language': 'python',
    'frequency': 'repeats',
    'repeatsEvery': 'day',
    'startDate': datetime.strptime('20140507', "%Y%m%d"),
    'endDate': datetime.now() + timedelta(days=365),
    'description': description,
    'status': 'active'
}


def suck(save_item, handle_error, source):
    def handle_response(r):
        if r.status_code == 200:
            soup = BeautifulSoup(r.text)
            el = soup.find('ul', { 'class': 'auto_archive' })
            links = el.find_all('a')

            for link in links:
                url = 'http://www.who.int' + link['href']
                if 'July' in link.contents[0] or 'August' in link.contents[0]:
                
                    r_sub = requests.get(url)
                    if r_sub.status_code != 200:
                        return
                    
                    soup_sub = BeautifulSoup(r_sub.text)

                    table = soup_sub.find('table', {'class': 'borderOn'})
                    if table:
                        pub_date = parse(link.contents[0])

                        if pub_date > parse('July 30 2014'):
                            continue

                        tags = ['ebola','disease','disaster']
                        
                        #countries = ['Guinea', 'Liberia', 'Sierra Leone']
                        to_find = ['3','4','6','7','9','10']
                        countries = {
                            '3': {
                                'name': 'Guinea',
                                'is_death': False
                            },
                            '4': {
                                'name': 'Guinea',
                                'is_death': True
                            },
                            '6': {
                                'name': 'Liberia',
                                'is_death': False
                            },
                            '7': {
                                'name': 'Liberia',
                                'is_death': True
                            },
                            '9': {
                                'name': 'Sierra Leone',
                                'is_death': False
                            },
                            '10': {
                                'name': 'Sierra Leone',
                                'is_death': True
                            }

                        }

                        rows = table.find_all('tr')
                        for t in to_find:
                            tds = rows[int(t)].find_all('td')

                            record = {
                                'country': countries[t]['name'],
                                'publishedAt': pub_date,
                                'tags': tags,
                                'fromURL': url
                            }

                            # confirmed
                            record['totalAffectedPersons'] = int(tds[2].contents[0])
                            record['tags'] = tags + ['confirmed']

                            if countries[t]['is_death']:
                                record['tags'] = record['tags'] + ['death']

                            item = transform(record)
                            save_item(item)
                            #print record

                            # suspected
                            record['totalAffectedPersons'] = int(tds[3].contents[0]) + int(tds[4].contents[0])
                            record['tags'] = tags

                            if countries[t]['is_death']:
                                record['tags'] = record['tags'] + ['death']

                            item = transform(record)
                            save_item(item)     

    r = requests.get('http://www.who.int/csr/don/archive/disease/ebola/en/')
    handle_response(r)


def transform(record):
    adj = 'suspected'
    if 'confirmed' in record['tags']:
        adj = 'confirmed'

    noun = 'cases'
    if 'death' in record['tags']:
        noun = 'deaths'
        
    
    summary = str(record['totalAffectedPersons']) + ' ' + adj + ' ebola ' + noun + ' in ' + record['country']
    content = summary

    def make_id():
        return 'who_' + record['publishedAt'].strftime('%s') + '_' + adj + '_' + noun

    data = {
        'remoteID': make_id(),
        'content': content,
        'publishedAt': record['publishedAt'],
        'geo': {
            'addressComponents': {
                'adminArea1': record['country']
            }
        },
        'source': 'who',
        'lifespan': 'temporary',
        'license': 'unknown',
        'fromURL': record['fromURL'],
        'summary': summary,
        'totalAffectedPersons': record['totalAffectedPersons'],
        'tags': [{'confidence': 1, 'name': tag} for tag in record['tags']]
    }

    return data
       




