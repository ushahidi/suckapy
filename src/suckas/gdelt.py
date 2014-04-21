import os
import requests
import zipfile

from datetime import datetime, date, timedelta


definition = {
    'internalID': 'b43be343-fca5-4415-b424-19e21468c33d',
    'sourceType': 'gdelt',
    'language': 'python',
    'frequency': 'repeats',
    'repeatsEvery': 'day',
    'startDate': datetime.now(),
    'endDate': datetime.now()
}


def suck(save_item, handle_error):
    cur_dir = os.path.dirname(os.path.realpath(__file__))
    local_filename = cur_dir + '/data/gdelt/latest-daily.zip'
    d = date.today() - timedelta(days=2)
    d_str = d.strftime("%Y%m%d")
    zip_url = 'http://data.gdeltproject.org/events/' + d_str + '.export.CSV.zip'

    download_file(zip_url, local_filename)

    printed = 0
    import sys
    with zipfile.ZipFile(local_filename, 'r') as z:
        to_open = [name for name in zfile.namelist() if name == d_str + ".export.CSV"]
        if to_open:
            with z.open(to_open[0]) as f:
                for line in f:
                    print line
                    printed = printed + 1
                    if printed > 5:
                        sys.exit()



def download_file(url, local_filename):
    r = requests.get(url, stream=True)
    with open(local_filename, 'w+') as f:
        for chunk in r.iter_content(chunk_size=1024): 
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)
                f.flush()
    return local_filename

