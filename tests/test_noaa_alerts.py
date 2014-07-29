from src.suckas import noaa_alerts
from datetime import datetime
import os


def test():
    def asserter(item):
        assert 'remoteID' in item and item['remoteID']
        assert 'summary' in item and item['summary']
        assert 'content' in item and item['content']
        assert 'tags' in item
        assert len(item['tags']) > 1
        assert isinstance(item['publishedAt'], datetime)

        for tag in item['tags']:
            assert 'name' in tag
            assert tag['confidence'] == 1

    lr = noaa_alerts.suck(asserter,'b',{})