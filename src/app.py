import logging
import time
import sys
import json
import importlib
import os.path, pkgutil
import suckas

from datetime import datetime
from qr import Queue
from config import settings
from cn_store_py.connect import get_connection
from cn_search_py.connect import (setup_indexes, 
    get_connection as get_search_connection)
from cn_search_py.collections import ItemCollection
from bson import objectid

logger = logging.getLogger('suckapy')

db = get_connection()
search_db = get_search_connection()
items = ItemCollection(search_db)

app_queue = Queue(settings.QUEUE_NAME, host=settings.REDIS_HOST, 
            port=settings.REDIS_PORT, password=settings.REDIS_PASSWORD)
transform_queue = Queue(settings.TRANSFORM_QUEUE_NAME, host=settings.REDIS_HOST, 
            port=settings.REDIS_PORT, password=settings.REDIS_PASSWORD)

app_queue.serializer = json
transform_queue.serializer = json

pkgpath = os.path.dirname(suckas.__file__)
sucka_names = [name for _, name, _ in pkgutil.iter_modules([pkgpath])]


def setup_sources(sucka_names):
    modules = [importlib.import_module('suckas.'+name) for name in sucka_names]

    def upsert_source(mod):
        definition = mod.definition
        return db.Source.find_and_modify(
            { 'internalID': definition['internalID'] },
            { '$set': definition },
            { 'upsert': True, 'new': True }
        )

    return [upsert_source(mod) for mod in modules if hasattr(mod, 'definition')]


def get_sucka_for_source(source):
    if 'uniqueName' not in source:
        return None
    source_type = source['uniqueName']
    if source_type not in sucka_names:
        return None

    return importlib.import_module('suckas.'+source_type)


def post_suck(source, last_retrieved=None):
    source['lastRun'] = datetime.now()
    source['hasRun'] = True

    if last_retrieved:
        source['lastRetrieved'] = last_retrieved

    source.save()
    return source


def save_item(data, refresh=False):
    item = items.make_model(data)
    saved = item.save(refresh=refresh)

    if saved:
        
        if 'created' in saved and saved['created']:
            id_str = str(saved['_id'])
            logger.info("Pushing task "+id_str)
            transform_queue.push(json.dumps({'id': id_str}))
        
        #id_str = str(saved['_id'])
        #logger.info("Pushing task "+id_str)
        #transform_queue.push(json.dumps({'id': id_str}))
        return saved

    return None


def handle_broken_source(source, data, error):
    source.status = 'failing'
    source.failData = data
    source.save()


def do_suck(source):
    sucka = get_sucka_for_source(source)

    if not sucka:
        logger.warn('no sucka found for ' + source['uniqueName'])
        return False

    last_retrieved = sucka.suck(save_item, handle_broken_source, source)
    return post_suck(source, last_retrieved)


def process_task(task):
    try:
        data = json.loads(task)
        source = db.Source.one({'_id': objectid.ObjectId(data['id'])})
        if source:
            do_suck(source)
    except Exception, e:
        import traceback
        logger.error("Problem! " + str(e))
        logger.error(traceback.format_exc())
        

def start_app():
    setup_sources(sucka_names)

    while True:
        try:
            task = app_queue.pop()
            if task:
                process_task(task)
            time.sleep(1)
        except KeyboardInterrupt:
            logger.warn("Exiting suckapy")
            sys.exit()


if __name__ == "__main__":
    args = sys.argv

    if len(args) > 1 and args[1] == '--source':
        source = db.Source.one({'_id': objectid.ObjectId(args[2])})
        if source:
            logger.info("Sucking for source "+source['uniqueName'])
            do_suck(source)
    else:
        logger.warn("Starting suckapy")
        start_app()