from src.suckas import unhcr
import os

data = {
    "name": "PTP Ref. Camp",
    "country": "Liberia",
    "region": "Grand Gedeh",
    "population": [
        {
            "module_name": [
                {
                    "EN": "Registered Refugee Population"
                },
                {
                    "FR": "Donnes dmographiques concernant la population affecte"
                }
            ],
            "module_type": "Total Population & Demogrpahy",
            "url": "http://data.unhcr.org/liberia/settlement.php?id=30&country=119&region=22",
            "value": "15379",
            "households": "5018",
            "updated_at": "2014-04-30 03:35:08"
        }
    ],
    "latitude": "6.067023000",
    "longitude": "-8.139816000",
    "instance_id": "liberia"
}


def test():
    item = unhcr.transform(data)
    assert 'addressComponents' in item['geo']
    assert item['geo']['addressComponents']['adminArea1'] == data['country']
    assert item['totalAffectedPersons'] == int(data['population'][0]['value'])
    assert item['remoteID'] == unhcr.make_id(data)
