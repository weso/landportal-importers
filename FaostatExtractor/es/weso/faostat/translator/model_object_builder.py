# coding=utf-8
'''
Created on 02/02/2014

@author: Dani
'''


from lpentities.observation import Observation
from lpentities.country import Country
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
from reconciler.country_reconciler import CountryReconciler


from datetime import datetime

from lpentities.year_interval import YearInterval
from reconciler.exceptions.unknown_country_error import UnknownCountryError


class ModelObjectBuilder(object):
    '''
    classdocs
    '''


    def __init__(self, registers, config, log):
        """
        Constructor

        """

        self.log = log
        self.config = config

        self._org_id = self.config.get("TRANSLATOR", "org_id")
        self._obs_int = int(self.config.get("TRANSLATOR", "obs_int"))
        self._sli_int = int(self.config.get("TRANSLATOR", "sli_int"))
        self._dat_int = int(self.config.get("TRANSLATOR", "dat_int"))
        self._igr_int = int(self.config.get("TRANSLATOR", "igr_int"))
        self._ind_int = int(self.config.get("TRANSLATOR", "ind_int"))
        self._sou_int = int(self.config.get("TRANSLATOR", "sou_int"))
        self.registers = registers

        self.country_dict = {}
        self.dataset = self.build_dataset()
        self.indicators_dict = {}
        self.default_computation = Computation(Computation.RAW)

        self.reconciler = CountryReconciler()


    def run(self):


        # for register in self.registers:
        #     self.build_model_objects_from_register(register)
        for i in range(1, 2000):
            self.build_model_objects_from_register(self.registers[i])
        self._update_config_id_values()
        return self.dataset

    def _update_config_id_values(self):  # TODO. No actualiza el archivo!!

        self.config.set("TRANSLATOR", "org_id", self._org_id)
        self.config.set("TRANSLATOR", "obs_int", self._obs_int)
        self.config.set("TRANSLATOR", "sli_int", self._sli_int)
        self.config.set("TRANSLATOR", "dat_int", self._dat_int)
        self.config.set("TRANSLATOR", "igr_int", self._igr_int)
        self.config.set("TRANSLATOR", "ind_int", self._ind_int)
        self.config.set("TRANSLATOR", "sou_int", self._sou_int)


    def build_dataset(self):
        #Creating dataset object
        print self._org_id
        dataset = Dataset(chain_for_id=self._org_id, int_for_id=self._dat_int, frequency=Dataset.YEARLY)
        self._dat_int += 1  # Updating id value

        #creating related objects
        #Organization
        org = Organization(chain_for_id=self._org_id,
                           name="FAO: Food and Agriculture Organization of the United Nations",
                           url="http://www.fao.org/")
        #datasource
        datasource = DataSource(name="Faostat. Statistcis division of the FAO",
                                chain_for_id=self._org_id,
                                int_for_id=self._sou_int)
        self._sou_int += 1
        #license
        license_type = License(description="Attribution and need permission for commercial use",
                                name="CopyrightFao",
                                republish=True,
                                url="http://www.fao.org/contact-us/terms/en/")
        #linking objects
        org.add_data_source(datasource)
        datasource.add_dataset(dataset)
        dataset.license_type = license_type

        #Returning result
        return dataset


    def build_model_objects_from_register(self, register):
        country = self.get_asociated_country(register[TranslatorConst.COUNTRY_CODE])
        if country is None:
            return  # It means that we are processing an obs from a non recognised country.
                    # We just have to ignore it

        new_observation = Observation(chain_for_id=self._org_id, int_for_id=self._obs_int)
        self._obs_int += 1

        self.add_indicator_to_observation(new_observation, register)  # DONE
        self.add_value_to_observation(new_observation, register)  # DONE
        self.add_computation_to_observation(new_observation)  # DONE
        self.add_reftime_to_observation(new_observation, register)  # DONE
        self.add_issued_to_observation(new_observation, register)  # DONE


        country.add_observation(new_observation)
        self.dataset.add_observation(new_observation)

    def add_issued_to_observation(self, observation, register):
        #Adding time in which the observation has been treated by us
        observation.issued = Instant(datetime.now())

    def add_reftime_to_observation(self, observation, register):
        observation.ref_time = YearInterval(year=register[TranslatorConst.YEAR])

    def add_computation_to_observation(self, observation):
        observation.computation = self.default_computation

    def add_value_to_observation(self, observation, register):
        value = Value()
        value.value_type = "float"
        if register[TranslatorConst.VALUE] is None or register[TranslatorConst.VALUE] == "":
            value.obs_status = Value.MISSING
        else:
            value.obs_status = Value.AVAILABLE
            value.value = register[TranslatorConst.VALUE]

        observation.value = value


    def add_measurement_unit_to_indicator(self, indicator, register):
        indicator.measurement_unit = MeasurementUnit(register[TranslatorConst.UNIT])


    def add_indicator_to_observation(self, observation, register):

        if register[TranslatorConst.ITEM_CODE] not in self.indicators_dict:
            self._add_indicator_to_dict(register)
        indicator = self.indicators_dict[register[TranslatorConst.ITEM_CODE]]
        observation.indicator = indicator

    def _add_indicator_to_dict(self, register):
        #name, description, id
        indicator = Indicator(name=register[TranslatorConst.ITEM],
                              description=self.get_indicator_description(register[TranslatorConst.ITEM_CODE]),
                              chain_for_id=self._org_id,
                              int_for_id=self._ind_int)
        self._ind_int += 1  # Updating id value
        self.add_measurement_unit_to_indicator(indicator, register)
        self.indicators_dict[register[TranslatorConst.ITEM_CODE]] = indicator

    def get_indicator_id(self, register):
        return "FAOSTAT_" + str(register[TranslatorConst.ITEM_CODE])

    def get_indicator_description(self, indicator_code):
        if indicator_code == 6601:
            return "Land Area. Total area in sq. km of the referred region"
        elif indicator_code == 6610:
            return "Agricultural land. Total area in sq. km. for agriculture of the referred region"
        elif indicator_code == 6661:
            return "Forest land. Total forest surface in sq. km of the referred region"
        elif indicator_code == 6621:
            return "Arable area. Total arable surface in sq. km. of the referred region"
        else:
            raise RuntimeError("Unknown indicator. No description found")


    def get_asociated_country(self, country_code):
        if country_code not in self.country_dict:
            try:
                self.country_dict[country_code] = self.reconciler.get_country_by_faostat_code(country_code)
            except UnknownCountryError:  # Trying to get an invalid country
                self.country_dict[country_code] = None  # By this, unsucessfull searches are executed only one time
                return None  # return None as a signal of "invalid country"
        return self.country_dict[country_code]
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

        
        
        
        
        
        
        
        
        
        
        
        
