import os
import requests
import zipfile

from datetime import datetime, date, timedelta
from .data.gdelt import (event_descriptions, ethnicities, knowngroups, 
    religions, event_types)
from rfc3987 import parse

description = """ GDELT is an ambitious project that attempts to capture 
        'what's happening around the world, what its context is and who's 
        involved, and how the world is feeling about it, every single day.' 
        This stream is focused on conflict incidents. Beware, it's a little 
        messy."""

definition = {
    'internalID': 'b43be343-fca5-4415-b424-19e21468c33d',
    'sourceType': 'gdelt',
    'language': 'python',
    'frequency': 'repeats',
    'repeatsEvery': 'day',
    'startDate': datetime.strptime('20140422', "%Y%m%d"),
    'endDate': datetime.now() + timedelta(days=365),
    'description': description
}


def suck(save_item, handle_error):
    cur_dir = os.path.dirname(os.path.realpath(__file__))
    local_filename = cur_dir + '/data/gdelt/latest-gdelt-daily.zip'
    d = date.today() - timedelta(days=2)
    d_str = d.strftime("%Y%m%d")
    zip_url = 'http://data.gdeltproject.org/events/' + d_str + '.export.CSV.zip'

    local_filename = download_file(zip_url, local_filename)
    lines = extract_contents(local_filename, d_str + ".export.CSV")

    for l in lines:
        rowd = row_to_dict(l.split('\t'))
        if is_relevant(rowd):
            item = transform(rowd)
            save_item(item)


def transform(record):
    return_data = {
        'remoteID': record['GLOBALEVENTID'],
        'content': get_from_data(record, event_descriptions),
        'createdAt': datetime.now(),
        'updatedAt': datetime.now(),
        'publishedAt': datetime.strptime(record['SQLDATE'], '%Y%m%d'),
        'lifespan': "temporary",
        'geo': {
            'addressComponents': {
                'formattedAddress': get_address(record)
            }
        },
        'language': {
            'code': 'en'
        },
        'source': 'gdelt',
        'tags': set_tags(record)
    }
    
    return_data['summary'] = return_data['content']
    
    for func in [set_coords, set_from_url]:
        return_data = func(record, return_data)
    
    return return_data
    

def is_relevant(record):
    if record['EventRootCode'][0] == '0':
        return False

    # EventRootCodes lower than 14 are mostly administrative. Boring.
    # Sometimes the EventRootCode is an unpredictable string like --, hence
    # the try/catch
    try:
        if int(record['EventRootCode']) < 14:
            return False
    except:
        return False

    return True


def row_to_dict(row):
    columns = [ "GLOBALEVENTID","SQLDATE","MonthYear","Year","FractionDate","Actor1Code","Actor1Name","Actor1CountryCode","Actor1KnownGroupCode","Actor1EthnicCode","Actor1Religion1Code","Actor1Religion2Code","Actor1Type1Code","Actor1Type2Code","Actor1Type3Code","Actor2Code","Actor2Name","Actor2CountryCode","Actor2KnownGroupCode","Actor2EthnicCode","Actor2Religion1Code","Actor2Religion2Code","Actor2Type1Code","Actor2Type2Code","Actor2Type3Code","IsRootEvent","EventCode","EventBaseCode","EventRootCode","QuadClass","GoldsteinScale","NumMentions","NumSources","NumArticles","AvgTone","Actor1Geo_Type","Actor1Geo_FullName","Actor1Geo_CountryCode","Actor1Geo_ADM1Code","Actor1Geo_Lat","Actor1Geo_Long","Actor1Geo_FeatureID","Actor2Geo_Type","Actor2Geo_FullName","Actor2Geo_CountryCode","Actor2Geo_ADM1Code","Actor2Geo_Lat","Actor2Geo_Long","Actor2Geo_FeatureID","ActionGeo_Type","ActionGeo_FullName","ActionGeo_CountryCode","ActionGeo_ADM1Code","ActionGeo_Lat","ActionGeo_Long","ActionGeo_FeatureID","DATEADDED","SOURCEURL"  ]
    obj = {}

    for idx, val in enumerate(row):
        obj[columns[idx]] = row[idx]

    return obj


def extract_contents(local_filename, target_file):
    with zipfile.ZipFile(local_filename, 'r') as z:
        to_open = [name for name in z.namelist() if name == target_file]
        if to_open:
            with z.open(to_open[0]) as f:
                for line in f:
                    yield line


