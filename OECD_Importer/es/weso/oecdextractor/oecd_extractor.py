'''
Created on 10/01/2014

@author: Miguel Otero
'''

import logging
from es.weso.oecdextractor.rest.rest_client import RestClient
from es.weso.oecdextractor.entities.location import Location
from es.weso.oecdextractor.entities.income import Income
from es.weso.oecdextractor.entities.region import Region
from es.weso.oecdextractor.entities.variable import Variable
from es.weso.oecdextractor.entities.data import Data

class OECDExtractor(object):
    '''
    This class calls the rest_client module and manages its responses creating objects
    that represent each dimension's member and each observation.
    '''
    
    logger = logging.getLogger('oecd_extractor')
    rest_client = RestClient()

    def __init__(self):
        '''
        Constructor
        '''
        self.incomes = []
        self.locations = []
        self.regions = []
        self.variables = []
        self.data = []
        
        
    def extract_members(self, dataset_id):
        '''
        This function calls the rest_client module and, for each value obtained, it
        creates an entity depending on its type (income, location, region or variable)
        and stores it in the pertinent array. If the value has been already stored, this
        is notified in the log.
        '''
        self.logger.info('Extracting members')
        values = self.rest_client.obtain_members(dataset_id)['value']
        for value in values:
            if value['DimensionCode'] == 'INCOME':
                income = Income(value['MemberName'], 
                                value['MemberCode'], 
                                value['Order'])
                if income not in self.incomes:
                    self.incomes.append(income)
                else:
                    self.logger.info('Income ' + income.code + ' already added')
            elif value['DimensionCode'] == 'LOCATION':
                location = Location(value['MemberName'], 
                                    value['MemberCode'], 
                                    value['ParentMemberCode'], 
                                    value['Order'], 
                                    value['MemberMetadata'])
                if location not in self.locations:
                    self.locations.append(location)
                else:
                    self.logger.info('Location ' + location.iso3_code + ' already added')
            elif value['DimensionCode'] == 'REGION':
                region = Region(value['MemberName'], 
                                value['MemberCode'], 
                                value['Order'])
                if region not in self.regions:
                    self.regions.append(region)
                else:
                    self.logger.info('Region ' + region.name + ' already added')
            elif value['DimensionCode'] == 'VARIABLE':
                variable = Variable(value['MemberName'], 
                                    value['MemberCode'], 
                                    value['ParentMemberCode'], 
                                    value['Order'], 
                                    value['MemberMetadata'])
                if variable not in self.variables:
                    self.variables.append(variable)
                else:
                    self.logger.info('Variable ' + variable.code + ' already added')
        
    def extract_data(self, dataset_id):
        '''
        This function calls the rest_client module and, for each value obtained, it
        creates an observation object based on the codes of each dimension and the members
        of these dimensions obtained in extract_members function
        '''
        self.logger.info('Extracting data')
        elements = self.rest_client.obtain_data(dataset_id)['value']
        for element in elements:
            income = self.find_element('INCOME', element['INCOME'])
            location = self.find_element('LOCATION', element['LOCATION'])
            region = self.find_element('REGION', element['REGION'])
            variable = self.find_element('VARIABLE', element['VARIABLE'])
            if 'YEAR' in element:
                year = element['YEAR']
            else:
                year = element['TIME']
            value = element['Value']
            data_element = Data(income, 
                                location, 
                                region,
                                variable,
                                year,
                                value)
            self.data.append(data_element)
            print data_element.income.code + ' ' + data_element.location.iso3_code + ' ' + data_element.region.name + ' ' + data_element.variable.name + ' ' + data_element.year + data_element.value + '\n'
        
            
    def find_element(self, element_type, key):
        '''
        This function is used by extract_data for locating an entity in its array by the
        entity code
        '''
        if element_type == 'INCOME':
            for income in self.incomes:
                if income.code == key:
                    return income
        elif element_type == 'LOCATION':
            for location in self.locations:
                if location.iso3_code == key:
                    return location
        elif element_type == 'REGION':
            for region in self.regions:
                if region.code == key:
                    return region
        elif element_type == 'VARIABLE':
            for variable in self.variables:
                if variable.code == key:
                    return variable
            