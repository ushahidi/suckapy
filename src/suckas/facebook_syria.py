from datetime import datetime, timedelta
import facepy
from facepy.exceptions import FacebookError
from config import settings
from dateutil.parser import parse
import csv
import os

description = """ About 1k Facebook pages relevant to ongoing conflict in Syria, 
courtesy of Eliot Higgins (aka Brown Moses) """

definition = {
    'internalID': '89e2ee06-bce0-4613-a300-42223ed2c2fe',
    'sourceType': 'facebook_syria',
    'language': 'python',
    'frequency': 'repeats',
    'repeatsEvery': 'hour',
    'startDate': datetime.strptime('20140507', "%Y%m%d"),
    'endDate': datetime.now() + timedelta(days=365),
    'description': description
}


def suck(save_item, handle_error, source):
    auth_token = facepy.utils.get_application_access_token(
        settings.FACEBOOK['app_id'],
        settings.FACEBOOK['app_secret'])


    graph = facepy.GraphAPI(auth_token)
    last_retrieved = {}
    cur_dir = os.path.dirname(os.path.realpath(__file__))
    local_filename = cur_dir + '/data/facebook_syria/facebook_pages.csv'

    with open(local_filename, 'rb') as f:
        reader = csv.reader(f)
        # Skip the headers
        reader.next()

        for row in reader:
            username = row[3]
            lr_key = username.replace('.','|')
            
            # Don't bother making requests for a page that no longer exists
            if 'lastRetrieved' in source and lr_key in source['lastRetrieved'] and source['lastRetrieved'] == 'Failing':
                continue
            
            got_content = get_content(username, graph, source, save_item)

            if not got_content:
                last_retrieved[lr_key] = 'Failing'
            else:
                last_retrieved[lr_key] = datetime.now().strftime("%s")

    return last_retrieved


def get_content(username, graph, source, save_item):
    try:
        page = graph.get(username)
    except FacebookError:
        return False

    kwargs = {
        'path': username+"/posts"
    }

    if 'lastRetrieved' in source and username in source['lastRetrieved']:
        kwargs['since'] = source['lastRetrieved'][username]

    posts = graph.get(**kwargs)

    for post in posts['data']:
        item = transform(post, page)
        if item:
            save_item(item)

    return True


def transform(record, page):
    if 'message' in record:
        message = record['message']
    elif 'story' in record:
        message = record['story']
    elif 'name' in record:
        message = record['name']
    elif 'description' in record:
        message = record['description']
    else:
        return None

    if 'location' in page:
        print page['location']

    if 'object_id' in record:
        object_id = record['object_id']
    elif 'id' in record:
        object_id = record['id']
    else:
        return None


    data = {
        'remoteID': object_id,
        'source': 'facebook_syria',
        'content': message,
        'lifespan': 'temporary',
        'geo': {
            'addressComponents': {
                'adminArea1': 'Syria'
            }
        },
        'fromURL': 'http://facebook.com/' + object_id,
        'publishedAt': parse(record['created_time'])
    }

    if 'picture' in record:
        data['image'] = record['picture']

    if 'status_type' in record and record['status_type'] == 'added_video' and 'source' in record:
        data['video'] = record['source']

    if 'location' in page:
        loc_str = ''

        if 'street' in page['location']:
            loc_str = loc_str + page['location']['street']

        if 'city' in page['location']:
            loc_str = loc_str + ' ' + page['location']['city']

        if 'country' in page['location']:
            loc_str = loc_str + ', ' + page['location']['country']

        data['geo']['locationIdentifiers'] = {
            'authorLocationName': loc_str
        }

    return data
    