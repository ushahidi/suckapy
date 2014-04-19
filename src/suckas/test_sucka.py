import datetime

definition = {
    'internalID': '265732a1-9bff-4e90-934d-c27be89c75ee',
    'sourceType': 'test_sucka',
    'language': 'python',
    'frequency': 'repeats',
    'repeatsEvery': 'hour',
    'startDate': datetime.datetime.now(),
    'endDate': datetime.datetime.now()
}

def suck(save_item, handle_error):
    data = {
      'remoteID': "291506692",
      'content': "Expel or deport individuals",
      'source': "gdelt",
      'fromURL': "http://www.theage.com.au/world/taliban-attackers-mistake-armed-contractors-for-christian-daycare-workers-20140330-zqolw.html",
      'summary': "Expel or deport individuals",
      'license': "unknown",
      'language': {
        'code': "en",
        'name': "English",
        'nativeName': "English"
      },
      'tags': [
        {
          'name': "Christianity",
          'confidence': 1
        },
        {
          'name': "deportation",
          'confidence': 1
        },
        {
          'name': "conflict",
          'confidence': 1
        }
      ],
      'geo': {
        'coords': [
          69.1833,
          34.5167
        ],
        'addressComponents': {
          'formattedAddress': "Kabul, Kabol, Afghanistan"
        }
      },
      'lifespan': "temporary"
    }

    item = save_item(data)
    return item