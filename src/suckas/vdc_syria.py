from bs4 import BeautifulSoup
import requests
from datetime import datetime, timedelta
import re
from dateutil.parser import parse

description = """ Violation Documentation Center in Syria is an independent, 
    civil non-profit, non-governmental organization that started its work of 
    monitoring and documenting the violations of human rights in Syria since 
    April 2011. http://www.vdc-sy.info/ """

definition = {
    'internalID': '1e44370d-6dcc-4813-b6cc-b104beeddc22',
    'sourceType': 'vdc_syria',
    'language': 'python',
    'frequency': 'repeats',
    'repeatsEvery': 'day',
    'startDate': datetime.strptime('20140507', "%Y%m%d"),
    'endDate': datetime.now() + timedelta(days=365),
    'description': description
}


def suck(save_item, handle_error, source):
    civilian_deaths_url = 'http://www.vdc-sy.info/index.php/en/martyrs/1/c29ydGJ5PWEua2lsbGVkX2RhdGV8c29ydGRpcj1ERVNDfGFwcHJvdmVkPXZpc2libGV8ZXh0cmFkaXNwbGF5PTB8'

    r = requests.get(civilian_deaths_url)
    if r.status_code == 200:
        soup = BeautifulSoup(r.text)
        rows = soup.find_all('tr')
        
        for row in rows[3:]:
            record = {
                'url': None,
                'name': None,
                'id': None,
                'sex': None,
                'province': None,
                'area': None,
                'date': None,
                'cause': None,
                'notes': None,
                'image': None,
                'video': None,
                'type': None
            }

            tds = row.contents

            if len(tds) < 5:
                continue

            record['url'] = 'http://www.vdc-sy.info' + tds[1].a['href']

            found = re.search('(\d+)', tds[1].a['href'])
            record['id'] = found.group(1)

            record['name'] = tds[1].a.text
            record['type'] = tds[3].text

            record['sex'] = tds[5].text
            record['province'] = tds[7].text
            record['area'] = tds[9].text
            record['date'] = tds[11].text
            record['cause'] = tds[13].text

            r_sub = requests.get(record['url'])
            if r_sub.status_code == 200:
                sub_soup = BeautifulSoup(r_sub.text)

                sub_rows = sub_soup.find_all('tr')

                record['image'] = sub_rows[3].contents[1].text
                record['notes'] = sub_rows[19].contents[1].text


                try:
                    record['video'] = sub_rows[21].contents[1].text
                except:
                    pass

            item = transform(record)
            save_item(item)


def transform(record):
    item = {
        'remoteID': record['id'],
        'source': 'vdc_syria',
        'summary': record['sex'] + ' ' + record['type'] + ' killed by ' + record['cause'],
        'content': record['name'] + ' killed by ' + record['cause'] + '. ' + record['notes'],
        'geo': {
            'addressComponents': {
                'adminArea1': 'Syria',
                'adminArea3': record['province'],
                'neighborhood': record['area']
            }
        },
        'tags': [
            {
                'name': 'conflict',
                'confidence': 1
            },
            {
                'name': 'death',
                'confidence': 1
            }
        ],
        'publishedAt': parse(record['date']),
        'fromURL': record['url']
    }

    if 'video' in record and record['video'] and len(record['video'].strip()) > 0:
        item['video'] = record['video']

    if 'image' in record and record['image'] and len(record['image'].strip()) > 0:
        item['image'] = record['image']


    return item




