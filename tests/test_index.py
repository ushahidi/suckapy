import os
os.environ['SUCKAPY'] = 'test'

import logging
import datetime
from cn_search_py import connect, collections, utils

logger = logging.getLogger(__name__)

def test():
    utils.delete_index('test_index')
    utils.create_index('test_index')
    utils.update_aliases('test_index', 'test_index')

    search_db = connect.get_connection()
    items = collections.ItemCollection(search_db, index='test_index')

    data = {
        'remoteID': '1',
        'content': 'test',
        'summary': 'more testing',
        'geo': {
            'coords': [1,2]
        },
        'source': 'test_source'
    }

    item = items.make_model(data)
    indexed = item.save(refresh=True)

    assert 'created' in indexed
    print "------- INSERTED ----------"
    print indexed

    new_item = items.make_model(data)
    new_indexed = new_item.save()

    print "------- UPSERTED ---------"
    print new_indexed

    assert new_indexed['_id'] == indexed['_id']
    assert 1 == 2

    params = [
        {
            'field': 'content',
            'value': data['content']
        }
    ]

    item = items.get(params)
    assert item['id'] == indexed['_id']

    utils.delete_index('test_index')

