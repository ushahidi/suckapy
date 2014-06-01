from datetime import datetime, timedelta
import facepy
from facepy.exceptions import FacebookError
from config import settings
from dateutil.parser import parse
from . import facebook_syria as facebook_base
import csv
import os

description = """ About 1k Facebook pages relevant to ongoing conflict in Syria, 
courtesy of Eliot Higgins (aka Brown Moses) """

definition = {
    'internalID': 'ee564003-c7be-49fe-bc3e-e2a0c40e55b1',
    'sourceType': 'facebook',
    'uniqueName': 'facebook_thailand',
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
    local_filename = cur_dir + '/data/facebook_thailand/facebook_pages.csv'

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
            
            got_content = facebook_base.get_content(username, graph, source, save_item, admin1='Thailand', source_key='facebook_thailand')

            if not got_content:
                last_retrieved[lr_key] = 'Failing'
            else:
                last_retrieved[lr_key] = datetime.now().strftime("%s")

    return last_retrieved



   
    