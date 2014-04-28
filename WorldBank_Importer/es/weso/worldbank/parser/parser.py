"""
Created on 18/12/2013

@author: Nacho
"""
import ConfigParser
from datetime import datetime
import logging

from lpentities.computation import Computation
from lpentities.data_source import DataSource
from lpentities.dataset import Dataset
from lpentities.indicator import Indicator
from lpentities.instant import Instant
from lpentities.license import License
from lpentities.measurement_unit import MeasurementUnit
from lpentities.observation import Observation
from lpentities.organization import Organization
from lpentities.slice import Slice
from lpentities.user import User
from lpentities.value import Value
from lpentities.year_interval import YearInterval
from reconciler.country_reconciler import CountryReconciler
from model2xml.model2xml import ModelToXMLTransformer
from requests.exceptions import ConnectionError

from es.weso.worldbank.rest.rest_client import RestClient


class Parser(object):
    countries = []
    observations = []


    def __init__(self):
        self.logger = logging.getLogger("es.weso.worldbank.parser.parser")
        self.config = ConfigParser.ConfigParser()
        self.config.read('../configuration/api_access.ini')

        self._reconciler = CountryReconciler()

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
        
        self._organization = self._build_default_organization()
        self._user = self._build_default_user()
        self._license = self._build_default_license()
        
    def model_to_xml(self):
        for datasource in self._user.organization.data_sources:
            for dataset in datasource.datasets:
                transformer = ModelToXMLTransformer(dataset, "Request", self._user)
                transformer.run()

    def extract_countries(self):
        response = RestClient.get(self.countries_url, {"format": "json"})
        countries = response[1]
        for country in countries:
            try:
                self.countries.append(self._reconciler.get_country_by_iso2(country['iso2Code']))
            except:
                try:
                    self.countries.append(self._reconciler.get_country_by_en_name(country['name']))
                except:
                    self.logger.warning("No country matches found for iso code" + country['iso2Code'])
                
    def _build_default_organization(self):
        return Organization(chain_for_id=self._org_id,
                            name=self.config.get("ORGANIZATION", "name"),
                            url=self.config.get("ORGANIZATION", "url"),
                            url_logo=self.config.get("ORGANIZATION", "url_logo"),
                            description=self.config.get("ORGANIZATION", "description"))
                                  
    def _build_default_user(self):
        return User(user_login="worldbank_importer",
                         organization=self._organization)
        
    def _build_default_license(self):
        return License(name=self.config.get("LICENSE", "name"),
                       description=self.config.get("LICENSE", "description"),
                       republish=self.config.get("LICENSE", "republish"),
                       url=self.config.get("LICENSE", "url"))
        
    def _build_data_source(self, data_source_name):
        data_source = DataSource(chain_for_id=self._org_id,
                                 int_for_id=self._sou_int,
                                 name=data_source_name,
                                 organization=self._organization)
        self._sou_int += 1 # Updating data sources id value
        return data_source
        
    def _build_data_set(self, data_source):
        frequency = Dataset.YEARLY
        dataset = Dataset(chain_for_id=self._org_id,
                              int_for_id=self._dat_int,
                              frequency=frequency,
                              license_type=self._license,
                              source=data_source)
        self._dat_int += 1  # Updating dataset int id value
        return dataset
    
    def _build_indicator(self, indicator_code, dataset, measurement_unit):
        indicator = Indicator(chain_for_id=self._org_id,
                              int_for_id=self._ind_int,
                              name_en=self.config.get(indicator_code, "name_en").decode(encoding="utf-8"),
                              name_es=self.config.get(indicator_code, "name_es").decode(encoding="utf-8"),
                              name_fr=self.config.get(indicator_code, "name_fr").decode(encoding="utf-8"), 
                              description_en=self.config.get(indicator_code, "desc_en").decode(encoding="utf-8"),
                              description_es=self.config.get(indicator_code, "desc_es").decode(encoding="utf-8"),
                              description_fr=self.config.get(indicator_code, "desc_fr").decode(encoding="utf-8"),
                              dataset=dataset,
                              measurement_unit=measurement_unit,
                              preferable_tendency=self._get_preferable_tendency_of_indicator(self.config.get(indicator_code, "tendency")),
                              topic=Indicator.TOPIC_TEMPORAL)  # TODO: temporal value
        self._ind_int += 1  # Updating indicator id int value
        
        return indicator
    
    def _build_slice(self, country, dataset, indicator):
        slice_object = Slice(chain_for_id=self._org_id,
                      int_for_id=self._sli_int,
                      dimension=country,
                      dataset=dataset,
                      indicator=indicator)
        self._sli_int += 1  # Updating int id slice value
        
        return slice_object
    
    def _build_value(self, indicator, country, date, value_element):
        value_object = Value(value_element,
                             Value.FLOAT,
                             Value.AVAILABLE)
        if value_object.value is None:
            value_object = Value(None,
                                 None,
                                 Value.MISSING)
            self.logger.warning('Missing value for ' + indicator.name_en + ', ' + country.name +
                                                        ', ' + date)
            
        return value_object
    
    def _build_observation(self, indicator, dataset, country, value, date):
        value_object = self._build_value(indicator,
                                         country, 
                                         date,
                                         value)
                                
        time = YearInterval(date)
        observation = Observation(chain_for_id=self._org_id,
                                  int_for_id=self._obs_int,
                                  ref_time=time,
                                  issued=Instant(datetime.now()),
                                  computation=Computation(Computation.RAW),
                                  value=value_object,
                                  indicator=indicator,
                                  dataset=dataset)
        self._obs_int += 1  # Updating obs int value
        
        return observation
    
    def extract_observations(self, historic, requested_year):
        for data_source_name in self.data_sources:
            indicators_section = self.config.get('data_sources', data_source_name)
            requested_indicators = dict(self.config.items(indicators_section))
            
            data_source = self._build_data_source(data_source_name)
            self._organization.add_data_source(data_source)
            dataset = self._build_data_set(data_source)
            data_source.add_dataset(dataset)
            
            #print data_source_name
            for indicator_element in requested_indicators:
                indicator_code = self.config.get(indicators_section, indicator_element)
                start = indicator_element.index('(') + 1
                end = indicator_element.index(')')
                measurement_unit = MeasurementUnit(indicator_element[start:end])
                indicator = self._build_indicator(indicator_code, dataset, measurement_unit)
                
                #print '\t' + indicator.name_en  + "--------------" + indicator.preferable_tendency + "-----------"
                for country in self.countries:
                    slice_object = self._build_slice(country, dataset, indicator)
                    dataset.add_slice(slice_object)  # TESTING EFFECT
                    #print '\t\t' + slice_object.slice_id + '\t' + slice_object.dimension.get_dimension_string()
                    uri = self.observations_url.replace('{ISO2CODE}', country.iso2)
                    uri = uri.replace('{INDICATOR.CODE}', indicator_code)
                    try:
                        response = RestClient.get(uri, {"format": "json"})
                        observations = response[1]
                        if observations is not None:
                            for observation_element in observations:
                                #print observation_element
                                observation = self._build_observation(indicator, 
                                                                      dataset, 
                                                                      country, 
                                                                      observation_element['value'], 
                                                                      observation_element['date'])
                                
                                if historic or observation_element['date'] == requested_year:
                                    country.add_observation(observation)
                                    dataset.add_observation(observation)
                                    slice_object.add_observation(observation)
                                    #if observation.value.obs_status is not Value.MISSING:
                                    #    print '\t\t\t' + observation.ref_time.get_time_string() + '\t' + str(observation.value.value) + ' ' + indicator.measurement_unit.name
                                    #else:
                                    #    print '\t\t\t' + observation.ref_time.get_time_string() + '\tMissing'
                    except (KeyError, ConnectionError, ValueError):
                        self.logger.error('Error retrieving response for \'' + uri + '\'')
                print indicator.name_en + ' FINISHED'

    @staticmethod
    def _get_preferable_tendency_of_indicator(tendency):
        if tendency.lower() == "decrease":
            return Indicator.DECREASE
        else:
            return Indicator.INCREASE
