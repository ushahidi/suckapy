import os
from bs4 import BeautifulSoup
import csv
cur_dir = os.path.dirname(os.path.realpath(__file__))


links_file = cur_dir + '/terrorism-pages-links.txt'

with open(cur_dir + '/facebook_pages.csv', 'w') as f:
    writer = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
    writer.writerow(["id","name","lastBackup","url"])
    for line in open(links_file):
        links = line.split(',')
        for link in links:
            els = BeautifulSoup(link)
            for el in els:
                try:
                    href = el.get('href')
                    if href:
                        #print href
                        pieces = href.split('/')
                        if 'pages' in href:
                            page_id = pieces[4]
                        else:
                            page_id = pieces[3]

                        #print el.get_text()
                        data = [
                            page_id,
                            '"'+el.get_text()+'"',
                            "2014-06-18T16:01:59Z",
                            page_id
                        ]
                        print ",".join(data)
                        #writer.writerow(data)
                except:
                    pass
