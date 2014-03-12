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


from datetime import datetime

from lpentities.year_interval import YearInterval


class ModelObjectBuilder(object):
    '''
    classdocs
    '''


    def __init__(self, registers, config, log):
        self.log = log
        self.config = config
        self.registers = registers
        self.country_list = []
        self.dataset = self.build_dataset()

        self.default_computation = Computation(Computation.RAW)

        '''
        Constructor
        '''

    def build_dataset(self):
        #Creating dataset object
        dataset = Dataset(dataset_id="resources_land_e", frequency="")

        #creating related objects
        #Organization
        org = Organization(name="FAO: Food and Agriculture Organization of the United Nations", url="http://www.fao.org/")
        #datasource
        datasource = DataSource(source_id="faostat", name="Faostat. Statistcis division of the FAO")
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

    def run(self):

        for register in self.registers:
            self.build_model_objects_from_register(register)
        return self.dataset

    def build_model_objects_from_register(self, register):
        country = self.get_asociated_country(register[TranslatorConst.COUNTRY])  # Done. BUT REVIEW HOW WE GET COUNTRIES

        new_observation = Observation(observation_id="abba")

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
        #name, description, id
        indicator = Indicator(name=register[TranslatorConst.ITEM],
                              description=self.get_indicator_description(register[TranslatorConst.ITEM_CODE]),
                              indicator_id=self.get_indicator_id(register))
        self.add_measurement_unit_to_indicator(indicator, register)
        observation.indicator = indicator

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
        '''
        Strategy: we are adding the filed "country_name" to the entity class country
        First we check if in our country list exist an object that has a field
        counrtry_code with the same value as the received one. If not, we ask for
        an object country and add it to self.country_list
        
        There are already code attributes in Country class, but not the faostat one
        that we are using. We are adding a new attribute to the standard Country
        objects to work with only in this method
        '''
        country_found = None
        for country in self.country_list:
            if country.country_code == country_code:
                country_found = country
                break
        if country_found is not None:
            return country_found
        else:
            new_country = self.TEMPORAL_get_country(country_code)
            new_country.country_code = country_code
            self.country_list.append(new_country)
            return new_country


    def TEMPORAL_get_country(self, country_name):
        no_whites_name = country_name.replace(" ", "")
        return Country(name=country_name, iso3=no_whites_name, iso2=no_whites_name)

        
        
        
        
        
        
        
        
        
        
        
        
