from config import settings
from elasticsearch import Elasticsearch
from .collections import ItemCollection


def get_connection():
    return Elasticsearch(host=settings.ES_HOST, port=settings.ES_PORT)

def setup_indexes(conn):
    conn.indices.create(ItemCollection.index, ignore=400)
    conn.indices.put_mapping(doc_type=ItemCollection.doc_type, 
      body=ItemCollection.mapping, index=ItemCollection.index)

