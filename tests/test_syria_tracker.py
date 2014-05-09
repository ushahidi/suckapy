from src.suckas import syria_tracker
import os

data = {"incident":{"incidentid":"4969","incidenttitle":"The Death Toll forApril","incidentdescription":"http:\/\/sn4hr.org\/?p=774\n\nSNHR has documented the killing of 1851 civilians by government forces, among them were 363 children (12 children a day), and 194 women at least.The number of victims who died under torture inside the government\u2019s detention centers was 229. (Asaverage, six people die under tortureevery day.)\nThe percentage of women and children victims is 31%; a clear indicator thatgovernment forces is deliberatelytargeting civilians.\nMore .. (http:\/\/sn4hr.org\/?p=774)\nThe Death Toll for April\nhttp:\/\/sn4hr.org\/?p=774\nhttp:\/\/www.sn4hr.orghttp\/\/www.facebook.com\/sn4hr.enghttp:\/\/twitter.com\/sn4hr\n\n============================================================\nCopyright \u00a9  2014 SNHR","incidentdate":"2014-05-03 17:14:00","incidentmode":"3","incidentactive":"1","incidentverified":"1","locationid":"48672","locationname":"Syria","locationlatitude":"34.640186","locationlongitude":"39.049411"},"categories":[{"category":{"id":10,"title":"Aggregate Report (\u062a\u0642\u0631\u064a\u0631 \u0625\u062c\u0645\u0627\u0644\u064a)"}},{"category":{"id":1001,"title":"Summary Report (\u062a\u0642\u0631\u064a\u0631 \u0645\u0644\u062e\u0635)"}},{"category":{"id":3,"title":"Killed (\u0642\u064f\u062a\u0650\u0644)"}}],"media":[{"id":9361,"type":4,"link":"http:\/\/sn4hr.org\/?p=774","thumb":'null'}],"comments":[],"customfields":[]}

def test():
    item = syria_tracker.transform(data)
    assert item['remoteID'] == data['incident']['incidentid']
    assert item['summary'] == data['incident']['incidenttitle']
    assert 'addressComponents' in item['geo']