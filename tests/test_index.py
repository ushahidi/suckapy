import os
os.environ['SUCKAPY'] = 'test'

import logging
import datetime
from cn_search_py import connect, collections

logger = logging.getLogger(__name__)

def test():
    search_db = connect.get_connection()
    search_db.indices.delete(index='item', ignore=[400, 404])
    items = collections.ItemCollection(search_db)
    connect.setup_indexes(search_db)

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

    assert indexed['created'] is True

    new_item = items.make_model(data)
    new_indexed = new_item.save()

    assert new_indexed['_id'] == indexed['_id']

    params = [
        {
            'field': 'content',
            'value': data['content']
        }
    ]

    item = items.get(params)
    assert item['id'] == indexed['_id']

