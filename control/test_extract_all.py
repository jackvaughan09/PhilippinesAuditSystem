from unittest import TestCase, main
from extract_all import extract_all
import os
from config import ABBREV_CITY_NAMES

class TestExtractAll(TestCase):
    def setUp(self):
        self.test_data = '../test_data'
        self.unzipped = '../test_data/unzipped'
        self.pdf = '../test_data/pdf'
        self.zipd = '../test_data/zip'
    def test_scrapability(self): # IGACOS causes problem in test of convert.sh
        """ We need all location-year combinations represented in output (convert.sh) """
        """ Issues of lack of output are caused by unconventional formatting """
        # all location-year combos present in /unzipped/
            # if not, then problem in FILENAME_TARGET
        cities_years = {
        'zipd':[filename.replace('-',' ').replace('Annual Audit Report','').replace('.zip','').split('  ') for filename in os.listdir(self.zipd)],
        'pdf':[(filename[2:].split('_'))[0].replace('-','') for filename in os.listdir(self.pdf) if filename.split('.')[1] == 'pdf']
        }
        for ind,fn in enumerate(cities_years['pdf']):
            for key in list(ABBREV_CITY_NAMES.keys()): 
                if key in fn:
                    cities_years['pdf'][ind] = fn.replace(key,ABBREV_CITY_NAMES[key])
        for city_year in cities_years['zipd']:
            self.assertIn((city_year[0]+city_year[1]).replace(' ',''), cities_years['pdf'])
        # all location-year combos present in combined dataframe
            # if not, then problem in TARGET_SENTENCE
        df = extract_all(self.pdf)
        for city_year in cities_years['zipd']:
            self.assertIn((city_year[0]+city_year[1]).replace(' ',''), df['city'].values+df['year'].values)
    def test_overflow_basic(self):
        """ All overflow must be recognized by scraper """
        # overflow will manifest as blank/nonsense headers
        # are there any nonsense headers?

        # are there any blank rows?
    def test_completeness(self):
        """ All of the tables from each document must appear in the combined dataframe """
        # there is no way to test this
        pass
    def test_overflow_lossy(self):
        """ Even correcting for poor formatting, need to keep all info """
        # are there any nonsense headers whose content is entirely lost from the output dataframe?
    def test_headers(self):
        """ Headers must be remapped to match CANON_HEADERS """

if __name__ == '__main__':
    main()
