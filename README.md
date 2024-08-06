# starbucks-mugs

Hey so I was looking for a database to save the cups I have collected from Starbucks
and came across this webscraper and website by @andorsk. (_thanks btw_)

Please do feel free to use my edits and update the `owned_mugs.txt` for your own use.
I do have some examples for data handling.

Thank you to starbucks-mugs.com for providing the data and @andorsk for the base code. Uses GoogleAPI for geocoding.
(sorry I stole your README and edited it)

Make sure to check my commit description for more info on what exactly I changed.

Note: I haven't been able to test the frontend due to it requiring the enviorment variable
and I ain't paying money for this.

## Environment Variables

|                         |                                                    |
|-------------------------|----------------------------------------------------|
| **GOOGLE_MAPS_API_KEY** | Set to Google Maps API Key. Required for GeoCoding |

## Usage

1. `python -m pip install -r requirements.txt`: Download reqs
2. `python starbucks-mugs.py update` to update the data.

## Contributing

Want to contribute? Sure! This was a small issue I had and wanted to put my skills to the test. 
Feel free to fork the code. 

## How to create for yourself? 

Just fork this repo and change the `data/owned_mugs.txt`, add set `GOOGLE_MAPS_API_KEY` as a secret in your repo settings, and you should be good to go
