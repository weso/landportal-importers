'''
Created on 10/02/2014

@author: Dani
'''
import logging
from ConfigParser import ConfigParser
from es.weso.countryrec.parser.file_parser import FileParser 
class CountryReconciler(object):
    '''
    classdocs
    '''


    def __init__(self):
        self.config = ConfigParser()
        self.config.read("../../../../files/configuration.ini")
        self.log = logging.getLogger("countryRec.log")
        self.clist = FileParser(self.config, self.log).run()
        '''
        Constructor
        '''
    
    def get_country_by_name(self, target_name):
        for country in self.clist:
            if country.get_name() == target_name:
                return self.convert_parsed_country_into_model_country(country)
                
        raise NoCountryFoundException(name = target_name)
    
    
    def get_country_by_iso3(self, target_iso3):
        for country in self.clist:
            if country.get_iso3() == target_iso3:
                return self.convert_parsed_country_into_model_country(country)
        raise NoCountryFoundException(iso3 = target_iso3)
    
    
    def get_country_by_un_code(self, target_un_code):
        for country in self.clist:
            if country.get_un_code() == target_un_code:
                return self.convert_parsed_country_into_model_country(country)
        raise NoCountryFoundException(un_code = target_un_code)
    
    
    def convert_parsed_country_into_model_country(self, parsed_country):
        #ADD REFF TO ENTITIES PROJECT
        return None
    
class NoCountryFoundException(Exception):
    def __init__(self, name=None, iso3=None, un_code=None):
        self.name = name
        self.iso3 = iso3
        self.un_code = None
    
    def __str__(self):
        return "No country found." + self.available_country_data()
    
    def available_country_data(self):
        result = ""
        if not self.name == None:
            result += "Name: {0}".format(self.name)
        if not self.iso3 == None:
            result += "ISO3: {0}".format(self.iso3)
        if not self.un_code == None:
            result += "UN_code: {0}".format(self.un_code)
        return result
