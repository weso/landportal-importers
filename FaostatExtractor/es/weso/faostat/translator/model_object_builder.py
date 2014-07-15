# coding=utf-8
'''
Created on 02/02/2014

@author: Dani
'''


from datetime import datetime

from lpentities.computation import Computation
from lpentities.data_source import DataSource
from lpentities.dataset import Dataset
from lpentities.indicator import Indicator
from lpentities.instant import Instant
from lpentities.license import License
from lpentities.measurement_unit import MeasurementUnit
from lpentities.observation import Observation
from lpentities.organization import Organization
from lpentities.value import Value
from lpentities.year_interval import YearInterval
from reconciler.exceptions.unknown_country_error import UnknownCountryError

from es.weso.faostat.translator.translator_const import TranslatorConst


class ModelObjectBuilder(object):
    """
    classdocs
    """


    def __init__(self, registers, config, log, reconciler, look_for_historical):
        """
        Constructor

        """

        self.log = log
        self._config = config

        self._org_id = self._config.get("TRANSLATOR", "org_id")

        if not look_for_historical:
            self._last_checked_year = int(self._config.get("HISTORICAL", "first_valid_year"))
            self._obs_int = int(self._config.get("TRANSLATOR", "obs_int"))
            self._sli_int = int(self._config.get("TRANSLATOR", "sli_int"))
            self._dat_int = int(self._config.get("TRANSLATOR", "dat_int"))
            self._igr_int = int(self._config.get("TRANSLATOR", "igr_int"))
        else:
            self._last_checked_year = 1900  # For instance.
            self._obs_int = 0
            self._sli_int = 0
            self._dat_int = 0
            self._igr_int = 0

        self._registers = registers

        self._indicators_dict = self._build_indicators_dict()

        self._country_dict = {}
        self._dataset = self.build_dataset()
        self._computations_dict = {}
        # self.default_computation = Computation(Computation.RAW)

        self.reconciler = reconciler


    def run(self):

        for register in self._registers:
            self.build_model_objects_from_register(register)
        # for i in range(1, 2000):  # Para pruebas
        #     self.build_model_objects_from_register(self.registers[i])
        return self._dataset


    def build_dataset(self):
        #Creating dataset object
        dataset = Dataset(chain_for_id=self._org_id, int_for_id=self._dat_int, frequency=Dataset.YEARLY)
        self._dat_int += 1  # Updating id value

        #creating related objects
        #Organization
        org = Organization(chain_for_id=self._config.get("ORGANIZATION", "chain_for_id"),
                           name=self._config.get("ORGANIZATION", "name"),
                           url=self._config.get("ORGANIZATION", "url"),
                           url_logo=self._config.get("ORGANIZATION", "url_logo"),
                           description_en=self._read_config_value("ORGANIZATION", "description_en"),
                           description_es=self._read_config_value("ORGANIZATION", "description_es"),
                           description_fr=self._read_config_value("ORGANIZATION", "description_fr"))
        #datasource
        datasource = DataSource(name=self._config.get("SOURCE", "name"),
                                chain_for_id=self._org_id,
                                int_for_id=self._config.get("SOURCE", "datasource_id"))
        #license
        license_type = License(description=self._config.get("LICENSE", "description"),
                               name=self._config.get("LICENSE", "name"),
                               republish=self._config.get("LICENSE", "republish"),
                               url=self._config.get("LICENSE", "url"))
        #linking objects
        org.add_data_source(datasource)
        datasource.add_dataset(dataset)
        dataset.license_type = license_type

        #Returning result
        return dataset

    def _read_config_value(self, section, field):
        return (self._config.get(section, field)).decode(encoding="utf-8")

    def build_model_objects_from_register(self, register):
        country = self.get_asociated_country(register[TranslatorConst.COUNTRY_CODE])

        new_observation = Observation(chain_for_id=self._org_id, int_for_id=self._obs_int)
        self._obs_int += 1

        self.add_indicator_to_observation(new_observation, register)  # DONE
        self.add_value_to_observation(new_observation, register)  # DONE
        self.add_computation_to_observation(new_observation, register)  # DONE
        self.add_reftime_to_observation(new_observation, register)  # DONE
        self.add_issued_to_observation(new_observation)  # DONE


        country.add_observation(new_observation)
        self._dataset.add_observation(new_observation)

        self._actualize_last_checked_date_if_needed(new_observation)


    def _actualize_last_checked_date_if_needed(self, new_observation):
        if new_observation.ref_time.year > self._last_checked_year:
            self._last_checked_year = new_observation.ref_time.year

    @staticmethod
    def add_issued_to_observation(observation):
        #Adding time in which the observation has been treated by us
        observation.issued = Instant(datetime.now())

    @staticmethod
    def add_reftime_to_observation(observation, register):
        observation.ref_time = YearInterval(year=register[TranslatorConst.YEAR])

    def add_computation_to_observation(self, observation, register):
        """
        In this method we are using an internal dictionary that could be avoided. We are doing this because
        it is expected that most of the received values for observations will be identical. So, if we store
        an object that represents a concrete string value, we don´t have to create plenty of Computation
        objects with the same internal properties. We are saving memory without introducing too much
        execution time (probably we also reduce it)

        """
        computation_text = register[TranslatorConst.COMPUTATION_PROCESS]
        if not computation_text in self._computations_dict:
            self._computations_dict[computation_text] = Computation(uri=computation_text)
        observation.computation = self._computations_dict[computation_text]

    @staticmethod
    def add_value_to_observation(observation, register):
        value = Value()
        value.value_type = "float"
        if register[TranslatorConst.VALUE] is None or register[TranslatorConst.VALUE] == "":
            value.obs_status = Value.MISSING
        else:
            value.obs_status = Value.AVAILABLE
            value.value = register[TranslatorConst.VALUE]

        observation.value = value


    def add_indicator_to_observation(self, observation, register):

        indicator = self._indicators_dict[register[TranslatorConst.ITEM_CODE]]
        observation.indicator = indicator


    @staticmethod
    def _parse_preferable_tendency(tendency):
        if tendency.lower() == "increase":
            return Indicator.INCREASE
        elif tendency.lower() == "decrease":
            return Indicator.DECREASE
        return Indicator.IRRELEVANT
    
    def _build_indicators_dict(self):
        result = {}

        #agricultural_land
        agricultural_land_ind = Indicator(chain_for_id=self._org_id, 
                                          int_for_id=int(self._read_config_value("INDICATOR", "agricultural_land_id")))
        agricultural_land_ind.name_en = self._read_config_value("INDICATOR", "agricultural_land_name_en")
        agricultural_land_ind.name_es = self._read_config_value("INDICATOR", "agricultural_land_name_es")
        agricultural_land_ind.name_fr = self._read_config_value("INDICATOR", "agricultural_land_name_fr")
        agricultural_land_ind.description_en = self._read_config_value("INDICATOR", "agricultural_land_desc_en")
        agricultural_land_ind.description_es = self._read_config_value("INDICATOR", "agricultural_land_desc_es")
        agricultural_land_ind.description_fr = self._read_config_value("INDICATOR", "agricultural_land_desc_fr")
        agricultural_land_ind.measurement_unit = MeasurementUnit(name = self._read_config_value("INDICATOR", "agricultural_land_unit_name"),
                                                            convert_to = self._read_config_value("INDICATOR", "agricultural_land_unit_type"),
                                                            factor = float(self._read_config_value("INDICATOR", "agricultural_land_unit_factor")))
        agricultural_land_ind.topic = self._read_config_value("INDICATOR", "agricultural_land_topic")
        agricultural_land_ind.preferable_tendency = self._parse_preferable_tendency(self._read_config_value("INDICATOR", "agricultural_land_tendency"))

        result[TranslatorConst.CODE_AGRICULTURAL_LAND] = agricultural_land_ind

        #arable_land
        arable_land_ind = Indicator(chain_for_id=self._org_id, 
                                    int_for_id=int(self._read_config_value("INDICATOR", "arable_land_id")))
        arable_land_ind.name_en = self._read_config_value("INDICATOR", "arable_land_name_en")
        arable_land_ind.name_es = self._read_config_value("INDICATOR", "arable_land_name_es")
        arable_land_ind.name_fr = self._read_config_value("INDICATOR", "arable_land_name_fr")
        arable_land_ind.description_en = self._read_config_value("INDICATOR", "arable_land_desc_en")
        arable_land_ind.description_es = self._read_config_value("INDICATOR", "arable_land_desc_es")
        arable_land_ind.description_fr = self._read_config_value("INDICATOR", "arable_land_desc_fr")
        arable_land_ind.measurement_unit = MeasurementUnit(name=self._read_config_value("INDICATOR", "arable_land_unit_name"),
                                                            convert_to = self._read_config_value("INDICATOR", "arable_land_unit_type"),
                                                            factor = float(self._read_config_value("INDICATOR", "arable_land_unit_factor")))
        arable_land_ind.topic = self._read_config_value("INDICATOR", "arable_land_topic")
        arable_land_ind.preferable_tendency = self._parse_preferable_tendency(self._read_config_value("INDICATOR", "arable_land_tendency"))

        result[TranslatorConst.CODE_ARABLE_LAND] = arable_land_ind
        
        #forest_area
        forest_area_ind = Indicator(chain_for_id=self._org_id, 
                                    int_for_id=int(self._read_config_value("INDICATOR", "forest_area_id")))
        forest_area_ind.name_en = self._read_config_value("INDICATOR", "forest_area_name_en")
        forest_area_ind.name_es = self._read_config_value("INDICATOR", "forest_area_name_es")
        forest_area_ind.name_fr = self._read_config_value("INDICATOR", "forest_area_name_fr")
        forest_area_ind.description_en = self._read_config_value("INDICATOR", "forest_area_desc_en")
        forest_area_ind.description_es = self._read_config_value("INDICATOR", "forest_area_desc_es")
        forest_area_ind.description_fr = self._read_config_value("INDICATOR", "forest_area_desc_fr")
        forest_area_ind.measurement_unit = MeasurementUnit(name = self._read_config_value("INDICATOR", "forest_area_unit_name"),
                                                            convert_to = self._read_config_value("INDICATOR", "forest_area_unit_type"),
                                                            factor = float(self._read_config_value("INDICATOR", "forest_area_unit_factor")))
        forest_area_ind.topic = self._read_config_value("INDICATOR", "forest_area_topic")
        forest_area_ind.preferable_tendency = self._parse_preferable_tendency(self._read_config_value("INDICATOR", "forest_area_tendency"))

        result[TranslatorConst.CODE_FOREST_LAND] = forest_area_ind
        
        #land_area
        land_area_ind = Indicator(chain_for_id=self._org_id, 
                                  int_for_id=int(self._read_config_value("INDICATOR", "land_area_id")))
        land_area_ind.name_en = self._read_config_value("INDICATOR", "land_area_name_en")
        land_area_ind.name_es = self._read_config_value("INDICATOR", "land_area_name_es")
        land_area_ind.name_fr = self._read_config_value("INDICATOR", "land_area_name_fr")
        land_area_ind.description_en = self._read_config_value("INDICATOR", "land_area_desc_en")
        land_area_ind.description_es = self._read_config_value("INDICATOR", "land_area_desc_es")
        land_area_ind.description_fr = self._read_config_value("INDICATOR", "land_area_desc_fr")
        land_area_ind.measurement_unit = MeasurementUnit(name = self._read_config_value("INDICATOR", "land_area_unit_name"),
                                                            convert_to = self._read_config_value("INDICATOR", "land_area_unit_type"),
                                                            factor = float(self._read_config_value("INDICATOR", "land_area_unit_factor")))
        land_area_ind.topic = self._read_config_value("INDICATOR", "land_area_topic")
        land_area_ind.preferable_tendency = self._parse_preferable_tendency(self._read_config_value("INDICATOR", "land_area_tendency"))

        result[TranslatorConst.CODE_LAND_AREA] = land_area_ind

        #relative_agricultural_land
        relative_agricultural_land_ind = Indicator(chain_for_id=self._org_id, 
                                                   int_for_id=int(self._read_config_value("INDICATOR", "relative_agricultural_land_id")))
        relative_agricultural_land_ind.name_en = self._read_config_value("INDICATOR", "relative_agricultural_land_name_en")
        relative_agricultural_land_ind.name_es = self._read_config_value("INDICATOR", "relative_agricultural_land_name_es")
        relative_agricultural_land_ind.name_fr = self._read_config_value("INDICATOR", "relative_agricultural_land_name_fr")
        relative_agricultural_land_ind.description_en = self._read_config_value("INDICATOR", "relative_agricultural_land_desc_en")
        relative_agricultural_land_ind.description_es = self._read_config_value("INDICATOR", "relative_agricultural_land_desc_es")
        relative_agricultural_land_ind.description_fr = self._read_config_value("INDICATOR", "relative_agricultural_land_desc_fr")
        relative_agricultural_land_ind.measurement_unit = MeasurementUnit(name = self._read_config_value("INDICATOR", "relative_agricultural_land_unit_name"),
                                                            convert_to = self._read_config_value("INDICATOR", "relative_agricultural_land_unit_type"))
        relative_agricultural_land_ind.topic = self._read_config_value("INDICATOR", "relative_agricultural_land_topic")
        relative_agricultural_land_ind.preferable_tendency = self._parse_preferable_tendency(self._read_config_value("INDICATOR", "relative_agricultural_land_tendency"))

        result[TranslatorConst.CODE_RELATIVE_AGRICULTURAL_LAND] = relative_agricultural_land_ind

        #relative_arable_land
        relative_arable_land_ind = Indicator(chain_for_id=self._org_id, 
                                             int_for_id= int(self._read_config_value("INDICATOR", "relative_arable_land_id")))
        relative_arable_land_ind.name_en = self._read_config_value("INDICATOR", "relative_arable_land_name_en")
        relative_arable_land_ind.name_es = self._read_config_value("INDICATOR", "relative_arable_land_name_es")
        relative_arable_land_ind.name_fr = self._read_config_value("INDICATOR", "relative_arable_land_name_fr")
        relative_arable_land_ind.description_en = self._read_config_value("INDICATOR", "relative_arable_land_desc_en")
        relative_arable_land_ind.description_es = self._read_config_value("INDICATOR", "relative_arable_land_desc_es")
        relative_arable_land_ind.description_fr = self._read_config_value("INDICATOR", "relative_arable_land_desc_fr")
        relative_arable_land_ind.measurement_unit = MeasurementUnit(name = self._read_config_value("INDICATOR", "relative_arable_land_unit_name"),
                                                            convert_to = self._read_config_value("INDICATOR", "relative_arable_land_unit_type"))
        relative_arable_land_ind.topic = self._read_config_value("INDICATOR", "relative_arable_land_topic")
        relative_arable_land_ind.preferable_tendency = self._parse_preferable_tendency(self._read_config_value("INDICATOR", "relative_arable_land_tendency"))

        result[TranslatorConst.CODE_RELATIVE_ARABLE_LAND] = relative_arable_land_ind
        
        #relative_forest_land
        relative_forest_land_ind = Indicator(chain_for_id=self._org_id, 
                                             int_for_id=int(self._read_config_value("INDICATOR", "relative_forest_land_id")))
        relative_forest_land_ind.name_en = self._read_config_value("INDICATOR", "relative_forest_land_name_en")
        relative_forest_land_ind.name_es = self._read_config_value("INDICATOR", "relative_forest_land_name_es")
        relative_forest_land_ind.name_fr = self._read_config_value("INDICATOR", "relative_forest_land_name_fr")
        relative_forest_land_ind.description_en = self._read_config_value("INDICATOR", "relative_forest_land_desc_en")
        relative_forest_land_ind.description_es = self._read_config_value("INDICATOR", "relative_forest_land_desc_es")
        relative_forest_land_ind.description_fr = self._read_config_value("INDICATOR", "relative_forest_land_desc_fr")
        relative_forest_land_ind.measurement_unit = MeasurementUnit(name = self._read_config_value("INDICATOR", "relative_forest_land_unit_name"),
                                                            convert_to = self._read_config_value("INDICATOR", "relative_forest_land_unit_type"))
        relative_forest_land_ind.topic = self._read_config_value("INDICATOR", "relative_forest_land_topic")
        relative_forest_land_ind.preferable_tendency = self._parse_preferable_tendency(self._read_config_value("INDICATOR", "relative_forest_land_tendency"))

        result[TranslatorConst.CODE_RELATIVE_FOREST_LAND] = relative_forest_land_ind

        return result


    def get_asociated_country(self, country_code):
        if country_code not in self._country_dict:
            try:
                self._country_dict[country_code] = self.reconciler.get_country_by_faostat_code(country_code)
            except UnknownCountryError:  # Trying to get an invalid country
                self._country_dict[country_code] = None  # By this, unsucessfull searches are executed only one time
                return None  # return None as a signal of "invalid country"
        return self._country_dict[country_code]