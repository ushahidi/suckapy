from datetime import datetime, timedelta
from dateutil.parser import parse
import xlrd
import os
import string

cur_dir = os.path.dirname(os.path.abspath(__file__))

description = """ Iraq New IDPs summary by Province from UNOCHA """

definition = {
    'internalID': 'fdafc7d7-774f-4df4-8a8b-d144f3c01359',
    'sourceType': 'unocha',
    'uniqueName': 'unocha_iraq_idp',
    'language': 'python',
    'frequency': 'repeats',
    'repeatsEvery': 'day',
    'startDate': datetime.strptime('20140507', "%Y%m%d"),
    'endDate': datetime.now() + timedelta(days=365),
    'description': description
}

def make_id(province,published_at):
    return "iraq_%s_%s" %("".join([l for l in list(province) if l in string.lowercase]), 
        published_at.strftime('%s'))

def suck(save_item, handle_error, source):
    workbook = xlrd.open_workbook(cur_dir + '/data/unocha_iraq_idp/latest.xlsx')
    worksheet = workbook.sheet_by_name('Summary Data')
    
    for row_num in range(5, worksheet.nrows - 3):
        save_item(transform(worksheet,row_num))


def transform(worksheet,row_num):
    households = int(worksheet.cell_value(row_num, 1))
    count = int(worksheet.cell_value(row_num, 8))
    admin3 = worksheet.cell_value(row_num, 0)
    published_at = parse(worksheet.cell_value(0, 0).split('-')[1].strip())

    item = {
        'remoteID': make_id(admin3,published_at),
        'source': 'unocha',
        'content': str(count) + ' from ' + str(households) + ' households reported in ' + admin3 + ', Iraq',
        'geo': {
            'addressComponents': {
                'adminArea1': 'Iraq',
                'adminArea3': admin3,
            }
        },
        'tags': [
            {
                'name': 'refugee',
                'confidence': 1
            },
            {
                'name': 'idp',
                'confidence': 1
            }
        ],
        'publishedAt': published_at,
        'license': 'unknown',
        'totalAffectedPersons': count
    }

    return item

