'''
Created on 14/01/2014

@author: Dani
'''

import urllib2
import sys

from es.weso.util.file_writer import FileWriter


class IpfriExtractor(object):
    '''
    classdocs
    '''

    def __init__(self, log, config):
        """
        Constructor

        """

        self.log = log
        self.config = config
        self.read_years()
        self.read_url_pattern()


    def read_years(self):
        '''
        This method put a list of available years in self.years
        '''
        #line_years should be a group of years separated by ","
        line_years = self.config.get("IPFRI", "available_years")
        self.years = line_years.split(",")


    def read_url_pattern(self):
        '''
        This method put a string in self.url_pattern, containing a URL
        in wich we should substitute "{year}" by a concrete year to
        dowload data of a certain date

        '''
        self.url_pattern = self.config.get("IPFRI", "url_pattern")



    def run(self):
        '''
        This method download all the info from IPFRI
        '''
        self.log.info("Initializing data extraction from IPFRI...")
        for year in self.years:
            self.download_year_data(year)
        self.log.info("Data extraction from IPFRI ended")



    def download_year_data(self, year):
        '''
        This method download info from a single year
        '''
        try:
            valid_url = self.url_pattern.replace("{year}", str(year))
            self.log.info("Tracking data from {0} ...".format(valid_url))
            response = urllib2.urlopen(valid_url)
            xls_content = response.read()
            file_name = self.config.get("IPFRI", "target_downloaded_file_pattern").replace("{year}", str(year))
            FileWriter.write_binary_to_file(xls_content, file_name)
            self.log.info("Tracking data from {0} ended.".format(valid_url))

        except BaseException as e:
            raise RuntimeError("Unable to download info from {0}. Data of that year will be ignored. Cause: {1}".
                               format(str(year), e.message))
        
        
        