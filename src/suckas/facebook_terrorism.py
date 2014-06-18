from datetime import datetime, timedelta
import facepy
from facepy.exceptions import FacebookError
from config import settings
from dateutil.parser import parse
from . import facebook_syria as facebook_base
import csv
import os

description = """ Facebook pages of terrorist organizations or journalists/agencies/etc tracking those organizations """

definition = {
    'internalID': '5a3c9e0f-b364-40f7-ba21-45907c672307',
    'sourceType': 'facebook',
    'uniqueName': 'facebook_terrorism',
    'language': 'python',
    'frequency': 'repeats',
    'repeatsEvery': 'hour',
    'startDate': datetime.strptime('20140507', "%Y%m%d"),
    'endDate': datetime.now() + timedelta(days=365),
    'description': description,
    'status': 'active'
}


def suck(save_item, handle_error, source):
    auth_token = facepy.utils.get_application_access_token(
        settings.FACEBOOK['app_id'],
        settings.FACEBOOK['app_secret'])


    graph = facepy.GraphAPI(auth_token)
    last_retrieved = {}
    cur_dir = os.path.dirname(os.path.realpath(__file__))
    local_filename = cur_dir + '/data/facebook_terrorism/facebook_pages.csv'

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
            
            author = {
                'name': row[1],
                'username': username
            }
            
            got_content = facebook_base.get_content(username, graph, source, save_item, author=author)

            if not got_content:
                last_retrieved[lr_key] = 'Failing'
            else:
                last_retrieved[lr_key] = datetime.now().strftime("%s")

    return last_retrieved