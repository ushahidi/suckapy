from src.suckas import who_ebola
import os


def test():
    def asserter(item):
        assert 'remoteID' in item and item['remoteID']
        assert 'content' in item and item['content']
        assert 'fromURL' in item and item['fromURL']

    lr = who_ebola.suck(asserter,'b',{})