'''
Created on 13/01/2014

@author: Dani

This class is used to download the entire database of UNDP. The constructor
receives a format to dowload it (xml, csv, json). To init the process the
"run" method should be called
'''
import sys
import logging
import urllib2
from ConfigParser import ConfigParser
from es.weso.unpd_entities.DataTable import DataTable
from es.weso.util.file_writer import FileWriter

class UNDPExtractor(object):
    '''
    classdocs
    '''


    def __init__(self, config, log,  extension):
        '''
        Constructor

        '''

        self.config = config
        self.log = log
        self.extension = extension
        self.tables = self.parse_urls()
    

    def parse_urls(self):
        '''
        There is a file containing all the names and URLs of the databases to download. This
        method returns a list of DataTable containing all this information
        '''
        result = []
        
        file_urls = open(self.config.get("UNDP", "file_tables"))
        lines = file_urls.readlines()
        file_urls.close()
        
        for line in lines: 
            if not line.startswith("#"):
                line = line.replace("\r", "")
                line = line.replace("\n", "")
                arr = line.split("\t")
                result.append(DataTable(arr[0], arr[1] + "." + self.extension))
        return result

    def run(self):
        '''
        Tracks the whole data form UNDP
        '''

        self.log.info("Initializing data extraction from UNDP...")
        table_counter = 0
        for table in self.tables:
            table_counter += 1
            file_name = '../../../downloaded_data/Table' + str(table_counter) + "." + self.extension
            self.extract_data(table, file_name)
        self.log.info("Data extraction from UNDP done.")
        

    def extract_data(self, table, file_name):
        """
       Tracks data from a single UNDP table

       """
        try:
            self.log.info('Extracting data form {0}, with URL {1}...'.format(table.name, table.url))
            response = urllib2.urlopen(table.url)
            xml_content = response.read()
            FileWriter.write_text_to_file(xml_content, file_name)
            self.log.info('data from {0} extracted.'.format(table.name))
        except BaseException as e:  # catch all
            self.log.warning("Error during the extraction from {0}. Cause: {1}. Data from that table ignored.".format(table.name, e.message))
            
        
        
        
        
        
        
        
        
        
        
