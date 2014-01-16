'''
Created on 14/01/2014

@author: Dani
'''
import logging
import urllib2
import sys
from ConfigParser import ConfigParser
from es.weso.util.file_writer import FileWriter
class IpfriExtractor(object):
    '''
    classdocs
    '''

    def __init__(self):
        self.log = logging.getLogger('ipfriextractor')
        self.configure_properties()
        self.read_years()
        self.read_url_pattern()
        '''
        Constructor
        '''
    '''
    This method put a properties file in self.config
    '''    
    def configure_properties(self):
        self.config = ConfigParser()
        self.config.read("../../../files/configuration.ini")
    
    '''
    This method put a list of available years in self.years 
    '''
    def read_years(self):
        #line_years should be a group of years separated by ","
        line_years = self.config.get("IPFRI", "available_years")
        self.years =  line_years.split(",")
    
    '''
    This method put a string in self.url_pattern, containing a URL
    in wich we should substitute "{year}" by a concrete year to
    dowload data of a certain date
    '''
    def read_url_pattern(self):
        self.url_pattern = self.config.get("IPFRI", "url_pattern")
        
    '''
    This method download all the info from IPFRI
    '''
    def run(self):
        self.log.info("Initializing data extraction from IPFRI...")
        for year in self.years:
            self.download_year_data(year)
        self.log.info("Data extraction from IPFRI ended")
    
    '''
    This method download info from a single year
    '''
    def download_year_data(self, year):
        try:
            valid_url = self.url_pattern.replace("{year}", str(year))
            self.log.info("Tracking data from {0} ...".format(valid_url))
            response = urllib2.urlopen(valid_url)
            xls_content = response.read()
            file_name = self.config.get("IPFRI","target_dowloaded_file_pattern").replace("{year}", str(year))
            FileWriter. write_binary_to_file(xls_content, file_name)
            self.log.info("Tracking data from {0} ended.".format(valid_url))
            
        except:
            e = sys.exc_info()[0]
            self.log.exception("Unable to download info from {0}. Data of that year will be ignored. Cause: {1}".format(str(year), e))
            raise #delete on final version
        
        
        