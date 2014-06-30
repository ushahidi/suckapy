from src.suckas import unocha_iraq_idp as un
import os
import xlrd

cur_dir = os.path.dirname(os.path.abspath(__file__))


def test():
    workbook = xlrd.open_workbook(cur_dir + '/data/unocha_iraq_idp/latest.xlsx')
    worksheet = workbook.sheet_by_name('Summary Data')
    
    for row_num in range(5, worksheet.nrows - 3):
        item = un.transform(worksheet,row_num)
        assert item['geo']['addressComponents']['adminArea3'] == 'Muthana'
        assert item['totalAffectedPersons'] == 174
        assert 'idp' in [tag['name'] for tag in item['tags']]

        break
    