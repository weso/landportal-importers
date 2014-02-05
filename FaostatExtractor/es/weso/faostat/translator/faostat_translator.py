'''
Created on 27/01/2014

@author: Dani
'''

import logging
import os
import re
from datetime import date
from ConfigParser import ConfigParser
from es.weso.faostat.translator.indicator_needed_resolver import IndicatorNeededResolver
from es.weso.faostat.translator.model_object_builder import ModelObjectBuilder
from es.weso.faostat.translator.translator_const import TranslatorConst
from es.weso.model_to_xml.model_to_xml_transformer import ModelToXMLTransformer
class FaostatTranslator(object):
    '''
    classdocs
    '''

    def __init__(self):
        self.config = ConfigParser()
        self.config.read("../../../../files/configuration.ini")
        self.log = logging.getLogger('faostatlog')
        self.observations = []  # it will contains all the data encapsuled in model objects
        self.needed_indicators = IndicatorNeededResolver(self.config, self.log).run()
        self.land_area_reference = {}  # It will data with the general country areas
                                    # The key of the dictionary will be formed by
                                    # country_name + year, and will contain the land_area
                                    # data associated to this value par
        '''
        Constructor
        '''

    def run(self, look_for_historical):
        '''
        Steps:
        
        Turn into list with fields
        Build model objects
        
        '''
        
        registers = self.turn_raw_data_into_registers(look_for_historical)
        dataset_model = self.build_model_objects_from_registers(registers)
        registers = None #Liberating memory
        self.generate_xml_from_dataset_model(dataset_model)
        
        #calculated_registers = RelativeRegistersCalculator(registers, self.land_area_reference)
        #calculated_registers = RelativeRegistersCalculator(registers, self.land_area_reference).run()
        #model_objects = turn_registers_into_model_objects(registers)
        #model_objects.append
        
    def generate_xml_from_dataset_model(self, dataset_model):
        xml_gen = ModelToXMLTransformer(dataset_model)
        xml_gen.run()
            
    def build_model_objects_from_registers(self, registers):
        builder = ModelObjectBuilder(registers, self.config, self.log)
        return builder.run()
    
    def get_csv_file_name(self):
        csv_file = os.listdir(self.config.get("FAOSTAT", "data_file_path"))[0]
        if csv_file[-4:] != '.csv':
            raise RuntimeError("Unexpected content while looking for indicators\
                . CSV file expected but {0} was found".format(csv_file))
        return self.config.get("FAOSTAT", "data_file_path") + "/" + csv_file
        
    
    def turn_raw_data_into_registers(self, look_for_historical):
        raw_data_file = open(self.get_csv_file_name())
        lines = raw_data_file.readlines()
        raw_data_file.close()
        result = []
        for i in range(1, len(lines)):
            try:
                candidate_register = self.create_field_list(lines[i], i + 1)
                if(self.pass_filters(candidate_register, look_for_historical)):
                    self.actualize_land_area_data_if_needed(candidate_register)      
                    result.append(self.create_field_list(lines[i], i + 1))  
            except RuntimeError as e:
                self.log.error("Error while parsing a row form the csv_file: {0}. Row will be ignored".format(str(e)))
        return result
    
    
    def actualize_land_area_data_if_needed(self, candidate_register):
        if not candidate_register[TranslatorConst.ITEM_CODE] == TranslatorConst.CODE_LAND_AREA:
            return
        key = self.key_for_land_area_ref(candidate_register)
        if(not self.land_area_reference.has_key(key)):
            self.land_area_reference[key] = candidate_register[TranslatorConst.VALUE]
        else:
            raise RuntimeError("Duplicated land area value for country {0} and \
                year {1}. The program will continue ignoring the new value, but\
                it looks like the data is corrupted"\
                .format(candidate_register[TranslatorConst.COUNTRY], candidate_register[TranslatorConst.YEAR]))       
        
    def key_for_land_area_ref(self, candidate_register):
        return str(candidate_register[TranslatorConst.COUNTRY_CODE]) + "_" + str(candidate_register[TranslatorConst.YEAR])
    
    def pass_filters(self, candidate_register, look_for_historical):
        '''
        Steps:
        Filter if needed by date
        Filter by indicator needed
        Filter checking data quality
        '''
        if( not look_for_historical and not self.pass_filter_current_date(candidate_register)):
            return False
        elif(not self.pass_filter_indicator_needed(candidate_register)):
            return False
        return True
    
    def pass_filter_current_date(self, candidate_register):
        if(candidate_register[TranslatorConst.YEAR] == date.today().year):
            return True
        return False
    
    def pass_filter_indicator_needed(self, candidate_register):
        if(candidate_register[TranslatorConst.ITEM] in self.needed_indicators):
            return True
        return False

    
    '''
    Return a list of all the values in a row of the csv file. 
    It receives a line with fields separated with "," and the
    number of that line in the original file 
    '''
    def create_field_list(self, line, index):
        primitive_data = line.split(",\"")  # The CSV file separate fields with comma, but there are commas inside
                                            # some fields, so we can split by ',' .All the fields but the first
                                            # starts with the character '"', so if we split by ",\"", we get the
                                            # expected result. We have to consider this when parsing values
        if len(primitive_data) != TranslatorConst.EXPECTED_NUMBER_OF_FILES:
            raise RuntimeError("Row {0} contains an non expected number of fileds. \
            The row must be ignored".format(str(index)))
        
        return self.parse_register_fields(primitive_data)
    
    '''
    Invokes the parsing order for each single data and put the result 
    in a common list
    '''
    def parse_register_fields(self, primitive_data):
        result = []     
        result.insert(TranslatorConst.COUNTRY_CODE, self.parse_country_code(primitive_data[TranslatorConst.COUNTRY_CODE]))
        result.insert(TranslatorConst.COUNTRY, self.parse_country(primitive_data[TranslatorConst.COUNTRY]))
        result.insert(TranslatorConst.ITEM_CODE, self.parse_item_code(primitive_data[TranslatorConst.ITEM_CODE]))
        result.insert(TranslatorConst.ITEM, self.parse_item(primitive_data[TranslatorConst.ITEM]))
        result.insert(TranslatorConst.ELEMENT_GROUP, self.parse_element_group(primitive_data[TranslatorConst.ELEMENT_GROUP]))
        result.insert(TranslatorConst.ELEMENT_CODE, self.parse_element_code(primitive_data[TranslatorConst.ELEMENT_CODE]))
        result.insert(TranslatorConst.ELEMENT, self.parse_element(primitive_data[TranslatorConst.ELEMENT]))
        result.insert(TranslatorConst.YEAR, self.parse_year(primitive_data[TranslatorConst.YEAR]))
        result.insert(TranslatorConst.UNIT, self.parse_unit(primitive_data[TranslatorConst.UNIT]))
        result.insert(TranslatorConst.VALUE, self.parse_value(primitive_data[TranslatorConst.VALUE]))
        result.insert(TranslatorConst.FLAG, self.parse_flag(primitive_data[TranslatorConst.FLAG]))
        
        return result
    
    def parse_country_code(self, primitive_data):
        '''
        If the received chain does not contain '"', it should be casteable
        to int. If it does, we have first to remove that '"' characters.
        They shloud be at the begening and the end of the string
        '''
        if not '"' in primitive_data:
            return int(primitive_data)
        else:
            return int(primitive_data[1:-1])
        
               
     
    def parse_country(self, primitive_data):
        '''
        We are receiving the name of a country with an '"' at the end
        '''
        return primitive_data[:-1]
     
    def parse_item_code(self, primitive_data):
        '''
        We are receiving an string containing a int number with a "'" at the end
        '''
        return int(primitive_data[:-1])
         
    def parse_item(self, primitive_data):
        '''
        We are receiving the name of an item with an '"' at the end
        '''
        return primitive_data[:-1]    
     
    def parse_element_group(self, primitive_data):
        '''
        We are receiving an string containing a int number with a "'" at the end
        '''
        return int(primitive_data[:-1])

   
    def parse_element_code(self, primitive_data):
        '''
        We are receiving an string containing a int number with a "'" at the end
        '''
        return int(primitive_data[:-1])  
     
    def parse_element(self, primitive_data):
        '''
        We are receiving the name of an element with an '"' at the end
        '''
        return primitive_data[:-1]    
     
    def parse_year(self, primitive_data):
        '''
        We are receiving an string containing a int number with a "'" at the end
        '''
        return int(primitive_data[:-1])  
     
    def parse_unit(self, primitive_data):
        '''
        We are receiving the name of the measure unit with an '"' at the end
        '''
        return primitive_data[:-1]    
     
    def parse_value(self, primitive_data):
        '''
        We are receiving a number with an " at the end and possibly a "."
        because of ot presentation format. Ej: 1000 = 1.000
        I THINK it works like this. It also coulb be expressing decimals.
        We have to check that
        '''
        return re.sub('\.|\"', "", primitive_data)   
     
    def parse_flag(self, primitive_data):
        '''
        We are receiving a flag sequence with an '"' at the end and a whitespace
        '''
        return primitive_data[:-2]    
    
    
        
        
        
        
        
        
        
        
        
        
