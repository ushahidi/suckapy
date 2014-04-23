from src.suckas import gdelt
import os

def test():
    cur_dir = os.path.dirname(os.path.realpath(__file__))
    local_filename = cur_dir + '/data/gdelt/latest-gdelt-daily.zip'

    lines = gdelt.extract_contents(local_filename, "20140419.export.CSV")

    for l in lines:
        rowd = gdelt.row_to_dict(l.split('\t'))
        if gdelt.is_relevant(rowd):
            item = gdelt.transform(rowd)
            assert 'remoteID' in item
            assert 'content' in item
            assert 'publishedAt' in item
            assert item['tags'] is not None
            for tag in item['tags']:
                assert 'name' in tag
