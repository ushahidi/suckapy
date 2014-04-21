**Note: *This is the Python port of [sucka](https://github.com/ushahidi/sucka).

# Sucka

#### Sucking in the world's crisis data. Byte by byte. 

Sucka can retrieve information from any source and transform that data to the structure used through the CrisisNET system. One crisis API to rule them all. 

Each source has a corresponding `sucka` module that understands where the third-party data is, how to get it, and how that data is structured. This third-party source could be a public API (like Twitter), or a more "static" dataset, like a CSV of incident reports created by an NGO. 

## Writing your own sucka

### For Experienced Python Devs

**1. Clone this repo and install dependencies from `requirements.txt`

**2. Create a module in the `suckas` package and define a `suck` function that accepts two arguments

    def suck(save_item, handle_error):
        # raw_data = retrieve data from API, file, whatever
        # item = transform data to a dict formatted like an Item
        # save_item(item)

**3. Add a `definition` property that tells the system how often this `sucka` should be run.
    
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

**4. Add a test to the `test` directory like `test_yourmodule.py`
**5. Create a new branch for your feature and make a pull request

See `src/modules/cn-store-py/models.py` to understand the structure of an `Item` document.

More detailed instructions coming soon.