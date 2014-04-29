import logging
from elasticsearch import Elasticsearch
from config import settings
from .models import Item
from .exceptions import DoesNotExist, MultipleObjectsReturned

logger = logging.getLogger(__name__)

class Collection(object):
    def make_model(self, data={}):
        return self.model(data, self)


    def _build_params(self, params):
        _params = []

        for param in params:
            if 'op' not in param:
                param['op'] = '='

            if param['op'] is '=':
                obj = {}
                obj[param['field']] = param['value']

                _params.append({ 'term': obj })

        if len(_params) is 0:
            return _params[0]

        
        return {
            "and": _params
        }


    def _search(self, params, limit=100, offset=0):
        body = {
            "query": {
                "filtered" : {
                    "filter" : self._build_params(params)
                }
            }
        }

        kwargs = {
            'index': self.index,
            'doc_type': self.doc_type,
            'body': body,

        }

        res = self.conn.search(**kwargs)

        return res

    
    def get(self, params):
        res = self._search(params)

        if res['hits']['total'] == 1:
            doc = res['hits']['hits'][0]['_source']
            doc['id'] = res['hits']['hits'][0]['_id']
            
            return doc

        if res['hits']['total'] == 0:
            raise DoesNotExist(
                "%s matching query does not exist. "
                "Lookup parameters were %s" %
                (self.model.__name__, params))

        raise self.model.MultipleObjectsReturned(
            "get() returned more than one %s -- it returned %s! "
            "Lookup parameters were %s" %
            (self.model.__name__, num, params))


    def find(self, params):
        res = self._search(params)


class ItemCollection(Collection):
    model = Item
    doc_type = 'item-type'
    index = 'item'
    mapping = {
        'properties': {
            'geo': {
                'properties': {
                    'coords': {
                        'type': 'geo_point'
                    }
                }
            },
            'remoteID': {
                "type" : "string", 
                "index" : "not_analyzed"
            }
        }
    }


    def __init__(self, conn):
        self.conn = conn

