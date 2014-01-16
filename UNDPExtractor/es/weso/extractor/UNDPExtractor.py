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
from es.weso.entities.DataTable import DataTable
from es.weso.util.file_writer import FileWriter

class UNDPExtractor(object):
    '''
    classdocs
    '''


    def __init__(self, extension):
        '''
        Constructor
        '''
        self.config = ConfigParser()
        self.config.read("../../../files/configuration.ini")
        self.extension = extension
        self.tables = self.parse_urls()
        self.log = logging.getLogger("UNDP_extractor")
    
    '''
    There is a file containing all the names and URLs of the databases to download. This
    method returns a list of DataTable containing all this information
    '''
    def parse_urls(self):  
        result = []
        
        file_urls = open(self.config.get("UNDP", "file_tables"))
        lines = file_urls.readlines();
        file_urls.close()
        
        for line in lines: 
            if(line.startswith("#") == False):
                line = line.replace("\r", "")
                line = line.replace("\n", "")
                arr = line.split("\t")
                print arr[0]
                result.append(DataTable(arr[0], arr[1] + "." + self.extension))
        return result

    '''
    Tracks the whole data form UNDP
    '''
    def run(self):
        self.log.info("Initializing data extraction from UNDP...")
        table_counter = 0
        for table in self.tables:
            table_counter += 1
            file_name = '../../../downloaded_data/Table' + str(table_counter) + "." + self.extension
            self.extract_data(table, file_name)
        self.log.info("Data extraction from UNDP done.")
        
    '''
    Tracks data from a single UNDP table
    '''
    def extract_data(self, table, file_name):
        try:
            self.log.info('Extracting data form {0}, with URL {1}...'.format(table.name, table.url))
            response = urllib2.urlopen(table.url)
            xml_content = response.read()
            FileWriter.write_text_to_file(xml_content, file_name)
            self.log.info('data from {0} extracted.'.format(table.name))
        except:  # catch all
            e = sys.exc_info()[0]
            self.log.exception("Error during the extraction from {0}. Cause: {1}. Data from that table ignored.".format(table.name, e))
            
        
        
        
        
        
        
        
        
        
        
