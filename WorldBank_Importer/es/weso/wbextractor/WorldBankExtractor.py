'''
Created on 18/12/2013

@author: Nacho
'''
import logging

from es.weso.wbextractor.entities import Indicator, Country, Observation
from es.weso.wbextractor.rest import RestClient
from requests.exceptions import ConnectionError

class WorldBankExtractor(object):
    '''
    classdocs
    '''
    
    rest_client = RestClient.RestClient("http://api.worldbank.org/v2/")
    logger = logging.getLogger("es.weso.wbextractor.WorldBankExtractor")
    indicators = []
    countries = []
    observations = []

    def __init__(self):
        '''
        Constructor
        '''        
        
    def extract_topic(self):
        self.logger.info("Extracting topics")
        #Actually topic's URL is hard-coded. It's better extract it
        #from property file
        response = self.rest_client.get("topics", {"format": "json"})
        wanted_topic = "Agriculture & Rural Development"
        topics = response[1]
        for topic in topics :
            if topic['value'] == wanted_topic :
                return topic['id']
        return None
    
    def extract_indicators_by_topic(self, topic_id):
        self.logger.info("Extracting indicators by topic with id " + topic_id)
        response = self.rest_client.get("topics/" + topic_id + "/indicators", 
                                        {"format": "json"})
        indicators = response[1]
        for indicator in indicators :
            self.indicators.append(Indicator.Indicator(indicator['id'], 
                                                       indicator['name'], 
                                                       indicator['sourceNote'],
                                                       indicator['sourceOrganization']))
    
    def extract_countries(self):
        self.logger.info("Extracting countries")
        response = self.rest_client.get("countries", {"format": "json"})
        countries = response[1]
        for country in countries :
            self.countries.append(Country.Country(country['name'], 
                                                  country['iso2Code'], 
                                                  country['id']))
    
    def extract_observations(self):
        self.logger.info("Extracting observations")
        for country in self.countries :
            for indicator in self.indicators :
                relative_uri = "countries/" + country.iso2 + "/indicators/" + indicator.indicator_id
                
                try:
                    response = self.rest_client.get(relative_uri, 
                                                {"format": "json"})
                    observations = response[1]
                    if observations != None :
                        for observation in observations :
                            self.observations.append(Observation.Observation(observation['date'],
                                                                             indicator,
                                                                             observation['value'],
                                                                             country))
                except (KeyError, ConnectionError):
                    self.logger.error("Error retrieving indicator " + indicator.indicator_id +
                                      " for country " + country.iso2)
                    pass 