**Note: *This is the Python port of [sucka](https://github.com/ushahidi/sucka).

# Sucka

#### Sucking in the world's crisis data. Byte by byte. 

Sucka can retrieve information from any source and transform that data to the structure used through the CrisisNET system. One crisis API to rule them all. 

Each source has a corresponding `sucka` module that understands where the third-party data is, how to get it, and how that data is structured. This third-party source could be a public API (like Twitter), or a more "static" dataset, like a CSV of incident reports created by an NGO. 

## Writing your own sucka

### For Experienced Python Devs

*1. Clone this repo and install dependencies from `requirements.txt`

    $ git clone https://github.com/ushahidi/suckapy.git
    $ pip install -r requirements.txt

*2. Create a module in the `suckas` package. 
    
    $ cd src/suckas && touch my_awesome_sucka.py

In `my_awesome_sucka.py` Define a `suck` function that accepts two arguments

    def suck(save_item, handle_error):
        # raw_data = retrieve data from API, file, whatever
        # item = transform data to a dict formatted like an Item
        # save_item(item)

So first you get data (like from an API, or CSV file), then you transform each row/record/etc from the data you retrieve into an `Item` (which is the structure used throughout CrisisNET to respresent anything with a time or place -- like an attack, or a tornado sighting, or the location of an open pharmacy. [Here's how an Item should be structured](https://github.com/ushahidi/suckapy/blob/master/src/cn_store_py/models.py)). Once you have an Item, you pass it to the `save_item` function. 

*3. Add a `definition` property that tells the system how often this `sucka` should be run.
    
    definition = {
        'internalID': 'b43be343-fca5-4415-b424-19e21468c33d',
        'sourceType': 'gdelt',
        'language': 'python',
        'frequency': 'repeats',
        'repeatsEvery': 'day',
        'startDate': datetime.strptime('20140420', "%Y%m%d"),
        'endDate': datetime.now() + timedelta(days=365)
    }

Note that `internalID` needs to be unique, so we recommend generating a uuid. 

    import uuid
    uuid.uuid4()

*4. Add a test to the `test` directory like `test_yourmodule.py` to verify that your `sucka` successfully and reliably creates `Item` documents.

*5. Create a new branch for your feature and make a pull request

Contact us if you have any questions. 
