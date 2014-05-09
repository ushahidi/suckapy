from src.suckas import youtube_syria

data = {
    u'snippet': {
        u'thumbnails': {
            u'default': {
                u'url': u'https: //i.ytimg.com/vi/9XYv7YRlXyQ/default.jpg'
            },
            u'high': {
                u'url': u'https: //i.ytimg.com/vi/9XYv7YRlXyQ/hqdefault.jpg'
            },
            u'medium': {
                u'url': u'https: //i.ytimg.com/vi/9XYv7YRlXyQ/mqdefault.jpg'
            }
        },
        u'title': u'\u0634\u0627\u0628\u0641\u064a\u0631\u064a\u0641\u0625\u062f\u0644\u0628\u064a\u0648\u062c\u0647\u0631\u0633\u0627\u0644\u0629\u0642\u0648\u064a\u0629\u0644\u0644\u0639\u0627\u0644\u0645\u0628\u0645\u0646\u0627\u0633\u0628\u0629\u0630\u0643\u0631\u0649\u0627\u0646\u0637\u0644\u0627\u0642\u0627\u0644\u062b\u0648\u0631\u0629',
        u'channelId': u'UC-LfCp5I_UdLlGLjO8BHhaQ',
        u'publishedAt': u'2014-03-18T16: 33: 21.000Z',
        u'liveBroadcastContent': u'none',
        u'channelTitle': u'',
        u'description': u'\u0634\u0627\u0628\u0645\u0646\u0645\u0639\u0631\u0629\u0627\u0644\u0646\u0639\u0645\u0627\u0646\u0641\u064a\u0631\u064a\u0641\u0625\u062f\u0644\u0628\u064a\u0648\u062c\u0647\u0631\u0633\u0627\u0626\u0644\u0646\u0642\u062f\u064a\u0629\u0633\u0627\u062e\u0631\u0629\u0644\u0644\u062f\u0648\u0644\u0627\u0644\u0639\u0631\u0628\u064a\u0629\u0648\u0627\u0644\u0645\u062c\u062a\u0645\u0639\u0627\u0644\u062f\u0648\u0644\u064a\u0628\u0645\u0646\u0627\u0633\u0628\u0629\u0627\u0644\u0630\u0643\u0631\u0649\u0627\u0644\u0633\u0646\u0648\u064a\u0629\u0627\u0644\u062b\u0627\u0644\u062b\u0629\u0644\u0627\u0646\u0637\u0644\u0627\u0642\u0629\u0627\u0644\u062b\u0648\u0631\u0629\u0627\u0644\u0633\u0648\u0631\u064a\u0629.'
    },
    u'kind': u'youtube#searchResult',
    u'etag': u'"ePFRUfYBkeQ2ncpP9OLHKB0fDw4/B5bEsGLFDeC73NWaX7jUrMzFTis"',
    u'id': {
        u'kind': u'youtube#video',
        u'videoId': u'9XYv7YRlXyQ'
    }
}


def test():
    item = youtube_syria.transform(data)
    assert item['remoteID'] == data['id']['videoId']
    assert item['summary'] == data['snippet']['title']
    assert 'addressComponents' in item['geo']
    assert item['image'] == data['snippet']['thumbnails']['high']['url'].replace(' ','')