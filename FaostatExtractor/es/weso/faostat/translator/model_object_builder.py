'''
Created on 02/02/2014

@author: Dani
'''
from es.weso.entities.observation import Observation
from es.weso.entities.country import Country
from es.weso.entities.indicator import Indicator
from es.weso.entities.license import License
from es.weso.entities.measurement_unit import MeasurementUnit
from es.weso.entities.float_value import FloatValue
from es.weso.entities.computation import Computation
from es.weso.entities.instant import Instant
from es.weso.entities.data_source import DataSource
from es.weso.entities.organization import Organization
from es.weso.entities.dataset import Dataset
from es.weso.entities.slice import Slice
from es.weso.faostat.translator.translator_const import TranslatorConst



#from es.weso.faostat.translator.faostat_translator import FaostatTranslator
class ModelObjectBuilder(object):
    '''
    classdocs
    '''


    def __init__(self, registers, config, log):
        self.log = log
        self.config = config
        self.registers = registers
        print len(registers)
        self.country_list = []
        self.dataset = Dataset("Weekly", None)
        '''
        Constructor
        '''
    def run(self):
        for register in self.registers:
            self.build_model_objects_from_register(register)
        return self.dataset
    
    def build_model_objects_from_register(self, register):
        country = self.get_asociated_country(register[TranslatorConst.COUNTRY]) 
        
        new_observation = Observation()
        
        self.add_indicator_to_observation(new_observation, register)
        self.add_measurement_unit_to_observation(new_observation, register)
        self.add_value_to_observation(new_observation, register)
        self.add_computation_to_observation(new_observation, register)
        self.add_reftime_to_observation(new_observation, register)
        self.add_issued_to_observation(new_observation, register)
        self.add_data_source_to_observation(new_observation, register)
        self.add_slice_to_observation(new_observation, register)
        
        country.add_observation(new_observation)
        
    def add_slice_to_observation(self, observation, register):
        if not "default_slice" in self.__dict__:
            self.default_slice = Slice("slice1") #Review this id
            self.dataset.add_slice(self.default_slice)
        self.default_slice.add_observation(observation)
                    
    def add_data_source_to_observation(self, observation, register):
        if "default_data_source" in self.__dict__:
            observation.data_source = self.default_data_source
        else:
            org = Organization("FAO: Food and Agriculture Organization of the United Nations")
            self.default_data_source = DataSource("FAOSTAT", "Large time-series and cross sectional\
                 data relating to hunger, food and agriculture for 245 \
                 countries and territories and 35 regional areas, from \
                 1961 to the most recent year. Innovate tools for visualization \
                 and basic statistical analysis", org)
            observation.data_source = self.default_data_source

    def add_issued_to_observation(self, observation, register):
        '''
        WE SHOULD SCRAP THE WEB IN ORDER TO GET THE DATE
        OF THE LAST UPDATE. AT THIS POINT, WE WILL INTRODUCE IT
        HARD-CODED
        
        09-may-2013
        '''
        observation.issued = Instant(2013)  # Now, we are only regarding at year,
                                            # not a complete date

    def add_reftime_to_observation(self, observation, register):
        observation.ref_time = Instant(register[TranslatorConst.YEAR])
    
    def add_computation_to_observation(self, observation, register):
        '''
        All the info is directly taken form the source, so all the computations are raw.
        There will be a single computation object. No need to create one for each obs.
        '''
        if "default_computation" in self.__dict__:
            observation.computation = self.default_computation
        else:
            self.default_computation = Computation(Computation.RAW)
            observation.computation = self.default_computation

    def add_value_to_observation(self, observation, register):
        observation.value = FloatValue(register[TranslatorConst.VALUE])

    def add_measurement_unit_to_observation(self, observation, register):
        observation.measure_unit = MeasurementUnit(register[TranslatorConst.UNIT])
        
        
    def add_indicator_to_observation(self, observation, register):
        indicator = Indicator(register[TranslatorConst.ITEM], \
                        self.get_indicator_description(register[TranslatorConst.ITEM_CODE]), \
                        self.get_license_object())
        observation.indicator = indicator
    
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
            
        
        
    def get_license_object(self):
        if 'default_license' in self.__dict__:
            return self.default_license
        else:
            self.default_license = License("Attribution and need permission for commercial use", \
                                           "http://www.fao.org/contact-us/terms/en/")
            return self.default_license


    def get_asociated_country(self, country_name):
        '''
        Strategy: we are adding the filed "country_name" to the entity class country
        First we check if in our country list exist an object that has a field
        country_name with the same value as the received one. It not, we aske for
        an object country and add it to self.country_list
        
        There is already an attributte name in Country class, that will probably
        contain the same value as the one we are introduccion in the objects, but
        it could not happend always. If country_name is not the same that appears
        in the official and common country list, the value will differ, and the
        strategy we are using would fail, creating duplicated objects that represents
        the same entity
        '''
        country_found = None
        for country in self.country_list:
            if country.country_name == country_name:
                country_found = country
                break
        if country_found != None:
            return country_found
        else:
            new_country = self.TEMPORAL_get_country(country_name)
            new_country.country_name = country_name
            self.country_list.append(new_country)
            return new_country 
        '''
        HERE WE SHOULD MAKE A REQUEST TO THE COUNTRY NORMALIZER.
        HOWEVER, AT THIS POINT, WE CAN AVOID THAT BY CALLING A METHOD
        '''
    
    def TEMPORAL_get_country(self, country_name):
        return Country(country_name, None, "http://someUri/" + country_name, country_name, country_name)
        
        
        
        
        
        
        
        
        
        
        
        
