from src.suckas import instagrammer
import os


def test():
    def asserter(item):
        assert 'remoteID' in item and item['remoteID']
        assert 'image' in item and item['image']

    lr = instagrammer.suck(asserter,'b',{})