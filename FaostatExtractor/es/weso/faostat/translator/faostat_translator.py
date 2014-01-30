'''
Created on 27/01/2014

@author: Dani
'''

import logging
import sys
import os
import re
from ConfigParser import ConfigParser
class FaostatTranslator(object):
    '''
    classdocs
    '''

    COUNTRY_CODE = 0
    COUNTRY = 1
    ITEM_CODE = 2
    ITEM = 3
    ELEMENT_GROUP = 4
    ELEMENT_CODE = 5
    ELEMENT = 6
    YEAR = 7
    UNIT = 8
    VALUE = 9
    FLAG = 10
    EXPECTED_NUMBER_OF_FILES = 11

    def __init__(self):
        self.config = ConfigParser()
        self.config.read("../../../../files/configuration.ini")
        self.log = logging.getLogger('faostatlog')
        self.observations = [] #it will contains all the data encapsuled in model objects
        '''
        Constructor
        '''

    def run(self, look_for_historical):
        '''
        Steps:
        
        Turn into list with fields
        Filter if needed by date
        Filter by indicator needed
        Filter checking data quality
        Build model objects
        '''
        self.registers = self.turn_raw_data_into_registers()
        
        
    def get_csv_file_name(self):
        csv_file = os.listdir(self.config.get("FAOSTAT", "data_file_path"))[0]
        if csv_file[-4:] != '.csv':
            raise RuntimeError("Unexpected content while looking for indicators. CSV file expected but {0} was found".format(csv_file))
        return self.config.get("FAOSTAT", "data_file_path") + "/" + csv_file
        
    
    def turn_raw_data_into_registers(self):
        raw_data_file = open(self.get_csv_file_name())
        lines = raw_data_file.readlines()
        raw_data_file.close()
            
        for i in range(1, len(lines)):
            try:
                candidate_register = self.create_field_list(lines[i], i+1)
                '''
                FILTROS
                '''
            except RuntimeError as e:
                print e
    
    '''
    Return a list of all the values in a row of the csv file. 
    It receives a line with fields separated with "," and the
    number of that line in the original file 
    '''
    def create_field_list(self, line, index):
        primitive_data = line.split(",\"") #The CSV file separate fields with comma, but there are commas inside
                                            #some field,s so we can split by ',' .All the fields but the first
                                            #starts with the character '"', so if we split by ",\"", we get the
                                            #expected result. We have to consider this when parsing values
        if len(primitive_data) != self.EXPECTED_NUMBER_OF_FILES:
            raise RuntimeError("Row {0} contains an non expected number of fileds. The row must be ignored".format(str(index)))
        
        return self.parse_register_fields(primitive_data)
    
    def parse_register_fields(self, primitive_data):
        result = []     
#         result [self.COUNTRY_CODE] = self.parse_country_code(primitive_data[self.COUNTRY_CODE])
        result.insert(self.COUNTRY_CODE, self.parse_country_code(primitive_data[self.COUNTRY_CODE]))
        result.insert(self.COUNTRY, self.parse_country(primitive_data[self.COUNTRY]))
        result.insert(self.ITEM_CODE,  self.parse_item_code(primitive_data[self.ITEM_CODE]))
        result.insert(self.ITEM,  self.parse_item(primitive_data[self.ITEM]))
        result.insert(self.ELEMENT_GROUP,  self.parse_element_group(primitive_data[self.ELEMENT_GROUP]))
        result.insert(self.ELEMENT_CODE,  self.parse_element_code(primitive_data[self.ELEMENT_CODE]))
        result.insert(self.ELEMENT,  self.parse_element(primitive_data[self.ELEMENT]))
        result.insert(self.YEAR,  self.parse_year(primitive_data[self.YEAR]))
        result.insert(self.UNIT,  self.parse_unit(primitive_data[self.UNIT]))
        result.insert(self.VALUE,  self.parse_value(primitive_data[self.VALUE]))
        result.insert(self.FLAG,  self.parse_flag(primitive_data[self.FLAG]))
        print '_________'
        for i in result:
            print i
            
        print '_________'
    
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
        return re.sub('\.|\"',"", primitive_data)   
     
    def parse_flag(self, primitive_data):
        '''
        We are receiving a flag sequence with an '"' at the end and a whitespace
        '''
        return primitive_data[:-2]    
    
    
        
        
        
        
        
        
        
        
        
        