'''
Created on 13/01/2014

@author: Dani
'''

import urllib2
import logging
import sys
from ConfigParser import ConfigParser
from es.weso.util.file_writer import FileWriter
class LandMatrixExtractorXML(object):
    
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        self.config = ConfigParser()
        self.config.read("../../../../files/configuration.ini")
        self.log = logging.getLogger('landmatrixlog')
    '''
    Downloads the entire Land Matrix database
    '''
    def run(self):
        try:
            self.log.info('Running Land matrix xml extractor...')
            response = urllib2.urlopen(self.config.get("LAND_MATRIX", "url_download"))
            xml_content = response.read()
            FileWriter.write_text_to_file(xml_content, self.config.get("LAND_MATRIX", "target_file"))       
            self.log.info('Land matrix xml extractor finished')
        except:
            e = sys.exc_info()[0]
            self.log.error("Unable to track data from {0}... Cause: {1}".format(self.config.get("LAND_MATRIX", "url_download"), e))
            raise
        
