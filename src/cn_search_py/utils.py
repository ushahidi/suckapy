from elasticsearch import Elasticsearch
from elasticsearch.helpers import scan
from .collections import ItemCollection
import sys

#Prod
TO_ES_HOST = 'fbd15e5cdc8f131c7ca72e9b3c371bb4-us-east-1.foundcluster.com'
TO_ES_PORT = 9200
TO_ES_AUTH = 'readwrite:1o8sfeq6prbpojdh73'

#Local
#TO_ES_HOST = 'localhost'
#TO_ES_PORT = 9200
#TO_ES_AUTH = None

#Staging
FROM_ES_HOST = 'b8dfbe45f9f8fb89036d56d6c6fa8152-us-east-1.foundcluster.com'
FROM_ES_PORT = 9200
FROM_ES_AUTH = 'readwrite:2ha0nxi5h8gl90ekop'

def reindex(from_index, to_index):
    es_current = Elasticsearch(host=FROM_ES_HOST, port=FROM_ES_PORT, http_auth=FROM_ES_AUTH)

    es_target = Elasticsearch(host=TO_ES_HOST, port=TO_ES_PORT, http_auth=TO_ES_AUTH)

    query = { "query" : { "match_all" : {} }}
    """
    query = {
        "query": {
            "filtered" : {
                "filter" : {
                    "not" : {
                        "term" : {
                            "source" : "gdelt"
                        }
                    }
                }
            }
        }
    }
    """

    all_docs = scan(client = es_current, query = query, scroll= "5m", 
        index = from_index, doc_type = ItemCollection.doc_type)

    items = ItemCollection(es_target, index=to_index)
    for a in all_docs:
        item = items.make_model(a['_source'])
        print 'storing ' + a['_id'] + ' from ' + item.data['source']
        item._index(id=a['_id'], body=item.data)



def create_index(index_name):
    es = Elasticsearch(host=TO_ES_HOST, port=TO_ES_PORT, http_auth=TO_ES_AUTH)

    es.indices.create(index_name, ignore=400)
    es.indices.put_mapping(doc_type=ItemCollection.doc_type, 
        body=ItemCollection.mapping, index=index_name)


def add_alias(index_name):
    es = Elasticsearch(host=TO_ES_HOST, port=TO_ES_PORT, http_auth=TO_ES_AUTH)
    es.indices.put_alias(index=index_name, name='item_alias', ignore=[400,404])


def update_aliases(from_index, to_index):
    es = Elasticsearch(host='localhost', port=9200)

    es.indices.delete_alias(index=from_index, name='item_alias', ignore=[400,404])
    es.indices.put_alias(index=to_index, name='item_alias', ignore=[400,404])


def delete_index(index_name):
    es = Elasticsearch(host='localhost', port=9200)

    es.indices.delete(index=index_name, ignore=[400,404])


def migrate_index(from_index, to_index):
    create_index(to_index)
    reindex(from_index, to_index)
    update_aliases(from_index, to_index)
    delete_index(from_index)


def update_by_query():
    es_target = Elasticsearch(host=TO_ES_HOST, port=TO_ES_PORT, http_auth=TO_ES_AUTH)

    query = {
        "query": {
            "filtered" : {
                "filter" : {
                    "term" : {
                        "source" : "facebook_syria"
                    }
                }
            }
        }
    }

    all_docs = scan(client = es_target, query = query, scroll= "5m", 
        index = 'item_alias', doc_type = ItemCollection.doc_type)

    items = ItemCollection(es_target, index='item_alias')
    for a in all_docs:
        item = items.make_model(a['_source'])
        item.data['license'] = 'facebook'
        item.data['source'] = 'facebook'
        print 'storing ' + a['_id'] + ' from ' + item.data['source']
        item._index(id=a['_id'], body=item.data)


if __name__ == "__main__":
    args = sys.argv

    if args[1] == 'reindex':
        reindex(args[2], args[3])

    if args[1] == 'migrate':
        migrate_index(args[2], args[3])

    if args[1] == 'create':
        create_index(args[2])

    if args[1] == 'alias':
        update_aliases(args[2], args[3])

    if args[1] == 'addalias':
        add_alias(args[2])

    if args[1] == 'updatequery':
        update_by_query()