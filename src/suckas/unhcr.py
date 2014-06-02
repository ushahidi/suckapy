import requests
from datetime import datetime, timedelta
from dateutil.parser import parse
import string

description = """ The Office of the United Nations High Commissioner for Refugees (UNHCR), also known as the UN Refugee Agency, is a United Nations agency mandated to protect and support refugees at the request of a government or the UN itself and assists in their voluntary repatriation, local integration or resettlement to a third country. Its headquarters are in Geneva, Switzerland and is a member of the United Nations Development Group. """

definition = {
    'internalID': '061e068d-10f9-472b-90b4-a10f9bee9862',
    'sourceType': 'unhcr',
    'uniqueName': 'unhcr',
    'language': 'python',
    'frequency': 'repeats',
    'repeatsEvery': 'day',
    'startDate': datetime.strptime('20140507', "%Y%m%d"),
    'endDate': datetime.now() + timedelta(days=365),
    'description': description
}

def make_id(record):
    population = record['population'][0]
    return "%s_%s_%s" %(record["instance_id"], 
        "".join([l for l in list(record['name']) if l in string.lowercase]), 
        parse(population['updated_at']).strftime('%s'))


def suck(save_item, handle_error, source):
    instances = [
        "car",
        "cotedivoire",
        "horn",
        "liberia",
        "mali",
        "southsudan",
        "syria",
        "thai"
    ]

    base_url = 'http://data.unhcr.org/api/population/get_settlements.json?instance_id='

    if 'lastRetrieved' not in source:
        source['lastRetrieved'] = {}

    for instance in instances:
        r = requests.get(base_url + instance)
    
        if r.status_code == 200:
            json_data = r.json()

            for record in json_data:
                if 'population' in record and len(record['population']) > 0:
                    item = transform(record)
                    save_item(item)
                else:
                    print record


def transform(record):
    def make_content(record):
        population = record['population'][0]

        households = ' individuals'
        if 'households' in population:
            households = ' from ' + population['households'] + ' households'

        return population['value'] + households + ' reported at ' + record['name'] + ' in ' + record['country'] 

    population = record['population'][0]
    
    item = {
        'remoteID': make_id(record),
        'source': 'unhcr',
        'content': make_content(record),
        'geo': {
            'addressComponents': {
                'adminArea1': record['country'],
                'adminArea3': record['region'],
            },
            'coords': [
                float(record['longitude']),
                float(record['latitude'])
            ]
        },
        'tags': [
            {
                'name': 'refugee',
                'confidence': 1
            }
        ],
        'publishedAt': parse(population['updated_at']),
        'license': 'unknown',
        'totalAffectedPersons': int(population['value'])
    }

    if 'url' in record:
        item['fromURL'] = record['url']

    return item

