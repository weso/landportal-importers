'''
Created on 18/12/2013

@author: Nacho
'''
import logging
import ConfigParser
import socket
from datetime import datetime

from es.weso.entities.user import User
from es.weso.entities.organization import Organization
from es.weso.entities.data_source import DataSource
from es.weso.entities.dataset import Dataset
from es.weso.entities.license import License
from es.weso.entities.country import Country
from es.weso.entities.observation import Observation
from es.weso.entities.computation import Computation
from es.weso.entities.measurement_unit import MeasurementUnit
from es.weso.entities.indicator import Indicator
from es.weso.entities.value import Value
from es.weso.entities.float_value import FloatValue
from es.weso.entities.year_interval import YearInterval
from es.weso.worldbank.rest.rest_client import RestClient
from es.weso.entities.slice import Slice

from requests.exceptions import ConnectionError

class Parser(object):
    '''
    classdocs
    '''  
    countries = []
    observations = []
    counter = 1


    def __init__(self):
        '''
        Constructor
        '''
        self.logger = logging.getLogger("es.weso.worldbank.parser.parser")    
        self.rest_client = RestClient()
        self.config = ConfigParser.ConfigParser()
        self.config.read('../configuration/api_access.ini')
        self.countries_url = self.config.get('URLs', 'country_list')
        self.observations_url = self.config.get('URLs', 'indicator_pattern')
        self.data_sources = dict(self.config.items('data_sources'))
        
    def extract_countries(self):
        response = self.rest_client.get(self.countries_url, {"format": "json"})
        countries = response[1]
        for country in countries :
            self.logger.info('Extracting country ' + country['iso2Code'] + ' (' + country['name'] + ')')
            self.countries.append(Country(country['name'],
                                          None,
                                          country['iso2Code'],
                                          country['id']))
    
    def extract_observations(self, historic, requested_year):
        organization = Organization("World Bank", 'http://www.worldbank.org/', None)
        ip = socket.gethostbyname(socket.gethostname())
        timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        user = User("worldbank_importer", ip, timestamp, organization)
        for data_source_name in self.data_sources:
            indicators_section = self.config.get('data_sources', data_source_name)
            requested_indicators = dict(self.config.items(indicators_section))
            data_source_id = 'wb_source_' + indicators_section
            data_source = DataSource(data_source_id, data_source_name, organization)
            organization.add_data_source(data_source)
            frequency = 'http://purl.org/linked-data/sdmx/2009/code#freq-A'
            dataset_id = 'wb_dataset_' + indicators_section
            dataset = Dataset(dataset_id, data_source_name, frequency, data_source)
            data_source.add_dataset(dataset)
            license_object = License('World Bank License', 
                                     'World Bank License', 
                                     True, 
                                     'www.worldbank.org/terms-of-use-datasets')
            print data_source_name
            for indicator_element in requested_indicators:
                start = indicator_element.index('(') + 1
                end = indicator_element.index(')')
                measurement_unit = MeasurementUnit(indicator_element[start:end])
                indicator = Indicator(self.config.get(indicators_section, indicator_element), 
                                      indicator_element, 
                                      license_object, 
                                      measurement_unit)
                print '\t' + indicator.name
                for country in self.countries:
                    slice_id = 'sli_' + indicator.name + '_' + country.iso3
                    slice_object = Slice(slice_id, country, dataset, indicator)
                    print '\t\t' + slice_object.slice_id + '\t' + slice_object.dimension.get_dimension_string()
                    uri = self.observations_url.replace('{ISO2CODE}', country.iso2)
                    uri = uri.replace('{INDICATOR.CODE}', indicator.name)
                    try:
                        response = self.rest_client.get(uri, {"format": "json"})
                        observations = response[1]
                        if observations != None :
                            for observation_element in observations :
                                value_object = FloatValue('http://purl.org/linked-data/sdmx/2009/code#obsStatus-A',
                                                          observation_element['value'])
                                if(value_object.value is None):
                                    value_object = Value('http://purl.org/linked-data/sdmx/2009/code#obsStatus-M')
                                time = YearInterval(observation_element['date'],
                                                    observation_element['date'],
                                                    observation_element['date'])
                                observation_id = "obs_" + indicator.name + '_' + country.iso3 + '_' + time.get_time_string()
                                observation = Observation(observation_id,
                                                          time,
                                                          None,
                                                          Computation('http://purl.org/weso/ontology/computex#Raw'),
                                                          value_object,
                                                          indicator,
                                                          data_source)
                                if(historic or observation_element['date'] == requested_year):
                                    country.add_observation(observation)
                                    data_source.add_observation(observation)
                                    slice_object.add_observation(observation)
                                    self.counter += 1
                                    self.logger.info(observation.ref_time.year + ' ' + indicator.name + ' ' + country.iso2)
                                    if(observation.value.obs_status is not 'http://purl.org/linked-data/sdmx/2009/code#obsStatus-M'):
                                        print '\t\t\t' + observation.ref_time.get_time_string() + '\t' + observation.value.get_value() + ' ' + indicator.measurement_unit.name
                                    else:
                                        print '\t\t\t' + observation.ref_time.get_time_string() + '\tMissing (in action)'
                                    self.logger.info('Observation retrieved for ' + indicator.name + 
                                                     ' for country ' + country.iso3 + ' and time ' + time.get_time_string())
                    except (KeyError, ConnectionError, ValueError):
                        self.logger.error('Error retrieving observation ' + indicator.name + 
                                          ' for country ' + country.iso3 + ' and time ' + time.get_time_string())
                print indicator.name + 'FINISHED'