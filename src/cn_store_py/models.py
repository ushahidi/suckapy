from mongokit import Document, INDEX_GEO2D
#from pymongo import objectid
import datetime

class Item(Document):
    __collection__ = 'items'
    use_schemaless = True
    structure = {
        'createdAt': datetime.datetime,
        'udpatedAt': datetime.datetime,
        'remoteID': basestring,
        'activeUntil': datetime.datetime,
        'lifespan': basestring,
        'content': basestring,
        'summary': basestring,
        'image': basestring,
        'geo': {
            'addressComponents': {
                'formattedAddress': basestring,
                'streetNumber': basestring,
                'streetName': basestring,
                'streetAddress': basestring,
                'neighborhood': basestring,
                'adminArea5': basestring, # city
                'adminArea4': basestring, # county
                'adminArea3': basestring, # state
                'adminArea2': basestring, # region
                'adminArea1': basestring, # country
                'postalCode': basestring
            },
            'mentionedPlaces': [basestring],
            # lng, lat
            'coords': None,
            'accuracy': int,
            'granularity': basestring,
            'locationIdentifiers': {
                'authorLocationName': basestring,
                'authorTimeZone': basestring
            }
        },
        'tags': [{
            'name': basestring,
            'confidence': int
        }],
        'language': {
            'code': basestring,
            'name': basestring,
            'nativeName': basestring
        },
        'source': basestring,
        'license': basestring
    }
    required_fields = ['remoteID', 'lifespan']
    indexes = [
        {
            'fields':[('geo.coords',INDEX_GEO2D)],
        }
    ]

    default_values = {
        'license': 'unknown',
        'lifespan': 'temporary',
        'createdAt': datetime.datetime.now
    }


class Source(Document):
    __collection__ = 'sources'
    use_schemaless = True
    
    structure = {
        'createdAt': datetime.datetime,
        'udpatedAt': datetime.datetime,
        'internalID': basestring,
        'sourceType': basestring,
        'frequency': basestring,
        'repeatsEvery': basestring,
        'hasRun': bool,
        'startDate': datetime.datetime,
        'endDate': datetime.datetime,
        'description': basestring,
        'status': basestring,
        'lastRun': datetime.datetime,
        'lastRetrieved': None,
        'filters': None,
        'failData': None
    }
    
    required_fields = [
        'internalID', 
        'sourceType',
        'frequency'
    ]
    
    indexes = [
        {
            'fields':[('internalID')],
        }
    ]

    default_values = {
        'status': 'active',
        'createdAt': datetime.datetime.now
    }

