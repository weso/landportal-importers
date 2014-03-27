"""
Created on 18/12/2013

@author: Nacho
"""
import logging
import ConfigParser
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

        self._org_id = self.config.get("TRANSLATOR", "org_id")
        self._obs_int = int(self.config.get("TRANSLATOR", "obs_int"))
        self._sli_int = int(self.config.get("TRANSLATOR", "sli_int"))
        self._dat_int = int(self.config.get("TRANSLATOR", "dat_int"))
        self._igr_int = int(self.config.get("TRANSLATOR", "igr_int"))
        self._ind_int = int(self.config.get("TRANSLATOR", "ind_int"))
        self._sou_int = int(self.config.get("TRANSLATOR", "sou_int"))

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
        organization = Organization(chain_for_id=self._org_id,
                                    name="World Bank",
                                    url='http://www.worldbank.org/',
                                    is_part_of=None)
        self.user = User(user_login="worldbank_importer",
                         organization=organization)
        for data_source_name in self.data_sources:
            indicators_section = self.config.get('data_sources', data_source_name)
            requested_indicators = dict(self.config.items(indicators_section))
            data_source = DataSource(chain_for_id=self._org_id,
                                     int_for_id=self._sou_int,
                                     name=data_source_name,
                                     organization=organization)
            self._sou_int += 1  # Updating datasource int id value
            organization.add_data_source(data_source)
            frequency = Dataset.YEARLY
            license_object = License('World Bank License',
                                     'World Bank License',
                                     True,
                                     'www.worldbank.org/terms-of-use-datasets')
            dataset = Dataset(chain_for_id=self._org_id,
                              int_for_id=self._dat_int,
                              frequency=frequency,
                              license_type=license_object,
                              source=data_source)
            self._dat_int += 1  # Updating dataset int id value
            data_source.add_dataset(dataset)
            print data_source_name
            for indicator_element in requested_indicators:
                start = indicator_element.index('(') + 1
                end = indicator_element.index(')')
                measurement_unit = MeasurementUnit(indicator_element[start:end])
                indicator = Indicator(chain_for_id=self._org_id,
                                      int_for_id=self._ind_int,
                                      name_en=indicator_element,
                                      name_es="Desconocido",  # TODO: translate
                                      name_fr="Inconnu",  # TODO: translate
                                      description_en=indicator_element,  # TODO: right now, same as name
                                      description_es="Desconocido",  # TODO: translate
                                      description_fr="Inconnu",  # TODO: translate
                                      dataset=dataset,
                                      measurement_unit=measurement_unit,
                                      topic=Indicator.TOPIC_TEMPORAL)  # TODO: temporal value
                self._ind_int += 1  # Updating indicator id int value
                print '\t' + indicator.name_en
                web_indiccator_id = self.config.get(indicators_section, indicator_element)
                for country in self.countries:
                    slice_object = Slice(chain_for_id=self._org_id,
                                         int_for_id=self._sli_int,
                                         dimension=country,
                                         dataset=dataset,
                                         indicator=indicator)
                    dataset.add_slice(slice_object)  # TESTING EFFECT
                    self._sli_int += 1  # Updating int id slice value
                    print '\t\t' + slice_object.slice_id + '\t' + slice_object.dimension.get_dimension_string()
                    uri = self.observations_url.replace('{ISO2CODE}', country.iso2)
                    uri = uri.replace('{INDICATOR.CODE}', web_indiccator_id)
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
                                    self.logger.warning('Missing value for ' + indicator.name_en + ', ' + country.name +
                                                        ', ' + observation_element['date'])
                                time = YearInterval(observation_element['date'])
                                observation = Observation(chain_for_id=self._org_id,
                                                          int_for_id=self._obs_int,
                                                          ref_time=time,
                                                          issued=Instant(datetime.now()),
                                                          computation=Computation(Computation.RAW),
                                                          value=value_object,
                                                          indicator=indicator,
                                                          dataset=dataset)
                                self._obs_int += 1  # Updating obs int value
                                if historic or observation_element['date'] == requested_year:
                                    country.add_observation(observation)
                                    dataset.add_observation(observation)
                                    slice_object.add_observation(observation)
                                    if observation.value.obs_status is not Value.MISSING:
                                        print '\t\t\t' + observation.ref_time.get_time_string() + '\t' + str(observation.value.value) + ' ' + indicator.measurement_unit.name
                                    else:
                                        print '\t\t\t' + observation.ref_time.get_time_string() + '\tMissing'
                    except (KeyError, ConnectionError, ValueError):
                        self.logger.error('Error retrieving response for \'' + uri + '\'')
                print indicator.name_en + ' FINISHED'