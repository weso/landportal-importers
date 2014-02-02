'''
Created on 18/12/2013

@author: Nacho
'''
import logging
import ConfigParser

from es.weso.entities.country import Country
from es.weso.entities.observation import Observation
from es.weso.worldbank.rest.rest_client import RestClient
from requests.exceptions import ConnectionError

class Parser(object):
    '''
    classdocs
    '''
    
    countries = []
    observations = []

    def __init__(self):
        '''
        Constructor
        '''
        self.logger = logging.getLogger("es.weso.worldbank.parser.parser")    
        self.rest_client = RestClient()
        self.config = ConfigParser.ConfigParser()
        self.config.read('../configuration/configuration.ini')
        self.countries_url = self.config.get('URLs', 'country_list')
        self.observations_url = self.config.get('URLs', 'indicator_pattern')
        self.indicator_names = dict(self.config.items('indicator_codes'))
        
    
    def extract_countries(self):
        self.logger.info("Extracting countries")
        response = self.rest_client.get(self.countries_url, {"format": "json"})
        countries = response[1]
        for country in countries :
            self.countries.append(Country(country['name'],
                                          country['name'], 
                                          None,
                                          country['iso2Code'], 
                                          country['id']))
    
    def extract_observations(self):
        self.logger.info("Extracting observations")
        for country in self.countries :
            for indicator_name in self.indicator_names:
                indicator_code = self.config.get('indicator_codes', indicator_name)
                uri = self.observations_url.replace('{ISO2CODE}', country.iso2)
                uri = uri.replace('{INDICATOR.CODE}', indicator_code)
                try:
                    response = self.rest_client.get(uri, {"format": "json"})
                    observations = response[1]
                    if observations != None :
                        for observation in observations :
                            country.add_observation(Observation(observation['date'],
                                                                observation['indicator'],
                                                                observation['value']))
                except (KeyError, ConnectionError):
                    self.logger.error("Error retrieving indicator " + indicator_code +
                                      " for country " + country.iso2)
                    pass
            for observation in country.has_observation:
                if(observation.value is not None):
                    print country.iso2 + ' ' + observation.year + ' ' + observation.value