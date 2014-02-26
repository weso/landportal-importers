"""
Created on 18/12/2013

@author: Nacho
"""
import logging
import ConfigParser
import socket
from datetime import datetime

from lpentities.user import User
from lpentities.organization import Organization
from lpentities.data_source import DataSource
from lpentities.dataset import Dataset
from lpentities.license import License
from lpentities.country import Country
from lpentities.observation import Observation
from lpentities.computation import Computation
from lpentities.measurement_unit import MeasurementUnit
from lpentities.indicator import Indicator
from lpentities.value import Value
from lpentities.year_interval import YearInterval
from es.weso.worldbank.rest.rest_client import RestClient
from lpentities.slice import Slice
from lpentities.instant import Instant
from model2xml.model2xml import ModelToXMLTransformer

from requests.exceptions import ConnectionError


class Parser(object):
    countries = []
    observations = []


    def __init__(self):
        self.logger = logging.getLogger("es.weso.worldbank.parser.parser")
        self.config = ConfigParser.ConfigParser()
        self.config.read('../configuration/api_access.ini')
        self.countries_url = self.config.get('URLs', 'country_list')
        self.observations_url = self.config.get('URLs', 'indicator_pattern')
        self.data_sources = dict(self.config.items('data_sources'))
        self.user = None

    def model_to_xml(self):
        for datasource in self.user.organization.data_sources:
            for dataset in datasource.datasets:
                transformer = ModelToXMLTransformer(dataset, "Request", self.user)
                transformer.run()


    def extract_countries(self):
        response = RestClient.get(self.countries_url, {"format": "json"})
        countries = response[1]
        for country in countries:
            self.countries.append(Country(country['name'],
                                          None,
                                          country['iso2Code'],
                                          country['id']))

    def extract_observations(self, historic, requested_year):
        organization = Organization("World Bank", 'http://www.worldbank.org/', None)
        ip = socket.gethostbyname(socket.gethostname())
        timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        self.user = User("worldbank_importer", ip, timestamp, organization)
        for data_source_name in self.data_sources:
            indicators_section = self.config.get('data_sources', data_source_name)
            requested_indicators = dict(self.config.items(indicators_section))
            data_source_id = 'wb_source_' + indicators_section
            data_source = DataSource(data_source_id, data_source_name, organization)
            organization.add_data_source(data_source)
            frequency = 'http://purl.org/linked-data/sdmx/2009/code#freq-A'
            dataset_id = 'wb_dataset_' + indicators_section
            license_object = License('World Bank License',
                                     'World Bank License',
                                     True,
                                     'www.worldbank.org/terms-of-use-datasets')
            dataset = Dataset(dataset_id, data_source_name, frequency, license_object, data_source)
            data_source.add_dataset(dataset)
            print data_source_name
            for indicator_element in requested_indicators:
                start = indicator_element.index('(') + 1
                end = indicator_element.index(')')
                measurement_unit = MeasurementUnit(indicator_element[start:end])
                indicator = Indicator(self.config.get(indicators_section, indicator_element),
                                      indicator_element,
                                      indicator_element,
                                      license_object,
                                      measurement_unit)
                print '\t' + indicator.name
                for country in self.countries:
                    slice_id = 'sli_' + indicator.indicator_id + '_' + country.iso3
                    slice_object = Slice(slice_id, country, dataset, indicator)
                    print '\t\t' + slice_object.slice_id + '\t' + slice_object.dimension.get_dimension_string()
                    uri = self.observations_url.replace('{ISO2CODE}', country.iso2)
                    uri = uri.replace('{INDICATOR.CODE}', indicator.indicator_id)
                    try:
                        response = RestClient.get(uri, {"format": "json"})
                        observations = response[1]
                        if observations is not None:
                            for observation_element in observations:
                                value_object = Value(observation_element['value'],
                                                     "float",
                                                     Value.AVAILABLE)
                                if value_object.value is None:
                                    value_object = Value(None,
                                                         None,
                                                         Value.MISSING)
                                    self.logger.warning('Missing value for ' + indicator.name + ', ' + country.name +
                                                        ', ' + observation_element['date'])
                                time = YearInterval(observation_element['date'],
                                                    observation_element['date'],
                                                    observation_element['date'])
                                observation_id = "obs_" + indicator.name + '_' + country.iso3 + '_' + time.get_time_string()
                                observation = Observation(observation_id,
                                                          time,
                                                          Instant(datetime.now()),
                                                          Computation(Computation.RAW),
                                                          value_object,
                                                          indicator,
                                                          data_source)
                                if historic or observation_element['date'] == requested_year:
                                    country.add_observation(observation)
                                    dataset.add_observation(observation)
                                    slice_object.add_observation(observation)
                                    if observation.value.obs_status is not Value.MISSING:
                                        print '\t\t\t' + observation.ref_time.get_time_string() + '\t' + observation.value.value + ' ' + indicator.measurement_unit.name
                                    else:
                                        print '\t\t\t' + observation.ref_time.get_time_string() + '\tMissing'
                    except (KeyError, ConnectionError, ValueError):
                        self.logger.error('Error retrieving response for \'' + uri + '\'')
                print indicator.name + ' FINISHED'