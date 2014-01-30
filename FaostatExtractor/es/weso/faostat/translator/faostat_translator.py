'''
Created on 27/01/2014

@author: Dani
'''

import logging
import sys
import os
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
        try:
            raw_data_file = open(self.get_csv_file_name())
            lines = raw_data_file.readlines()
            raw_data_file.close()
        except RuntimeError as e:
            print e
            return
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
        result = []
        primitive_data = line.split(",\"")
        if len(primitive_data) != self.EXPECTED_NUMBER_OF_FILES:
            raise RuntimeError("Row {0} contains an non expected number of fileds. The row must be ignored".format(str(index)))
        return result
        
        
        
        
        
        
        
        
        
        
        