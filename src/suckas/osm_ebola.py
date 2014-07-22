import requests
from datetime import datetime, timedelta
from dateutil.parser import parse
import json
import os
import re

cur_dir = os.path.dirname(os.path.abspath(__file__))

description = """ Open Street Map layers focused on Ebola outbreak in west Africa """

definition = {
    'internalID': '01d41d9a-2fd6-4571-adc3-751f32caf28d',
    'sourceType': "osm",
    'uniqueName': "osm_ebola",
    'language': "python",
    'frequency': "repeats",
    'repeatsEvery': "day",
    'startDate': datetime.strptime('20140507', "%Y%m%d"),
    'endDate': datetime.now() + timedelta(days=365),
    'description': description,
    'status': 'active'
}


def suck(save_item, handle_error, source):
    files = [
        ['confirmed-dead', ['ebola','death','confirmed','disease','disaster']],
        ['confirmed', ['ebola','confirmed','disease','disaster']],
        ['cured', ['ebola','confirmed','cured','disease','disaster']],
        ['probable-dead', ['ebola','death','disease','disaster']],
        ['probable-dead-2', ['ebola','death','disease','disaster']],
        ['sierra-leon-confirmed-dead', ['ebola','death','confirmed','disease','disaster']],
        ['sierra-leon-confirmed', ['ebola','confirmed','disease','disaster']],
        ['sierra-leon-suspected', ['ebola','disease','disaster']],
        ['sierra-leon-unvalidated-suspected', ['ebola','disease','disaster']],
        ['sierre-leon-suspected-dead', ['ebola','death','disease','disaster']],
        ['suspected',['ebola','disease','disaster']],
        ['suspected-2',['ebola','disease','disaster']]
    ]

    for f in files:
        with open(cur_dir + '/data/osm_ebola/' + f[0] + '.geojson') as json_file:
            geo_json = json.load(json_file)
        
            items = [transform(feature, f[1]) for feature in geo_json['features']]
    
            for item in items:
                save_item(item)


def transform(record, tags):
    coords = record['geometry']['coordinates']
    content = record['properties']['description']
    
    url = None
    url_match = re.search("(?P<url>https?://[^\s]+)", content)
    if url_match:
        url = url_match.group()
    
    summary = record['properties']['description']

    dates = [d.group() for d in re.finditer("(\d+\s\w+\s2014)", content)]
    dates2 = [d.group() for d in re.finditer("(\w+\s\d+\s2014)", content)]

    if len(dates) > 0 and dates[0]:
        pub_date = parse(dates[0])
    elif len(dates2) > 0 and dates2[0]:
        pub_date = parse(dates2[0])
    else:
        pub_date = datetime.today()

    num_match = re.search("(?P<num>\d+)\scas", summary)
    if num_match:
        number_impacted = num_match.group("num")
        try:
            number_impacted = int(number_impacted)
        except:
            number_impacted = 1
    else:
        number_impacted = 1


    if 'facebook' in url:
        source = 'facebook'
        license = 'facebook'
    elif 'twitter' in url:
        source = 'twitter'
        license = 'twitter'
    else:
        source = 'osm'
        license = 'odbl'

    
    def make_id():
        return '_'.join(str(e) for e in coords) + "_" + ''.join(str(e) for e in tags)

    
    data = {
        'remoteID': make_id(),
        'content': content,
        'publishedAt': pub_date,
        'geo': {
            'coords': coords
        },
        'source': source,
        'lifespan': 'temporary',
        'license': license,
        'fromURL': url,
        'summary': summary,
        'totalAffectedPersons': number_impacted,
        'tags': [{'confidence': 1, 'name': tag} for tag in tags]
    }

    return data

