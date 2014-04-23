# coding=utf-8
'''
Created on 02/02/2014

@author: Dani
'''


from lpentities.observation import Observation
from lpentities.indicator import Indicator
from lpentities.license import License
from lpentities.measurement_unit import MeasurementUnit
from lpentities.computation import Computation
from lpentities.instant import Instant
from lpentities.data_source import DataSource
from lpentities.organization import Organization
from lpentities.dataset import Dataset
from lpentities.value import Value
from es.weso.faostat.translator.translator_const import TranslatorConst


from datetime import datetime

from lpentities.year_interval import YearInterval
from reconciler.exceptions.unknown_country_error import UnknownCountryError


class ModelObjectBuilder(object):
    """
    classdocs
    """


    def __init__(self, registers, config, log, reconciler):
        """
        Constructor

        """

        self.log = log
        self._config = config

        self._org_id = self._config.get("TRANSLATOR", "org_id")
        self._obs_int = int(self._config.get("TRANSLATOR", "obs_int"))
        self._sli_int = int(self._config.get("TRANSLATOR", "sli_int"))
        self._dat_int = int(self._config.get("TRANSLATOR", "dat_int"))
        self._igr_int = int(self._config.get("TRANSLATOR", "igr_int"))
        self._ind_int = int(self._config.get("TRANSLATOR", "ind_int"))
        self._sou_int = int(self._config.get("TRANSLATOR", "sou_int"))
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
        # for i in range(1, 2000):
        #     self.build_model_objects_from_register(self.registers[i])
        self._update_config_id_values()
        return self._dataset

    def _update_config_id_values(self):  # TODO. No actualiza el archivo!!

        self._config.set("TRANSLATOR", "org_id", self._org_id)
        self._config.set("TRANSLATOR", "obs_int", self._obs_int)
        self._config.set("TRANSLATOR", "sli_int", self._sli_int)
        self._config.set("TRANSLATOR", "dat_int", self._dat_int)
        self._config.set("TRANSLATOR", "igr_int", self._igr_int)
        self._config.set("TRANSLATOR", "ind_int", self._ind_int)
        self._config.set("TRANSLATOR", "sou_int", self._sou_int)


    def build_dataset(self):
        #Creating dataset object
        print self._org_id
        dataset = Dataset(chain_for_id=self._org_id, int_for_id=self._dat_int, frequency=Dataset.YEARLY)
        self._dat_int += 1  # Updating id value

        #creating related objects
        #Organization
        org = Organization(chain_for_id=self._org_id,
                           name=self._config.get("ORGANIZATION", "name"), # ""
                           url=self._config.get("ORGANIZATION", "url"),  # ""
                           url_logo=self._config.get("ORGANIZATION", "url_logo"))  # ""
        #datasource
        datasource = DataSource(name=self._config.get("SOURCE", "name"),  # "F"
                                chain_for_id=self._org_id,
                                int_for_id=self._sou_int)
        self._sou_int += 1
        #license
        license_type = License(description=self._config.get("LICENSE", "description"),  # ""
                               name=self._config.get("LICENSE", "name"),  # ""
                               republish=self._config.get("LICENSE", "republish"),  #
                               url=self._config.get("LICENSE", "url"))  # ""
        #linking objects
        org.add_data_source(datasource)
        datasource.add_dataset(dataset)
        dataset.license_type = license_type

        #Returning result
        return dataset


    def build_model_objects_from_register(self, register):
        country = self.get_asociated_country(register[TranslatorConst.COUNTRY_CODE])

        new_observation = Observation(chain_for_id=self._org_id, int_for_id=self._obs_int)
        self._obs_int += 1

        self.add_indicator_to_observation(new_observation, register)  # DONE
        self.add_value_to_observation(new_observation, register)  # DONE
        self.add_computation_to_observation(new_observation, register)  # DONE
        self.add_reftime_to_observation(new_observation, register)  # DONE
        self.add_issued_to_observation(new_observation, register)  # DONE


        country.add_observation(new_observation)
        self._dataset.add_observation(new_observation)

    def add_issued_to_observation(self, observation, register):
        #Adding time in which the observation has been treated by us
        observation.issued = Instant(datetime.now())

    def add_reftime_to_observation(self, observation, register):
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

    def add_value_to_observation(self, observation, register):
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


    def _read_config_value(self, section, field):
        return (self._config.get(section, field)).decode(encoding="utf-8")

    def _build_indicators_dict(self):
        result = {}

        #agricultural_land
        agricultural_land_ind = Indicator(chain_for_id=self._org_id, int_for_id=self._ind_int)
        self._ind_int += 1
        agricultural_land_ind.name_en = self._read_config_value("INDICATOR", "agricultural_land_name_en")
        agricultural_land_ind.name_es = self._read_config_value("INDICATOR", "agricultural_land_name_es")
        agricultural_land_ind.name_fr = self._read_config_value("INDICATOR", "agricultural_land_name_fr")
        agricultural_land_ind.description_en = self._read_config_value("INDICATOR", "agricultural_land_desc_en")
        agricultural_land_ind.description_es = self._read_config_value("INDICATOR", "agricultural_land_desc_es")
        agricultural_land_ind.description_fr = self._read_config_value("INDICATOR", "agricultural_land_desc_fr")
        agricultural_land_ind.measurement_unit = MeasurementUnit("1000 Ha")
        agricultural_land_ind.topic = Indicator.TOPIC_TEMPORAL
        agricultural_land_ind.preferable_tendency = Indicator.INCREASE

        result[TranslatorConst.CODE_AGRICULTURAL_LAND] = agricultural_land_ind

        #arable_land
        arable_land_ind = Indicator(chain_for_id=self._org_id, int_for_id=self._ind_int)
        self._ind_int += 1
        arable_land_ind.name_en = self._read_config_value("INDICATOR", "arable_land_name_en")
        arable_land_ind.name_es = self._read_config_value("INDICATOR", "arable_land_name_es")
        arable_land_ind.name_fr = self._read_config_value("INDICATOR", "arable_land_name_fr")
        arable_land_ind.description_en = self._read_config_value("INDICATOR", "arable_land_desc_en")
        arable_land_ind.description_es = self._read_config_value("INDICATOR", "arable_land_desc_es")
        arable_land_ind.description_fr = self._read_config_value("INDICATOR", "arable_land_desc_fr")
        arable_land_ind.measurement_unit = MeasurementUnit("1000 Ha")
        arable_land_ind.topic = Indicator.TOPIC_TEMPORAL
        arable_land_ind.preferable_tendency = Indicator.INCREASE

        result[TranslatorConst.CODE_ARABLE_LAND] = arable_land_ind
        
        #forest_area
        forest_area_ind = Indicator(chain_for_id=self._org_id, int_for_id=self._ind_int)
        self._ind_int += 1
        forest_area_ind.name_en = self._read_config_value("INDICATOR", "forest_area_name_en")
        forest_area_ind.name_es = self._read_config_value("INDICATOR", "forest_area_name_es")
        forest_area_ind.name_fr = self._read_config_value("INDICATOR", "forest_area_name_fr")
        forest_area_ind.description_en = self._read_config_value("INDICATOR", "forest_area_desc_en")
        forest_area_ind.description_es = self._read_config_value("INDICATOR", "forest_area_desc_es")
        forest_area_ind.description_fr = self._read_config_value("INDICATOR", "forest_area_desc_fr")
        forest_area_ind.measurement_unit = MeasurementUnit("1000 Ha")
        forest_area_ind.topic = Indicator.TOPIC_TEMPORAL
        forest_area_ind.preferable_tendency = Indicator.INCREASE

        result[TranslatorConst.CODE_FOREST_LAND] = forest_area_ind
        
        #land_area
        land_area_ind = Indicator(chain_for_id=self._org_id, int_for_id=self._ind_int)
        self._ind_int += 1
        land_area_ind.name_en = self._read_config_value("INDICATOR", "land_area_name_en")
        land_area_ind.name_es = self._read_config_value("INDICATOR", "land_area_name_es")
        land_area_ind.name_fr = self._read_config_value("INDICATOR", "land_area_name_fr")
        land_area_ind.description_en = self._read_config_value("INDICATOR", "land_area_desc_en")
        land_area_ind.description_es = self._read_config_value("INDICATOR", "land_area_desc_es")
        land_area_ind.description_fr = self._read_config_value("INDICATOR", "land_area_desc_fr")
        land_area_ind.measurement_unit = MeasurementUnit("1000 Ha")
        land_area_ind.topic = Indicator.TOPIC_TEMPORAL
        land_area_ind.preferable_tendency = Indicator.INCREASE

        result[TranslatorConst.CODE_LAND_AREA] = land_area_ind

        #relative_agricultural_land
        relative_agricultural_land_ind = Indicator(chain_for_id=self._org_id, int_for_id=self._ind_int)
        self._ind_int += 1
        relative_agricultural_land_ind.name_en = self._read_config_value("INDICATOR", "relative_agricultural_land_name_en")
        relative_agricultural_land_ind.name_es = self._read_config_value("INDICATOR", "relative_agricultural_land_name_es")
        relative_agricultural_land_ind.name_fr = self._read_config_value("INDICATOR", "relative_agricultural_land_name_fr")
        relative_agricultural_land_ind.description_en = self._read_config_value("INDICATOR", "relative_agricultural_land_desc_en")
        relative_agricultural_land_ind.description_es = self._read_config_value("INDICATOR", "relative_agricultural_land_desc_es")
        relative_agricultural_land_ind.description_fr = self._read_config_value("INDICATOR", "relative_agricultural_land_desc_fr")
        relative_agricultural_land_ind.measurement_unit = MeasurementUnit("%")
        relative_agricultural_land_ind.topic = Indicator.TOPIC_TEMPORAL
        relative_agricultural_land_ind.preferable_tendency = Indicator.INCREASE

        result[TranslatorConst.CODE_RELATIVE_AGRICULTURAL_LAND] = relative_agricultural_land_ind

        #relative_arable_land
        relative_arable_land_ind = Indicator(chain_for_id=self._org_id, int_for_id=self._ind_int)
        self._ind_int += 1
        relative_arable_land_ind.name_en = self._read_config_value("INDICATOR", "relative_arable_land_name_en")
        relative_arable_land_ind.name_es = self._read_config_value("INDICATOR", "relative_arable_land_name_es")
        relative_arable_land_ind.name_fr = self._read_config_value("INDICATOR", "relative_arable_land_name_fr")
        relative_arable_land_ind.description_en = self._read_config_value("INDICATOR", "relative_arable_land_desc_en")
        relative_arable_land_ind.description_es = self._read_config_value("INDICATOR", "relative_arable_land_desc_es")
        relative_arable_land_ind.description_fr = self._read_config_value("INDICATOR", "relative_arable_land_desc_fr")
        relative_arable_land_ind.measurement_unit = MeasurementUnit("%")
        relative_arable_land_ind.topic = Indicator.TOPIC_TEMPORAL
        relative_arable_land_ind.preferable_tendency = Indicator.INCREASE

        result[TranslatorConst.CODE_RELATIVE_ARABLE_LAND] = relative_arable_land_ind
        
        #relative_forest_land
        relative_forest_land_ind = Indicator(chain_for_id=self._org_id, int_for_id=self._ind_int)
        self._ind_int += 1
        relative_forest_land_ind.name_en = self._read_config_value("INDICATOR", "relative_forest_land_name_en")
        relative_forest_land_ind.name_es = self._read_config_value("INDICATOR", "relative_forest_land_name_es")
        relative_forest_land_ind.name_fr = self._read_config_value("INDICATOR", "relative_forest_land_name_fr")
        relative_forest_land_ind.description_en = self._read_config_value("INDICATOR", "relative_forest_land_desc_en")
        relative_forest_land_ind.description_es = self._read_config_value("INDICATOR", "relative_forest_land_desc_es")
        relative_forest_land_ind.description_fr = self._read_config_value("INDICATOR", "relative_forest_land_desc_fr")
        relative_forest_land_ind.measurement_unit = MeasurementUnit("%")
        relative_forest_land_ind.topic = Indicator.TOPIC_TEMPORAL
        relative_forest_land_ind.preferable_tendency = Indicator.INCREASE

        result[TranslatorConst.CODE_RELATIVE_FOREST_LAND] = relative_forest_land_ind

        return result

    #The next commented method is obsolete. Descriptions should come from config files

    # def get_indicator_description(self, indicator_code):
    #
    #     if indicator_code == TranslatorConst.CODE_LAND_AREA:
    #         return "Land Area. Total area in sq. km of the referred region"
    #     elif indicator_code == TranslatorConst.CODE_AGRICULTURAL_LAND:
    #         return "Agricultural land. Total area in sq. km. for agriculture of the referred region"
    #     elif indicator_code == TranslatorConst.CODE_FOREST_LAND:
    #         return "Forest land. Total forest surface in sq. km of the referred region"
    #     elif indicator_code == TranslatorConst.CODE_ARABLE_LAND:
    #         return "Arable land. Total arable surface in sq. km. of the referred region"
    #     elif indicator_code == TranslatorConst.CODE_RELATIVE_ARABLE_LAND:
    #         return "Relative arable land. Percentage of arable land from the total land area of the referred region"
    #     elif indicator_code == TranslatorConst.CODE_RELATIVE_FOREST_LAND:
    #         return "Relative forest land. Percentage of forest land from the total land area of the referred region"
    #     elif indicator_code == TranslatorConst.CODE_RELATIVE_AGRICULTURAL_LAND:
    #         return "Arable agricultural land. Percentage of agricultural land from the total land area of the referred region"
    #     else:
    #         raise RuntimeError("Unknown indicator. No description found")


    def get_asociated_country(self, country_code):
        if country_code not in self._country_dict:
            try:
                self._country_dict[country_code] = self.reconciler.get_country_by_faostat_code(country_code)
            except UnknownCountryError:  # Trying to get an invalid country
                self._country_dict[country_code] = None  # By this, unsucessfull searches are executed only one time
                return None  # return None as a signal of "invalid country"
        return self._country_dict[country_code]
        # country_found = None
        # for country in self.country_list:
        #     if country.country_code == country_code:
        #         country_found = country
        #         break
        # if country_found is not None:
        #     return country_found
        # else:
        #     new_country = CountryReconciler.get_country_by_faostat_code()
        #     self.country_list.append(new_country)
        #     return new_country


