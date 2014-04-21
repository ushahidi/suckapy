import os
os.environ['SUCKAPY'] = 'test'

import logging
import datetime
import os.path, pkgutil
import suckas
from src import app

logger = logging.getLogger(__name__)

def test():
    pkgpath = os.path.dirname(suckas.__file__)
    sucka_names = [name for _, name, _ in pkgutil.iter_modules([pkgpath])]

    sources = app.setup_sources(sucka_names)

    assert len(sources) > 0
    assert 'internalID' in sources[0] and len(sources[0]['internalID']) > 0

    source = [s for s in sources if s['sourceType'] == 'test_sucka'][0]
    sucka = app.get_sucka_for_source(source)

    assert hasattr(sucka, 'definition')
    assert sucka.definition['internalID'] == source['internalID']

    now = datetime.datetime.now()

    source = app.do_suck(source)
    assert source['lastRun'] > now
    assert source['lastRetrieved']['remoteID'] == '291506692'

    