def download_file(url, local_filename):
    r = requests.get(url, stream=True)
    with open(local_filename, 'w+') as f:
        for chunk in r.iter_content(chunk_size=1024): 
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)
                f.flush()
    return local_filename



""" Helper methods for transform """
def get_from_data(record, labeled_data):
    found_items = filter(lambda x: str(x['code']) == record['EventCode'], 
        labeled_data.data)
    if found_items:
        return found_items[0]['label']

    return ""


def get_address(record):
    if len(record['Actor1Geo_FullName']) > 0:
        return record['Actor1Geo_FullName']

    if len(record['Actor2Geo_FullName']) > 0:
        return record['Actor2Geo_FullName']

    return None


def set_coords(record, return_data):
    if len(record['Actor2Geo_Lat']) > 0 or len(record['Actor1Geo_Lat']):
        if len(record['Actor1Geo_Lat']) > 0:
            coords = map(float, [record['Actor1Geo_Long'], record['Actor1Geo_Lat']])
        else:
            coords = map(float, [record['Actor2Geo_Long'], record['Actor2Geo_Lat']])

        return_data['geo']['coords'] = coords

    return return_data


def set_from_url(record, return_data):
    if len(record['SOURCEURL']) > 0:
        try:
            parse(record['SOURCEURL'], rule='IRI')
            return_data['fromURL'] = record['SOURCEURL']
        except:
            pass

    return return_data


def set_tags(record):
    code_to_tag = {
        '14': ['protest', 'conflict'],
        '145': ['physical-violence', 'riot', 'conflict'],
        '1451': ['physical-violence', 'riot', 'conflict'],
        '1452': ['physical-violence', 'riot', 'conflict'],
        '1453': ['physical-violence', 'riot', 'conflict'],
        '1454': ['physical-violence', 'riot', 'conflict'],
        '1711': ['property-loss', 'conflict'],
        '1712': ['property-loss', 'conflict'],
        '173': ['arrest', 'conflict'],
        '174': ['deportation', 'conflict'],
        '175': ['physical-violence', 'conflict'],
        '181': ['physical-violence', 'abduction', 'conflict'],
        '18': ['physical-violence', 'conflict'],
        '1821': ['physical-violence', 'sexual-violence', 'conflict'],
        '1822': ['physical-violence', 'torture', 'conflict'],
        '1823': ['physical-violence', 'death', 'conflict'],
        '183': ['physical-violence', 'death', 'suicide-bombing', 'conflict'],
        '1831': ['physical-violence', 'death', 'suicide-bombing', 'conflict'],
        '1832': ['physical-violence', 'death', 'suicide-bombing', 'conflict'],
        '1833': ['physical-violence', 'death', 'conflict'],
        '185': ['physical-violence', 'death', 'assassination', 'conflict'],
        '186': ['physical-violence', 'assassination', 'conflict'],
        '19': ['conflict'],
        '191': ['restrict-movement', 'conflict'],
        '192': ['occupation', 'conflict'],
        '193': ['conflict', 'armed-conflict'],
        '194': ['conflict', 'armed-conflict'],
        '201': ['conflict', 'mass-violence'],
        '202': ['conflict', 'mass-violence', 'death', 'physical-violence'],
        '203': ['conflict', 'mass-violence', 'death', 'physical-violence', 'ethnic-violence']
    }

    def tags_for_props(props, tag_list, tags=[]):
        for prop in props:
            val = str(record[prop])
            matches = [tag for tag in tag_list if str(tag['code']) == val]
            tags += [match['label'] for match in matches]

        return tags

    tags = tags_for_props(['Actor1EthnicCode', 'Actor2EthnicCode'], ethnicities.data)
    
    tags = tags_for_props(['Actor1KnownGroupCode', 'Actor2KnownGroupCode'], 
        knowngroups.data, tags)
    
    tags = tags_for_props(['Actor1Religion1Code', 'Actor1Religion2Code', 
        'Actor2Religion1Code', 'Actor2Religion2Code'], religions.data, tags)
    
    tags = tags_for_props(['Actor1Type1Code', 'Actor1Type2Code','Actor1Type3Code', 
        'Actor2Type1Code','Actor2Type2Code','Actor2Type3Code'], 
        event_types.data, tags)

    for key in ['EventCode', 'EventRootCode', 'EventBaseCode']:
        if record[key] in code_to_tag:
            tags = tags + code_to_tag[record[key]]

    no_dupes = list(set(tags))

    return [{'name':tag, 'confidence':1} for tag in no_dupes]
